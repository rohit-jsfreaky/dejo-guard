"""Day-0 probe: does ArmorIQ sign a plan of dejo__<class> steps, and what does check() say per class?
Run from the repo root: uv run --project app/guard python evidence/probes/day0_plan.py"""
import json, sys, time
from dejo_guard.armor import Gate
from dejo_guard.classes import CLASSES

gate = Gate()
t = time.time()
task = gate.start_task("day-0 probe: compare prices", ("read", "navigate", "submit_form", "type_payment"), {"dejo-guard.vercel.app"})
print("plan:", json.dumps({"plan_id": task.plan_id, "refused": task.refused, "classes": task.classes, "s": round(time.time() - t, 2)}))
for cls in sys.argv[1:] or ["read", "navigate", "submit_form", "type_payment", "submit_payment"]:
    d = gate.decide(cls, {"page": "https://dejo-guard.vercel.app/shop", "because": "probe"})
    print("check:", json.dumps({"cls": cls, "action": d.action, "reason": (d.reason or "")[:160], "policy": d.matched_policy, "delegation": d.delegation_id, "ms": d.ms}))
