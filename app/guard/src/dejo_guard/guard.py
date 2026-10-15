"""The guard: read the page, name the action, let ArmorIQ decide, then act or refuse.

Hooked into Dejo at the two places a page is touched:
  GuardedSession._perform   every live action (`dejo_act`), after Dejo has found the element
                            and before Playwright touches it.
  GuardedExecutor._do       every step of a saved replay (`dejo_run`), classified from the
                            LIVE page — never from the recording, which may be out of date.

And one place under both: while an action runs, any write request it fires (POST, PUT, PATCH,
DELETE) is paused in the browser until ArmorIQ has decided it. That is how a plain-looking
"Continue" button whose script posts a payment is still caught.
"""

from __future__ import annotations

import contextlib
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from dejo import actions
from dejo.executor import Executor
from dejo.operations import ActionFailed, Session

from .armor import Decision, Gate
from .classes import DEFAULT_PLAN, classify, network_class
from .facts import ELEMENT_FACTS_JS, FRAME_PAYMENT_JS, PageFacts, from_element, site_of
from .feed import Feed

# The user's task words → the extra classes that task may use. A fixed table, printed by
# `dejo-guard plan "<task>"`, so the user can see exactly what a sentence unlocks. Anything
# not unlocked here is outside the plan, and ArmorIQ refuses it as drift.
TASK_WORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (r"\b(buy|purchase|order|checkout|check out|pay|place)\b", ("submit_form", "state_change", "submit_payment")),
    (r"\b(add|cart|basket|reserve|save|send|post|submit|apply|subscribe|sign up|register|create|update)\b",
     ("submit_form", "state_change")),
    (r"\b(upload|attach)\b", ("upload",)),
)

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
# Requests a page sends on its own (analytics pings) are not something the agent did.
WATCHED_TYPES = {"document", "fetch", "xhr"}
# A class that already IS a write, approved as such: its own request is expected.
WRITES = {"submit_form", "submit_payment", "state_change"}
# Classes whose action only loads a page: writes during them belong to the page, not to the agent.
PAGE_LOADS = {"navigate", "new_domain", "read", "download"}
# How long an action's window may stay open for the writes it fires, and how much quiet closes it.
WRITE_SETTLE_MS = 4000
QUIET_MS = 700


def plan_for(goal: str) -> tuple[str, ...]:
    classes = list(DEFAULT_PLAN)
    for pattern, extra in TASK_WORDS:
        if re.search(pattern, goal, re.IGNORECASE):
            classes.extend(extra)
    return tuple(dict.fromkeys(classes))


class GuardStop(ActionFailed):
    """ArmorIQ did not allow this action. Carries the decision so the reply can explain it."""

    def __init__(self, decision: Decision, facts: PageFacts, because: str):
        self.decision = decision
        self.facts = facts
        self.because = because
        super().__init__(_say(decision, because))


def _say(d: Decision, because: str) -> str:
    if d.action == "hold":
        return (f"HELD by ArmorIQ: `{d.cls}` ({because}) needs approval. Ask the user to approve it in "
                f"ArmorIQ → Held Actions, then call guard_wait. Do not try another way round.")
    return f"BLOCKED by ArmorIQ: `{d.cls}` ({because}) — {d.reason}. Do not try another way round."


@dataclass
class Pending:
    """A held action, kept so it can run the moment ArmorIQ says the hold was approved."""

    decision: Decision
    redo: Any  # zero-argument callable that performs the action again
    facts: PageFacts
    because: str


@dataclass
class _Window:
    """One agent action, while the writes it fires are still arriving."""

    facts: PageFacts
    cls: str
    intent: str
    redo: Any
    stopped: list[GuardStop] = field(default_factory=list)
    passed: list[Any] = field(default_factory=list)


@dataclass
class Guard:
    gate: Gate = field(default_factory=Gate)
    feed: Feed = field(default_factory=Feed)
    pending: dict[str, Pending] = field(default_factory=dict)
    last_stop: GuardStop | None = None
    notices: list[str] = field(default_factory=list)  # writes refused after an action had returned
    _armed: set[int] = field(default_factory=set)
    _window: _Window | None = None
    _last_window: _Window | None = None
    _last_request_at: float = 0.0

    # ------------------------------------------------------------- the task

    def start_task(self, goal: str, sites: set[str], classes: tuple[str, ...] | None = None) -> dict[str, Any]:
        task = self.gate.start_task(goal, classes or plan_for(goal), sites)
        self.feed.write({"task_id": task.id, "goal": goal, "action": "plan", "cls": ",".join(task.classes),
                         "decision": "refused" if task.refused else "signed", "reason": task.refused,
                         "plan_id": task.plan_id, "because": f"sites: {', '.join(sorted(sites)) or 'any'}"})
        return {"task_id": task.id, "plan_id": task.plan_id, "classes": list(task.classes),
                "sites": sorted(task.sites), "refused": task.refused}

    def ensure_task(self, intent: str, url: str | None) -> None:
        """No declared task yet: declare the narrowest one — look around this one site."""
        if self.gate.task is None:
            site = site_of(url) if url and url.startswith("http") else ""
            self.start_task(intent or "browse", {site} if site else set(), DEFAULT_PLAN)

    # ------------------------------------------------------------- reading

    def facts(self, page: Any, action: str, target: Any = None, value: str | None = None) -> PageFacts:
        url = _safe(lambda: page.url, "")
        if action in ("goto", "new_tab"):
            return PageFacts(action=action, page_url=url, target_url=value)
        raw = None
        if target is not None:
            raw = _safe(lambda: target.evaluate(ELEMENT_FACTS_JS), None)
        elif action == "press":
            raw = _safe(lambda: page.evaluate_handle("document.activeElement").evaluate(ELEMENT_FACTS_JS), None)
        facts = from_element(action, raw, page_url=url) if (raw or target is not None) else PageFacts(action=action, page_url=url)
        if action == "press":
            facts.key = value
            facts.unreadable = False
        facts.page_has_payment = self.page_has_payment(page)
        return facts

    @staticmethod
    def page_has_payment(page: Any) -> bool:
        for frame in _safe(lambda: page.frames, []):
            if _safe(lambda f=frame: f.evaluate(FRAME_PAYMENT_JS), False):
                return True
        return False

    # ------------------------------------------------------------- deciding

    def check(self, facts: PageFacts, *, intent: str = "", redo: Any = None) -> Decision:
        """Describe, ask ArmorIQ, write it down. Raises GuardStop unless ArmorIQ allowed it."""
        self.ensure_task(intent, facts.target_url or facts.page_url)
        task = self.gate.task
        described = classify(facts, task.sites if task else set())
        return self.ask(described.cls, described.because, facts, intent=intent, redo=redo)

    def ask(self, cls: str, because: str, facts: PageFacts, *, intent: str = "", redo: Any = None,
            late: bool = False) -> Decision:
        args = {"page": facts.page_url, "because": because, "words": facts.words, "intent": intent,
                **({"to": facts.target_url or facts.href} if (facts.target_url or facts.href) else {})}
        decision = self.gate.decide(cls, args)
        task = self.gate.task
        self.feed.write({"task_id": task.id if task else None, "goal": task.goal if task else None,
                         "action": facts.action, "cls": cls, "because": because, "decision": decision.action,
                         "reason": decision.reason, "policy": decision.matched_policy,
                         "delegation_id": decision.delegation_id, "plan_id": decision.plan_id,
                         "page_url": facts.page_url, "words": facts.words, "ms": decision.ms,
                         "facts": facts.to_dict()})
        if not decision.allowed:
            stop = GuardStop(decision, facts, because)
            if decision.action == "hold" and decision.delegation_id and redo is not None:
                self.pending[decision.delegation_id] = Pending(decision, redo, facts, because)
            if late:
                self.notices.append(f"The page itself (not your action) tried `{cls}` ({because}); "
                                    f"ArmorIQ answered {decision.action} ({decision.reason}). Nothing was sent.")
            else:
                self.last_stop = stop
            raise stop
        return decision

    # ------------------------------------------------------------- watching
    #
    # The watch is armed once per browser and never taken off. Every write a page sends — during an agent's
    # action or seconds after it, from a script the agent never saw — is paused until ArmorIQ has decided it.
    # A write inside an action's window belongs to that action; one after it is reported as "after <action>".

    def arm(self, context: Any) -> None:
        if id(context) not in self._armed:
            self._armed.add(id(context))
            context.route("**/*", self._on_request)

    def _on_request(self, route: Any, request: Any) -> None:
        self._last_request_at = time.monotonic()
        w = self._window or self._last_window
        method = request.method.upper()
        page_url = _safe(lambda: request.frame.page.url, "") or (w.facts.page_url if w else "")
        has_payment = bool(w and w.facts.page_has_payment and w.facts.page_url.split("#")[0] == page_url.split("#")[0])
        if (w is None or method not in WRITE_METHODS or request.resource_type not in WATCHED_TYPES
                or (site_of(request.url) != site_of(page_url) and not has_payment)):
            route.fallback()
            return
        # A navigation asks for a page, not for a write. Writes fired while a page loads (its analytics, its
        # own fetches) are still decided by ArmorIQ and still dropped if refused — but they are the page's,
        # so a refusal is reported as a notice, never as a refusal of the agent's navigation.
        live = w is self._window and w.cls not in PAGE_LOADS
        if live and w.cls in WRITES:  # the action itself was decided as a write: its own request is expected
            route.fallback()
            return
        if live and w.stopped:  # this action was refused once: nothing else it fires may leave
            route.abort("blockedbyclient")
            return
        described = network_class(method, request.url, _safe(lambda: request.post_data, None), has_payment)
        label = f"{w.facts.action}→{method}" if live else f"page during/after {w.facts.action}→{method}"
        sent = PageFacts(action=label, page_url=page_url, target_url=request.url, words=w.facts.words,
                         page_has_payment=has_payment)
        try:
            self.ask(described.cls, described.because, sent, intent=w.intent, redo=w.redo if live else None, late=not live)
        except GuardStop as stop:
            route.abort("blockedbyclient")
            if live:
                w.stopped.append(stop)
            return
        finally:
            self._last_request_at = time.monotonic()  # deciding took time; that was not quiet
        if live:
            w.passed.append(request)
        route.fallback()

    @contextlib.contextmanager
    def watching(self, page: Any, facts: PageFacts, cls: str, *, intent: str, redo: Any) -> Iterator[None]:
        """Open this action's window on the always-on watch, and keep it open until the page goes quiet."""
        self.arm(page.context)
        window = _Window(facts, cls, intent, redo)
        self._window = self._last_window = window
        try:
            yield
            # A write waits about a second for ArmorIQ, so the click returns before its writes have gone
            # out — and a script may chain a second write after the first. Stay in this window until the
            # page has sent nothing for QUIET_MS, so every write it fires is decided as part of it and an
            # allowed one finishes before the agent's next step can navigate away from it.
            began = time.monotonic()
            answered = 0
            while time.monotonic() - began < WRITE_SETTLE_MS / 1000:
                while answered < len(window.passed):  # an allowed write: let it finish first
                    _safe(window.passed[answered].response, None)
                    answered += 1
                    self._last_request_at = time.monotonic()
                _safe(lambda: page.wait_for_timeout(150), None)
                if answered == len(window.passed) and time.monotonic() - max(self._last_request_at, began) >= QUIET_MS / 1000:
                    break
        finally:
            self._window = None
        if window.stopped:
            raise window.stopped[0]

    # ------------------------------------------------------------- holds

    def wait(self, delegation_id: str, timeout_s: float) -> dict[str, Any]:
        pending = self.pending.get(delegation_id)
        state = self.gate.wait(delegation_id, timeout_s)
        self.feed.write({"task_id": self.gate.task.id if self.gate.task else None, "action": "approval",
                         "cls": pending.decision.cls if pending else "?", "decision": state,
                         "delegation_id": delegation_id, "because": "ArmorIQ delegation status"})
        if state != "approved":
            return {"ok": False, "status": state,
                    "next": "Still waiting — call guard_wait again." if state == "pending"
                    else f"ArmorIQ says {state}. Do not do this action."}
        if pending is None:
            return {"ok": True, "status": state, "next": "Approved. Repeat the action; ArmorIQ will allow it once."}
        self.pending.pop(delegation_id, None)
        # Asking again is what spends the approval: ArmorIQ answers allow by this delegation.
        return {"ok": True, "status": state, "result": pending.redo()}


def _safe(fn: Any, default: Any) -> Any:
    try:
        return fn()
    except Exception:  # noqa: BLE001 - a page that cannot be read is described as unknown
        return default


# ---------------------------------------------------------------- Dejo hooks

GUARD: Guard | None = None


def current() -> Guard:
    global GUARD
    if GUARD is None:
        GUARD = Guard()
    return GUARD


class GuardedSession(Session):
    """Dejo's cold-path session with ArmorIQ between finding an element and touching it."""

    _intent = ""

    def act(self, intent: str, action: Any, *, ref: str | None = None, value: str | None = None,
            to: str | None = None) -> dict[str, Any]:
        self._intent = intent
        self._redo = lambda: Session.act(self, intent, action, ref=ref, value=value, to=to)
        return super().act(intent, action, ref=ref, value=value, to=to)

    def _perform(self, action: Any, *, ref: str | None, value: str | None, to: str | None = None) -> Any:
        guard = current()
        try:
            spec = actions.spec_for(action)
        except actions.UnknownAction as unknown:
            raise ActionFailed(str(unknown)) from unknown
        redo = getattr(self, "_redo", None)
        page = self.browser.page

        if spec.session_handled:
            guard.check(guard.facts(page, action, value=value), intent=self._intent, redo=redo)
            self._do_here(action, value)
            return None

        element = self.browser.describe(self._element_for(ref)) if spec.needs_target else None
        if element is None and ref is not None:
            element = self.browser.describe(self._element_for(ref))
        target = self.browser.locate(element) if element else None
        second = self.browser.locate(self._element_for(to)) if spec.needs_second_target else None

        facts = guard.facts(page, action, target, value)
        decision = guard.check(facts, intent=self._intent, redo=redo)
        with guard.watching(page, facts, decision.cls, intent=self._intent, redo=redo):
            try:
                self.last_result = actions.perform(action, page=page, target=target, value=value, second=second)
            except actions.ActionNeedsMore as incomplete:
                raise ActionFailed(str(incomplete)) from incomplete
            self.browser.settle()
        return element


class GuardedExecutor(Executor):
    """Dejo's replay, with every remembered step re-described from the live page first."""

    def _do(self, step: Any, target: Any, *, domain: str) -> bool:
        guard = current()
        page = self.browser.page
        guard.ensure_task(f"replay a saved task on {domain}", page.url if page.url.startswith("http") else f"https://{domain}")
        action = step.action if step.action != "read" else "read"
        if action == "read":
            facts = PageFacts(action="read", page_url=page.url)
        elif action in ("goto", "new_tab"):
            facts = guard.facts(page, action, value=step.value)
        else:
            facts = guard.facts(page, action, target, step.value)
        redo = lambda: self._do(step, target, domain=domain)
        decision = guard.check(facts, intent=getattr(step, "intent", "") or "", redo=redo)
        with guard.watching(page, facts, decision.cls, intent=getattr(step, "intent", ""), redo=redo):
            return super()._do(step, target, domain=domain)
