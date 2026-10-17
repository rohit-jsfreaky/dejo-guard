# Upstream issues for ArmorIQ (Rohit opens these)

Where: https://github.com/armoriq/Voice-of-Developer → New issue (the SDK repo is not public). One issue per block.
Everything below was seen on our own org, 15–16 Oct 2026, armoriq-sdk 0.6.10. Evidence links point at this repo.

---

## Issue 1 — template "Pain Point or Friction Report"

**Title:** `[Pain Point] SDK local mode blocks every action: /iap/public-key returns enabled:false`

**Which area:** SDK (Python), local enforcement

**What happened?**
In SDK `mode="local"`, `enforce()` blocks every tool with `reason: token-signature-invalid`, even for tools the policy
allows. The SDK (0.6.10, `session._enforce_local_impl`) verifies the intent token against the key from
`GET https://api.armoriq.ai/iap/public-key` — and that endpoint answers:

```
{"alg":"EdDSA","enabled":false,"publicKey":null,"jwk":null}
```

So there is no key to verify with, and local mode fails closed on everything. On 16 Oct 00:12 IST the same SDK logged
`fetched IAP public key could not be parsed as Ed25519`. We switched to `mode="sdk"` (server-side check, ~0.8–1 s per
action) to keep going.

Repro: start a session with `SessionOptions(mode="local")`, `start_plan([...])`, then `enforce("<allowed tool>", {})` →
`block / token-signature-invalid`. `curl https://api.armoriq.ai/iap/public-key` shows the disabled key.
Evidence: https://github.com/rohit-jsfreaky/dejo-guard/blob/main/evidence/probe-day0.md

**What did this cost you?** ~2 hours to find; and a browser agent pays ~1 s per click in SDK mode instead of local mode's
~0.5 s.

**How often?** Every local-mode call.

**What would a good outcome look like?** `/iap/public-key` returns the real Ed25519 key (or the docs say local mode is
off and how to configure a key), so local enforcement works offline-fast as documented.

---

## Issue 2 — template "Feature or Capability Request"

**Title:** `[Request] Let a policy see what an action means (browser agents), and set up agents/policies with an API key`

**Role:** Developer building a browser agent on ArmorIQ (hackathon: Flow State)

**What do you need?**
1. *A way for a policy to decide on what an action means, not only its tool name.* A browser agent has one tool —
   `click(ref=e12)`. The native policy engine sees `resource.toolName` only (OPA input has no arguments), and the
   `armor.policy.v1` profiles reject anything that isn't bash / file / network / MCP: `POST /policies/sync` with a
   browser statement answers `Unknown tool in statements[0]: browser_click` and
   `Unknown condition field: args.element_label`. We worked around it by describing each click from the page's
   structure (form submit, card field, link to another site…) and sending that as a named plan step
   (`dejo__submit_payment`) that the native policy decides. It works — 8 of 8 attacks stopped, 0 of 68 normal steps held
   — but it would be cleaner as fields the policy reads: `browser.action_class`, `browser.domain`,
   `browser.form_method`, `browser.has_payment_fields`.
2. *Agent registration and policy import with the API key.* `armoriq login` gives an API key, but
   `POST /agent/register`, `POST /policies/yaml/import` and `/activate` need the dashboard JWT. So a tool like ours
   can't set itself up in one command; every user has to click through Inventory and Policies by hand.

**How are you handling this today?** (1) Named plan steps per action class; (2) `dejo-guard init` writes the policy
YAML with the org id from `armoriq login` and prints the two dashboard steps.

**Anything else?** Repo + evidence: https://github.com/rohit-jsfreaky/dejo-guard · eval:
https://github.com/rohit-jsfreaky/dejo-guard/blob/main/docs/FINDING.md · smaller things we hit on the way: the
docs' example policy still has `status: active`, which the importer rejects (the UI only says "check YAML syntax");
`toolEnforcement` applies only to tools also listed in `allowedTools`.

## Note 3 — ArmorIQ Tools (Policy Studio), found 17 Oct 2026

1. **The folder access rule refuses Windows paths.** `C:/Users/<me>/.dejo-guard` and `C:\Users\<me>\.dejo-guard` both
   fail with "Use a canonical absolute folder path without . or .. segments"; only POSIX paths (`/Users/...`) save.
   Claude Code on Windows passes `C:\...` paths to its file tools, so a folder rule can't protect anything there.
2. **After a reload, tool rules move to "scoped or advanced rules preserved unchanged".** Rules saved from the simple
   editor (`forbid Bash`, `forbid WebFetch`) are active and enforced, but the editor shows "No rules" and lists them
   only as raw JSON, which makes it look as if the save failed.
3. **A new tool rule starts with `Read` already typed** in the tool box, so typing a name appends to it
   (`ReadBash`). Easy to publish a rule that matches nothing.
