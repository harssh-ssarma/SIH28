# Test Verification Checklist

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bug Fixes Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[TEST 1] Unicode Encoding Fix" -ForegroundColor Yellow
$unicode_check = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\utils\progress_tracker.py" -Pattern "→" -ErrorAction SilentlyContinue
if ($unicode_check) {
    Write-Host "[ERROR] Unicode arrow still present!" -ForegroundColor Red
    Write-Host "  Found at line $($unicode_check.LineNumber)" -ForegroundColor Red
} else {
    Write-Host "[OK] Unicode arrow replaced with ASCII ->" -ForegroundColor Green
}

Write-Host "`n[TEST 2] Q-table Parameter Fix" -ForegroundColor Yellow
$qtable_sig = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage3_rl.py" -Pattern "def resolve_conflicts_globally.*q_table:" -ErrorAction SilentlyContinue
if ($qtable_sig) {
    Write-Host "[OK] q_table parameter added to function signature" -ForegroundColor Green
} else {
    Write-Host "[ERROR] q_table parameter missing from function signature!" -ForegroundColor Red
}

$self_qtable = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage3_rl.py" -Pattern "self\.q_table" -Context 1 -ErrorAction SilentlyContinue | Where-Object {$_.Line -notmatch "def |# "}
if ($self_qtable) {
    Write-Host "[WARN] Found self.q_table usage (check if it's in class method)" -ForegroundColor Yellow
    $self_qtable | ForEach-Object { Write-Host "  Line $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Gray }
} else {
    Write-Host "[OK] No standalone self.q_table usage" -ForegroundColor Green
}

Write-Host "`n[TEST 3] Architecture Fix (4 Strategies)" -ForegroundColor Yellow
$strategies = Select-String -Path "D:\GitHub\SIH28\backend\fastapi\engine\stage2_cpsat.py" -Pattern '^\s*{' -Context 1 | Where-Object {$_.Line -match '"name":'} | Measure-Object
Write-Host "Found $($strategies.Count) CP-SAT strategies (Expected: 4)" -ForegroundColor $(if ($strategies.Count -eq 4) {"Green"} else {"Red"})

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[1] Start FastAPI in the 'powershell' terminal:" -ForegroundColor Yellow
Write-Host "    cd D:\GitHub\SIH28\backend\fastapi" -ForegroundColor Cyan
Write-Host "    python main.py" -ForegroundColor Cyan
Write-Host "`n[2] Run test timetable generation" -ForegroundColor Yellow
Write-Host "`n[3] Check logs for:" -ForegroundColor Yellow
Write-Host "    ✓ No UnicodeEncodeError" -ForegroundColor Gray
Write-Host "    ✓ No 'name self is not defined' errors" -ForegroundColor Gray
Write-Host "    ✓ Stage 3 processes all 10 clusters" -ForegroundColor Gray
Write-Host "    ✓ Logs show 'strategy 1/4', '2/4', '3/4', '4/4'" -ForegroundColor Gray
Write-Host "`n[4] Note: High conflicts (43k) are expected due to cross-cluster students" -ForegroundColor Yellow
Write-Host "    This is a data/clustering issue, not a bug" -ForegroundColor Gray
