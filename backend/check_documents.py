"""Script to check uploaded documents in Azure AI Search."""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def check_documents():
    """Check documents in Azure AI Search and Blob Storage."""
    print("=" * 60)
    print("Checking Document Status")
    print("=" * 60)
    
    # Check Azure AI Search
    try:
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_API_KEY")
        search_index = os.getenv("AZURE_SEARCH_INDEX_NAME")
        
        print(f"\n[1] Checking Azure AI Search index: {search_index}")
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=AzureKeyCredential(search_key)
        )
        
        # Search for all documents
        results = search_client.search(
            search_text="*",
            top=1000,
            select=["documentId", "title", "category", "chunkIndex", "content"]
        )
        
        # Group by document ID
        documents = {}
        for result in results:
            doc_id = result.get("documentId")
            if doc_id not in documents:
                documents[doc_id] = {
                    "title": result.get("title"),
                    "category": result.get("category"),
                    "chunks": 0,
                    "first_chunk_preview": None
                }
            documents[doc_id]["chunks"] += 1
            if result.get("chunkIndex") == 0:
                content = result.get("content", "")[:200]
                documents[doc_id]["first_chunk_preview"] = content
        
        print(f"[OK] Found {len(documents)} document(s) in search index:")
        for doc_id, info in documents.items():
            print(f"\n  Document ID: {doc_id}")
            print(f"  Title: {info['title']}")
            print(f"  Category: {info['category'] or 'N/A'}")
            print(f"  Chunks: {info['chunks']}")
            if info['first_chunk_preview']:
                print(f"  Preview: {info['first_chunk_preview'][:100]}...")
                
    except Exception as e:
        print(f"[ERROR] Error checking Azure AI Search: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Check Azure Blob Storage
    try:
        print(f"\n[2] Checking Azure Blob Storage")
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
        
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        
        blobs = list(container_client.list_blobs())
        print(f"[OK] Found {len(blobs)} blob(s) in container '{container_name}':")
        for blob in blobs[:10]:  # Show first 10
            print(f"  - {blob.name} ({blob.size} bytes, uploaded: {blob.last_modified})")
        if len(blobs) > 10:
            print(f"  ... and {len(blobs) - 10} more")
            
    except Exception as e:
        print(f"[ERROR] Error checking Azure Blob Storage: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_documents()
