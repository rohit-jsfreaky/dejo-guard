"""guard.yaml — the user's own additions to a task's PLAN. Never to the decision: ArmorIQ's policy still decides.

Lives at ~/.dejo-guard/guard.yaml (`dejo-guard init` writes the default below). Two keys:

  sites:  classes added to every task that names one of these sites
  words:  extra task words (a regex) that unlock classes, next to the built-in ones

Only classes the guard knows are accepted; anything else is ignored with a warning on stderr.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

from .classes import CLASSES
from .config import HOME

PATH = HOME / "guard.yaml"

DEFAULT = """\
# Dejo Guard — your additions to a task's plan.
# These only widen WHAT A TASK MAY ASK FOR. Your ArmorIQ policy still decides every action:
# a class listed here as `hold` in the policy is still held for your approval.
#
# Classes: read navigate type_text interact download new_domain type_secret type_payment
#          submit_form submit_payment state_change upload run_script unknown

# Every task on these sites may also use these classes.
sites: {}
#  github.com: [submit_form, state_change]     # e.g. tasks on GitHub may submit forms and star repos

# Extra task words (regular expressions) and the classes they unlock.
words: {}
#  "\\\\b(star|follow)\\\\b": [state_change]
"""


def load(path: Path | None = None) -> dict[str, Any]:
    path = path or PATH
    if not path.is_file():
        return {"sites": {}, "words": {}}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as problem:
        print(f"[dejo-guard] {path} is not valid YAML, ignoring it: {problem}", file=sys.stderr, flush=True)
        return {"sites": {}, "words": {}}
    return {"sites": _clean(data.get("sites"), path, "sites"), "words": _clean(data.get("words"), path, "words")}


def _clean(section: Any, path: Path, name: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for key, classes in (section or {}).items():
        good = [c for c in (classes or []) if c in CLASSES]
        bad = [c for c in (classes or []) if c not in CLASSES]
        if bad:
            print(f"[dejo-guard] {path} {name}.{key}: unknown classes ignored: {bad}", file=sys.stderr, flush=True)
        if good:
            out[str(key)] = good
    return out


def extra_classes(goal: str, sites: set[str], user: dict[str, Any] | None = None) -> tuple[str, ...]:
    user = user if user is not None else load()
    extra: list[str] = []
    for site in sites:
        extra.extend(user["sites"].get(site, []))
    for pattern, classes in user["words"].items():
        try:
            if re.search(pattern, goal, re.IGNORECASE):
                extra.extend(classes)
        except re.error:
            print(f"[dejo-guard] guard.yaml words: bad pattern {pattern!r}, ignored", file=sys.stderr, flush=True)
    return tuple(dict.fromkeys(extra))


def write_default(path: Path | None = None) -> bool:
    path = path or PATH
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT, encoding="utf-8")
    return True
