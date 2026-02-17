"""Supabase Service - Unified storage, vector DB, and metadata management."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import uuid
from app.config import settings

# Supabase client
_supabase_client = None


def get_supabase_client():
    """Get or create Supabase client."""
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_service_key:
            print("[WARNING] Supabase not configured")
            return None
        
        try:
            from supabase import create_client, Client
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            print("[OK] Supabase client initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize Supabase: {e}")
            return None
    
    return _supabase_client


class SupabaseStorageService:
    """Handle file storage with Supabase Storage."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.bucket = settings.supabase_storage_bucket
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure storage bucket exists."""
        if not self.client:
            return
        
        try:
            # Try to get bucket info
            self.client.storage.get_bucket(self.bucket)
            print(f"[OK] Storage bucket '{self.bucket}' ready")
        except Exception:
            try:
                # Create bucket if it doesn't exist
                self.client.storage.create_bucket(
                    self.bucket,
                    options={"public": False}
                )
                print(f"[OK] Created storage bucket '{self.bucket}'")
            except Exception as e:
                print(f"[WARNING] Could not create bucket: {e}")
    
    def upload_file(self, file_path: str, file_content: bytes, content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload a file to Supabase Storage."""
        if not self.client:
            return None
        
        try:
            result = self.client.storage.from_(self.bucket).upload(
                file_path,
                file_content,
                {"content-type": content_type}
            )
            return file_path
        except Exception as e:
            print(f"[ERROR] Failed to upload file: {e}")
            return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download a file from Supabase Storage."""
        if not self.client:
            return None
        
        try:
            result = self.client.storage.from_(self.bucket).download(file_path)
            return result
        except Exception as e:
            print(f"[ERROR] Failed to download file: {e}")
            return None
    
    def get_public_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Get a signed URL for file download."""
        if not self.client:
            return None
        
        try:
            result = self.client.storage.from_(self.bucket).create_signed_url(
                file_path,
                expires_in
            )
            return result.get("signedURL")
        except Exception as e:
            print(f"[ERROR] Failed to get signed URL: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage."""
        if not self.client:
            return False
        
        try:
            self.client.storage.from_(self.bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete file: {e}")
            return False
    
    def list_files(self, folder: str = "") -> List[Dict]:
        """List files in a folder."""
        if not self.client:
            return []
        
        try:
            result = self.client.storage.from_(self.bucket).list(folder)
            return result
        except Exception as e:
            print(f"[ERROR] Failed to list files: {e}")
            return []


class SupabaseVectorService:
    """Handle vector search with Supabase pgvector."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self._initialized = False
    
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
        """Add a document chunk to the vector store."""
        if not self.client:
            return False
        
        try:
            chunk_id = f"{document_id}_{chunk_index}" if chunk_index is not None else document_id
            
            data = {
                "id": chunk_id,
                "document_id": document_id,
                "content": content,
                "embedding": content_vector,
                "title": title,
                "category": category,
                "tags": tags or [],
                "chunk_index": chunk_index or 0,
                "metadata": json.dumps(metadata) if metadata else None,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("documents").upsert(data).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add document: {e}")
            return False
    
    async def add_documents_batch(self, documents: List[Dict]) -> bool:
        """Add multiple document chunks."""
        if not self.client:
            return False
        
        try:
            formatted_docs = []
            for doc in documents:
                formatted_doc = {
                    "id": doc.get("id"),
                    "document_id": doc.get("documentId"),
                    "content": doc.get("content"),
                    "embedding": doc.get("contentVector"),
                    "title": doc.get("title"),
                    "category": doc.get("category"),
                    "tags": doc.get("tags", []),
                    "layer": doc.get("layer"),
                    "chunk_index": doc.get("chunkIndex", 0),
                    "metadata": json.dumps(doc.get("metadata")) if doc.get("metadata") else None,
                    "created_at": datetime.utcnow().isoformat()
                }
                formatted_docs.append(formatted_doc)
            
            # Batch insert
            result = self.client.table("documents").upsert(formatted_docs).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add documents batch: {e}")
            return False
    
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        query_text: Optional[str] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar documents using vector similarity."""
        if not self.client:
            return []
        
        try:
            # Use Supabase RPC for vector similarity search
            result = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k,
                    "filter_category": filters.get("category") if filters else None
                }
            ).execute()
            
            return [{
                "id": r.get("id"),
                "documentId": r.get("document_id"),
                "content": r.get("content"),
                "title": r.get("title"),
                "category": r.get("category"),
                "tags": r.get("tags", []),
                "score": r.get("similarity"),
                "metadata": json.loads(r.get("metadata")) if r.get("metadata") else None
            } for r in result.data]
        except Exception as e:
            print(f"[ERROR] Vector search failed: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document."""
        if not self.client:
            return False
        
        try:
            result = self.client.table("documents").delete().eq(
                "document_id", document_id
            ).execute()
            print(f"[OK] Deleted document chunks for {document_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete document: {e}")
            return False


class SupabaseMetadataService:
    """Handle metadata storage (conversations, messages, ratings)."""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    # Conversation methods
    def create_conversation(self, conversation_id: str, title: str = "New Conversation", language: str = "en") -> Optional[str]:
        """Create a new conversation."""
        if not self.client:
            return None
        
        try:
            data = {
                "id": conversation_id,
                "title": title,
                "language": language,
                "message_count": 0,
                "total_response_time_ms": 0,
                "average_response_time_ms": 0,
                "total_queries": 0,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            self.client.table("conversations").insert(data).execute()
            return conversation_id
        except Exception as e:
            print(f"[ERROR] Failed to create conversation: {e}")
            return None
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a conversation by ID."""
        if not self.client:
            return None
        
        try:
            result = self.client.table("conversations").select("*").eq(
                "id", conversation_id
            ).single().execute()
            return result.data
        except Exception as e:
            return None
    
    def update_conversation(self, conversation_id: str, **kwargs) -> bool:
        """Update conversation fields."""
        if not self.client:
            return False
        
        try:
            kwargs["updated_at"] = datetime.utcnow().isoformat()
            self.client.table("conversations").update(kwargs).eq(
                "id", conversation_id
            ).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update conversation: {e}")
            return False
    
    def list_conversations(self, limit: int = 50) -> List[Dict]:
        """List recent conversations."""
        if not self.client:
            return []
        
        try:
            result = self.client.table("conversations").select("*").order(
                "updated_at", desc=True
            ).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"[ERROR] Failed to list conversations: {e}")
            return []
    
    # Message methods
    def add_message(self, message_id: str, conversation_id: str, role: str, content: str,
                   sources: Optional[List] = None, response_time_ms: Optional[float] = None) -> bool:
        """Add a message to a conversation."""
        if not self.client:
            return False
        
        try:
            data = {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "sources": sources,
                "response_time_ms": response_time_ms,
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("messages").insert(data).execute()
            
            # Update conversation stats
            conv = self.get_conversation(conversation_id)
            if conv:
                updates = {
                    "message_count": conv.get("message_count", 0) + 1,
                }
                if role == "user":
                    updates["total_queries"] = conv.get("total_queries", 0) + 1
                if response_time_ms and response_time_ms > 0:
                    total_time = conv.get("total_response_time_ms", 0) + response_time_ms
                    total_queries = updates.get("total_queries", conv.get("total_queries", 0))
                    updates["total_response_time_ms"] = total_time
                    if total_queries > 0:
                        updates["average_response_time_ms"] = total_time / total_queries
                
                self.update_conversation(conversation_id, **updates)
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add message: {e}")
            return False
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation."""
        if not self.client:
            return []
        
        try:
            result = self.client.table("messages").select("*").eq(
                "conversation_id", conversation_id
            ).order("created_at").execute()
            return result.data
        except Exception as e:
            print(f"[ERROR] Failed to get messages: {e}")
            return []
    
    # Rating methods
    def add_rating(self, rating_id: str, message_id: str, conversation_id: str, rating: int) -> bool:
        """Add a rating for a message."""
        if not self.client:
            return False
        
        try:
            data = {
                "id": rating_id,
                "message_id": message_id,
                "conversation_id": conversation_id,
                "rating": rating,
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("ratings").insert(data).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to add rating: {e}")
            return False
    
    def get_average_rating(self, days: int = 30) -> float:
        """Get average rating over time period."""
        if not self.client:
            return 0.0
        
        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            result = self.client.table("ratings").select("rating").gte(
                "created_at", cutoff
            ).execute()
            
            if result.data:
                ratings = [r["rating"] for r in result.data]
                return sum(ratings) / len(ratings)
            return 0.0
        except Exception as e:
            print(f"[ERROR] Failed to get average rating: {e}")
            return 0.0
    
    # Analytics methods
    def get_analytics_summary(self, days: int = 30) -> Dict:
        """Get analytics summary."""
        if not self.client:
            return {}
        
        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Total conversations
            convs = self.client.table("conversations").select("id", count="exact").gte(
                "updated_at", cutoff
            ).execute()
            
            # Total messages
            msgs = self.client.table("messages").select("id", count="exact").gte(
                "created_at", cutoff
            ).execute()
            
            # Average response time
            response_times = self.client.table("messages").select("response_time_ms").gte(
                "created_at", cutoff
            ).gt("response_time_ms", 0).execute()
            
            avg_response = 0
            if response_times.data:
                times = [r["response_time_ms"] for r in response_times.data if r.get("response_time_ms")]
                avg_response = sum(times) / len(times) if times else 0
            
            return {
                "total_conversations": convs.count or 0,
                "total_messages": msgs.count or 0,
                "average_response_time_ms": avg_response,
                "average_rating": self.get_average_rating(days),
                "period_days": days
            }
        except Exception as e:
            print(f"[ERROR] Failed to get analytics: {e}")
            return {}


# Global service instances
storage_service = SupabaseStorageService()
vector_service = SupabaseVectorService()
metadata_service = SupabaseMetadataService()
