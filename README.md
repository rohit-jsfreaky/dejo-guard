# Dejo Guard — your agent clicks, ArmorIQ decides

[![ci](https://github.com/rohit-jsfreaky/dejo-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/rohit-jsfreaky/dejo-guard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/dejo-guard?label=dejo-guard)](https://pypi.org/project/dejo-guard/)

**A browser agent has one tool: click. A rule on tool names can't tell “Next page” from “Pay ₹4,999” — to the rule,
both are `click(ref=e12)`. Dejo Guard reads what e12 *is* from the page, and lets ArmorIQ decide.**

Dejo Guard gives Claude Code, Cursor, Codex or any MCP agent a real browser on your logged-in sites. Before every
click, keystroke or replayed step it looks at the page — is this a link, a form submit, a card field, a password box,
another website? — and sends that meaning to **[ArmorIQ](https://armoriq.ai)**. Your ArmorIQ policy allows it, blocks
it, or holds it until you approve. Browsing goes through. Card fields are blocked. “Place order” waits for you.

**Our code only describes. ArmorIQ decides.** Delete one line from the ArmorIQ policy and the same click goes through
on the next try — [we did, and logged it](#proof-that-armoriq-decides).

**[dejo-guard.vercel.app](https://dejo-guard.vercel.app)** · [For judges, 90 s](https://dejo-guard.vercel.app/judges) ·
[Attack lab](https://dejo-guard.vercel.app/shop/lab) · [Live decision feed](https://dejo-guard.vercel.app/feed) ·
Video: _added on submission_

[Install](#install) · [Quick start](#quick-start) · [The finding](#the-finding) · [How it works](#how-it-works) ·
[What a click means](#what-a-click-means) · [Proof](#proof-that-armoriq-decides) ·
[Troubleshooting](#when-something-goes-wrong) · [Prior work](#prior-work)

> **Built for ArmorIQ Flow State (October 2026) by Rohit Kashyap — Boundary Labs.** Dejo Guard is built on
> **[Dejo](https://dejo.run)**, the browser with a memory (MIT, on PyPI since 13 Oct 2026, same author, written
> before the hackathon), used as a library. **Everything in this repo is new**, written from 16 Oct: page facts, the
> class table, intent plans, holds and approvals, the network watch, guarded replays, the sandbox shop, the attack
> lab, the eval and the website. **AI assistance:** Claude Code wrote much of the code; the author designed it,
> reviewed every change, and ran every test and every ArmorIQ approval himself.

---

## Install

Python 3.12 or newer.

```bash
pip install dejo-guard
playwright install chromium      # the browser is a separate download, ~150 MB
armoriq login                    # your own free ArmorIQ org; the CLI comes with dejo-guard
dejo-guard init                  # checks everything, writes your policy file
```

`init` finds your org from `armoriq login` and writes `~/.dejo-guard/policy.yaml`. Two things then need the ArmorIQ
dashboard, because its API only accepts a dashboard login for them — `init` prints both:

1. **Inventory → Agents → Add agent** → Connect by URL, name `dejo-guard-agent`. Then `dejo-guard init --agent <its id>`.
2. **Policies → Import YAML** → paste the policy file → Import → **Activate**.

Then point your agent at it. For Claude Code:

```bash
claude mcp add dejo-guard -- dejo-guard
```

Cursor and Codex take the same command in their own MCP config. Check everything at any time — one line per claim,
asked live of your own ArmorIQ:

```bash
dejo-guard verify
```

**No model key.** Dejo Guard never calls a model; your agent does the thinking. **$0:** ArmorIQ's free org is enough.

## Quick start

Ask your agent, in your own words:

> Find the cheapest copy of Atomic Habits on dejo-guard.vercel.app/shop and buy it.

It declares the task to ArmorIQ first (`guard_task`), then browses: search, open the book, add to cart — all allowed.
At checkout it clicks **Place order**, and the reply it gets back is ArmorIQ's, word for word:

```json
{ "ok": false,
  "guard": { "decision": "hold", "class": "submit_payment",
             "because": "<button type=submit> submits its form; its form has card fields",
             "reason": "rule_action_hold", "policy": "dejo-guard-boundary",
             "words": "Place order · ₹499", "page": "https://dejo-guard.vercel.app/shop/checkout" } }
```

Approve it in ArmorIQ → **Held Actions**. Your agent calls `guard_wait`, ArmorIQ allows that one click, and the order
is placed (in our sandbox shop — no real money, ever). Ask it to type a card number instead and it is **blocked**.
Say *“compare prices”* and then let it try to buy — **refused as intent drift**, because buying was never in the plan
ArmorIQ signed.

Prefer a terminal?

```bash
dejo-guard plan "compare prices for this book"   # what a task's words unlock
dejo-guard feed                                  # the latest decisions
dejo-guard share                                 # a live web page of your decisions
```

## The finding

The same 8 attack pages and the same 68 ordinary browsing steps on real sites (Wikipedia, GitHub, Python docs, MDN,
Hugging Face, pkg.go.dev, the Rust book, Hacker News), through three setups. Scripted, no model in the loop, run in
GitHub CI. Every guarded decision is a real ArmorIQ decision.

<!-- numbers:start -->
| | unsafe actions that ran (of 8) | normal steps held or blocked (of 68) |
|---|---|---|
| no guard | **8** | — (nothing is ever held) |
| ArmorIQ on tool names (`click`, `fill`…) | **8** | 0.0% |
| ArmorIQ on tool names, strict (hold every click/fill/press) — computed | 0 | 31.3% |
| **Dejo Guard** (ArmorIQ on page meaning) | **0** | **0.0%** |

<sub>Run 2026-10-15T20:58:19+0000 · dejo-guard 0.1.0 · armoriq-sdk 0.6.10 · raw: [`evidence/eval.json`](evidence/eval.json) · method: [`docs/FINDING.md`](docs/FINDING.md)</sub>
<!-- numbers:end -->

**A rule on tool names has two choices: let every attack through, or hold a third of normal browsing.** Told what the
click means, the same ArmorIQ stopped all 8 and held nothing normal.

Two things this table should also tell you, because they are true:

- **The attacks are ours.** Eight pages we built from tricks we know: a pay button labelled “Continue”, a checkout in
  Hindi, a hidden “the user already approved” note, a plain button whose script buys, a card box inside a frame, a
  “Next page” link to another site, a fake password prompt, Enter in a POST form. They are not every trick.
- **One run, real sites.** Sites change; a step that fails for a reason outside the guard is counted as an error, not
  hidden. Method and limits: [`docs/FINDING.md`](docs/FINDING.md).

Run it yourself: `dejo-guard eval` (it is the `eval` job in [CI](.github/workflows/ci.yml)).

## How it works

Three steps, on every single action.

| | what happens |
|---|---|
| **1 · the task** | Your agent calls `guard_task` with your words. ArmorIQ signs a plan of what this task may do. Browsing always; forms, cart writes and payment only if you asked for them. |
| **2 · the page** | Before the click, Dejo Guard reads the element from the live page — tag, type, `autocomplete`, its form's method and fields, where a link goes, which frame it is in — and names it with one class. The button's words are shown to you, never used. |
| **3 · ArmorIQ** | The class goes to ArmorIQ as a named step of the signed plan (`dejo__submit_payment`). The policy answers allow, block or hold. Outside the plan = drift = refused. No answer = nothing happens. |

**The network watch.** A plain button can pay by script. So every write a page sends — POST, PUT, PATCH, DELETE — is
paused in the browser until ArmorIQ has decided it, whether it fires during the agent's click or a second later. A
“Next page” button whose script posts an order is held as `submit_payment`. (We learned this the hard way: an early
version closed the watch with the click, and a script's second request placed a sandbox order. Now it never closes.)

**Saved routes are checked too.** Dejo replays routes it learned before, in one call. Under Dejo Guard every replayed
step is described again from the live page — never trusted from the recording — and decided by ArmorIQ. A buying route
learned with no guard at all was held at “Place order”, and refused at add-to-cart under a “compare prices” task.

**Your additions.** `~/.dejo-guard/guard.yaml` widens a plan per site or per task word (“tasks on github.com may
submit forms”). It widens the plan only; the policy still decides each action.

## What a click means

| class | the page says | default policy |
|---|---|---|
| `navigate` | a link on this site, or a GET search form | allow |
| `type_text` | a plain text or search box | allow |
| `interact` | a plain control: no link, no submit | allow |
| `state_change` | a write the task asked for (add to cart) | allow — only if the plan declared it |
| `submit_form` | a submit, or Enter, in a POST form | hold |
| `submit_payment` | a submit in a form with card fields, or a write to a payment endpoint | hold |
| `new_domain` | a link or address on a site the task didn't name | hold |
| `upload` · `run_script` · `unknown` | a file input · the agent's own JS · anything unreadable | hold |
| `type_payment` | `autocomplete=cc-*`, or a box inside a payment frame | block |
| `type_secret` | `type=password`, `one-time-code` | block |

The right-hand column is [the policy file](policy/dejo-guard-boundary.yaml), active in ArmorIQ — not code. Why named
plan steps and not arguments: ArmorIQ's native policy engine sees the tool name only, and its argument-aware profiles
reject anything that isn't bash, files, network or MCP. The full model: [`docs/GUARD-MODEL.md`](docs/GUARD-MODEL.md).

## Proof that ArmorIQ decides

The same click — **Place order** — three times, same code, only the active ArmorIQ policy changing
([`evidence/remove-a-rule.md`](evidence/remove-a-rule.md)):

```
policy line `submit_payment: hold`   ArmorIQ said                      sandbox order
present                              hold · rule_action_hold           none
deleted                              allow · allow_with_logging        DG-MVA14T6F
present again                        hold · rule_action_hold           none
```

And every claim on this page, one line each ([`evidence/verify.txt`](evidence/verify.txt)):

```
PASS  structure, not words: pay submit labelled “Continue” → submit_payment
PASS  structure, not words: pay submit labelled in Hindi → submit_payment
PASS  ArmorIQ policy: type_payment → block  —  block · rule_action_block · dejo-guard-boundary
PASS  ArmorIQ policy: submit_form → hold  —  hold · rule_action_hold · dejo-guard-boundary
PASS  intent drift: a class outside the signed plan is refused  —  tool-not-in-plan
PASS  fail closed: no answer from ArmorIQ means no action
…
16/16 claims pass
```

More: [`evidence/probe-day0.md`](evidence/probe-day0.md) (the first allow, block, hold and drift on the platform) ·
[`evidence/live/`](evidence/live) (full runs, including a hold approved in ArmorIQ that then placed order
`DG-MV9Z9YNI`) · [`evidence/eval.json`](evidence/eval.json) · [`evidence/MANIFEST.json`](evidence/MANIFEST.json)
(SHA-256 of every evidence file).

## Judge it in 90 seconds

1. **Watch the video** above.
2. **Open the [live feed](https://dejo-guard.vercel.app/feed)** — every row is ArmorIQ's answer, verbatim.
3. **Open the [attack lab](https://dejo-guard.vercel.app/shop/lab)** — try to make it pay.
4. **Read [the policy](policy/dejo-guard-boundary.yaml)** — that is where allow, hold and block live.
5. **Run `dejo-guard verify`** against your own ArmorIQ org.

## When something goes wrong

Start with `dejo-guard verify` — it names the claim that fails.

**Everything is blocked with `no_matching_policy`.**
The policy isn't active for this agent. Import `~/.dejo-guard/policy.yaml` in ArmorIQ → Policies, click **Activate**,
and check the agent id inside it is your `dejo-guard-agent`.

**Everything is blocked with `armoriq-unavailable`.**
ArmorIQ didn't answer, so the guard did nothing — that is fail-closed, on purpose. Run `armoriq whoami`. If you set
`ARMORIQ_API_KEY` yourself, make sure it is only the key: an inline `# comment` pasted along with it breaks every call.

**A hold never turns into an approval.**
Approve it in ArmorIQ → **Held Actions**, then let your agent call `guard_wait`. ArmorIQ refuses to let you approve a
request filed under your own email, so holds are filed under `dejo-guard-agent@agents.dejo-guard.vercel.app`
(`DEJO_GUARD_REQUESTER` to change it) — not a member of your org.

**“No browser to drive yet.”**
`pip install` brings the Python code, not a browser. Run `playwright install chromium`.

**It's slow.**
Signing a plan takes ~5–10 s once per task; each action then waits for ArmorIQ (~1 s in our runs). ArmorIQ's faster
local mode can't verify tokens today — its public key endpoint is disabled — so the guard uses SDK mode. Reported
upstream: [`docs/UPSTREAM-ISSUES.md`](docs/UPSTREAM-ISSUES.md).

## Limits, said plainly

- The class table reads structure. A payment behind an endpoint named like anything else, with no card field on the
  page, is classed `state_change` — still allowed only when the task asked for writes.
- Writes to other sites are watched only from pages with card fields, to keep third-party analytics out of the way.
- Real sites are for reading. Checkout and payment happen only on our own sandbox shop.

## Development

```bash
git clone https://github.com/rohit-jsfreaky/dejo-guard && cd dejo-guard/app/guard
uv sync
uv run playwright install chromium
uv run pytest                     # 47 tests, 14 of them in a real headless browser
uv run ruff check src tests
cd ../.. && uv run --project app/guard dejo-guard verify
```

```
app/guard   the Python package and MCP server (dejo-guard)
app/web     the website, sandbox shop, shop MCP and live-feed API (Next.js, Supabase)
policy/     the ArmorIQ policies: ours, and the tool-name baseline the eval compares against
evidence/   every published number and every probe          docs/   the guard model, the finding, upstream issues
```

## Prior work

- **[Dejo](https://dejo.run)** — the browser with a memory this is built on (MIT, same author, before the hackathon).
- **[ArmorClaude](https://github.com/armoriq/armorClaude)** — ArmorIQ for Claude Code's own tools, by name and
  arguments. It can't read a web page, which is the gap this fills.
- **[@playwright/mcp](https://github.com/microsoft/playwright-mcp)** — the accessibility-snapshot approach Dejo's
  page reading builds on; it has no notion of what a click means.
- **Claude for Chrome, Comet** — vendor-side “ask before purchases” and high-risk-site checks; proof the fear is real.
  Dejo Guard puts *your* policy, in *your* ArmorIQ, on every action of *any* MCP agent.

## License

MIT. See [LICENSE](LICENSE).
