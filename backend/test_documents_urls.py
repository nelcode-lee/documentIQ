#!/usr/bin/env python3
"""Test the documents endpoint to check for download URLs."""

import requests

def test_documents_endpoint():
    """Test the documents endpoint for download URLs."""

    print('Testing documents endpoint for download URLs...')

    try:
        response = requests.get('http://localhost:8000/api/documents', timeout=10)

        if response.status_code == 200:
            docs = response.json()
            print(f'Success! Retrieved {len(docs)} documents')

            # Check first few documents for download URLs
            for i, doc in enumerate(docs[:3]):
                print(f'Document {i+1}: {doc.get("title", "Untitled")}')
                print(f'  Source: {doc.get("source", "unknown")}')
                print(f'  Download URL: {bool(doc.get("downloadUrl"))}')
                print(f'  downloadUrl value: {repr(doc.get("downloadUrl"))}')
                print(f'  All keys: {list(doc.keys())}')
                if doc.get('downloadUrl'):
                    url = doc['downloadUrl']
                    print(f'  URL preview: {url[:80]}...')
                print()

        else:
            print(f'Failed: HTTP {response.status_code}')
            print(response.text[:500])

    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_documents_endpoint()