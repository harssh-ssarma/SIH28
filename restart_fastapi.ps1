# Restart FastAPI server to load architecture-fixed code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restarting FastAPI Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Stop old FastAPI process
Write-Host "`n[1/3] Stopping old FastAPI process..." -ForegroundColor Yellow
$fastapi_process = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    $cmdline -like "*main.py*" -and $cmdline -like "*fastapi*"
}

if ($fastapi_process) {
    Write-Host "Found FastAPI process (PID: $($fastapi_process.Id))" -ForegroundColor Gray
    Stop-Process -Id $fastapi_process.Id -Force
    Start-Sleep -Seconds 2
    Write-Host "[OK] Stopped old FastAPI process" -ForegroundColor Green
} else {
    Write-Host "[WARN] No FastAPI process found (may already be stopped)" -ForegroundColor Yellow
}

# 2. Clear Python cache
Write-Host "`n[2/3] Clearing Python bytecode cache..." -ForegroundColor Yellow
Get-ChildItem -Path "D:\GitHub\SIH28\backend\fastapi" -Filter "*.pyc" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path "D:\GitHub\SIH28\backend\fastapi" -Filter "__pycache__" -Directory -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host "[OK] Cleared cache" -ForegroundColor Green

# 3. Start new FastAPI server
Write-Host "`n[3/3] Starting new FastAPI server..." -ForegroundColor Yellow
Set-Location "D:\GitHub\SIH28\backend\fastapi"

Write-Host "[INFO] Starting FastAPI in new terminal..." -ForegroundColor Cyan
Write-Host "[INFO] Check the new 'python' terminal for logs" -ForegroundColor Cyan

# Start in new terminal window so you can see logs
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\GitHub\SIH28\backend\fastapi; python main.py"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "FastAPI Server Restarted!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n[NEXT STEP] Wait 5 seconds, then test timetable generation" -ForegroundColor Yellow
Write-Host "[EXPECT] Logs should show 'strategy 1/4', '2/4', '3/4', '4/4'" -ForegroundColor Yellow
Write-Host "[EXPECT] Stage 3 should NOT show 'engine.stage2_cpsat' logs" -ForegroundColor Yellow
Write-Host "[EXPECT] Progress should reach 100% without getting stuck" -ForegroundColor Yellow
