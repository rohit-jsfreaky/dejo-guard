# RESEARCH — facts with sources (Dejo Guard)

Idea research: `hackathon_ideas/contexts/flowstate-RUN-2.md`, `armoriq-flow-state-FIELD-2026-10-15*.md`,
`evidence-flowstate-chatgpt-*.txt`, `evidence-fuzail-*.png`. Not checked = NOT VERIFIED.

## Judges and sponsor taste
- Fuzail Kazi, X, 8 Oct 2026: "Hiring 2 engineers to join the Developer Products team at @armoriqAI … You ship dev tools end
  to end, know how AI and systems really work, and obsess over the developer experience." 9 Oct: "We're hosting a hackathon".
- Fuzail, X, 4 Oct 2026 (x.com/fuzailkazi_/status/2106703593881616738): "will pay $1,000 to whoever builds an agent that doesn't
  do this" — 28 s video: intent "fix the flaky checkout test" → `fs.read`/`test.run` on intent, `db.reset("staging")` drifting,
  `db.drop("production")` blocked, "Intent drift detected · blocked before it ran". Frames saved: `evidence-fuzail-video-*.png`.
- ArmorIQ, X, 12 Dec 2025: "AI browsers aren't getting hacked. They're getting manipulated. One hidden prompt in a URL fragment
  and your 'smart' browser becomes an obedient idiot."

## ArmorIQ platform facts (probed 15–16 Oct with our org)
- Native policy engine input = `{context, subject, policies, resource: {toolName}}` — no arguments (Spokesperson finding 7).
- `armor.policy.v1` profile via `POST /policies/sync` (API key works): rejects `browser_click` ("Unknown tool"), custom fields
  ("Unknown condition field: args.element_label"); `defaults.decision` must be allow/deny/hold; statements need
  `principal` + `resource` objects. Known fields: tool.name, bash.program, bash.raw, bash.hasWriteRedirection, file.path,
  network.host, mcp.server (docs.armoriq.ai, ArmorClaude policy rules). Probe 16 Oct 00:16 IST; nothing was activated.
- `/iap/enforce` with API key + arguments → `{"allowed":true,"action":"allow","reason":"no-active-policies"}` (no profile).
- SDK local mode (16 Oct 00:12 IST): plan + token 5.2–6.9 s; enforce allow 0.48–1.1 s, block `policy_constraints_not_satisfied`,
  hold `rule_action_hold` (no delegation id in local mode → use sdk `check()` for holds). Warning: "fetched IAP public key could
  not be parsed as Ed25519"; `GET /iap/public-key` → `{"alg":"EdDSA","enabled":false,"publicKey":null,"jwk":null}`.
- SDK sdk mode (15 Oct): plan + token ~3.8 s, check 0.9–1.8 s.
- Dashboard endpoints (`/agent/agents`, `/policies`) need the dashboard JWT: API key → 401 "Access token is required".
- Policy import quirks + holds need a 2nd identity: `D:\my_projects\hackathons\spokesperson\evidence\armoriq-findings-live.md`.
- Free org quotas: 2 MCP, 4 agents, 2 policies, 2 proxies (docs, read 10 Oct).
- MCP registration: "Endpoint: Public HTTPS URL" (docs).
- `armoriq login` = device flow, mints an API key scoped to the user's org (docs, SDK & CLI).
- No browser-agent product or doc page in ArmorIQ docs (`llms-full.txt`, grep 16 Oct).

## Dejo (pre-existing, disclosed)
- PyPI `dejo` 0.1.1 and `dejo-mcp` 0.1.1, Python ≥ 3.11, MIT © 2026 Rohit Kashyap; releases 13–14 Oct 2026 UTC.
- Install: `pip install dejo-mcp` + `playwright install chromium` (~150 MB) + `claude mcp add dejo -- dejo-mcp`.
- `dejo_act(intent, action, ref, value, to)`; controls carry `use` strings like `role=button|Sign in`; stdio MCP only.
- Benchmark in the Dejo repo: 30 journeys (`benchmarks/benchmark-journeys10.json`) → our false-hold baseline.

## Field (34 confirmed, 15 Oct night)
- 0 browser-agent entries; 0 commits matching `armoriq browser/playwright/checkout` since 10 Oct.
- Closest: IntentGate (MCP gateway, signed plan + argument binding, `npx`), Udte Bhawre (desktop companions, Playwright MCP in a
  marketplace, tool-name guard; unconfirmed entry), Huddle.
- Outside (GitHub, created since Aug): a handful of browser guards (playwright-write-guard, mexx-browser-agent risk firewall,
  browser-account-guard) — little exposure.
- ArmorIQ's August event repos: refund/invoice/insurance/SRE agents — do not resemble them.

## Demand proof (vendors, not users)
- Claude for Chrome: "lets Claude intervene if it detects that you are on a high-risk website" (support.claude.com).
- Comet: "asks permission for sensitive operations such as purchases" (ChatGPT research, 15 Oct).
- User-voice incident posts are thin (X/HN searches 16 Oct) — say so; Rohit's own daily browser automation is the user voice.

## Learned the hard way (fill during the build — goes into the README)
- …
