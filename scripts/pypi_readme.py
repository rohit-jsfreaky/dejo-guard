"""Copy the root README into the package for PyPI, with relative links made absolute (PyPI can't follow them).

    python scripts/pypi_readme.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOB = "https://github.com/rohit-jsfreaky/dejo-guard/blob/main/"
TREE = "https://github.com/rohit-jsfreaky/dejo-guard/tree/main/"


def absolute(match: re.Match[str]) -> str:
    text, target = match.group(1), match.group(2)
    if re.match(r"^(https?:|mailto:|#)", target):
        return match.group(0)
    path = target.removeprefix("./")
    base = TREE if (ROOT / path).is_dir() else BLOB
    return f"[{text}]({base}{path})"


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    out = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", absolute, readme)
    (ROOT / "app" / "guard" / "README.md").write_text(out, encoding="utf-8")
    print(f"app/guard/README.md written ({len(out)} chars)")


if __name__ == "__main__":
    main()
