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
t0 = time.time(); c = ArmorIQClient(agent_id="spokesperson-agent", user_id=email); t1 = time.time()
s = c.for_user(email).start_session(SessionOptions(mode="sdk", default_mcp_name="voice", validity_seconds=600))
names = ["voice__reply", "voice__topic_tech", "voice__commitment_none"]
t2 = time.time(); tok = s.start_plan([{"name": n, "args": {"p": 1}} for n in names], goal="latency probe"); t3 = time.time()
times = []
for n in names:
    a = time.time(); r = s.check(n, {"p": 1}, user_email=email); times.append((n, r.action, round(time.time() - a, 2)))
print("client init s:", round(t1 - t0, 2), "| plan+token s:", round(t3 - t2, 2))
for x in times: print("check", x)
