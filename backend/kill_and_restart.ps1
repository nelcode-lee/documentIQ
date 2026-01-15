# PowerShell script to fully kill backend and restart it
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Killing Backend Server" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all processes on port 8000
Write-Host "[1] Stopping processes on port 8000..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($processes) {
    $processes | ForEach-Object {
        Write-Host "  Stopping process $_..." -ForegroundColor Gray
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  [OK] Stopped $($processes.Count) process(es)" -ForegroundColor Green
} else {
    Write-Host "  [OK] No processes found on port 8000" -ForegroundColor Green
}
Start-Sleep -Seconds 2

# Step 2: Clear Python cache
Write-Host ""
Write-Host "[2] Clearing Python cache files..." -ForegroundColor Yellow
$cacheFiles = Get-ChildItem -Path ".." -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
$cacheDirs = Get-ChildItem -Path ".." -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue

if ($cacheFiles -or $cacheDirs) {
    $cacheFiles | Remove-Item -Force -ErrorAction SilentlyContinue
    $cacheDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $total = $cacheFiles.Count + $cacheDirs.Count
    Write-Host "  [OK] Cleared $total cache items" -ForegroundColor Green
} else {
    Write-Host "  [OK] No cache files found" -ForegroundColor Green
}

# Step 3: Verify port is free
Write-Host ""
Write-Host "[3] Verifying port 8000 is free..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
$remaining = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "  [WARNING] Port 8000 still in use!" -ForegroundColor Red
    Write-Host "  You may need to manually kill remaining processes" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 8000 is free" -ForegroundColor Green
}

# Step 4: Start backend
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Starting Backend Server" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location $PSScriptRoot

# Start the server
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host ""
python start_backend.py
