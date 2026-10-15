# ROADMAP — NOT in this build

New ideas go here, never into the hackathon build. Revisit after 17 Oct.

- Merge the guard into Dejo itself as `dejo --guard` (after the hackathon, Rohit's call).
- `browser.*` fields in ArmorIQ's `armor.policy.v1` (upstream proposal) so the policy can read page facts directly.
- Approve-from-phone page (push notification → one tap) instead of the ArmorIQ dashboard.
- Per-site learned allowlists: after N approvals of the same action, suggest a rule.
- Network-level guard: block non-GET requests the page fires that no click explains.
- Chrome extension mode for the user's everyday browser.
- Team mode: one org policy for every developer's browser agent.
