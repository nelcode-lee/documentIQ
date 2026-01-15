"""Test the actual API endpoint to see what's returned."""
import requests
import json

try:
    response = requests.get('http://localhost:8000/api/documents')
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response Type: {type(data)}")
        print(f"Response Length: {len(data) if isinstance(data, list) else 'N/A'}")
        print()
        
        if isinstance(data, list):
            print(f"Found {len(data)} documents")
            if len(data) > 0:
                print("\nFirst document:")
                print(json.dumps(data[0], indent=2))
        else:
            print("Response (not a list):")
            print(json.dumps(data, indent=2))
    else:
        print(f"Error Response:")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to API at http://localhost:8000")
    print("Is the backend server running?")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
