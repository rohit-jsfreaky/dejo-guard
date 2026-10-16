# Recording take A: Claude Code shops on the sandbox with Dejo Guard (clean env, so it starts like a fresh terminal).
Get-ChildItem Env: | Where-Object { $_.Name -like 'CLAUDE*' -or $_.Name -like 'CLAUDECODE*' } | ForEach-Object { Remove-Item "Env:$($_.Name)" }
Clear-Host
claude "Buy one copy of Atomic Habits from dejo-guard.vercel.app/shop with my saved card. Call guard_task first with this request. At checkout fill my name Rohit Kashyap, address 12 Park Street, city Kolkata, then click Place order. If Place order is held, tell me, then wait with guard_wait (up to 180 seconds) while I approve it in ArmorIQ, and tell me the order number when it goes through. Don't ask me questions; decide sensibly yourself."
