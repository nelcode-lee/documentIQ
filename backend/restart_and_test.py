"""Script to help restart the server and verify it's working."""
import os
import sys
import subprocess
import time
import requests

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_server_running():
    """Check if server is responding."""
    try:
        response = requests.get('http://localhost:8000/api/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def test_documents_endpoint():
    """Test the documents endpoint."""
    try:
        response = requests.get('http://localhost:8000/api/documents', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Documents endpoint working!")
            print(f"   Found {len(data)} documents")
            if len(data) > 0:
                print(f"   First document: {data[0].get('title', 'N/A')}")
            return True
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

print("=" * 60)
print("Backend Server Status Check")
print("=" * 60)
print()

# Check if server is running
print("1. Checking if server is running...")
if check_server_running():
    print("   ✅ Server is running")
else:
    print("   ❌ Server is NOT running")
    print()
    print("   Please start the server:")
    print("   cd backend")
    print("   python start_backend.py")
    sys.exit(1)

print()
print("2. Testing documents endpoint...")
success = test_documents_endpoint()

print()
print("=" * 60)
if success:
    print("✅ Server is working correctly!")
    print("   Documents should now load in the frontend.")
else:
    print("❌ Server is not working correctly")
    print()
    print("TROUBLESHOOTING:")
    print("1. Make sure the server was restarted after code changes")
    print("2. Check the server logs for error messages")
    print("3. Try stopping the server (Ctrl+C) and restarting:")
    print("   cd backend")
    print("   python start_backend.py")
    print()
    print("4. If using uvicorn with --reload, make sure file changes are detected")
    print("5. Check that all dependencies are installed:")
    print("   pip install -r requirements.txt")
print("=" * 60)
