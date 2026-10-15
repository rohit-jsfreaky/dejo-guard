import os, json, httpx, sys
from pathlib import Path
SP = Path("D:/my_projects/hackathons/spokesperson")
for line in (SP / ".env").read_text(encoding="utf-8").splitlines():
    line = line.split("#", 1)[0].strip()
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
KEY = os.environ["ARMORIQ_API_KEY"]; B = "https://api.armoriq.ai"
H = {"X-API-Key": KEY, "Content-Type": "application/json"}
c = httpx.Client(timeout=30)
def p(tag, r): print("---", tag, r.status_code, r.text.replace(KEY, "<KEY>")[:500])
fields = ["args.element_label", "arguments.element_label", "tool.args.element_label", "input.element_label"]
stmts = [{"id": f"s{i}", "effect": "forbid", "action": {"type": "tool", "eq": "browser_click"},
          "conditions": [{"field": f, "op": "matches", "value": "*order*"}]} for i, f in enumerate(fields)]
stmts.append({"id": "hold_send", "effect": "require_approval", "action": {"type": "tool", "eq": "browser_submit"}, "conditions": []})
doc = {"schemaVersion": "armor.policy.v1", "kind": "PolicyProfile", "metadata": {"name": "browser-probe"},
       "defaults": {"decision": "permit", "conflictResolution": "deny_overrides"}, "statements": stmts}
if sys.argv[1] == "set":
    p("sync", c.post(B + "/policies/sync", headers=H, json={"policy": doc, "source": "probe"}))
    for args in [{"element_label": "Place order"}, {"element_label": "Next page"}]:
        p(f"enforce click {args}", c.post(B + "/iap/enforce", headers=H, json={"tool": "browser_click", "arguments": args}))
    p("enforce submit", c.post(B + "/iap/enforce", headers=H, json={"tool": "browser_submit", "arguments": {}}))
elif sys.argv[1] == "reset":
    reset = {"schemaVersion": "armor.policy.v1", "kind": "PolicyProfile", "metadata": {"name": "default-permit"},
             "defaults": {"decision": "permit", "conflictResolution": "deny_overrides"}, "statements": []}
    p("reset", c.post(B + "/policies/sync", headers=H, json={"policy": reset, "source": "probe-reset"}))
