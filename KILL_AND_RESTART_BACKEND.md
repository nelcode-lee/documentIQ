# Kill and Restart Backend - Complete Guide

## Quick Method (PowerShell Script)

Run the provided script:

```powershell
cd backend
.\kill_and_restart.ps1
```

## Manual Method

### Step 1: Kill All Processes on Port 8000

**PowerShell:**
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

**Command Prompt:**
```cmd
for /f "tokens=5" %a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %a
```

### Step 2: Clear Python Cache (Optional but Recommended)

**PowerShell:**
```powershell
cd backend
Get-ChildItem -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
```

**Command Prompt:**
```cmd
cd backend
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc
```

### Step 3: Verify Port is Free

```powershell
netstat -ano | findstr :8000
```

If nothing is returned, the port is free.

### Step 4: Start Backend

```powershell
cd backend
python start_backend.py
```

## One-Line Command (PowerShell)

To do everything at once:

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }; Get-ChildItem backend -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force; Get-ChildItem backend -Recurse -Filter "*.pyc" | Remove-Item -Force; cd backend; python start_backend.py
```

## Verify Backend Started Successfully

1. Check the terminal output - you should see:
   ```
   [OK] Settings loaded
   [OK] FastAPI app imported successfully
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```

2. Test the endpoint:
   ```powershell
   python backend/restart_and_test.py
   ```

   Or visit: http://localhost:8000/api/documents

## If Processes Won't Die

If processes are stuck, use:

```powershell
# Find all Python processes
Get-Process python | Select-Object Id, ProcessName, StartTime

# Kill specific process by ID
Stop-Process -Id <PID> -Force
```

Or restart your terminal/command prompt and try again.

## Troubleshooting

**"Port still in use" error:**
- Wait a few seconds and try again (Windows takes time to release ports)
- Restart your terminal
- Check for other services using port 8000

**"Permission denied" error:**
- Run PowerShell/Command Prompt as Administrator
- Check if antivirus is blocking Python processes

**"Module not found" after restart:**
- Make sure you're in the `backend` directory
- Run: `pip install -r requirements.txt`
