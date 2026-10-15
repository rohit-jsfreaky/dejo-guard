# Day-0 probe — ArmorIQ decides Dejo Guard's action classes (16 Oct 2026, ~01:25 IST)

Org "rohit kashyap's Workspace" (157f1d31-83ad-46e9-90f4-2536f6130b68).
Script: `evidence/probes/day0_plan.py` (run: `uv run --project app/guard python evidence/probes/day0_plan.py <classes>`).
SDK: armoriq-sdk 0.6.10, SDK mode (server-side `/iap/sdk/enforce`). Requester = `dejo-guard-agent@agents.dejo-guard.vercel.app`.

## Setup done through the dashboard API (dashboard login, in-browser)
- Agent registered: `POST /agent/register {name, url, orgId}` → `dejo-guard-agent`, agentId `9255530a-72a5-46c6-845e-ce6cfb8c1540`,
  url https://dejo-guard.vercel.app. (`description` is rejected: "property description should not exist".)
- Policy imported: `POST /policies/yaml/import {yaml, onConflict:'replace'}` → `dejo-guard-boundary`,
  policyId `fc6474c7-eedc-4a8c-916b-f2bb516b52d1`; `POST /policies/{id}/activate` → 201 "Policy activated successfully".
  YAML = `policy/dejo-guard-boundary.yaml` (made by `dejo-guard policy --org … --agent …`).

## Run 1 — before any policy (01:15 IST)
plan of `dejo__read, dejo__navigate, dejo__submit_form, dejo__type_payment` signed in 11.83 s (plan 563cfe6b-5bca-40ca-baa0-91be1754c4db).
Every check → `block` / `no_matching_policy` (fail closed). `dejo__submit_payment` (not declared) → `tool-not-in-plan`.

## Run 2 — policy active (01:25 IST), plan 1e2f67bd-0346-424f-83c6-03f67526eae1, signed in 6.63 s
| class | ArmorIQ action | reason | matched policy | delegation | ms |
|---|---|---|---|---|---|
| read | **allow** | allow_with_logging | dejo-guard-boundary | — | 1012 |
| navigate | **allow** | allow_with_logging | dejo-guard-boundary | — | 809 |
| type_payment | **block** | rule_action_block | dejo-guard-boundary | — | 1133 |
| submit_form | **hold** | rule_action_hold | dejo-guard-boundary | 82d7bc05-95a6-4227-a1a8-13ed84d3be6f | 2156 |
| submit_payment (not in plan) | **block** | tool-not-in-plan (intent drift) | — | — | 0 |

## Findings
- The `dejo` MCP name in plan steps is NOT registered yet and the agent-targeted policy still matched
  (`matched_policy=dejo-guard-boundary`). Registration of the guard MCP is still required by the rules — next step.
- SDK local mode is unusable today: `_enforce_local_impl` verifies the token against `GET /iap/public-key`, which returns
  `enabled:false, publicKey:null` → every local enforce = `token-signature-invalid`. → upstream issue.
- `tool-not-in-plan` is decided inside the ArmorIQ SDK (client side) and never reaches the dashboard.
