# MASTER-PLAN — Dejo Guard (Fri 16 Oct → Sat 17 Oct 2026, IST)

**Submit by Sat 17 Oct, 6:00 PM IST** (hard close 11:30 PM). Other deadlines in the same window: AMD MotherTongue Sun 18 Oct
3:30 PM; Graph Hacks dropped. When time is short, cut P1 and polish — never the ArmorIQ decisions, the eval number, the live
URL or the video.

## Phase 0 — setup + probes (Fri morning, ~2 h)
- [ ] Rohit: sign in at platform.armoriq.ai in the Playwright window (dashboard login needed for policy import + registration).
- [ ] Free the Spokesperson slots: deactivate its policy, remove `voice`/`facts` MCPs (screenshot first; Spokesperson is dropped).
- [ ] Register agent `dejo-guard-agent` + MCP `sandbox-shop` (Vercel URL); import + activate `dejo-guard-boundary` (GUARD-MODEL §5).
- [ ] Probe: one plan with `read`/`navigate`/`submit_form`/`type_payment` steps through local mode → allow/hold/block + a real
      delegation approved by Rohit → `evidence/probe-day0.md`.
- [ ] Official init: `uv init --vcs none app/guard`; `npx create-next-app@latest app/web` (no git); sandbox shop as a Next.js route
      group or a tiny static site in `app/shop`.

## Phase 1 — guard core (Fri, ~5 h)
- [ ] MCP server `dejo-guard` wrapping Dejo's session (same tool names as dejo-mcp + `guard_status`).
- [ ] Page-fact extractor + class table (GUARD-MODEL §2) with unit tests on fixture HTML (labels in English + Hindi, mislabelled
      submit, payment iframe, password, plain link).
- [ ] ArmorIQ client: plan per task, local enforce per action, sdk `check()` for holds, fail closed, feed writer.
- [ ] **Record act 2** (Claude Code browsing + add to cart, allowed).

## Phase 2 — shop, attacks, holds, drift (Fri night, ~4 h)
- [ ] Sandbox shop: catalog, cart, checkout with fake card form, order MCP (`list_orders`, `get_order`), 6–10 attack pages
      (hidden injection, "Continue" = pay submit, card iframe, new-domain redirect, auto-submit form, Hindi labels).
- [ ] Holds end to end (approve in ArmorIQ → guard continues); **record act 3**.
- [ ] Intent plan + drift + replay pre-check; remove-a-rule demo; **record act 4**.

## Phase 3 — prove (Sat morning, ~3 h)
- [ ] `guard-eval`: same attack pages × 3 arms (no guard / tool-name policy / Dejo Guard) → `evidence/eval.json`.
- [ ] False holds: Dejo's 30 journeys with guard on → `evidence/false-holds.json`. Runs in GitHub CI, not on the laptop.
- [ ] `docs/FINDING.md` (question, data, method, control, limits); manifest with commit + hashes.
- [ ] Upstream issue text (public key disabled + no browser vocabulary) for Rohit to open.

## Phase 4 — ship (Sat, done by 6 PM)
- [ ] Web: landing (what it is in 10 s), /judges (90-second path), live feed; deploy on Vercel.
- [ ] README in kit order; Dejo + AI disclosure first screen; numbers re-synced.
- [ ] Video ≤ 90 s from the clips; deck PDF; proof screenshots.
- [ ] Zero-context install test; Rohit walkthrough (he explains the class table + policy).
- [ ] Submit on HackBriven by 6 PM; launch post on X.
