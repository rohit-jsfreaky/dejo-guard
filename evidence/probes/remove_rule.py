"""Remove-a-rule: the same click, decided by whatever the ACTIVE ArmorIQ policy says at that moment.

Run once per policy state, with a label:
    uv run --project app/guard python evidence/probes/remove_rule.py before     # policy as published
    (remove `submit_payment: hold` from the active policy on ArmorIQ)
    uv run --project app/guard python evidence/probes/remove_rule.py removed
    (put the line back)
    uv run --project app/guard python evidence/probes/remove_rule.py restored

Each run: a fresh throwaway browser, the buying task, the book in the cart, the checkout filled, then the one click
that matters — "Place order". Appends one line per run to evidence/remove-a-rule.jsonl. Our code is identical in all
three runs; only the policy on ArmorIQ changes.
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

import httpx

from dejo_guard.server import build_server

SHOP = "https://dejo-guard.vercel.app/shop"
label = sys.argv[1] if len(sys.argv) > 1 else "run"
tmp = Path(tempfile.mkdtemp(prefix=f"dejo-guard-rule-{label}-"))
server = build_server(db_path=str(tmp / "d.db"), profile=str(tmp / "p"), profiles_dir=str(tmp / "ps"), headless=True)
tools = server._tool_manager  # noqa: SLF001


def act(intent: str, action: str, ref: str | None = None, value: str | None = None) -> dict:
    return tools.get_tool("dejo_act").fn(intent=intent, action=action, ref=ref, value=value)


def newest_order() -> str | None:
    orders = httpx.get(f"{SHOP.rsplit('/shop', 1)[0]}/api/shop/orders", timeout=20).json().get("orders") or []
    return orders[0]["id"] if orders else None


try:
    tools.get_tool("guard_task").fn(task="buy Atomic Habits from this shop", sites=["dejo-guard.vercel.app"])
    act("open the book", "goto", value=SHOP + "/p/atomic-habits")
    act("add it to the cart", "click", ref="button:has-text('Add to cart')")
    act("go to checkout", "goto", value=SHOP + "/checkout")
    act("fill my name", "fill", ref="input[name=name]", value="Rule Test")
    act("fill my address", "fill", ref="input[name=address]", value="1 Test Lane")
    act("fill my city", "fill", ref="input[name=city]", value="Kolkata")
    before = newest_order()
    reply = act("place the order", "click", ref="button[type=submit]")
    time.sleep(2)
    after = newest_order()
    g = reply.get("guard") or {}
    from dejo_guard import guard as guard_mod

    # ArmorIQ's own words for this click, from the guard's feed (an allowed click's reply carries no guard block).
    said = next((r for r in guard_mod.current().feed.recent(10) if r["cls"] == "submit_payment" and r["action"] == "click"), {})
    row = {
        "label": label,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "click": "Place order",
        "decision": g.get("decision", "allow" if reply.get("ok") else "error"),
        "class": g.get("class", "submit_payment"),
        "reason": g.get("reason") or said.get("reason"),
        "policy": g.get("policy") or said.get("policy"),
        "hold_id": g.get("hold_id"),
        "order_placed": after if after and after != before else None,
        "error": None if reply.get("ok") or g else reply.get("error"),
    }
    out = Path(__file__).resolve().parents[1] / "remove-a-rule.jsonl"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, indent=2, ensure_ascii=False))
finally:
    server.dejo_tools.close()  # type: ignore[attr-defined]
