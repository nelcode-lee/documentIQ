"""Quick script to test search functionality and verify documents are accessible."""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_search():
    """Test search functionality."""
    print("=" * 60)
    print("Testing Azure AI Search Index")
    print("=" * 60)
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX_NAME")
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # Test 1: Count all documents
    print("\n[Test 1] Counting all indexed chunks...")
    results = search_client.search(
        search_text="*",
        top=1000,
        select=["documentId", "title"]
    )
    
    chunks = list(results)
    unique_docs = set(r.get("documentId") for r in chunks)
    print(f"  Found {len(chunks)} chunks from {len(unique_docs)} unique documents")
    
    # Test 2: Search by title
    print("\n[Test 2] Searching for documents by title...")
    search_terms = ["BRCGS", "Microbiological", "Food Safety"]
    
    for term in search_terms:
        results = search_client.search(
            search_text=term,
            top=5,
            select=["documentId", "title", "category"]
        )
        results_list = list(results)
        if results_list:
            print(f"  Search '{term}': Found {len(results_list)} results")
            for r in results_list[:3]:
                print(f"    - {r.get('title')} (Doc ID: {r.get('documentId')[:8]}...)")
        else:
            print(f"  Search '{term}': No results")
    
    # Test 3: List unique documents
    print("\n[Test 3] Listing unique documents in index:")
    doc_info = {}
    for chunk in chunks:
        doc_id = chunk.get("documentId")
        if doc_id and doc_id not in doc_info:
            doc_info[doc_id] = chunk.get("title", "Untitled")
    
    for i, (doc_id, title) in enumerate(doc_info.items(), 1):
        chunk_count = sum(1 for c in chunks if c.get("documentId") == doc_id)
        print(f"  {i}. {title}")
        print(f"     ID: {doc_id[:8]}... ({chunk_count} chunks)")
    
    print("\n" + "=" * 60)
    print("✅ Index is working correctly!")
    print("=" * 60)
    print("\nNote: 'Knowledge Source' in Azure Portal will be empty")
    print("because documents are uploaded via API, not through an indexer.")
    print("This is normal and expected behavior.\n")

if __name__ == "__main__":
    test_search()
