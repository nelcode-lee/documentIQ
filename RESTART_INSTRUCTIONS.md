# How to Restart Backend Server

## The Problem
The backend server is still running old code and needs to be manually restarted to pick up the fixes.

## Solution: Manual Restart Required

### Step 1: Stop the Current Server
1. Find the terminal/command prompt where the backend server is running
2. Press **Ctrl+C** to stop the server
3. Wait a few seconds for it to fully stop

### Step 2: Restart the Server
In the same terminal, run:

```bash
cd backend
python start_backend.py
```

Or if you're using uvicorn directly:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify It's Working
After the server starts (you'll see "Application startup complete"), test it:

**Option 1: Use the test script**
```bash
python backend/restart_and_test.py
```

**Option 2: Test in browser**
Open: http://localhost:8000/api/documents

**Option 3: Test with curl**
```bash
curl http://localhost:8000/api/documents
```

### Expected Result
- ✅ Server starts without errors
- ✅ `/api/documents` returns 200 OK with JSON array of 7 documents
- ✅ Frontend displays documents correctly

## If Server Won't Start

1. **Check for port conflicts:**
   ```bash
   netstat -ano | findstr :8000
   ```
   If you see processes, kill them first

2. **Check Python environment:**
   ```bash
   python --version
   pip list | grep fastapi
   ```

3. **Reinstall dependencies if needed:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Check .env file exists:**
   ```bash
   ls backend/.env
   ```
   Make sure it has all required Azure credentials

## Why Manual Restart?
- The `--reload` flag should auto-reload, but sometimes it doesn't catch all changes
- Python bytecode cache might need clearing
- Import errors might only show on fresh start
- Settings/environment might need re-initialization

## Verification
After restarting, you should see in the server logs:
```
[INFO] Retrieved X chunks from search index
[INFO] Returning 7 documents from list_documents endpoint
```

If you see errors, check the logs for details.
