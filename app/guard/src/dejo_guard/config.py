"""Where things live and which identity the guard uses. Environment first, then `.env` files."""

from __future__ import annotations

import json
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


PLATFORM_BACKEND = "https://api.armoriq.ai"


def backend() -> str:
    """The ArmorIQ backend the SDK talks to (the SDK's own default unless ARMORIQ_BACKEND_URL says otherwise)."""
    return (setting("ARMORIQ_BACKEND_URL") or PLATFORM_BACKEND).rstrip("/")


def login_file() -> Path:
    """Where `armoriq login` saves its key. ArmorClaude and ArmorCodex installs write the same file."""
    return Path.home() / ".armoriq" / "credentials.json"


def saved_login() -> dict | None:
    try:
        data = json.loads(login_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def api_key() -> tuple[str | None, str]:
    """Dejo Guard's ArmorIQ key and where it came from, or (None, why not).

    ARMORIQ_API_KEY wins. A saved login is used only when it was made for the backend the guard
    talks to: installing ArmorClaude from ArmorIQ Tools overwrites the same file with a key for
    another backend, and that key must not be sent to platform.armoriq.ai.
    """
    key = setting("ARMORIQ_API_KEY")
    if key:
        return key, "ARMORIQ_API_KEY"
    login = saved_for_backend()
    if login is not None:
        return login["apiKey"], str(login_file())
    others = sorted({f"{p.get('backend')} ({p.get('product') or 'another ArmorIQ product'})"
                     for p in saved_logins() if p.get("backend")})
    if others:
        return None, (f"{login_file()} only holds keys for {', '.join(others)}, not {backend()}; "
                      "set ARMORIQ_API_KEY for Dejo Guard or run `armoriq login`")
    return None, "no ARMORIQ_API_KEY and no `armoriq login`"


def saved_logins() -> list[dict]:
    """Every saved login with a key: the old one-login file, or each profile of the newer file
    (`{"active": …, "profiles": {name: {backend, product, apiKey, …}}}`), the active one first."""
    data = saved_login() or {}
    if isinstance(data.get("profiles"), dict):
        profiles = data["profiles"]
        names = sorted(profiles, key=lambda name: name != data.get("active"))
        found = [profiles[name] for name in names if isinstance(profiles[name], dict)]
    else:
        found = [data]
    return [p for p in found if isinstance(p.get("apiKey"), str) and p["apiKey"].startswith("ak_")]


def saved_for_backend() -> dict | None:
    """The saved login made for the guard's backend. A login that names no backend is the
    Python SDK's `armoriq login`, which only knows the platform."""
    for login in saved_logins():
        if str(login.get("backend") or backend()).rstrip("/") == backend():
            return login
    return None


def feed_path() -> Path:
    return Path(setting("DEJO_GUARD_FEED_DB") or HOME / "feed.db")


def agent_id() -> str:
    return setting("ARMORIQ_AGENT_ID", DEFAULT_AGENT_ID) or DEFAULT_AGENT_ID


def requester() -> str:
    return setting("DEJO_GUARD_REQUESTER", DEFAULT_REQUESTER) or DEFAULT_REQUESTER
