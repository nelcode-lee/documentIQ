"""Vector store manager for document search (Supabase pgvector or Azure AI Search)."""

from app.config import settings
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta

# Global singleton instance
_vector_store_instance = None
_documents_cache = None
_documents_cache_time = None
CACHE_TTL_SECONDS = 30  # Cache documents for 30 seconds


def get_vector_store() -> 'VectorStoreManager':
    """Get singleton VectorStoreManager instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreManager()
    return _vector_store_instance


class VectorStoreManager:
    """Manage vector operations with Supabase pgvector or Azure AI Search."""
    
    def __init__(self):
        """Initialize vector store client."""
        self.use_supabase = bool(settings.supabase_url and settings.supabase_anon_key)
        self.use_azure = bool(settings.azure_search_endpoint and settings.azure_search_api_key)
        
        self.supabase_client = None
        self.search_client = None
        
        if self.use_supabase:
            try:
                from supabase import create_client
                self.supabase_client = create_client(
                    settings.supabase_url,
                    settings.supabase_anon_key
                )
                print("[OK] Vector store using Supabase pgvector")
            except Exception as e:
                print(f"[WARNING] Could not initialize Supabase: {e}")
                self.use_supabase = False
        
        if not self.use_supabase and self.use_azure:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            credential = AzureKeyCredential(settings.azure_search_api_key)
            self.search_client = SearchClient(
                endpoint=settings.azure_search_endpoint,
                index_name=settings.azure_search_index_name,
                credential=credential
            )
            print("[OK] Vector store using Azure AI Search")
        
        if not self.use_supabase and not self.use_azure:
            print("[WARNING] No vector store backend configured - search will be limited")
    
    async def add_document(
        self,
        document_id: str,
        content: str,
        content_vector: List[float],
        title: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        chunk_index: Optional[int] = None
    ) -> bool:
        """
        Add a document chunk to the search index.
        
        Args:
            document_id: Original document ID
            content: Text content of the chunk
            content_vector: Embedding vector
            title: Document title
            category: Document category
            tags: Document tags
            metadata: Additional metadata
            chunk_index: Index of this chunk in the document
            
        Returns:
            True if successful
        """
        chunk_id = f"{document_id}_{chunk_index}" if chunk_index is not None else document_id
        
        if self.use_supabase:
            try:
                self.supabase_client.table("documents").insert({
                    "id": chunk_id,
                    "document_id": document_id,
                    "content": content,
                    "embedding": content_vector,
                    "title": title,
                    "category": category,
                    "tags": tags or [],
                    "chunk_index": chunk_index or 0,
                    "metadata": metadata or {}
                }).execute()
                return True
            except Exception as e:
                print(f"Error adding document to Supabase: {e}")
                raise
        
        if self.use_azure:
            try:
                doc = {
                    "id": chunk_id,
                    "documentId": document_id,
                    "content": content,
                    "contentVector": content_vector,
                    "title": title,
                    "category": category,
                    "tags": tags or [],
                    "chunkIndex": chunk_index or 0,
                    "metadata": json.dumps(metadata) if metadata else None,
                }
                result = self.search_client.upload_documents(documents=[doc])
                return result[0].succeeded
            except Exception as e:
                print(f"Error adding document to Azure Search: {e}")
                raise
        
        return False
    
    async def add_documents_batch(
        self,
        documents: List[Dict]
    ) -> bool:
        """
        Add multiple document chunks to the search index in a single batch.
        
        Args:
            documents: List of document dictionaries with required fields
            
        Returns:
            True if all documents succeeded
        """
        if not documents:
            return True
        
        if self.use_supabase:
            try:
                formatted_docs = []
                for doc in documents:
                    chunk_id = doc.get("id") or f"{doc.get('documentId')}_{doc.get('chunkIndex', 0)}"
                    formatted_docs.append({
                        "id": chunk_id,
                        "document_id": doc.get("documentId"),
                        "content": doc.get("content"),
                        "embedding": doc.get("contentVector"),
                        "title": doc.get("title"),
                        "category": doc.get("category"),
                        "tags": doc.get("tags", []),
                        "chunk_index": doc.get("chunkIndex", 0),
                        "metadata": doc.get("metadata") or {}
                    })
                
                # Insert in batches
                batch_size = 100
                for i in range(0, len(formatted_docs), batch_size):
                    batch = formatted_docs[i:i + batch_size]
                    self.supabase_client.table("documents").insert(batch).execute()
                
                return True
            except Exception as e:
                print(f"Error adding documents batch to Supabase: {e}")
                raise
        
        if self.use_azure:
            try:
                formatted_docs = []
                for doc in documents:
                    formatted_doc = {
                        "id": doc.get("id"),
                        "documentId": doc.get("documentId"),
                        "content": doc.get("content"),
                        "contentVector": doc.get("contentVector"),
                        "title": doc.get("title"),
                        "category": doc.get("category"),
                        "tags": doc.get("tags", []),
                        "layer": doc.get("layer"),
                        "chunkIndex": doc.get("chunkIndex", 0),
                        "uploadedAt": doc.get("uploadedAt"),
                        "metadata": json.dumps(doc.get("metadata")) if doc.get("metadata") else None,
                    }
                    formatted_docs.append(formatted_doc)
                
                batch_size = 100
                all_succeeded = True
                
                for i in range(0, len(formatted_docs), batch_size):
                    batch = formatted_docs[i:i + batch_size]
                    result = self.search_client.upload_documents(documents=batch)
                    batch_succeeded = all(r.succeeded for r in result)
                    if not batch_succeeded:
                        all_succeeded = False
                        print(f"Warning: Some documents in batch {i//batch_size + 1} failed to upload")
                
                return all_succeeded
            except Exception as e:
                print(f"Error adding documents batch to Azure Search: {e}")
                raise
        
        return False
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        query_text: Optional[str] = None,
        filters: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant documents using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            query_text: Optional text query for hybrid search
            filters: Optional filter expression
            
        Returns:
            List of search results with content and metadata
        """
        if self.use_supabase:
            try:
                # Try RPC function first (may have different signatures)
                try:
                    # Try the standard signature
                    result = self.supabase_client.rpc("match_documents", {
                        "query_embedding": query_embedding,
                        "match_count": top_k,
                        "filter_category": None  # No category filter
                    }).execute()
                except Exception as rpc_error:
                    # If RPC fails, fall back to direct table query with text search
                    print(f"[INFO] RPC match_documents not available, using text search: {rpc_error}")
                    if query_text:
                        result = self.supabase_client.table("documents").select("*").ilike("content", f"%{query_text}%").limit(top_k).execute()
                    else:
                        result = self.supabase_client.table("documents").select("*").limit(top_k).execute()
                
                formatted_results = []
                for row in result.data:
                    formatted_results.append({
                        "id": row.get("id"),
                        "documentId": row.get("document_id"),
                        "content": row.get("content"),
                        "title": row.get("title"),
                        "category": row.get("category"),
                        "tags": row.get("tags", []),
                        "score": row.get("similarity", 0.8),
                        "metadata": row.get("metadata"),
                    })
                
                return formatted_results
            except Exception as e:
                print(f"Error searching Supabase: {e}")
                # Final fallback - return all documents
                try:
                    result = self.supabase_client.table("documents").select("*").limit(top_k).execute()
                    return [{
                        "id": row.get("id"),
                        "documentId": row.get("document_id"),
                        "content": row.get("content"),
                        "title": row.get("title"),
                        "category": row.get("category"),
                        "tags": row.get("tags", []),
                        "score": 0.5,
                        "metadata": row.get("metadata"),
                    } for row in result.data]
                except:
                    pass
                return []
        
        if self.use_azure:
            try:
                from azure.search.documents.models import VectorizedQuery
                
                search_query = query_text or "*"
                
                vector_queries = None
                if query_embedding:
                    vector_query = VectorizedQuery(
                        vector=query_embedding,
                        k_nearest_neighbors=top_k,
                        fields="contentVector"
                    )
                    vector_queries = [vector_query]
                
                results = self.search_client.search(
                    search_text=search_query,
                    vector_queries=vector_queries,
                    top=top_k,
                    filter=filters,
                    select=["id", "documentId", "content", "title", "category", "tags", "chunkIndex", "metadata", "uploadedAt"]
                )
                
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        "id": result.get("id"),
                        "documentId": result.get("documentId"),
                        "content": result.get("content"),
                        "title": result.get("title"),
                        "category": result.get("category"),
                        "tags": result.get("tags", []),
                        "score": result.get("@search.score"),
                        "metadata": json.loads(result.get("metadata")) if result.get("metadata") else None,
                    })
                
                return formatted_results
            except Exception as e:
                print(f"Error searching Azure Search: {e}")
                raise
        
        return []
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks of a document from the index.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        if self.use_supabase:
            try:
                self.supabase_client.table("documents").delete().eq("document_id", document_id).execute()
                print(f"[OK] Deleted chunks for document {document_id} from Supabase")
                return True
            except Exception as e:
                print(f"[ERROR] Error deleting document from Supabase: {e}")
                raise
        
        if self.use_azure:
            try:
                search_results = self.search_client.search(
                    search_text="*",
                    filter=f"documentId eq '{document_id}'",
                    select=["id"]
                )
                
                ids_to_delete = []
                for result in search_results:
                    ids_to_delete.append({"id": result["id"]})
                
                if ids_to_delete:
                    result = self.search_client.delete_documents(documents=ids_to_delete)
                    print(f"[OK] Deleted {len(ids_to_delete)} chunks for document {document_id}")
                    return all(r.succeeded for r in result)
                
                print(f"[INFO] No chunks found for document {document_id}")
                return True
            except Exception as e:
                print(f"[ERROR] Error deleting document from Azure Search: {e}")
                raise
        
        return False
    
    async def list_all_documents(self, use_cache: bool = True) -> List[Dict]:
        """
        List all unique documents in the vector store.
        
        Args:
            use_cache: Whether to use cached results (default True)
        
        Returns:
            List of unique documents with metadata
        """
        global _documents_cache, _documents_cache_time
        
        # Check cache first
        if use_cache and _documents_cache is not None and _documents_cache_time is not None:
            if datetime.utcnow() - _documents_cache_time < timedelta(seconds=CACHE_TTL_SECONDS):
                return _documents_cache
        
        if self.use_supabase:
            try:
                # Fetch all rows using pagination (Supabase max is 1000 per request)
                docs_map = {}
                page_size = 1000
                offset = 0
                
                while True:
                    result = self.supabase_client.table("documents").select(
                        "document_id, title, category, tags, layer, created_at"
                    ).range(offset, offset + page_size - 1).execute()
                    
                    if not result.data:
                        break
                    
                    # Deduplicate by document_id
                    for row in result.data:
                        doc_id = row.get("document_id")
                        if doc_id and doc_id not in docs_map:
                            docs_map[doc_id] = {
                                "documentId": doc_id,
                                "title": row.get("title"),
                                "category": row.get("category"),
                                "layer": row.get("layer"),
                                "tags": row.get("tags", []),
                                "uploadedAt": row.get("created_at")
                            }
                    
                    # If we got fewer rows than page_size, we've reached the end
                    if len(result.data) < page_size:
                        break
                    
                    offset += page_size
                
                docs_list = list(docs_map.values())
                print(f"[INFO] Found {len(docs_list)} unique documents in Supabase")
                
                # Update cache
                _documents_cache = docs_list
                _documents_cache_time = datetime.utcnow()
                return docs_list
            except Exception as e:
                print(f"Error listing documents from Supabase: {e}")
                return []
        
        if self.use_azure:
            try:
                results = self.search_client.search(
                    search_text="*",
                    select=["documentId", "title", "category", "tags", "uploadedAt"],
                    top=1000
                )
                
                docs_map = {}
                for result in results:
                    doc_id = result.get("documentId")
                    if doc_id and doc_id not in docs_map:
                        docs_map[doc_id] = {
                            "documentId": doc_id,
                            "title": result.get("title"),
                            "category": result.get("category"),
                            "tags": result.get("tags", []),
                            "uploadedAt": result.get("uploadedAt")
                        }
                
                docs_list = list(docs_map.values())
                # Update cache
                _documents_cache = docs_list
                _documents_cache_time = datetime.utcnow()
                return docs_list
            except Exception as e:
                print(f"Error listing documents from Azure Search: {e}")
                return []
        
        return []


def invalidate_documents_cache():
    """Invalidate the documents cache (call after uploads/deletes)."""
    global _documents_cache, _documents_cache_time
    _documents_cache = None
    _documents_cache_time = None
