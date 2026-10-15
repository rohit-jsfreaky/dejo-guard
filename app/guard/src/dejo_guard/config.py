"""Where things live and which identity the guard uses. Environment first, then `.env` files."""

from __future__ import annotations

import os
from pathlib import Path

HOME = Path(os.environ.get("DEJO_GUARD_HOME") or Path.home() / ".dejo-guard")

# The agent registered on platform.armoriq.ai. `dejo-guard init` prints how to register it.
DEFAULT_AGENT_ID = "dejo-guard-agent"

# Holds are filed under this identity, which is NOT a member of the org. ArmorIQ refuses to
# let a member approve a request filed under their own email, so the requester must differ
# from the person approving.
DEFAULT_REQUESTER = "dejo-guard-agent@agents.dejo-guard.vercel.app"

# The MCP name every plan step is filed under: `dejo__navigate`, `dejo__submit_form` …
STEP_PREFIX = "dejo"

_loaded = False


def load_env() -> None:
    """Read KEY=VALUE lines from ./.env and ~/.dejo-guard/.env. Real environment wins."""
    global _loaded
    if _loaded:
        return
    _loaded = True
    for path in (Path.cwd() / ".env", HOME / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def setting(name: str, default: str | None = None) -> str | None:
    load_env()
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def feed_path() -> Path:
    return Path(setting("DEJO_GUARD_FEED_DB") or HOME / "feed.db")


def agent_id() -> str:
    return setting("ARMORIQ_AGENT_ID", DEFAULT_AGENT_ID) or DEFAULT_AGENT_ID


def requester() -> str:
    return setting("DEJO_GUARD_REQUESTER", DEFAULT_REQUESTER) or DEFAULT_REQUESTER
