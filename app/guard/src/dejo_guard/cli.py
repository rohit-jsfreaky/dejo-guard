"""`dejo-guard` — the MCP server, plus a few commands a person runs once.

    dejo-guard               run the MCP server on stdio (what `claude mcp add` starts)
    dejo-guard init          check the setup and print the next steps
    dejo-guard policy        print the ArmorIQ policy YAML to import
    dejo-guard plan "<task>" show which action classes a task's words unlock
    dejo-guard feed          print the latest decisions
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from . import config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dejo-guard", description="ArmorIQ decides every browser-agent action.")
    sub = parser.add_subparsers(dest="command")
    serve = sub.add_parser("serve", help="run the MCP server on stdio (the default)")
    serve.add_argument("--http", type=int, metavar="PORT", help="serve over streamable HTTP on this port instead (for onboarding)")
    serve.add_argument("--public-host", help="also accept this Host header over HTTP (a tunnel's hostname)")
    share = sub.add_parser("share", help="make a hosted live feed and stream every decision to it")
    share.add_argument("--site", default="https://dejo-guard.vercel.app")
    share.add_argument("--label", default=None)
    ini = sub.add_parser("init", help="check the setup, write the policy for your org, print the next steps")
    ini.add_argument("--agent", help="the dejo-guard-agent id from the ArmorIQ dashboard")
    ver = sub.add_parser("verify", help="one PASS/FAIL line per claim (live ArmorIQ checks unless --offline)")
    ver.add_argument("--offline", action="store_true")
    ev = sub.add_parser("eval", help="run the eval: attack lab + journeys, 3 arms -> evidence/eval.json")
    ev.add_argument("arms", nargs="*", help="none, names, guard (default: all)")
    pol = sub.add_parser("policy", help="print the ArmorIQ policy YAML")
    pol.add_argument("--org", default="<your org id>")
    pol.add_argument("--agent", default="<dejo-guard-agent id>")
    plan = sub.add_parser("plan", help="show what a task's words (and guard.yaml) unlock")
    plan.add_argument("task")
    plan.add_argument("--site", action="append", default=[], help="a site the task names (guard.yaml sites)")
    feed = sub.add_parser("feed", help="print the latest decisions")
    feed.add_argument("-n", type=int, default=20)
    feed.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.command in (None, "serve"):
        from .server import run_http, run_stdio

        if getattr(args, "http", None):
            run_http(args.http, args.public_host)
        else:
            run_stdio()
        return 0
    if args.command == "share":
        return _share(args.site, args.label)
    if args.command == "policy":
        from .policy import policy_yaml

        sys.stdout.write(policy_yaml(args.org, args.agent))
        return 0
    if args.command == "plan":
        from . import userplan
        from .facts import site_of
        from .guard import plan_for

        sites = {site_of(s) for s in args.site}
        print(" ".join(dict.fromkeys((*plan_for(args.task), *userplan.extra_classes(args.task, sites)))))
        return 0
    if args.command == "feed":
        from .feed import Feed

        rows = Feed().recent(args.n)
        if args.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
            return 0
        for r in reversed(rows):
            when = time.strftime("%H:%M:%S", time.localtime(r["at"]))
            print(f"{when}  {r['decision']:<8} {r['cls']:<15} {r['action']:<10} {(r['words'] or '')[:30]:<30} "
                  f"{(r['reason'] or '')[:60]}")
        return 0
    if args.command == "init":
        return _init(args.agent)
    if args.command == "verify":
        from .verify import main as verify_main

        return verify_main(["--offline"] if args.offline else [])
    if args.command == "eval":
        from .eval import main as eval_main

        return eval_main(args.arms)
    return 1


def _share(site: str, label: str | None) -> int:
    """Make a hosted feed and save its write token in ~/.dejo-guard/.env (never printed)."""
    import httpx

    res = httpx.post(f"{site.rstrip('/')}/api/feed/new", json={"label": label}, timeout=20)
    data = res.json()
    if not data.get("ok"):
        print(f"could not make a feed: {data}")
        return 1
    env = config.HOME / ".env"
    env.parent.mkdir(parents=True, exist_ok=True)
    keep = [line for line in (env.read_text(encoding="utf-8").splitlines() if env.exists() else [])
            if not line.startswith(("DEJO_GUARD_FEED_URL=", "DEJO_GUARD_FEED_TOKEN=", "DEJO_GUARD_FEED_ID="))]
    keep += [f"DEJO_GUARD_FEED_URL={data['post']}", f"DEJO_GUARD_FEED_TOKEN={data['token']}", f"DEJO_GUARD_FEED_ID={data['id']}"]
    env.write_text("\n".join(keep) + "\n", encoding="utf-8")
    print(f"Live feed: {data['watch']}")
    print(f"Every decision is now also sent there. The write token is saved in {env}.")
    return 0


def _init(agent_uuid: str | None = None) -> int:
    """Check the setup, fill in what `armoriq login` already knows, and print the two dashboard steps left."""
    ok = True
    key, source = config.api_key()
    org = config.setting("ARMORIQ_ORG_ID") or (
        (config.saved_for_backend() or {}).get("orgId") if source == str(config.login_file()) else None) or None
    print(f"ArmorIQ key ........ {f'found ({source})' if key else f'MISSING: {source}. Run `armoriq login` or set ARMORIQ_API_KEY'}")
    print(f"ArmorIQ org ........ {org or 'unknown — `armoriq login` fills it, or set ARMORIQ_ORG_ID'}")
    ok &= bool(key)
    print(f"ArmorIQ agent ...... {config.agent_id()}")
    print(f"Holds filed as ..... {config.requester()}  (not an org member, so you can approve them)")
    print(f"Decision feed ...... {config.feed_path()}")
    from . import userplan
    from .policy import policy_yaml

    made = userplan.write_default()
    print(f"Plan additions ..... {userplan.PATH}{'  (written, all empty)' if made else ''}")
    try:
        import dejo  # noqa: F401

        print("Dejo ............... installed")
    except ImportError:
        print("Dejo ............... MISSING")
        ok = False
    policy_file = config.HOME / "policy.yaml"
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    policy_file.write_text(policy_yaml(org or "<your org id>", agent_uuid or "<dejo-guard-agent id>"), encoding="utf-8")
    print(f"Policy ............. {policy_file}{'' if agent_uuid else '  (agent id still a placeholder)'}")
    print()
    print("Two steps on platform.armoriq.ai (its API needs your dashboard login for these):")
    if not agent_uuid:
        print(f"  1. Inventory → Agents → Add agent → Connect by URL. Name: {config.agent_id()}, URL: any https URL.")
        print("     Copy the agent id it shows, then run:  dejo-guard init --agent <that id>")
    print(f"  {'1' if agent_uuid else '2'}. Policies → Import YAML → paste {policy_file.name} → Import → Activate.")
    print()
    print("Then:  claude mcp add dejo-guard -- dejo-guard")
    print('       ask your agent: "compare prices for Atomic Habits on dejo-guard.vercel.app/shop, then buy the cheapest"')
    print("       check it any time with:  dejo-guard verify")
    return 0 if ok else 1
