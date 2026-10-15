"""Our code describes; ArmorIQ decides. No module but the gate may produce a decision word."""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "dejo_guard"
DECISIONS = {"allow", "block", "hold", "deny", "permit"}


def _decision_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in DECISIONS:
            hits.append(f"{path.name}:{node.lineno} {node.value!r}")
    return hits


def test_describing_code_has_no_decision_words():
    for name in ("classes.py", "facts.py"):
        assert _decision_literals(SRC / name) == [], name


def test_guard_never_builds_a_decision():
    tree = ast.parse((SRC / "guard.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "Decision"]
    assert calls == []


def test_gate_only_says_block_when_armoriq_cannot_answer():
    # armor.py builds a Decision itself only to fail closed (no plan / ArmorIQ unreachable).
    tree = ast.parse((SRC / "armor.py").read_text(encoding="utf-8"))
    own = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "Decision"
           and n.args and isinstance(n.args[0], ast.Constant)]
    assert {n.args[0].value for n in own} == {"block"}
