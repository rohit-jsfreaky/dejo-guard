"""The ArmorIQ policy this guard is built for. The decisions live HERE, in ArmorIQ — not in code.

`dejo-guard policy` prints it. Import it on platform.armoriq.ai (Policies → Import YAML) or with
`POST /policies/yaml/import`, then activate it. Change a line and the guard behaves differently
on the next action — with no change to the guard.
"""

from __future__ import annotations

from .classes import CLASSES

# What each class gets by default. Anything not `allow` is listed under toolEnforcement.
DEFAULT_RULES: dict[str, str] = {
    "read": "allow",
    "navigate": "allow",
    "type_text": "allow",
    "interact": "allow",
    "download": "allow",
    "type_secret": "block",
    "type_payment": "block",
    "submit_form": "hold",
    "submit_payment": "hold",
    "state_change": "allow",  # a write the task declared (cart, save); drift-blocked otherwise
    "new_domain": "hold",
    "upload": "hold",
    "run_script": "hold",
    "unknown": "hold",
}


def policy_yaml(org_id: str = "<your org id>", agent_target_id: str = "<dejo-guard-agent id>",
                rules: dict[str, str] | None = None, name: str = "dejo-guard-boundary") -> str:
    rules = {**DEFAULT_RULES, **(rules or {})}
    allowed = [c for c in CLASSES if rules.get(c) in ("allow", "hold", "block")]
    enforced = {c: rules[c] for c in allowed if rules[c] != "allow"}
    lines = [
        "# Dejo Guard boundary. Each browser action is a named step (dejo__<class>); ArmorIQ decides.",
        "# A class must be in allowedTools for its toolEnforcement to apply; an unlisted class is blocked.",
        "apiVersion: armor.io/v1",
        "kind: Policy",
        "metadata:",
        f"  name: {name}",
        f"  orgId: {org_id}",
        "  targetType: agent",
        f"  targetId: {agent_target_id}",
        "spec:",
        "  priority: 100",
        "  defaultEnforcementAction: block",
        "  memberRules:",
        "    '*':",
        "      allowedTools:",
        *[f"      - {c}" for c in allowed],
        "      toolEnforcement:",
        *[f"        {c}: {a}" for c, a in enforced.items()],
    ]
    return "\n".join(lines) + "\n"
