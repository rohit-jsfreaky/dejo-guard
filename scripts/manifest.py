"""Write evidence/MANIFEST.json: the commit, the versions, and a SHA-256 for every file under evidence/.

    python scripts/manifest.py

Anyone can re-hash the files and compare. Run it last, after every other evidence file is in place.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "MANIFEST.json"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()


def main() -> None:
    files = {}
    for path in sorted(EVIDENCE.rglob("*")):
        if path.is_file() and path != OUT:
            files[path.relative_to(ROOT).as_posix()] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
    lock = (ROOT / "app" / "guard" / "uv.lock").read_text(encoding="utf-8")

    def pinned(name: str) -> str | None:
        block = lock.split(f'name = "{name}"\n', 1)
        return block[1].split('version = "', 1)[1].split('"', 1)[0] if len(block) > 1 else None

    manifest = {
        "written": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": git("rev-parse", "HEAD") or None,
        "uncommitted_changes": bool(git("status", "--porcelain")),
        "versions": {name: pinned(name) for name in ("dejo", "dejo-mcp", "armoriq-sdk", "mcp", "playwright")},
        "armoriq": {
            "org": "157f1d31-83ad-46e9-90f4-2536f6130b68",
            "agent": {"dejo-guard-agent": "9255530a-72a5-46c6-845e-ce6cfb8c1540",
                      "dejo-toolname-baseline": "1adda49e-ad9d-42ae-9d62-81250ad75282"},
            "policies": {"dejo-guard-boundary": "fc6474c7-eedc-4a8c-916b-f2bb516b52d1",
                         "toolname-baseline": "9f76ad4f-88a4-47cb-989e-ae6a75379f32"},
            "mcp_servers": {"sandbox-shop": "ada0215a-d8cd-40fa-ac2e-3c16ba32bc10", "dejo": "46bbc80d-106f-4612-b220-4e859e19d3d6"},
        },
        "files": files,
    }
    OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{len(files)} files hashed → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
