# Where evidence/eval.json came from

GitHub Actions run https://github.com/rohit-jsfreaky/dejo-guard/actions/runs/38804741784 (workflow_dispatch, job `eval`,
commit 8cc4976), artifact `eval`. Downloaded with `gh run download 38804741784 -n eval` and copied here unchanged.

An earlier run (38804246743) is NOT used: the CI secret held the .env line with its inline comment, so every ArmorIQ
call failed closed (`armoriq-unavailable: UnicodeEncodeError`). Fixed by resetting the secret to the bare key.
