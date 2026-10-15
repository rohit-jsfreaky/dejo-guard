"""The class table: page facts → one action class. Structure only, never words.

This file DESCRIBES an action. It does not decide anything — there is no allow or deny here.
The class becomes a named ArmorIQ plan step (`dejo__<class>`) and ArmorIQ's policy decides.
`docs/GUARD-MODEL.md` §2 is the human version of this table; keep the two in step.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .facts import PageFacts, site_of

# Every class the guard can name. The ArmorIQ policy must list each one (allowedTools),
# because a tool missing from the policy is blocked by the org's no-match rule.
CLASSES = (
    "read",
    "navigate",
    "type_text",
    "interact",
    "download",
    "type_secret",
    "type_payment",
    "submit_form",
    "submit_payment",
    "state_change",
    "new_domain",
    "upload",
    "run_script",
    "unknown",
)

# Every task's plan declares these, so ArmorIQ's POLICY answers for them (allow, or hold/block by rule) and
# the decision shows on the ArmorIQ dashboard. What a task did NOT ask for — forms, cart writes, payment —
# stays out of the plan unless the user's words unlock it (guard.TASK_WORDS); ArmorIQ refuses those as drift.
DEFAULT_PLAN = ("read", "navigate", "type_text", "interact", "download", "new_domain",
                "type_secret", "type_payment", "upload", "run_script", "unknown")

# Dejo actions that only look, scroll or wait. They change nothing on the server.
_LOOKING = {
    "read", "hover", "focus", "blur", "scroll", "scroll_to", "wait", "wait_for", "highlight",
    "hide_highlight", "screenshot", "select_text", "switch_tab", "dismiss_when_seen",
    "restart_trail", "reload", "back", "forward", "set_time",
}
_TEXT_ENTRY = {"fill", "type", "clear"}
_CLICKS = {"click", "double_click", "tap", "check", "uncheck", "set_checked", "select", "dispatch_event", "drag"}

_FILE_EXT = (".pdf", ".zip", ".csv", ".xlsx", ".xls", ".doc", ".docx", ".exe", ".msi", ".dmg", ".apk", ".tar", ".gz")


@dataclass(frozen=True)
class Described:
    cls: str
    because: str  # which page fact made it this class — shown in the feed and the approval


def classify(f: PageFacts, plan_sites: set[str]) -> Described:
    """One action, one class. The first matching rule wins; order goes from most to least risky."""
    a = f.action

    if a in ("goto", "new_tab") and f.target_url:
        return _going_to(f.target_url, plan_sites, "goto")
    if a in _LOOKING or a in ("goto", "new_tab"):
        return Described("read" if a not in ("reload", "back", "forward") else "navigate", f"`{a}` changes nothing")
    if a == "evaluate":
        return Described("run_script", "runs the agent's own JavaScript in the page")
    if f.unreadable:
        return Described("unknown", "the element could not be read")

    if a == "upload" or f.is_file_input:
        return Described("upload", "file input")

    if a in _TEXT_ENTRY:
        if f.is_payment_field or (f.cross_origin_frame and f.page_has_payment):
            return Described("type_payment", _pay_why(f))
        if f.is_secret_field:
            return Described("type_secret", f"input type={f.type or 'text'} autocomplete={f.autocomplete or '-'}")
        if f.is_text_field:
            return Described("type_text", f"plain <{f.tag}> field")
        return Described("unknown", f"text entry into <{f.tag}>")

    if a == "press":
        # Enter in a form field submits the form, exactly like the submit button would.
        if (f.key or "").lower() in ("enter", "numpadenter") and f.in_form:
            return _submitting(f, "Enter inside a form", plan_sites)
        return Described("interact", f"key {f.key or '?'}")

    if a in _CLICKS:
        if f.cross_origin_frame and f.page_has_payment:
            return Described("submit_payment", "control inside a cross-origin frame that holds card fields")
        if f.is_submit:
            return _submitting(f, f"<{f.tag} type={f.type or 'submit'}> submits its form", plan_sites)
        if f.href and not f.href.startswith(("javascript:", "#")) and f.href.split("#")[0] != f.page_url.split("#")[0]:
            if f.link_download or f.href.lower().split("?")[0].endswith(_FILE_EXT):
                return Described("download", "link to a file")
            return _going_to(f.href, plan_sites, "link")
        if f.is_payment_field:
            return Described("type_payment", _pay_why(f))
        # A plain control. If its click fires a write request, the network guard names it
        # `state_change` (or `submit_payment` on a page with card fields) before it leaves.
        return Described("interact", f"<{f.tag}{' role=' + f.role if f.role else ''}> with no link or form submit")

    return Described("unknown", f"action `{a}`")


def _going_to(url: str, plan_sites: set[str], how: str) -> Described:
    site = site_of(url)
    if plan_sites and site not in plan_sites:
        return Described("new_domain", f"{how} to {site}, not in this task's sites ({', '.join(sorted(plan_sites))})")
    return Described("navigate", f"{how} to {site}")


def _submitting(f: PageFacts, how: str, plan_sites: set[str]) -> Described:
    if f.form_has_payment or f.page_has_payment:
        where = "its form has card fields" if f.form_has_payment else "the page has card fields"
        return Described("submit_payment", f"{how}; {where}")
    # A GET form (a search box) only builds a URL and goes there. It writes nothing.
    if (f.form_method or "get") == "get" and not f.form_has_secret:
        return _going_to(f.form_action or f.page_url, plan_sites, f"{how} (method GET)")
    return Described("submit_form", f"{how} (method {(f.form_method or 'get').upper()})")


def _pay_why(f: PageFacts) -> str:
    if f.autocomplete.startswith("cc-") or " cc-" in f" {f.autocomplete}":
        return f"autocomplete={f.autocomplete}"
    if f.cross_origin_frame:
        return "field inside a cross-origin payment frame"
    return f"card field (name={f.field_name or '?'})"


# Machine names on a write request that mean money moves: the endpoint's path, or the keys of
# the body it carries. Like an input's `name`, these are written for programs, not people.
_PAY_PATH = re.compile(r"/(checkout|pay|payment|payments|order|orders|purchase|billing|charge)(/|$|\?)", re.IGNORECASE)
_PAY_KEYS = re.compile(r"(card.?num|cardnumber|cvc|cvv|csc|payment.?method|payment_intent|upi|vpa|card_token)", re.IGNORECASE)


def network_class(method: str, url: str, body: str | None, page_has_payment: bool) -> Described:
    """A write request fired by a plain click, named before it leaves the browser."""
    path = url.split("://", 1)[-1].partition("/")[2]
    if page_has_payment:
        return Described("submit_payment", f"{method} request from a page with card fields")
    if _PAY_PATH.search("/" + path):
        return Described("submit_payment", f"{method} to a payment endpoint (/{path.split('?')[0]})")
    if body and _PAY_KEYS.search(body):
        return Described("submit_payment", f"{method} body carries payment fields")
    return Described("state_change", f"{method} request fired by the click (/{path.split('?')[0]})")
