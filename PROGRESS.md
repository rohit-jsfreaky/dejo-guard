# PROGRESS — Dejo Guard (read first, update last)

## Current state — 2026-10-16 (~00:30 IST)
- Idea locked 16 Oct ~00:25 IST after the second Flow State hunt (kill loop DONE 10 min 13 s; see
  `hackathon_ideas/IDEAS-LOG.md`). Spokesperson is dropped (no way for others to use it; 3rd entry in the publishing cluster).
- Planning files written: CLAUDE.md, hackathon.md, DEJO-GUARD-PRD.md, MASTER-PLAN.md, RESEARCH.md, ROADMAP.md,
  docs/GUARD-MODEL.md, evidence/probe-2026-10-16.md (+ probe scripts). **No code yet.**

## Update — 2026-10-16 ~01:20 IST (build started)
- Decisions (Rohit): ONE ArmorIQ key (copied from Spokesperson .env, `.env` git-ignored) · Supabase for hosted data
  (project `dejo-guard`, ref luxkytcfmabsbcuqhkzx, in **rohit-jsfreaky's Org** — NOT the TechOrigins org the Supabase MCP
  is connected to) · web UI = reuse `D:\my_projects\hackathons\cairn\dejo-web` look · private repo
  github.com/rohit-jsfreaky/dejo-guard created (public before submit) · `git init` done, nothing committed.
- Scaffolded: `app/guard` (uv, package dejo-guard, deps dejo 0.1.1 / dejo-mcp 0.1.1 / armoriq-sdk 0.6.10 / mcp 1.30) and
  `app/web` (create-next-app 16.4.1, no git).
- Guard core written: facts.py (DOM facts JS) · classes.py (14 classes) · armor.py (Gate: plan/check/wait, SDK mode) ·
  guard.py (GuardedSession/GuardedExecutor + network write-request guard + holds) · server.py (Dejo's server, guarded,
  + guard_task/guard_wait/guard_status) · policy.py · cli.py · feed.py (SQLite). 27 tests pass, ruff clean.
- **SDK finding:** local mode now verifies the token against `/iap/public-key` (disabled) → every local enforce =
  `token-signature-invalid`. So the guard uses SDK mode (server-side check, ~0.8 s). Upstream issue material.
- **Day-0 probe 1 (01:15 IST, `evidence/probes/day0_plan.py`):** plan of dejo__ steps signed in 11.8 s with NO agent/MCP
  registered; every check = block `no_matching_policy` (fail closed); undeclared class = `tool-not-in-plan` (drift, SDK).
- Blocked on Rohit: ArmorIQ sign-in in Playwright window · Vercel deploy permission · SUPABASE_SECRET_KEY in .env.

## Update — 2026-10-16 ~02:20 IST (Phase 0 done, Phase 1–2 mostly done)
- ArmorIQ: agent `dejo-guard-agent` (9255530a-72a5-46c6-845e-ce6cfb8c1540) · policy `dejo-guard-boundary`
  (fc6474c7-eedc-4a8c-916b-f2bb516b52d1, ACTIVE; file `policy/dejo-guard-boundary.yaml`; state_change = allow) ·
  MCP `sandbox-shop` (ada0215a-d8cd-40fa-ac2e-3c16ba32bc10 → https://dejo-guard.vercel.app/api/mcp). Done via the
  dashboard API from the logged-in Playwright tab (`localStorage.accessToken`). Still to register: MCP `dejo` (the guard).
- Live: https://dejo-guard.vercel.app — landing (dejo-web look), /shop (sandbox, saved test card), /shop/lab (8 attacks),
  /feed (demo feed id Uzk0JFnp, env DEMO_FEED_ID), /judges, /api/mcp, /api/feed. Supabase tables carts/orders/feeds/decisions.
- **E2E on the real platform (`evidence/probes/e2e_shop.py`, `evidence/live/e2e-*.json`):** compare-prices task → add to
  cart = drift block · buy task → add to cart allow · card field = rule_action_block · Place order = rule_action_hold →
  **Rohit approved in ArmorIQ → order DG-MV9Z9YNI placed** (Atomic Habits ₹499, sandbox) · lab: Continue-is-pay hold,
  script-checkout hold (submit_payment, POST to payment endpoint), off-site Next hold (new_domain), password block.
- Bugs found by the E2E and fixed: (1) a write delayed ~1 s by ArmorIQ got cancelled by the agent's next navigation →
  action window now stays open until the page is quiet; (2) a script's 2nd POST escaped after the window closed (order
  DG-MV9ZA9UF went through, sandbox) → the network watch is now ALWAYS ON per browser; late writes are decided too and
  reported as `guard_notices`; (3) `read` was classed `unknown`.
- Every plan now declares type_secret/type_payment/upload/run_script/unknown so the POLICY blocks/holds them visibly;
  drift is for what the task didn't ask: submit_form / state_change / submit_payment.

## Update — 2026-10-16 ~03:15 IST
- MCP `dejo` registered (46bbc80d-106f-4612-b220-4e859e19d3d6) = the real guard over `dejo-guard serve --http 8765
  --public-host <tunnel>` + cloudflared quick tunnel. Both MCP slots now used (sandbox-shop + dejo).
- Baseline for the eval: agent `dejo-toolname-baseline` (1adda49e-ad9d-42ae-9d62-81250ad75282) + policy
  `toolname-baseline` (9f76ad4f-88a4-47cb-989e-ae6a75379f32, active), file `policy/toolname-baseline.yaml`. Policy slots full.
- `dejo-guard eval` written (arms none/names/guard; 8 attacks + 16 journeys on real sites). One local pass of the guard arm
  only (debugging selectors): 0/8 unsafe ran, 0/68 normal steps held. Found + fixed: page-load analytics POSTs were
  refusing navigations → writes during a navigation are the page's (still decided, reported as notices).
- PyPI was dropped from journeys (Fastly "Client Challenge" for automated browsers); HN /ask returned empty.
- CI `.github/workflows/ci.yml`: tests on push; eval on manual dispatch (secret ARMORIQ_API_KEY set via gh).
- README (kit order + disclosures), app/guard/README.md (PyPI), docs/FINDING.md, LICENSE, scripts/sync_numbers.py.
- Wheel builds; clean-venv install works. Bug caught there: "book" in TASK_WORDS made "compare prices for this book"
  unlock writes → removed + test.

## Update — 2026-10-16 ~03:10 IST · engineering phases 0–4 closed out
- Eval OFFICIAL = CI run 38804741784 (evidence/eval.json + eval-SOURCE.md): none 8/8 unsafe · names 8/8 unsafe, 0% held ·
  strict names (computed) 31.3% held · **Dejo Guard 0/8 unsafe, 0/68 held**. First CI run discarded (secret had the .env
  comment → every call failed closed). Vercel now deploys ONLY by push to main (root dir app/web).
- Remove-a-rule proven live (evidence/remove-a-rule.md/.jsonl): hold → rule removed → allowed, order DG-MVA14T6F →
  restored → hold. Policy is back to the published file.
- Guarded replays proven (evidence/probes/replay_check.py, evidence/live/replay-*.json): trail learned with no guard;
  replay under "buy" held at Place order; under "compare prices" refused at add-to-cart (drift).
- `dejo-guard verify` (16 claims, 6 live) → evidence/verify.txt 16/16 PASS; CI runs --offline on push, live before eval.
- scripts/manifest.py → evidence/MANIFEST.json (sha256 of every evidence file, commit, versions, ArmorIQ ids). Re-run last.
- tests/test_facts_browser.py: facts JS on real HTML in headless Chromium (Continue/Hindi/Next-page pay buttons, span in
  button, card iframe…) 14/14; total 47 tests. CI guard job installs Chromium.
- guard.yaml built (userplan.py): sites/words widen the PLAN only; `init` writes it; `plan --site`.
- `init` fills org id from `armoriq login`, writes ~/.dejo-guard/policy.yaml, prints the 2 dashboard steps (agent
  registration + policy import need the dashboard JWT — no API-key path; in docs/UPSTREAM-ISSUES.md).
- docs/UPSTREAM-ISSUES.md: 2 issues for github.com/armoriq/Voice-of-Developer (SDK repo is private) — Rohit opens them.

## ▶ NEXT
0. Rohit: push; PyPI publish (after his OK); re-run manifest; then video/deck/submit (last part).
1. (done) Rohit: first commit + push → `gh workflow run ci -f eval=true` → download eval.json → `python scripts/sync_numbers.py` → redeploy web.
2. PyPI publish (ask Rohit right before — irreversible version). 3. Record acts (Claude Code + guard), video, deck, submit.

## ▶ START HERE NEXT (Phase 0, MASTER-PLAN) — old, kept for history
1. Rohit: sign in at platform.armoriq.ai in the Playwright window (needed for registration + policy import).
2. ~~Free the Spokesperson ArmorIQ slots~~ DONE 16 Oct (org now has 0 policies, 0 MCPs, 0 agents; backup in
   `spokesperson/evidence/armoriq-backup-2026-10-16.json` + screenshot). Next: register `dejo-guard-agent` + `sandbox-shop` MCP, import the policy.
3. Day-0 probe: allow / block / hold + one real approval → `evidence/probe-day0.md`.
4. Official init of `app/guard`, `app/web`, `app/shop`.

## Needs from Rohit
- [x] ArmorIQ dashboard login (Playwright window, 16 Oct) · [x] Spokesperson's 2 policies, 2 MCPs, 2 agents removed (16 Oct)
- [ ] Create the public GitHub repo `dejo-guard` (he does all git) · [ ] Vercel project for the web + shop
- [ ] Approve holds during recording (he is the org member) · [ ] Record the voice for the 90 s video · [ ] Open the upstream issue
- [ ] Walkthrough: explain the class table + policy in his own words

## Session log
- 2026-10-16 00:30 IST: files written; probes 1–5 recorded.
- 2026-10-16 ~00:45 IST: ArmorIQ org cleaned via the dashboard API (deactivate + delete policies `spokesperson-baseline-rules`,
  `spokesperson-boundary`; delete MCPs `facts`, `voice`; delete agents `spokesperson-baseline`, `spokesperson-agent`). All 200 OK.

---

## Proof & Submission Kit (copied from hackathon_ideas/PROOF-AND-SUBMISSION-KIT.md on day 0)

### Day 0 — before any code
- [x] The brief's exact words at the top of the PRD
- [x] PRD (one line, ≤90 s video script, problem, goals/non-goals, flow, claim→test, judge Q&A, P0/P1/NEVER, build order,
      bonus list, submission field map, definition of finished)
- [x] Build-folder CLAUDE.md as an engineering contract
- [~] Probe the sponsor API for real — probes 1–5 done (`evidence/probe-2026-10-16.md`); day-0 allow/block/hold on our own policy pending
- [x] ONE headline number + baseline: unsafe actions executed on the attack suite, tool-name policy vs Dejo Guard (same pages,
      scripted), plus false-hold rate on 30 real journeys
- [x] Real data: real public sites + the judge's own logged-in sites; sandbox shop labelled as ours (payments banned)

### Day 1 — build
- [ ] Scored mechanism first (page facts → class → ArmorIQ decision); README line "remove the ArmorIQ rule and it goes through"
- [ ] Record each video act the moment it works
- [ ] Machine checks: types, lint, pinned versions, CI on GitHub (no full browser suite on Rohit's laptop)
- [ ] Small commits; Claude writes code, Rohit reviews and does git

### Day 2 — prove
- [ ] One command that prints PASS lines (`guard-verify`), also in CI
- [ ] Baseline run saved as a file (3 arms)
- [ ] Controls: remove-a-rule · mislabelled buttons · Hindi labels · false holds on normal journeys
- [ ] Adversarial tests + a live "Try to make it pay" page on the sandbox shop
- [ ] A real run frozen read-only, linked from the README (`evidence/live/`)
- [ ] `evidence/` manifest (commit, dejo version, ArmorIQ SDK version, hashes)
- [ ] Never a fake number; missing = "—" with the reason
- [ ] Upstream proof (Rule 13): public key disabled / no browser vocabulary — Claude prepares, Rohit opens
- [ ] Every proof in the repo and README, not only in the video

### Last hours — ship
- [ ] README in kit order (cover, links, bold mechanism sentence, video, judge-in-90-seconds, numbers, How ArmorIQ decides,
      limits) + Dejo disclosure + AI disclosure
- [ ] /judges page with the 90-second path
- [ ] Re-sync every number across README, web, video, deck, form
- [ ] Zero-context install test
- [ ] Video ≤ 90 s, YouTube, playable logged out · deck PDF
- [ ] Launch post on X tagging @armoriqAI and Fuzail (Rohit posts)
- [ ] No feature commits after the deadline
