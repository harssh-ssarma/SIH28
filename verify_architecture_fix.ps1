# Verify Architecture Fix is Applied

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verifying Architecture Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[CHECK 1] CP-SAT Strategies..." -ForegroundColor Yellow
$strategies = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage2_cpsat.py" -Pattern "STRATEGIES = \[" -Context 0,60 | Out-String
$strategy_count = ([regex]::Matches($strategies, '{\s*"name":')).Count
Write-Host "Found $strategy_count strategies (Expected: 4)" -ForegroundColor $(if ($strategy_count -eq 4) {"Green"} else {"Red"})

Write-Host "`n[CHECK 2] Stage 3 RL No CP-SAT Import..." -ForegroundColor Yellow
$cpsat_import = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage3_rl.py" -Pattern "from.*stage2_cpsat|AdaptiveCPSATSolver" -ErrorAction SilentlyContinue
if ($cpsat_import) {
    Write-Host "[ERROR] Stage 3 still imports CP-SAT!" -ForegroundColor Red
    $cpsat_import | ForEach-Object { Write-Host "  Line $($_.LineNumber): $($_.Line)" -ForegroundColor Red }
} else {
    Write-Host "[OK] No CP-SAT imports in Stage 3" -ForegroundColor Green
}

Write-Host "`n[CHECK 3] Q-learning Helper Function..." -ForegroundColor Yellow
$rl_helper = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage3_rl.py" -Pattern "def _resolve_cluster_conflicts_with_rl" -ErrorAction SilentlyContinue
if ($rl_helper) {
    Write-Host "[OK] Q-learning helper function exists at line $($rl_helper.LineNumber)" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Q-learning helper function missing!" -ForegroundColor Red
}

Write-Host "`n[CHECK 4] Stage 3 Uses Q-learning (Not CP-SAT)..." -ForegroundColor Yellow
$rl_call = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage3_rl.py" -Pattern "_resolve_cluster_conflicts_with_rl\(" -ErrorAction SilentlyContinue
if ($rl_call) {
    Write-Host "[OK] Stage 3 calls Q-learning function" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Stage 3 doesn't call Q-learning!" -ForegroundColor Red
}

Write-Host "`n[CHECK 5] FastAPI Server Status..." -ForegroundColor Yellow
$fastapi_running = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    $cmdline -like "*main.py*"
}
if ($fastapi_running) {
    $start_time = $fastapi_running.StartTime
    $runtime = (Get-Date) - $start_time
    Write-Host "[OK] FastAPI running (PID: $($fastapi_running.Id), Started: $start_time)" -ForegroundColor Green
    if ($runtime.TotalMinutes -lt 2) {
        Write-Host "[GOOD] Server recently restarted ($([Math]::Round($runtime.TotalSeconds))s ago) - fresh code loaded" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Server running for $([Math]::Round($runtime.TotalMinutes)) minutes - may be old code" -ForegroundColor Yellow
    }
} else {
    Write-Host "[ERROR] FastAPI not running!" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($strategy_count -eq 4 -and -not $cpsat_import -and $rl_helper -and $rl_call -and $fastapi_running) {
    Write-Host "[SUCCESS] All checks passed! Architecture fix applied correctly." -ForegroundColor Green
    Write-Host "`n[NEXT STEP] Run a test timetable generation and check:" -ForegroundColor Yellow
    Write-Host "  1. Logs show 'strategy 1/4', '2/4', '3/4', '4/4'" -ForegroundColor Gray
    Write-Host "  2. Stage 3 has NO 'engine.stage2_cpsat' logs" -ForegroundColor Gray
    Write-Host "  3. Progress reaches 100% smoothly" -ForegroundColor Gray
    Write-Host "  4. Quality score 70-90% (not 33%)" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Some checks failed - review above" -ForegroundColor Red
}
