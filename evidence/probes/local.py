import os, time
from pathlib import Path
SP = Path("D:/my_projects/hackathons/spokesperson")
for line in (SP / ".env").read_text(encoding="utf-8").splitlines():
    line = line.split("#", 1)[0].strip()
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
os.environ["ARMORIQ_OBSERVABILITY"] = "false"
from armoriq_sdk import ArmorIQClient, SessionOptions
email = os.environ.get("ARMORIQ_AGENT_EMAIL")
c = ArmorIQClient(agent_id="spokesperson-agent", user_id=email)
s = c.for_user(email).start_session(SessionOptions(mode="local", default_mcp_name="voice", validity_seconds=600))
names = ["voice__reply", "voice__topic_tech", "voice__dm_send", "voice__commitment_meeting"]
a = time.time()
try:
    tok = s.start_plan([{"name": n, "args": {"p": 1}} for n in names], goal="local-mode probe")
    print("plan+token s:", round(time.time() - a, 2))
except Exception as e:
    print("start_plan:", type(e).__name__, str(e)[:300])
for n in names:
    b = time.time()
    try:
        r = s.enforce(n, {"p": 1}); print("enforce", n, r.action, (r.reason or "")[:80], "deleg=", getattr(r, "delegation_id", None), "policy=", r.matched_policy, round(time.time() - b, 3))
    except Exception as e:
        print("enforce", n, type(e).__name__, str(e)[:160], round(time.time() - b, 3))
