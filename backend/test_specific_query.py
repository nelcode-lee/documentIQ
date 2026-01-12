"""Test a specific query to see what results are returned."""

import os
import sys
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from app.services.embedding_service import EmbeddingService

# Fix Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def test_query():
    """Test a specific query."""
    query = "How does Issue 9 expect the HACCP team to validate critical limits before implementing changes?"
    
    print("=" * 70)
    print(f"Testing Query: {query}")
    print("=" * 70)
    
    # Initialize services
    embedding_service = EmbeddingService()
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_API_KEY")
    search_index = os.getenv("AZURE_SEARCH_INDEX_NAME")
    
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=search_index,
        credential=AzureKeyCredential(search_key)
    )
    
    # Step 1: Generate embedding
    print("\n[Step 1] Generating query embedding...")
    try:
        query_embedding = embedding_service.generate_embedding(query)
        print(f"  ✅ Embedding generated: {len(query_embedding)} dimensions")
    except Exception as e:
        print(f"  ❌ Error generating embedding: {e}")
        return
    
    # Step 2: Search with text only (keyword search)
    print("\n[Step 2] Text-only search results:")
    try:
        results = search_client.search(
            search_text=query,
            top=5,
            select=["documentId", "title", "content", "chunkIndex"]
        )
        results_list = list(results)
        print(f"  Found {len(results_list)} results:")
        for i, result in enumerate(results_list, 1):
            print(f"\n  Result {i} (Score: {result.get('@search.score', 0):.4f}):")
            print(f"    Document: {result.get('title')}")
            print(f"    Chunk: {result.get('chunkIndex')}")
            content_preview = result.get('content', '')[:200]
            print(f"    Preview: {content_preview}...")
    except Exception as e:
        print(f"  ❌ Error in text search: {e}")
    
    # Step 3: Vector search
    print("\n[Step 3] Vector search results:")
    try:
        from azure.search.documents.models import VectorizedQuery
        vector_query = VectorizedQuery(
            vector=query_embedding,
            k_nearest_neighbors=5,
            fields="contentVector"
        )
        
        results = search_client.search(
            search_text="*",
            vector_queries=[vector_query],
            top=5,
            select=["documentId", "title", "content", "chunkIndex"]
        )
        results_list = list(results)
        print(f"  Found {len(results_list)} results:")
        for i, result in enumerate(results_list, 1):
            print(f"\n  Result {i} (Score: {result.get('@search.score', 0):.4f}):")
            print(f"    Document: {result.get('title')}")
            print(f"    Chunk: {result.get('chunkIndex')}")
            content_preview = result.get('content', '')[:200]
            print(f"    Preview: {content_preview}...")
    except Exception as e:
        print(f"  ❌ Error in vector search: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Search for keywords from the query
    print("\n[Step 4] Keyword-based searches:")
    keywords = ["Issue 9", "HACCP", "critical limits", "validate"]
    for keyword in keywords:
        try:
            results = search_client.search(
                search_text=keyword,
                top=3,
                select=["documentId", "title", "chunkIndex"]
            )
            results_list = list(results)
            if results_list:
                print(f"  '{keyword}': Found {len(results_list)} chunks")
                for r in results_list[:2]:
                    print(f"    - {r.get('title')} (chunk {r.get('chunkIndex')})")
            else:
                print(f"  '{keyword}': No results")
        except Exception as e:
            print(f"  '{keyword}': Error - {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_query()
