"""`dejo-guard verify` — one PASS/FAIL line per claim. Exit code 1 if any claim fails.

Offline checks run anywhere. Live checks ask the real ArmorIQ (need ARMORIQ_API_KEY and the published policy);
`--offline` skips them. Run from the repo root so the evidence checks can find their files.
"""

from __future__ import annotations

import ast
import json
import os
import re
from collections.abc import Callable
from pathlib import Path

from .armor import Gate
from .classes import classify
from .facts import PageFacts

SRC = Path(__file__).resolve().parent
DECISION_WORDS = {"allow", "block", "hold", "deny", "permit"}
results: list[tuple[bool, str, str]] = []


def check(claim: str) -> Callable[[Callable[[], str]], Callable[[], str]]:
    def wrap(fn: Callable[[], str]) -> Callable[[], str]:
        try:
            detail = fn()
            results.append((True, claim, detail))
        except Exception as problem:  # noqa: BLE001 - a failed claim is reported, not raised
            results.append((False, claim, f"{type(problem).__name__}: {problem}"))
        return fn

    return wrap


def offline() -> None:
    @check("describing code holds no decision words (our code describes, ArmorIQ decides)")
    def _() -> str:
        for name in ("classes.py", "facts.py"):
            tree = ast.parse((SRC / name).read_text(encoding="utf-8"))
            hits = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value in DECISION_WORDS]
            assert not hits, f"{name}: {hits}"
        return "classes.py, facts.py"

    page = "https://dejo-guard.vercel.app/shop/checkout"
    cases = [
        ("pay submit labelled “Continue”", {"action": "click", "tag": "button", "is_submit": True, "in_form": True, "form_method": "post",
                                                 "form_has_payment": True, "words": "Continue"}, "submit_payment"),
        ("pay submit labelled in Hindi", {"action": "click", "tag": "button", "is_submit": True, "in_form": True, "form_method": "post",
                                               "form_has_payment": True, "words": "ऑर्डर करें"}, "submit_payment"),
        ("card field by autocomplete", {"action": "fill", "tag": "input", "autocomplete": "cc-number", "is_payment_field": True,
                                            "is_text_field": True}, "type_payment"),
        ("password box", {"action": "fill", "tag": "input", "type": "password", "is_secret_field": True, "is_text_field": True}, "type_secret"),
        ("“Next page” link to another site", {"action": "click", "tag": "a", "href": "https://evil.example/pay", "words": "Next page"}, "new_domain"),
        ("search box", {"action": "fill", "tag": "input", "type": "search", "is_text_field": True}, "type_text"),
        ("link on the same site", {"action": "click", "tag": "a", "href": "https://dejo-guard.vercel.app/shop/p/2"}, "navigate"),
    ]
    for label, facts, want in cases:
        @check(f"structure, not words: {label} → {want}")
        def _(facts=facts, want=want) -> str:
            got = classify(PageFacts(page_url=page, **facts), {"dejo-guard.vercel.app"}).cls
            assert got == want, f"got {got}"
            return got

    if not Path("evidence/eval.json").is_file():  # outside the repo (an installed copy): nothing to compare
        return

    @check("README numbers match evidence/eval.json")
    def _() -> str:
        report = json.loads(Path("evidence/eval.json").read_text(encoding="utf-8"))
        g = report["summary"]["guard"]
        n = report["summary"]["names"]
        readme = Path("README.md").read_text(encoding="utf-8")
        block = re.search(r"<!-- numbers:start -->(.*?)<!-- numbers:end -->", readme, re.DOTALL).group(1)
        assert f"**{g['unsafe_ran']}**" in block and f"**{n['unsafe_ran']}**" in block, "unsafe counts differ"
        assert f"{g['false_hold_rate']}%" in block, "false-hold rate differs"
        return f"guard {g['unsafe_ran']}/{g['attacks']} unsafe, {g['false_hold_rate']}% held · names {n['unsafe_ran']}/{n['attacks']}"

    @check("site numbers match evidence/eval.json")
    def _() -> str:
        report = json.loads(Path("evidence/eval.json").read_text(encoding="utf-8"))
        site = json.loads(Path("app/web/src/data/eval.json").read_text(encoding="utf-8"))
        assert site["unsafe_dejo_guard"] == report["summary"]["guard"]["unsafe_ran"]
        assert site["unsafe_tool_name_policy"] == report["summary"]["names"]["unsafe_ran"]
        assert site["false_hold_rate"] == report["summary"]["guard"]["false_hold_rate"]
        return f"ran_at {site['ran_at']}"


def live() -> None:
    gate = Gate()
    task = gate.start_task("verify: buy a book from this shop", ("read", "navigate", "type_payment", "submit_form"),
                           {"dejo-guard.vercel.app"})

    @check("ArmorIQ signs the task's plan")
    def _() -> str:
        assert task.plan_id and not task.refused, task.refused
        return f"plan {task.plan_id}"

    for cls, want, reason in [("navigate", "allow", None), ("type_payment", "block", "rule_action_block"),
                              ("submit_form", "hold", "rule_action_hold")]:
        @check(f"ArmorIQ policy: {cls} → {want}")
        def _(cls=cls, want=want, reason=reason) -> str:
            d = gate.decide(cls, {"page": "https://dejo-guard.vercel.app/shop", "because": "verify"})
            assert d.action == want, f"got {d.action} ({d.reason})"
            assert reason is None or d.reason == reason, f"reason {d.reason}"
            return f"{d.action} · {d.reason} · {d.matched_policy}"

    @check("intent drift: a class outside the signed plan is refused")
    def _() -> str:
        d = gate.decide("submit_payment", {"page": "https://dejo-guard.vercel.app/shop", "because": "verify"})
        assert d.action == "block" and "not-in-plan" in (d.reason or ""), f"got {d.action} ({d.reason})"
        return d.reason or ""

    @check("fail closed: no answer from ArmorIQ means no action")
    def _() -> str:
        saved = os.environ.get("ARMORIQ_API_KEY")
        os.environ["ARMORIQ_API_KEY"] = "ak_live_not_a_real_key"
        try:
            bad = Gate()
            bad.start_task("verify: fail closed", ("read",), set())
            d = bad.decide("read", {})
        finally:
            if saved is not None:
                os.environ["ARMORIQ_API_KEY"] = saved
        assert d.action == "block", f"got {d.action}"
        return (d.reason or "")[:90]


def main(argv: list[str] | None = None) -> int:
    args = argv or []
    offline()
    if "--offline" not in args:
        live()
    for ok, claim, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {claim}  —  {detail}")
    failed = sum(not ok for ok, _, _ in results)
    print(f"\n{len(results) - failed}/{len(results)} claims pass")
    return 1 if failed else 0
