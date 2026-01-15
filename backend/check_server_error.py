"""Check what error the running server is actually returning."""
import requests
import json

try:
    response = requests.get('http://localhost:8000/api/documents')
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()
    
    if response.status_code != 200:
        print("Error Response:")
        print(response.text)
        print()
        
        # Try to parse as JSON
        try:
            error_data = response.json()
            print("Parsed Error JSON:")
            print(json.dumps(error_data, indent=2))
        except:
            print("Could not parse as JSON")
    else:
        data = response.json()
        print(f"Success! Got {len(data)} documents")
        
except requests.exceptions.ConnectionError:
    print("Cannot connect to server. Is it running?")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
