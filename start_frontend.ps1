# PowerShell script to start frontend with proper execution policy
Write-Host "Starting Frontend Development Server..." -ForegroundColor Cyan

# Set execution policy for this process
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force

# Change to frontend directory
Set-Location "$PSScriptRoot\frontend"

# Start the dev server
npm run dev