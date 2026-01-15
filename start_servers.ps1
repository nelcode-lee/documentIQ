# PowerShell script to start both frontend and backend servers

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Starting Frontend and Backend Servers" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Get the script directory (project root)
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Step 1: Start Backend
Write-Host "[1] Starting Backend Server..." -ForegroundColor Yellow
Write-Host "    Directory: $projectRoot\backend" -ForegroundColor Gray

$backendScript = {
    Set-Location "$using:projectRoot\backend"
    Write-Host "    Starting backend..." -ForegroundColor Gray
    python start_backend.py
}

# Start backend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend'; python start_backend.py" -WindowStyle Normal

Write-Host "    [OK] Backend server starting in new window" -ForegroundColor Green
Start-Sleep -Seconds 2

# Step 2: Start Frontend
Write-Host ""
Write-Host "[2] Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "    Directory: $projectRoot\frontend" -ForegroundColor Gray

# Start frontend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; npm run dev" -WindowStyle Normal

Write-Host "    [OK] Frontend server starting in new window" -ForegroundColor Green

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Servers Starting..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:5173 (or check the terminal)" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit this script (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
