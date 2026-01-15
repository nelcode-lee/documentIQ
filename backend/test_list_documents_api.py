"""Test script to debug the list_documents API endpoint logic."""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
import json

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_list_documents_logic():
    """Test the exact logic used in list_documents endpoint."""
    print("=" * 80)
    print("Testing list_documents Logic")
    print("=" * 80)
    print()
    
    try:
        from app.config import settings
        
        # Initialize clients (same as endpoint)
        search_credential = AzureKeyCredential(settings.azure_search_api_key)
        search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=search_credential
        )
        
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        container_client = blob_service_client.get_container_client(
            settings.azure_storage_container_name
        )
        
        print(f"[1] Configuration")
        print(f"    Search Endpoint: {settings.azure_search_endpoint}")
        print(f"    Search Index: {settings.azure_search_index_name}")
        print(f"    Storage Container: {settings.azure_storage_container_name}")
        print()
        
        # Step 1: Search for chunks (same as endpoint)
        print("[2] Searching for chunks...")
        try:
            results = search_client.search(
                search_text="*",
                top=500,
                select=["documentId", "title", "category", "tags", "metadata", "uploadedAt", "chunkIndex"]
            )
            print("    ✅ Search query executed successfully")
        except Exception as e:
            print(f"    ❌ Search failed with all fields: {e}")
            print("    Trying with minimal fields...")
            results = search_client.search(
                search_text="*",
                top=500,
                select=["documentId", "title", "category", "chunkIndex"]
            )
        
        # Convert to list
        try:
            results_list = list(results)
            print(f"    ✅ Retrieved {len(results_list)} chunks")
        except Exception as e:
            print(f"    ❌ Failed to convert to list: {e}")
            import traceback
            traceback.print_exc()
            return
        
        if len(results_list) == 0:
            print("    ⚠️  No chunks found!")
            return
        
        # Step 2: Group by documentId
        print()
        print("[3] Grouping by documentId...")
        documents_dict = {}
        seen_doc_ids = set()
        
        for result in results_list:
            doc_id = result.get("documentId")
            if not doc_id:
                print(f"    ⚠️  Found chunk without documentId: {result.get('id', 'unknown')}")
                continue
            
            if doc_id in seen_doc_ids:
                continue
            
            seen_doc_ids.add(doc_id)
            
            # Parse metadata
            metadata_str = result.get("metadata")
            metadata = {}
            if metadata_str:
                try:
                    metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                except Exception as e:
                    print(f"    ⚠️  Failed to parse metadata for {doc_id}: {e}")
            
            # Get uploadedAt
            uploaded_at = result.get("uploadedAt")
            if not uploaded_at and metadata.get("processed_at"):
                uploaded_at = metadata.get("processed_at")
            
            # Handle uploadedAt formatting
            try:
                if uploaded_at:
                    if hasattr(uploaded_at, 'isoformat'):
                        uploaded_at_str = uploaded_at.isoformat()
                    elif isinstance(uploaded_at, str):
                        uploaded_at_str = uploaded_at
                    else:
                        from datetime import datetime
                        uploaded_at_str = datetime.utcnow().isoformat()
                else:
                    from datetime import datetime
                    uploaded_at_str = datetime.utcnow().isoformat()
            except Exception as e:
                print(f"    ⚠️  Error formatting uploadedAt for {doc_id}: {e}")
                from datetime import datetime
                uploaded_at_str = datetime.utcnow().isoformat()
            
            # Extract layer
            doc_layer = None
            if metadata and metadata.get("layer"):
                doc_layer = metadata.get("layer")
            if not doc_layer:
                doc_layer = result.get("layer")
            
            documents_dict[doc_id] = {
                "id": doc_id,
                "title": result.get("title", "Untitled Document"),
                "category": result.get("category"),
                "tags": result.get("tags", []),
                "layer": doc_layer,
                "uploadedAt": uploaded_at_str,
                "status": "completed",
                "source": "uploaded",
                "metadata": metadata
            }
        
        print(f"    ✅ Created {len(documents_dict)} unique documents")
        for doc_id, doc_info in documents_dict.items():
            print(f"       - {doc_info['title']} ({doc_id[:8]}...)")
        print()
        
        # Step 3: Get blob information
        print("[4] Getting blob information...")
        try:
            blob_list = container_client.list_blobs()
            blob_dict = {}
            for blob in blob_list:
                blob_dict[blob.name] = {
                    "fileSize": blob.size,
                    "lastModified": blob.last_modified.isoformat() if hasattr(blob.last_modified, 'isoformat') else None,
                    "fileType": blob.name.split('.')[-1].lower() if '.' in blob.name else None
                }
            print(f"    ✅ Found {len(blob_dict)} blobs")
            for blob_name in list(blob_dict.keys())[:5]:
                print(f"       - {blob_name}")
            if len(blob_dict) > 5:
                print(f"       ... and {len(blob_dict) - 5} more")
        except Exception as e:
            print(f"    ❌ Error accessing blob storage: {e}")
            import traceback
            traceback.print_exc()
            blob_dict = {}
        
        print()
        
        # Step 4: Merge blob metadata with document info
        print("[5] Merging blob metadata with documents...")
        documents_list = []
        matched_blobs = set()
        
        for doc_id, doc_info in documents_dict.items():
            # Try to find blob for this document
            blob_info = None
            matched_blob_name = None
            for blob_name, blob_data in blob_dict.items():
                if blob_name.startswith(doc_id):
                    blob_info = blob_data
                    matched_blob_name = blob_name
                    matched_blobs.add(blob_name)
                    break
            
            if not blob_info:
                print(f"    ⚠️  No blob found for document {doc_id[:8]}... ({doc_info['title']})")
            
            # Build document response (simulate DocumentResponse creation)
            doc_response_data = {
                "id": doc_info["id"],
                "title": doc_info["title"],
                "category": doc_info.get("category"),
                "tags": doc_info.get("tags", []),
                "layer": doc_info.get("layer"),
                "uploadedAt": doc_info["uploadedAt"],
                "status": doc_info["status"],
                "source": doc_info.get("source", "uploaded"),
                "fileType": blob_info.get("fileType") if blob_info else None,
                "fileSize": blob_info.get("fileSize") if blob_info else None
            }
            
            # Validate required fields
            required_fields = ["id", "title", "uploadedAt", "status"]
            missing_fields = [f for f in required_fields if not doc_response_data.get(f)]
            if missing_fields:
                print(f"    ❌ Document {doc_id[:8]}... missing required fields: {missing_fields}")
            else:
                documents_list.append(doc_response_data)
        
        print(f"    ✅ Created {len(documents_list)} document responses")
        
        # Check for unmatched blobs
        unmatched_blobs = set(blob_dict.keys()) - matched_blobs
        if unmatched_blobs:
            print(f"    ⚠️  Found {len(unmatched_blobs)} blob(s) that don't match any document:")
            for blob_name in list(unmatched_blobs)[:3]:
                print(f"       - {blob_name}")
        
        print()
        print("=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Chunks retrieved: {len(results_list)}")
        print(f"Unique documents: {len(documents_dict)}")
        print(f"Blobs found: {len(blob_dict)}")
        print(f"Documents with blobs: {len(matched_blobs)}")
        print(f"Final document list: {len(documents_list)}")
        print()
        
        # Show sample document
        if documents_list:
            print("Sample document:")
            sample = documents_list[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_list_documents_logic()
