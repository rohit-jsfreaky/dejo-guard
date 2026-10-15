# Guard model — how one click becomes an ArmorIQ decision

Rohit must be able to explain every line here (the judges hire for "how AI and systems really work"). Anything marked ⚠️ is
not yet proven on the live platform; Day-0 probes confirm it and this file changes in the same commit.

## 1. The pipeline
```
agent (Claude Code …) ──MCP──► dejo-guard ──► Dejo resolves the element (ref → live element)
                                   │
                                   ├─ 1. page facts   (DOM only: role, tag, type, autocomplete, form action+method,
                                   │                    href target domain, iframe origin, input kind, current URL)
                                   ├─ 2. action class (fixed table below — structure, never words)
                                   ├─ 3. ArmorIQ step  `dejo__<class>` (+ `dejo__site_<domain-class>`)
                                   ├─ 4. ArmorIQ decides: local enforce (plan + policy) → allow | block | hold
                                   │        hold → SDK check() in sdk mode → delegation id → poll until approved/rejected
                                   └─ 5. act or refuse; write the decision to the feed (trace id, class, page, rule)
```
Our code has no allow/deny branch. Its only branch is fail-closed: no answer from ArmorIQ = no action.

## 2. Action classes (from structure)
| class | page facts that make it | default ArmorIQ rule |
|---|---|---|
| `read` | `dejo_read`, screenshots, text extraction | allow |
| `navigate` | link with `href` (GET), back/forward, `goto` on a declared domain | allow |
| `type_text` | typing into a plain text/search input | allow |
| `type_secret` | input `type=password`, `autocomplete=current-password/new-password/one-time-code` | block |
| `type_payment` | `autocomplete=cc-*`, inputs inside a payment-provider iframe, names like `cardnumber`/`cvc` (structure first) | block |
| `submit_form` | button/input `type=submit` or a click that submits a form (method POST) | hold |
| `submit_payment` | submit of a form with card fields (or on a page with them), or a write to a payment path (`/checkout`, `/pay`, `/orders`…) or carrying payment keys | hold |
| `interact` | a plain control: no link, no form submit (tabs, toggles, JS buttons) | allow |
| `state_change` | a write (POST/PUT/PATCH/DELETE) a click fires, caught by the always-on network watch | allow — only if the task's plan declared it, else drift |
| `new_domain` | navigation to a domain not declared in the plan | hold |
| `download` | click that starts a download | allow (logged) |
| `unknown` | anything the table can't place | hold (fail safe) |

Words on the button are shown to the human in the approval ("Place order"), never used to pick the class.

## 2b. The network watch (always on)
Armed once per browser context (`context.route("**/*")`) and never removed. Every same-site write (fetch/xhr/document
POST, PUT, PATCH, DELETE) — and any write from a page with card fields — is paused until ArmorIQ decides it. While an
agent action runs, its writes belong to it (window stays open until 700 ms of quiet, max 4 s). A write fired later by
the page's own script is still decided, labelled `after <action>`, and reported to the agent as `guard_notices`.
Found the hard way (16 Oct E2E): a window that closed with the click let a script's second POST place an order.

## 3. Intent plan (drift)
At task start the guard declares a plan: `goal` = the user's task text, `steps` = one entry per class the task needs, plus the
declared domains. Every plan declares `read, navigate, type_text, interact, download, new_domain, type_secret, type_payment, upload,
run_script, unknown`, so the POLICY answers for them visibly. The task's words (`guard.TASK_WORDS`) add `submit_form`,
`state_change`, `submit_payment` ("add to cart", "buy"…); without them those are drift. The user widens it
in `~/.dejo-guard/guard.yaml` (`sites:` classes for every task on a site, `words:` extra task words → classes; written
empty by `dejo-guard init`, see `userplan.py`). That file only widens the PLAN; the policy still decides each action.
An action whose class is not in the signed plan is **drift** → ArmorIQ refuses it (not in plan). This is the browser version
of Fuzail's `db.drop("production")` demo.

## 4. Saved replays
`dejo_run` replays under the task the agent declared (or a default read-only plan). Every replayed step is described
again from the LIVE page — never from the recording, which may be stale — and decided by ArmorIQ; a hold or block stops
the replay at that step. Proven 16 Oct (`evidence/probes/replay_check.py`, `evidence/live/replay-*.json`): a buying
trail learned with no guard was held at "Place order" under a buying task, and refused at add-to-cart (drift) under
"compare prices".

## 5. The ArmorIQ policy (native, imported as YAML)
```yaml
apiVersion: armor.io/v1
kind: Policy
metadata: { name: dejo-guard-boundary, orgId: <org>, targetType: agent, targetId: <dejo-guard-agent id> }
spec:
  priority: 100
  defaultEnforcementAction: block        # no-match = block (fail closed)
  memberRules:
    '*':
      allowedTools: [read, navigate, type_text, download,
                     type_secret, type_payment,
                     submit_form, submit_payment, state_change, new_domain, unknown]
      toolEnforcement:
        type_secret: block
        type_payment: block
        submit_form: hold
        submit_payment: hold
        new_domain: hold
        unknown: hold
```
(Tools must be in `allowedTools` for `toolEnforcement` to apply; no `status:` line; import via
`POST /policies/yaml/import` then `/activate` — dashboard login needed.)

## 6. Identities
- Agent: `dejo-guard-agent` (registered on the platform).
- Requests filed under a non-member identity (`guard@agents.<our-domain>`) so a member can approve holds (self-approval is
  refused).
- MCP onboarded: `sandbox-shop` (our hosted shop's MCP, public HTTPS). The local guard is proven onboarded through a tunnel
  for the evidence screenshot ⚠️ (confirm whether a local server can be listed).

## 7. What ArmorIQ cannot do today (and what we say about it)
- Native policy input carries the tool name only — no arguments. → named steps per class.
- `armor.policy.v1` profiles: closed tool list and fields (bash, file.path, network.host, mcp.server). → our upstream
  suggestion: `browser.*` fields (`browser.action_class`, `browser.domain`, `browser.form_method`).
- `/iap/public-key` disabled → local verification can't check signatures. → upstream issue.
