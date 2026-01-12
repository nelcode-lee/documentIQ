"""Vector store manager for Azure AI Search."""

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from app.config import settings
from typing import List, Dict, Optional
import json


class VectorStoreManager:
    """Manage vector operations with Azure AI Search."""
    
    def __init__(self):
        """Initialize Azure AI Search client."""
        credential = AzureKeyCredential(settings.azure_search_api_key)
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index_name,
            credential=credential
        )
    
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
        try:
            doc = {
                "id": f"{document_id}_{chunk_index}" if chunk_index is not None else document_id,
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
            print(f"Error adding document to vector store: {e}")
            raise
    
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
        try:
            if not documents:
                return True
            
            # Format documents for Azure Search
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
                    "layer": doc.get("layer"),  # Include layer field
                    "chunkIndex": doc.get("chunkIndex", 0),
                    "uploadedAt": doc.get("uploadedAt"),  # Added missing field
                    "metadata": json.dumps(doc.get("metadata")) if doc.get("metadata") else None,
                }
                formatted_docs.append(formatted_doc)
            
            # Upload in batches (Azure Search has limits)
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
            print(f"Error adding documents batch to vector store: {e}")
            raise
    
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
            filters: Optional OData filter expression
            
        Returns:
            List of search results with content and metadata
        """
        try:
            # Build search query
            search_query = query_text or "*"
            
            # Create vector query using VectorizedQuery class
            vector_queries = None
            if query_embedding:
                vector_query = VectorizedQuery(
                    vector=query_embedding,
                    k_nearest_neighbors=top_k,
                    fields="contentVector"
                )
                vector_queries = [vector_query]
            
            # Execute search (hybrid: both vector and keyword search)
            results = self.search_client.search(
                search_text=search_query,
                vector_queries=vector_queries,
                top=top_k,
                filter=filters,
                select=["id", "documentId", "content", "title", "category", "tags", "chunkIndex", "metadata", "uploadedAt"]
            )
            
            # Format results
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
            print(f"Error searching vector store: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks of a document from the index.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            # Search for all chunks of this document
            search_results = self.search_client.search(
                search_text="*",
                filter=f"documentId eq '{document_id}'",
                select=["id"]
            )
            
            # Collect IDs to delete (convert to list to iterate)
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
            print(f"[ERROR] Error deleting document from vector store: {e}")
            raise
