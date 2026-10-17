"""Dejo's MCP server with ArmorIQ in front of every page action.

Same tools as `dejo-mcp`, so an agent that knows Dejo already knows this. Three are new:
  guard_task    declare the task before acting — the goal and the sites. ArmorIQ signs the
                plan; anything outside it is refused as drift.
  guard_wait    wait for a held action to be approved in ArmorIQ, then run it.
  guard_status  the current plan and the last decisions.

Never print to stdout — stdio is the MCP transport.
"""

from __future__ import annotations

import contextlib
import functools
import sys
from typing import Any

import dejo_mcp.server as dejo_server
from mcp.server.fastmcp import FastMCP

from . import guard as guard_mod
from .classes import CLASSES
from .facts import PageFacts, site_of
from .guard import GuardedExecutor, GuardedSession, GuardStop, plan_for

GUARD_RULES = (
    "\n\nDEJO GUARD: every page action here is decided by ArmorIQ from what the action MEANS on "
    "the page (a link, a form submit, a card field), not from the tool name.\n"
    "1. Before acting on a website, call guard_task with the user's request in their own words "
    "and the site(s). That is the plan ArmorIQ signs. Actions outside it are refused as drift.\n"
    "2. A reply with guard.decision='hold' means ArmorIQ wants a human to approve. Tell the user "
    "what is waiting (guard.words, guard.page) and to approve it in ArmorIQ → Held Actions, then "
    "call guard_wait with guard.hold_id. A reply with guard.decision='block' is final.\n"
    "3. Never try to get round a hold or a block another way (a different button, a script, a "
    "URL). That is exactly what the guard exists to stop."
)


def _log(message: str) -> None:
    print(f"[dejo-guard] {message}", file=sys.stderr, flush=True)


def _guard_reply(stop: GuardStop) -> dict[str, Any]:
    d = stop.decision
    return {
        "ok": False,
        "error": str(stop),
        "guard": {
            "decision": d.action,
            "class": d.cls,
            "because": stop.because,
            "reason": d.reason,
            "policy": d.matched_policy,
            "hold_id": d.delegation_id,
            "plan_id": d.plan_id,
            "words": stop.facts.words,
            "page": stop.facts.page_url,
        },
    }


def _guarded(fn: Any) -> Any:
    """Run a Dejo tool; if the guard stopped it, say so in a structured way."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        guard = guard_mod.current()
        guard.last_stop = None
        result = fn(*args, **kwargs)
        stop = guard.last_stop
        reply = result
        if stop is not None:
            guard.last_stop = None
            reply = _guard_reply(stop)
        if guard.notices and isinstance(reply, dict):
            reply = {**reply, "guard_notices": list(guard.notices)}
            guard.notices.clear()
        return reply

    return wrapper


def build_server(**dejo_options: Any) -> FastMCP:
    # Dejo builds its sessions and replays from these two names. Pointing them at the guarded
    # versions puts ArmorIQ in front of every action without changing a line of Dejo.
    dejo_server.Session = GuardedSession  # type: ignore[misc]
    dejo_server.Executor = GuardedExecutor  # type: ignore[misc]
    server = dejo_server.build_server(**dejo_options)
    server._mcp_server.name = "dejo-guard"
    server._mcp_server.instructions = (server.instructions or "") + GUARD_RULES
    guard = guard_mod.current()
    tools = server._tool_manager

    for name in ("dejo_act", "dejo_run", "dejo_repair"):
        tool = tools.get_tool(name)
        if tool is not None:
            tool.fn = _guarded(tool.fn)

    read_tool = tools.get_tool("dejo_read")
    if read_tool is not None:
        original_read = read_tool.fn

        @functools.wraps(original_read)
        def guarded_read(*args: Any, **kwargs: Any) -> Any:
            dejo_tools = server.dejo_tools  # type: ignore[attr-defined]
            url = ""
            # No page yet is fine: the read itself will say so.
            with contextlib.suppress(Exception):
                url = dejo_tools.worker.submit(lambda browser: browser.page.url)
            try:
                guard.check(PageFacts(action="read", page_url=url), intent=kwargs.get("intent") or "read the page")
            except GuardStop as stop:
                return _guard_reply(stop)
            return original_read(*args, **kwargs)

        read_tool.fn = guarded_read

    @server.tool()
    def guard_task(task: str, sites: list[str] | None = None) -> dict[str, Any]:
        """Declare the task BEFORE acting on any website. Call this first, every new task.

        ArmorIQ signs a plan from it: the goal plus the kinds of action this task may use
        (looking and navigating always; forms, carts and payments only when the task asks
        for them). An action outside the plan is refused as intent drift.

        Args:
            task: the user's request, in their own words — "compare prices for this book",
                "add the cheapest one to my cart", "buy it".
            sites: the site(s) this task works on, as domains ("amazon.in"). Going to any
                other site is held for approval.
        """
        wanted = {site_of(s) for s in (sites or []) if s}
        result = guard.start_task(task, wanted, plan_for(task))
        if result["refused"]:
            return {"ok": False, **result, "next": "ArmorIQ refused this plan. Tell the user why."}
        return {"ok": True, **result,
                "next": ("Plan signed by ArmorIQ. `classes` are in the plan; ArmorIQ's policy still allows, "
                         "holds or blocks each one. `drift_if` would be refused as intent drift. "
                         "Go ahead — dejo_run first, then explore if unknown.")}

    @server.tool()
    def guard_wait(hold_id: str, seconds: int = 90) -> dict[str, Any]:
        """Wait for a held action to be approved in ArmorIQ, then run it.

        Args:
            hold_id: `guard.hold_id` from the reply that was held.
            seconds: how long to wait this call (at most 240). Call again if still pending.
        """
        dejo_tools = server.dejo_tools  # type: ignore[attr-defined]
        timeout = max(1, min(int(seconds), 240))
        try:
            return dejo_tools.worker.submit(lambda _browser: guard.wait(hold_id, timeout))
        except GuardStop as stop:
            return _guard_reply(stop)
        except Exception as failure:  # noqa: BLE001
            return {"ok": False, "error": str(failure)}

    @server.tool()
    def guard_status() -> dict[str, Any]:
        """The plan ArmorIQ signed for this task, the held actions, and the last decisions."""
        task = guard.gate.task
        return {
            "ok": True,
            "task": None if task is None else {
                "id": task.id, "goal": task.goal, "plan_id": task.plan_id, "classes": list(task.classes),
                "sites": sorted(task.sites), "refused": task.refused,
            },
            "held": [{"hold_id": k, "class": p.decision.cls, "words": p.facts.words, "page": p.facts.page_url}
                     for k, p in guard.pending.items()],
            "recent": [{k: r[k] for k in ("action", "cls", "decision", "reason", "page_url", "words")}
                       for r in guard.feed.recent(10)],
            "classes": list(CLASSES),
        }

    return server


def run_stdio() -> None:
    from dejo.home import setting

    # Dejo hard-codes a 1280x800 page (docs/DEJO-LIMITATIONS.md). DEJO_GUARD_VIEWPORT=WxH overrides it, so a headed
    # window narrower than 1280 px shows the whole page instead of cutting it off.
    size = setting("DEJO_GUARD_VIEWPORT")
    if size and "x" in size:
        import dejo.browser as dejo_browser

        w, h = (int(v) for v in size.lower().split("x", 1))
        dejo_browser.VIEWPORT.update({"width": w, "height": h})

    if setting("DEJO_GUARD_RECORD"):
        # Recording mode (stage.py): frames at 1920 px wide whatever the page size, like a 1080p screen.
        import dejo.browser as dejo_browser

        context_options = dejo_browser.Browser._context_options
        scale = 1920 / dejo_browser.VIEWPORT["width"]
        dejo_browser.Browser._context_options = lambda self: {**context_options(self), "device_scale_factor": scale}

    headed = (setting("DEJO_GUARD_HEADED") or "") in ("1", "true", "yes")
    if headed:
        # Dejo launches Chrome with --no-sandbox, which puts a warning bar on every headed window (DEJO-LIMITATIONS 3).
        import dejo.browser as dejo_browser

        # Playwright adds the flag itself unless the launch asks for Chrome's sandbox.
        launch_options = dejo_browser.Browser._launch_options
        dejo_browser.Browser._launch_options = lambda self: {**launch_options(self), "chromium_sandbox": True}
        # --test-type hides Chrome's "unsupported command-line flag" bar for Dejo's own flags.
        if "--test-type" not in dejo_browser.QUIET_ARGS:
            dejo_browser.QUIET_ARGS.append("--test-type")

    server = build_server(
        agent=setting("DEJO_AGENT"),
        profile=setting("DEJO_PROFILE"),
        profiles_dir=setting("DEJO_PROFILES_DIR"),
        db_path=setting("DEJO_DB"),
        headless=not headed,
    )
    _log("ready — ArmorIQ decides every page action. Call guard_task first.")
    try:
        server.run()
    finally:
        server.dejo_tools.close()  # type: ignore[attr-defined]


def run_http(port: int, public_host: str | None = None) -> None:
    """The same server over streamable HTTP at /mcp — how the guard is onboarded on platform.armoriq.ai.

    `public_host` is the one extra Host header to accept (a tunnel's hostname). Everything else keeps the MCP
    library's DNS-rebinding protection: only localhost may talk to it.
    """
    from dejo.home import setting
    from mcp.server.transport_security import TransportSecuritySettings

    server = build_server(agent=setting("DEJO_AGENT"), profile=setting("DEJO_PROFILE"),
                          profiles_dir=setting("DEJO_PROFILES_DIR"), db_path=setting("DEJO_DB"))
    server.settings.host = "127.0.0.1"
    server.settings.port = port
    hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*", *([public_host] if public_host else [])]
    server.settings.transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True, allowed_hosts=hosts,
        allowed_origins=[f"http://{h}" for h in hosts] + ([f"https://{public_host}"] if public_host else []))
    _log(f"serving on http://127.0.0.1:{port}/mcp")
    try:
        server.run(transport="streamable-http")
    finally:
        server.dejo_tools.close()  # type: ignore[attr-defined]
