"""Copy the eval's numbers from evidence/eval.json into the site and the README. Nothing is typed by hand.

    python scripts/sync_numbers.py

Missing arm or missing number → null on the site ("—") and "—" in the README, with the reason.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evidence" / "eval.json"
SITE = ROOT / "app" / "web" / "src" / "data" / "eval.json"
README = ROOT / "README.md"


def main() -> None:
    report = json.loads(EVAL.read_text(encoding="utf-8"))
    s = report["summary"]
    guard, names = s.get("guard", {}), s.get("names", {})
    none = s.get("none", {})
    site = {
        "note": f"Copied by scripts/sync_numbers.py from evidence/eval.json (run {report['finished']}).",
        "attacks": guard.get("attacks"),
        "unsafe_none": none.get("unsafe_ran"),
        "unsafe_tool_name_policy": names.get("unsafe_ran"),
        "unsafe_dejo_guard": guard.get("unsafe_ran"),
        "false_hold_rate": guard.get("false_hold_rate"),
        "false_hold_rate_names": names.get("false_hold_rate"),
        "strict_names_false_hold_rate": (s.get("names_strict_computed") or {}).get("false_hold_rate"),
        "journeys": guard.get("journeys"),
        "journey_steps": guard.get("journey_steps_decided"),
        "ran_at": report["finished"],
    }
    SITE.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")

    d = lambda v, suf="": "—" if v is None else f"{v}{suf}"  # noqa: E731
    table = "\n".join([
        "| | unsafe actions that ran (of {}) | normal steps held or blocked (of {}) |".format(d(site["attacks"]), d(site["journey_steps"])),
        "|---|---|---|",
        f"| no guard | **{d(site['unsafe_none'])}** | — (nothing is ever held) |",
        f"| ArmorIQ on tool names (`click`, `fill`…) | **{d(site['unsafe_tool_name_policy'])}** | {d(site['false_hold_rate_names'], '%')} |",
        f"| ArmorIQ on tool names, strict (hold every click/fill/press) — computed | 0 | {d(site['strict_names_false_hold_rate'], '%')} |",
        f"| **Dejo Guard** (ArmorIQ on page meaning) | **{d(site['unsafe_dejo_guard'])}** | **{d(site['false_hold_rate'], '%')}** |",
        "",
        f"<sub>Run {report['finished']} · dejo-guard {report['versions']['dejo-guard']} · armoriq-sdk "
        f"{report['versions']['armoriq-sdk']} · raw: [`evidence/eval.json`](evidence/eval.json) · method: "
        f"[`docs/FINDING.md`](docs/FINDING.md)</sub>",
    ])
    text = README.read_text(encoding="utf-8")
    text = re.sub(r"<!-- numbers:start -->.*?<!-- numbers:end -->",
                  f"<!-- numbers:start -->\n{table}\n<!-- numbers:end -->", text, flags=re.S)
    README.write_text(text, encoding="utf-8")
    print(json.dumps(site, indent=2))


if __name__ == "__main__":
    main()
