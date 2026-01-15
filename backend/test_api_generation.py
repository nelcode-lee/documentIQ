#!/usr/bin/env python3
"""Test the document generation API endpoint."""

import requests
import json
import sys

def test_document_generation_api():
    """Test the document generation API."""

    # Test data for document generation
    test_request = {
        'documentType': 'risk-assessment',
        'format': 'markdown',
        'title': 'API Test - Warehouse Safety Assessment',
        'category': 'Safety',
        'tags': ['safety', 'warehouse', 'risk-assessment'],
        'projectReference': 'WH-2024-001',
        'siteLocation': 'Main Warehouse',
        'author': 'Safety Manager',
        'reviewDate': '2024-12-31',
        'version': '1.0',
        'useStandards': True,
        'data': {
            'activityDescription': 'Loading and unloading operations',
            'location': 'Loading bay area',
            'hazards': [{
                'hazard': 'Vehicle movement near personnel',
                'whoMightBeHarmed': 'Warehouse staff',
                'howHarmed': 'Struck by vehicle, crushed injuries'
            }],
            'responsiblePerson': 'Operations Manager',
            'reviewDate': '2024-12-31'
        }
    }

    print('Testing document generation API...')

    try:
        response = requests.post(
            'http://localhost:8000/api/generate/document',
            json=test_request,
            timeout=60
        )

        print(f'HTTP Status: {response.status_code}')

        if response.status_code == 200:
            result = response.json()
            print('SUCCESS: Document generated')
            print(f'Document ID: {result.get("documentId", "N/A")}')
            print(f'Content length: {len(result.get("content", ""))} characters')
            print(f'Status: {result.get("status", "unknown")}')

            # Show first few lines of content
            content = result.get("content", "")
            lines = content.split('\n')[:10]
            print('\nGenerated content preview:')
            print('-' * 40)
            for line in lines:
                print(line)
            print('-' * 40)

            return True
        else:
            print(f'FAILED: HTTP {response.status_code}')
            print('Response:', response.text[:1000])
            return False

    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
        return False
    except Exception as e:
        print(f'Unexpected error: {e}')
        return False

if __name__ == "__main__":
    success = test_document_generation_api()
    sys.exit(0 if success else 1)