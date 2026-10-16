# Recording take E: with `submit_payment: hold` deleted from the ArmorIQ policy, the same Place order click goes through.
$flag = "D:\my_projects\hackathons\dejo-guard-video\recorder\raw\e.flag"
Get-ChildItem Env: | Where-Object { $_.Name -like 'CLAUDE*' } | ForEach-Object { Remove-Item "Env:$($_.Name)" }
Clear-Host
while (-not (Test-Path "D:\my_projects\hackathons\dejo-guard-video\recorder\raw\e.ready")) { Start-Sleep -Milliseconds 300 }
Write-Host "ArmorIQ policy dejo-guard-boundary: the line 'submit_payment: hold' was just deleted." -ForegroundColor Yellow
Write-Host "Same guard, same code, same click: Place order on the sandbox checkout." -ForegroundColor Yellow
Write-Host ""
Set-Location D:\my_projects\hackathons\dejo-guard
uv run --no-sync --project app/guard python evidence/probes/remove_rule.py removed 2>$null | Select-String -Pattern '"(label|click|decision|class|reason|policy|order_placed)"'
Write-Host ""
Write-Host "Restoring the rule in ArmorIQ..." -ForegroundColor Yellow
New-Item -ItemType File -Force $flag | Out-Null
