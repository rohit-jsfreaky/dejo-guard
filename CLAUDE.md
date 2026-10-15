# CLAUDE.md — Dejo Guard (read this first, every session)

**Dejo Guard = a browser agent that can use your logged-in websites, where ArmorIQ decides every click by what the click
MEANS on the page, not by the tool's name.**

> Pitch (the sentence a judge repeats): *"A browser agent has one tool: click. A rule on tool names can't tell 'Next page'
> from 'Pay ₹4,999'. Dejo Guard reads what each click means from the page itself and lets ArmorIQ decide. You said
> 'compare prices'; the agent is on the checkout page; ArmorIQ holds it."*
> One-sentence flip (Rule 11): everyone guards the agent's *arguments*; for a browser the arguments are meaningless
> (`ref: e12`). **Only the page knows that e12 is the Pay button.**

Built for **ArmorIQ Flow State** (online, 10–17 Oct 2026). **Deadline: Sat 17 Oct 2026, 11:30 PM IST (Luma) — submit by
6:00 PM IST.** Solo: Rohit (team "Boundary Labs"). Rules: `hackathon.md` — it outranks everything.
PRD = the truth: `DEJO-GUARD-PRD.md`. How a click becomes an ArmorIQ decision: `docs/GUARD-MODEL.md`. Live state:
`PROGRESS.md`. Facts with sources: `RESEARCH.md`. Idea research: `D:\my_projects\hackathon_ideas\contexts\flowstate-*`,
`armoriq-flow-state-*`, `evidence-flowstate-*`, `evidence-fuzail-*`.

## Who judges, and what they want
The organiser (Fuzail Kazi) runs this hackathon **to hire 2 engineers for ArmorIQ's Developer Products team**: "You ship dev
tools end to end, know how AI and systems really work, and obsess over the developer experience." So: a real dev tool,
installed in one command, working on the judge's OWN setup in 5 minutes, at $0, with ArmorIQ doing the deciding.

## ⛔ Locked decisions (16 Oct 2026)
1. **ArmorIQ decides, visibly.** Our code only DESCRIBES each action (page facts → named steps). ArmorIQ's policy allows,
   blocks or holds. Test that proves it: remove one rule from the ArmorIQ policy → that action goes through. Fail closed:
   ArmorIQ unreachable = nothing happens.
2. **Decide by page STRUCTURE, never by button words.** Labels lie ("Continue" can be a pay button) and change with language.
   Classes come from the DOM: a link that only navigates, a form submit, a password field, a card field (`autocomplete=cc-*`,
   payment iframes), a new domain, a download. Words are only a hint shown to the human.
3. **Intent drift is the headline.** At task start the guard declares a plan to ArmorIQ (goal + the action classes the task
   needs). An action outside the declared plan = drift → blocked or held (ArmorIQ's own core idea, Fuzail's 4 Oct video).
4. **Dejo is pre-existing and DISCLOSED.** `dejo` (MIT, PyPI 0.1.1, Rohit's own; Cairn won at Sibyl Labs, Sep 2026) is used
   as a library. **All guard code is new, written from 16 Oct**, in its own repo/package `dejo-guard`. README says so in the
   first screen.
5. **No real money, ever** (rule 7). Checkout and payment happen only on our own hosted **sandbox shop**. Real sites are used
   for reading and for held actions that never execute without approval.
6. **The user's own agent drives** (Claude Code, Claude Desktop, Cursor, Codex) through MCP. Dejo Guard makes no LLM calls
   of its own. No OpenRouter, no model key needed. Eval suites are scripted (no LLM); the video uses Claude Code.
7. **$0 to run:** ArmorIQ free org, Vercel free tier, local browser. ArmorIQ key comes from `armoriq login` (judges use
   their own org) or our demo key on the hosted pages. Keys live in `.env`, never committed, never printed.
8. **Never fake a number.** Every number in README / video / deck comes from a file in `evidence/` made by a script.
   Missing = "—" with the reason.
9. **Claude writes the code; Rohit reviews, understands and does all git.** Hand him one-line commit messages. Disclose AI
   assistance in the README. Use official init commands (`uv init --vcs none`, `create-next-app` without git).
10. **Laptop safety:** no full browser test suites on Rohit's laptop. Suites run in GitHub CI; locally only single runs.
11. **Look:** light, professional SaaS (memory: light mode, no gradients, Hanken Grotesk + a mono face, Phosphor icons). Never
    Inter, Lucide, the cream/rust palette, or red-heavy screens. Allowed = green, held = amber, blocked = slate with a strike.

## ArmorIQ facts to respect (RESEARCH.md has sources and dates)
- Free org quotas: **2 MCP servers, 4 agents, 2 policies, 2 proxies.** All slots free since 16 Oct (Spokesperson's policies,
  MCPs and agents deleted; backup in `spokesperson/evidence/armoriq-backup-2026-10-16.json`).
- Every agent and MCP must be **onboarded on platform.armoriq.ai**; MCP registration needs a **public HTTPS URL**.
- The native policy engine sees **tool names only, never arguments** (OPA input = `resource.toolName`). The argument-aware
  `armor.policy.v1` profiles reject custom tools ("Unknown tool") and custom fields — they know bash, files, network host,
  MCP server only. → Page facts are sent as **named plan steps** that the native policy decides (proven live in Spokesperson).
- `toolEnforcement` (hold/block) applies only to tools also listed in `allowedTools`; unlisted = block (no-match = block).
- Policy import: `POST /policies/yaml/import {yaml, onConflict:'replace'}` with NO `status:` line, then
  `POST /policies/{id}/activate` — needs the dashboard login (JWT), not the API key.
- SDK local mode decides allow/block/hold in ~0.5 s per action after a ~5 s plan signing; holds need SDK `check()` (sdk mode)
  to create a delegation. Self-approval is refused: requests go under a non-member identity, a member approves.
- `/iap/public-key` returns `enabled:false, publicKey:null` (16 Oct) → local mode can't verify signatures. Upstream report.

## Folder map
```
dejo-guard/
├── CLAUDE.md            this file
├── hackathon.md         rules + submission checklist — outranks everything
├── DEJO-GUARD-PRD.md    video script, user flow, claims→tests, judge Q&A, scope, build order
├── MASTER-PLAN.md       phases with hours to the deadline
├── PROGRESS.md          live state + the proof kit — read first, update last
├── RESEARCH.md          facts with sources
├── ROADMAP.md           NOT in this build
├── docs/GUARD-MODEL.md  page facts → action classes → ArmorIQ steps → decision
├── evidence/            one file per published number + probes + run manifest
└── app/                 guard (python pkg + MCP) · web (Next.js: landing, /judges, live feed) · shop (sandbox + its MCP)
```
