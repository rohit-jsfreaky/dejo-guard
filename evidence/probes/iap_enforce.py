import os, json, httpx
from pathlib import Path
SP = Path("D:/my_projects/hackathons/spokesperson")
for line in (SP / ".env").read_text(encoding="utf-8").splitlines():
    line = line.split("#", 1)[0].strip()
    if "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
KEY = os.environ["ARMORIQ_API_KEY"]
H = {"X-API-Key": KEY, "Content-Type": "application/json"}
c = httpx.Client(timeout=30)
for path, body in [
    ("/policies/profiles/active", None),
    ("/iap/enforce", {"tool": "browser_click", "arguments": {"element_role": "button", "element_label": "Place order", "page_url": "https://shop.test/checkout"}}),
]:
    r = c.get("https://api.armoriq.ai" + path, headers=H) if body is None else c.post("https://api.armoriq.ai" + path, headers=H, json=body)
    print("---", path, r.status_code); print(r.text.replace(KEY, "<KEY>")[:900])
