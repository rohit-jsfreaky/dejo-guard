# Dejo Guard — your agent clicks, ArmorIQ decides

**A browser agent has one tool: click. A rule on tool names can't tell “Next page” from “Pay ₹4,999” — both are
`click(ref=e12)`. Dejo Guard reads what e12 *is* from the page itself, names it, and lets ArmorIQ allow it, block it,
or hold it for you.**

[Live site](https://dejo-guard.vercel.app) · [For judges (90 s)](https://dejo-guard.vercel.app/judges) ·
[Attack lab](https://dejo-guard.vercel.app/shop/lab) · [Live decision feed](https://dejo-guard.vercel.app/feed) ·
Video: _link added on submission_ · Built for **ArmorIQ Flow State**, October 2026, by Rohit Kashyap (Boundary Labs)

> **Disclosure.** Dejo Guard is built on **[Dejo](https://dejo.run)** (MIT, on PyPI since 13 Oct 2026, same author,
> written before this hackathon) and uses it as a library: the browser with a memory. **Everything in this repo is
> new, written from 16 Oct 2026**: page facts, the class table, intent plans, holds and approvals, the network watch,
> replay checks, the MCP wrapper, the sandbox shop, the attack lab, the eval and the website.
> **AI assistance:** Claude Code wrote much of the code; the author designed it, reviewed every change, and ran every
> test and every ArmorIQ approval himself.

## What it does

Your own agent (Claude Code, Codex, Cursor…) gets a real browser through MCP. Before every click, keystroke or
replayed step, Dejo Guard:

1. **reads the page** — is this a link, a form submit, a card field (`autocomplete=cc-*`), a password box, another site?
   Never the button's words: “Continue” can be a pay button, and a Hindi checkout has no word “pay” in it;
2. **names the action** with one of 14 classes (`navigate`, `submit_payment`, `type_payment`, `new_domain`…);
3. **asks ArmorIQ** — the class is sent as a named step (`dejo__submit_payment`) of the plan ArmorIQ signed for this
   task. Your ArmorIQ policy answers allow, block or hold. Outside the plan = intent drift = refused.

While an action runs, an always-on **network watch** pauses every write the page sends (POST/PUT/PATCH/DELETE) until
ArmorIQ has decided it — so a plain-looking “Next page” button whose script posts an order is still held.

**Our code only describes. ArmorIQ decides.** There is no allow/deny branch in the guard (a test checks it). Delete
the `submit_payment: hold` line from the policy and the same click goes through on the next try. If ArmorIQ can't be
reached, nothing happens.

## The finding

On the 8 pages of the attack lab and on ordinary read-only journeys across real public sites (Wikipedia, GitHub,
Python docs, MDN, Hugging Face, pkg.go.dev, the Rust book, Hacker News), scripted, no model in the loop, same pages for
every arm. Every guarded decision is a real ArmorIQ decision.

<!-- numbers:start -->
| | unsafe actions that ran (of 8) | normal steps held or blocked (of 68) |
|---|---|---|
| no guard | **8** | — (nothing is ever held) |
| ArmorIQ on tool names (`click`, `fill`…) | **8** | 0.0% |
| ArmorIQ on tool names, strict (hold every click/fill/press) — computed | 0 | 31.3% |
| **Dejo Guard** (ArmorIQ on page meaning) | **0** | **0.0%** |

<sub>Run 2026-10-15T20:58:19+0000 · dejo-guard 0.1.0 · armoriq-sdk 0.6.10 · raw: [`evidence/eval.json`](evidence/eval.json) · method: [`docs/FINDING.md`](docs/FINDING.md)</sub>
<!-- numbers:end -->

## Judge it in 90 seconds

1. **Watch the video** (top). Claude Code shops on our sandbox: browsing allowed, “Place order” held until approved in
   ArmorIQ, the card field blocked, “compare prices” refused when it tries to buy.
2. **Open the [live feed](https://dejo-guard.vercel.app/feed)** — every row is ArmorIQ's answer, word for word
   (`rule_action_hold`, `rule_action_block`, `tool-not-in-plan`) and the policy that matched.
3. **Open the [attack lab](https://dejo-guard.vercel.app/shop/lab)** — 8 pages built to fool an agent, each with the
   class the guard gives it.
4. **Read [the policy](policy/dejo-guard-boundary.yaml)** — that file, active in ArmorIQ, is where allow/hold/block live.
5. **Proof it's real:** [`evidence/probe-day0.md`](evidence/probe-day0.md) (first allow/block/hold/drift on the
   platform), [`evidence/live/`](evidence/live) (end-to-end runs, including a hold approved in ArmorIQ that then placed
   sandbox order `DG-MV9Z9YNI`), [`evidence/eval.json`](evidence/eval.json).

## Try it on your own agent (5 minutes, $0)

```bash
pip install dejo-guard
playwright install chromium          # the browser, about 150 MB
armoriq login                        # your own free ArmorIQ org
dejo-guard init                      # checks the setup, prints the next steps
dejo-guard policy --org <org id> --agent <agent id> > policy.yaml   # import it in ArmorIQ, then Activate
claude mcp add dejo-guard -- dejo-guard
```

Then ask your agent: *“Compare prices for Atomic Habits on dejo-guard.vercel.app/shop, then buy the cheapest.”*
Approve the held order in ArmorIQ → **Held Actions**. Want a live page of your own decisions? `dejo-guard share`.

## How ArmorIQ decides (and what ArmorIQ can't do yet)

| class | the page says | default policy |
|---|---|---|
| `navigate` | a link on this site, or a GET search form | allow |
| `type_text` | a plain text or search box | allow |
| `interact` | a plain control: no link, no submit | allow |
| `state_change` | a write the task asked for (add to cart) | allow — only if declared in the plan |
| `submit_form` | a submit, or Enter, in a POST form | hold |
| `submit_payment` | a submit in a form with card fields, or a write to a payment endpoint | hold |
| `new_domain` | a link or address on a site the task didn't name | hold |
| `upload`, `run_script`, `unknown` | a file input, the agent's own JS, anything unreadable | hold |
| `type_payment` | `autocomplete=cc-*`, or a box in a payment frame | block |
| `type_secret` | `type=password`, `one-time-code` | block |

Why named plan steps and not arguments: ArmorIQ's native policy engine sees the tool name only (its OPA input is
`resource.toolName`), and the argument-aware `armor.policy.v1` profiles reject unknown tools and fields — so page facts
travel as named steps that the native policy decides. Full model: [`docs/GUARD-MODEL.md`](docs/GUARD-MODEL.md).
What we found about ArmorIQ on the way (public key disabled, so SDK local mode can't verify tokens; no browser
vocabulary in `armor.policy.v1`): [`RESEARCH.md`](RESEARCH.md).

## Limits (said plainly)

- Each action waits for ArmorIQ: about a second in SDK mode, plus ~5–10 s to sign a plan once per task.
- The class table reads structure. A site that hides a payment behind an endpoint named like anything else, with no
  card field on the page, is classed `state_change` — still only allowed when the task asked for writes.
- Writes to other sites are watched only from pages with card fields (to keep third-party analytics out of the way).
- Real sites are used for reading; checkout and payment happen only on our own sandbox shop (rule 7: no real money).

## Repo map

```
app/guard   the Python package + MCP server (dejo-guard)      app/web   the site, sandbox shop, shop MCP, feed API
policy/     the ArmorIQ policies (ours + the tool-name baseline)  evidence/ every published number and every probe
docs/       GUARD-MODEL.md (how a click becomes a decision), FINDING.md (the eval's method)
```

MIT © 2026 Rohit Kashyap.
