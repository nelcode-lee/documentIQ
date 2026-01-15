"""Test the endpoint with a direct FastAPI test client."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing /api/documents endpoint...")
try:
    response = client.get("/api/documents")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Got {len(data) if isinstance(data, list) else 'non-list'} items")
        if isinstance(data, list) and len(data) > 0:
            print(f"First document ID: {data[0].get('id', 'N/A')}")
            print(f"First document title: {data[0].get('title', 'N/A')}")
    else:
        print(f"Error: {response.text}")
        print(f"Status code: {response.status_code}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
