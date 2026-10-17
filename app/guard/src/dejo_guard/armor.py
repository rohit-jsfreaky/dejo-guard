"""The gate: name the action, ask ArmorIQ, return ArmorIQ's answer verbatim.

There is no allow/deny logic in this file. Its only branch of its own is fail-closed: if
ArmorIQ cannot be reached or errors, the answer is `block` with reason `armoriq-unavailable`.

How a task maps onto ArmorIQ:
  start_task  → `start_plan`: the goal + one step per action class the task may use, all under
                the `dejo` MCP name. ArmorIQ signs it and returns an intent token.
  decide      → `check(dejo__<class>)` in SDK mode: ArmorIQ's policy answers allow/block/hold.
                A class that is not in the signed plan is refused by ArmorIQ as
                `tool-not-in-plan` — that is intent drift.
  hold        → ArmorIQ files a delegation under the guard's requester identity; a member of
                the org approves it on platform.armoriq.ai; `wait` polls ArmorIQ for the status
                and then asks ArmorIQ again, which answers allow by the approved delegation.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .classes import DEFAULT_PLAN
from .config import STEP_PREFIX, agent_id, api_key, load_env, requester


@dataclass
class Decision:
    action: str  # allow | block | hold
    reason: str | None
    cls: str
    matched_policy: str | None = None
    delegation_id: str | None = None
    plan_id: str | None = None
    ms: int = 0

    @property
    def allowed(self) -> bool:
        return self.action == "allow"


@dataclass
class Task:
    id: str
    goal: str
    classes: tuple[str, ...]
    sites: set[str]
    plan_id: str | None = None
    refused: str | None = None  # ArmorIQ refused the whole plan
    session: Any = None
    started: float = field(default_factory=time.time)


class Gate:
    def __init__(self, agent: str | None = None) -> None:
        load_env()
        self.agent = agent or agent_id()
        os.environ.setdefault("ARMORIQ_OBSERVABILITY", "false")
        logging.getLogger("httpx").setLevel(logging.WARNING)  # stderr is the MCP log; keep it readable
        self._client: Any = None
        self.task: Task | None = None
        self.requester = requester()

    def client(self) -> Any:
        if self._client is None:
            from armoriq_sdk import ArmorIQClient

            key, source = api_key()
            if key is None:  # fail closed, with the reason the user needs
                raise RuntimeError(f"no ArmorIQ key for Dejo Guard: {source}")
            self._client = ArmorIQClient(api_key=key, agent_id=self.agent, user_id=self.requester)
        return self._client

    # ------------------------------------------------------------------ plan

    def start_task(self, goal: str, classes: tuple[str, ...] = DEFAULT_PLAN, sites: set[str] | None = None) -> Task:
        """Declare what this task may do. ArmorIQ signs it, or refuses it outright."""
        from armoriq_sdk import SessionOptions

        classes = tuple(dict.fromkeys(("read", *classes)))  # looking is always part of a task
        task = Task(id=uuid.uuid4().hex[:12], goal=goal, classes=classes, sites=set(sites or ()))
        self.task = task
        try:
            session = self.client().for_user(self.requester).start_session(
                SessionOptions(mode="sdk", default_mcp_name=STEP_PREFIX, validity_seconds=3600)
            )
            steps = [{"name": f"{STEP_PREFIX}__{c}", "args": {"sites": sorted(task.sites)}} for c in classes]
            token = session.start_plan(steps, goal=goal)
            task.session = session
            task.plan_id = token.plan_id
        except Exception as problem:  # noqa: BLE001 - every failure here means "no plan"
            meta = getattr(problem, "metadata", None) or {}
            denied = meta.get("denied_tools") if isinstance(meta, dict) else None
            if type(problem).__name__ == "PolicyBlockedException":
                task.refused = f"ArmorIQ refused the plan: {', '.join(denied) if denied else str(problem)[:200]}"
            else:
                task.refused = f"armoriq-unavailable: {type(problem).__name__}: {str(problem)[:200]}"
        return task

    # ---------------------------------------------------------------- decide

    def decide(self, cls: str, args: dict[str, Any]) -> Decision:
        began = time.perf_counter()
        task = self.task
        if task is None or task.session is None:
            why = task.refused if task else "no task declared"
            return Decision("block", why, cls, ms=_ms(began))
        try:
            result = task.session.check(f"{STEP_PREFIX}__{cls}", args, user_email=self.requester)
            return Decision(
                action=result.action,
                reason=result.reason,
                cls=cls,
                matched_policy=result.matched_policy,
                delegation_id=getattr(result, "delegation_id", None),
                plan_id=task.plan_id,
                ms=_ms(began),
            )
        except Exception as problem:  # noqa: BLE001 - fail closed
            return Decision("block", f"armoriq-unavailable: {type(problem).__name__}: {str(problem)[:200]}", cls,
                            plan_id=task.plan_id, ms=_ms(began))

    def status(self, delegation_id: str) -> str:
        """pending | approved | rejected | expired | none — ArmorIQ's own word for a hold."""
        try:
            return self.client().get_delegation_status(delegation_id)
        except Exception as problem:  # noqa: BLE001
            return f"error: {type(problem).__name__}"

    def wait(self, delegation_id: str, timeout_s: float, interval_s: float = 3.0) -> str:
        deadline = time.time() + timeout_s
        while True:
            state = self.status(delegation_id)
            if state != "pending" or time.time() >= deadline:
                return state
            time.sleep(interval_s)


def _ms(began: float) -> int:
    return int((time.perf_counter() - began) * 1000)
