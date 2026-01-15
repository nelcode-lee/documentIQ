#!/usr/bin/env python3
"""Test script for document generation functionality."""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.document_generator import DocumentGenerator
from app.services.document_store import DocumentStore, DOCX_AVAILABLE, PDF_AVAILABLE, AZURE_AVAILABLE

def test_document_generation():
    """Test the document generation system."""

    print("Document Generation System Test")
    print("=" * 50)

    # Check capabilities
    print(f"DOCX Support: {DOCX_AVAILABLE}")
    print(f"PDF Support: {PDF_AVAILABLE}")
    print(f"Azure Storage: {AZURE_AVAILABLE}")
    print()

    try:
        # Initialize services
        generator = DocumentGenerator()
        store = DocumentStore()

        print("Services initialized successfully")

        # Test data for risk assessment
        test_data = {
            'activityDescription': 'Manual handling operations in warehouse',
            'location': 'Main warehouse storage area',
            'hazards': [
                {
                    'hazard': 'Manual lifting of heavy boxes',
                    'whoMightBeHarmed': 'Warehouse operatives',
                    'howHarmed': 'Musculoskeletal injuries, back strain'
                },
                {
                    'hazard': 'Slips and trips on wet floors',
                    'whoMightBeHarmed': 'All personnel working in area',
                    'howHarmed': 'Falls, fractures, head injuries'
                }
            ],
            'responsiblePerson': 'Warehouse Manager',
            'reviewDate': '2024-12-31'
        }

        print("Generating test risk assessment...")

        # Generate document
        result = asyncio.run(generator.generate_document(
            document_type='risk-assessment',
            title='Warehouse Manual Handling Risk Assessment',
            author='Safety Officer',
            data=test_data,
            use_standards=True,
            format='markdown'
        ))

        print(f"Document generated successfully! Length: {len(result['content'])} characters")

        # Show sample output
        print("\nSample generated content:")
        print("-" * 30)
        lines = result['content'].split('\n')[:15]  # First 15 lines
        for line in lines:
            print(line)
        if len(result['content'].split('\n')) > 15:
            print("... (truncated)")
        print("-" * 30)

        # Test document storage
        print("\nTesting document storage...")

        metadata = {
            "title": "Warehouse Manual Handling Risk Assessment",
            "author": "Safety Officer",
            "documentType": "risk-assessment",
            "category": "Safety",
            "version": "1.0"
        }

        download_url = asyncio.run(store.store_generated_document(
            document_id="test-doc-123",
            content=result["content"],
            metadata=metadata,
            format="markdown"
        ))

        if download_url:
            print(f"Document stored successfully!")
            print(f"Download URL: {download_url}")
        else:
            print("Document storage returned no URL (may be expected in local mode)")

        print("\nAll tests passed! Document generation system is operational.")

        return True

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_document_generation()
    sys.exit(0 if success else 1)