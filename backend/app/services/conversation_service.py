"""Conversation service for storing and managing chat conversations."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from app.config import settings
from app.models.chat import (
    Conversation, ConversationMessage, ChatRating, ChatFeedback,
    ChatAnalyticsSummary
)
import json
import uuid


class ConversationService:
    """Service to manage chat conversations and persistence."""

    def __init__(self):
        """Initialize conversation service - uses Supabase or Azure Blob Storage."""
        self.use_supabase = bool(settings.supabase_url and settings.supabase_anon_key)
        self.use_azure = bool(settings.azure_storage_connection_string)
        
        self.blob_service_client = None
        self.supabase_client = None
        
        if self.use_supabase:
            try:
                from supabase import create_client
                self.supabase_client = create_client(
                    settings.supabase_url,
                    settings.supabase_anon_key
                )
                print("[OK] Conversation service using Supabase")
            except Exception as e:
                print(f"[WARNING] Could not initialize Supabase: {e}")
                self.use_supabase = False
        
        if not self.use_supabase and self.use_azure:
            from azure.storage.blob import BlobServiceClient
            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
            self.conversations_container = "conversations"
            self.messages_container = "conversation-messages"
            self.ratings_container = "conversation-ratings"
            self.feedback_container = "conversation-feedback"
            self._ensure_containers()
        
        if not self.use_supabase and not self.use_azure:
            print("[WARNING] No storage backend configured for conversations - using in-memory fallback")
            self._memory_store = {
                "conversations": {},
                "messages": {},
                "ratings": {},
                "feedback": {}
            }

    def _ensure_containers(self):
        """Ensure required blob containers exist."""
        if not self.blob_service_client:
            return
            
        containers = [
            self.conversations_container,
            self.messages_container,
            self.ratings_container,
            self.feedback_container
        ]

        for container in containers:
            try:
                self.blob_service_client.create_container(container)
                print(f"[INFO] Created container: {container}")
            except Exception as e:
                if "ContainerAlreadyExists" not in str(e):
                    print(f"[WARNING] Could not create container {container}: {e}")

    def _blob_name(self, container: str, id: str) -> str:
        """Generate blob name for storing data."""
        return f"{container}/{id}.json"

    def _save_to_blob(self, container: str, id: str, data: dict):
        """Save data to Azure Blob Storage."""
        if not self.blob_service_client:
            return
            
        blob_name = self._blob_name(container, id)
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container, blob=blob_name
            )

            # Add metadata
            data["_metadata"] = {
                "saved_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }

            json_data = json.dumps(data, default=str, indent=2)
            blob_client.upload_blob(json_data, overwrite=True)
        except Exception as e:
            print(f"[ERROR] Failed to save {id} to {container}: {e}")
            raise

    def _load_from_blob(self, container: str, id: str) -> Optional[dict]:
        """Load data from Azure Blob Storage."""
        if not self.blob_service_client:
            return None
            
        blob_name = self._blob_name(container, id)
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container, blob=blob_name
            )
            data = blob_client.download_blob().readall().decode('utf-8')
            return json.loads(data)
        except Exception as e:
            if "BlobNotFound" in str(e) or "404" in str(e):
                return None
            print(f"[ERROR] Failed to load {id} from {container}: {e}")
            return None

    def _list_blobs(self, container: str, prefix: str = "") -> List[str]:
        """List blob names in container."""
        if not self.blob_service_client:
            return []
            
        try:
            container_client = self.blob_service_client.get_container_client(container)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"[ERROR] Failed to list blobs in {container}: {e}")
            return []

    # Conversation Management
    def create_conversation(self, title: str = "New Conversation", language: str = "en") -> str:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow()

        if self.use_supabase:
            try:
                self.supabase_client.table("conversations").insert({
                    "id": conversation_id,
                    "title": title,
                    "language": language,
                    "message_count": 0,
                    "total_response_time_ms": 0,
                    "average_response_time_ms": 0,
                    "total_queries": 0,
                    "is_active": True,
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat()
                }).execute()
                return conversation_id
            except Exception as e:
                print(f"[ERROR] Failed to create conversation in Supabase: {e}")
                raise
        
        if self.use_azure:
            conversation = Conversation(
                id=conversation_id,
                title=title,
                created_at=now,
                updated_at=now,
                message_count=0,
                language=language,
                total_response_time_ms=0.0,
                average_response_time_ms=0.0,
                total_queries=0,
                is_active=True
            )
            self._save_to_blob(self.conversations_container, conversation_id, conversation.dict())
            return conversation_id
        
        # In-memory fallback
        self._memory_store["conversations"][conversation_id] = {
            "id": conversation_id,
            "title": title,
            "language": language,
            "message_count": 0,
            "created_at": now,
            "updated_at": now,
            "total_response_time_ms": 0,
            "average_response_time_ms": 0,
            "total_queries": 0,
            "is_active": True
        }
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        if self.use_supabase:
            try:
                result = self.supabase_client.table("conversations").select("*").eq("id", conversation_id).execute()
                if result.data and len(result.data) > 0:
                    data = result.data[0]
                    data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    # Provide default for language if not in table
                    if "language" not in data:
                        data["language"] = "en"
                    return Conversation(**data)
                return None
            except Exception as e:
                print(f"[ERROR] Failed to get conversation from Supabase: {e}")
                return None
        
        if self.use_azure:
            data = self._load_from_blob(self.conversations_container, conversation_id)
            if data and "_metadata" in data:
                del data["_metadata"]

            if data:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                return Conversation(**data)
            return None
        
        # In-memory fallback
        data = self._memory_store["conversations"].get(conversation_id)
        if data:
            return Conversation(**data)
        return None

    def update_conversation(self, conversation: Conversation):
        """Update conversation metadata."""
        if self.use_supabase:
            try:
                self.supabase_client.table("conversations").update({
                    "title": conversation.title,
                    "message_count": conversation.message_count,
                    "total_response_time_ms": conversation.total_response_time_ms,
                    "average_response_time_ms": conversation.average_response_time_ms,
                    "total_queries": conversation.total_queries,
                    "is_active": conversation.is_active,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", conversation.id).execute()
                return
            except Exception as e:
                print(f"[ERROR] Failed to update conversation in Supabase: {e}")
                raise
        
        if self.use_azure:
            self._save_to_blob(self.conversations_container, conversation.id, conversation.dict())
            return
        
        # In-memory fallback
        self._memory_store["conversations"][conversation.id] = conversation.dict()

    def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List recent conversations."""
        if self.use_supabase:
            try:
                result = self.supabase_client.table("conversations").select("*").order("updated_at", desc=True).limit(limit).execute()
                conversations = []
                for data in result.data:
                    data["created_at"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    # Provide default for language if not in table
                    if "language" not in data:
                        data["language"] = "en"
                    conversations.append(Conversation(**data))
                return conversations
            except Exception as e:
                print(f"[ERROR] Failed to list conversations from Supabase: {e}")
                return []
        
        if self.use_azure:
            blob_names = self._list_blobs(self.conversations_container)
            conversations = []
            for blob_name in blob_names[-limit:]:
                conversation_id = blob_name.replace(f"{self.conversations_container}/", "").replace(".json", "")
                conversation = self.get_conversation(conversation_id)
                if conversation:
                    conversations.append(conversation)
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            return conversations
        
        # In-memory fallback
        convs = list(self._memory_store["conversations"].values())
        convs.sort(key=lambda x: x.get("updated_at", datetime.min), reverse=True)
        return [Conversation(**c) for c in convs[:limit]]

    # Message Management
    def add_message(self, message: ConversationMessage):
        """Add a message to a conversation."""
        if self.use_supabase:
            try:
                # Build insert data - messages table uses created_at instead of timestamp
                insert_data = {
                    "id": message.id,
                    "conversation_id": message.conversation_id,
                    "role": message.role,
                    "content": message.content,
                    "sources": message.sources if message.sources else [],
                    "response_time_ms": message.response_time_ms,
                    "created_at": message.timestamp.isoformat()  # Use created_at column
                }
                
                self.supabase_client.table("messages").insert(insert_data).execute()
                
                # Update conversation stats
                conversation = self.get_conversation(message.conversation_id)
                if conversation:
                    conversation.message_count += 1
                    conversation.updated_at = datetime.utcnow()
                    if message.role == "user":
                        conversation.total_queries += 1
                    if message.response_time_ms and message.response_time_ms > 0:
                        conversation.total_response_time_ms += message.response_time_ms
                        conversation.average_response_time_ms = (
                            conversation.total_response_time_ms / conversation.total_queries
                            if conversation.total_queries > 0 else 0
                        )
                    self.update_conversation(conversation)
                return
            except Exception as e:
                print(f"[ERROR] Failed to add message to Supabase: {e}")
                raise
        
        if self.use_azure:
            message_blob_id = f"{message.conversation_id}-{message.id}"
            self._save_to_blob(self.messages_container, message_blob_id, message.dict())

            conversation = self.get_conversation(message.conversation_id)
            if conversation:
                conversation.message_count += 1
                conversation.updated_at = datetime.utcnow()
                conversation.total_queries += 1 if message.role == "user" else 0

                if message.response_time_ms and message.response_time_ms > 0:
                    conversation.total_response_time_ms += message.response_time_ms
                    conversation.average_response_time_ms = (
                        conversation.total_response_time_ms / conversation.total_queries
                        if conversation.total_queries > 0 else 0
                    )
                self.update_conversation(conversation)
            return
        
        # In-memory fallback
        self._memory_store["messages"][message.id] = message.dict()

    def get_conversation_messages(self, conversation_id: str) -> List[ConversationMessage]:
        """Get all messages for a conversation."""
        if self.use_supabase:
            try:
                result = self.supabase_client.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at").execute()
                messages = []
                for data in result.data:
                    # Map created_at to timestamp for the model
                    data["timestamp"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    if "created_at" in data:
                        del data["created_at"]
                    messages.append(ConversationMessage(**data))
                return messages
            except Exception as e:
                print(f"[ERROR] Failed to get messages from Supabase: {e}")
                return []
        
        if self.use_azure:
            prefix = f"{self.messages_container}/{conversation_id}-"
            blob_names = self._list_blobs(self.messages_container, prefix)

            messages = []
            if not blob_names:
                blob_names = self._list_blobs(self.messages_container, "")

            for blob_name in blob_names:
                message_blob_id = blob_name.replace(f"{self.messages_container}/", "").replace(".json", "")
                data = self._load_from_blob(self.messages_container, message_blob_id)

                if data and "_metadata" in data:
                    del data["_metadata"]

                if data:
                    if isinstance(data.get("timestamp"), str):
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    if data.get("conversation_id") == conversation_id:
                        messages.append(ConversationMessage(**data))

            messages.sort(key=lambda x: x.timestamp)
            return messages
        
        # In-memory fallback
        msgs = [m for m in self._memory_store["messages"].values() if m.get("conversation_id") == conversation_id]
        return [ConversationMessage(**m) for m in sorted(msgs, key=lambda x: x.get("timestamp", datetime.min))]

    # Rating System
    def add_rating(self, rating: ChatRating):
        """Add a rating for a message."""
        if self.use_supabase:
            try:
                self.supabase_client.table("ratings").insert({
                    "id": rating.id,
                    "message_id": rating.message_id,
                    "conversation_id": rating.conversation_id,
                    "rating": rating.rating,
                    "created_at": rating.timestamp.isoformat()  # Use created_at column
                }).execute()
                return
            except Exception as e:
                print(f"[ERROR] Failed to add rating to Supabase: {e}")
                raise
        
        if self.use_azure:
            self._save_to_blob(self.ratings_container, rating.id, rating.dict())
            return
        
        # In-memory fallback
        self._memory_store["ratings"][rating.id] = rating.dict()

    def get_message_ratings(self, message_id: str) -> List[ChatRating]:
        """Get all ratings for a message."""
        if self.use_supabase:
            try:
                result = self.supabase_client.table("ratings").select("*").eq("message_id", message_id).execute()
                ratings = []
                for data in result.data:
                    # Map created_at to timestamp for the model
                    data["timestamp"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    if "created_at" in data:
                        del data["created_at"]
                    ratings.append(ChatRating(**data))
                return ratings
            except Exception as e:
                print(f"[ERROR] Failed to get ratings from Supabase: {e}")
                return []
        
        if self.use_azure:
            prefix = f"{self.ratings_container}/{message_id}-"
            blob_names = self._list_blobs(self.ratings_container, prefix)

            ratings = []
            for blob_name in blob_names:
                rating_id = blob_name.replace(f"{self.ratings_container}/", "").replace(".json", "")
                data = self._load_from_blob(self.ratings_container, rating_id)

                if data and "_metadata" in data:
                    del data["_metadata"]

                if data:
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    ratings.append(ChatRating(**data))

            return ratings
        
        # In-memory fallback
        return [ChatRating(**r) for r in self._memory_store["ratings"].values() if r.get("message_id") == message_id]

    def get_average_rating(self, conversation_id: Optional[str] = None, days: int = 30) -> float:
        """Get average rating, optionally filtered by conversation or time."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        if self.use_supabase:
            try:
                query = self.supabase_client.table("ratings").select("rating, created_at, conversation_id")
                if conversation_id:
                    query = query.eq("conversation_id", conversation_id)
                result = query.execute()
                
                ratings = []
                for data in result.data:
                    timestamp = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    if timestamp >= cutoff_date:
                        ratings.append(data["rating"])
                
                return sum(ratings) / len(ratings) if ratings else 0.0
            except Exception as e:
                print(f"[ERROR] Failed to get average rating from Supabase: {e}")
                return 0.0
        
        if self.use_azure:
            blob_names = self._list_blobs(self.ratings_container)
            ratings = []

            for blob_name in blob_names:
                rating_id = blob_name.replace(f"{self.ratings_container}/", "").replace(".json", "")
                data = self._load_from_blob(self.ratings_container, rating_id)

                if data and "_metadata" in data:
                    del data["_metadata"]

                if data:
                    rating_timestamp = datetime.fromisoformat(data["timestamp"])

                    if rating_timestamp >= cutoff_date:
                        if conversation_id is None or data["conversation_id"] == conversation_id:
                            ratings.append(data["rating"])

            return sum(ratings) / len(ratings) if ratings else 0.0
        
        # In-memory fallback
        ratings = [r["rating"] for r in self._memory_store["ratings"].values() 
                   if (conversation_id is None or r.get("conversation_id") == conversation_id)]
        return sum(ratings) / len(ratings) if ratings else 0.0

    # Feedback System
    def add_feedback(self, feedback: ChatFeedback):
        """Add detailed feedback for a message."""
        if self.use_supabase:
            try:
                self.supabase_client.table("feedback").insert({
                    "id": feedback.id,
                    "message_id": feedback.message_id,
                    "conversation_id": feedback.conversation_id,
                    "feedback_type": feedback.feedback_type,
                    "comment": feedback.comment,
                    "created_at": feedback.timestamp.isoformat()  # Use created_at column
                }).execute()
                return
            except Exception as e:
                print(f"[ERROR] Failed to add feedback to Supabase: {e}")
                raise
        
        if self.use_azure:
            self._save_to_blob(self.feedback_container, feedback.id, feedback.dict())
            return
        
        # In-memory fallback
        self._memory_store["feedback"][feedback.id] = feedback.dict()

    def get_message_feedback(self, message_id: str) -> List[ChatFeedback]:
        """Get all feedback for a message."""
        if self.use_supabase:
            try:
                result = self.supabase_client.table("feedback").select("*").eq("message_id", message_id).execute()
                feedback_list = []
                for data in result.data:
                    # Map created_at to timestamp for the model
                    data["timestamp"] = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                    if "created_at" in data:
                        del data["created_at"]
                    feedback_list.append(ChatFeedback(**data))
                return feedback_list
            except Exception as e:
                print(f"[ERROR] Failed to get feedback from Supabase: {e}")
                return []
        
        if self.use_azure:
            prefix = f"{self.feedback_container}/{message_id}-"
            blob_names = self._list_blobs(self.feedback_container, prefix)

            feedback_list = []
            for blob_name in blob_names:
                feedback_id = blob_name.replace(f"{self.feedback_container}/", "").replace(".json", "")
                data = self._load_from_blob(self.feedback_container, feedback_id)

                if data and "_metadata" in data:
                    del data["_metadata"]

                if data:
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    feedback_list.append(ChatFeedback(**data))

            return feedback_list
        
        # In-memory fallback
        return [ChatFeedback(**f) for f in self._memory_store["feedback"].values() if f.get("message_id") == message_id]

    # Analytics
    def get_chat_analytics(self, days: int = 30) -> ChatAnalyticsSummary:
        """Get comprehensive chat analytics."""
        conversations = self.list_conversations(limit=1000)
        total_messages = 0
        total_response_time = 0
        ratings = []

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_conversations = [c for c in conversations if c.updated_at >= cutoff_date]

        for conv in recent_conversations:
            total_messages += conv.message_count
            total_response_time += conv.total_response_time_ms

            messages = self.get_conversation_messages(conv.id)
            for message in messages:
                message_ratings = self.get_message_ratings(message.id)
                ratings.extend([r.rating for r in message_ratings])

        avg_conversation_length = (
            total_messages / len(recent_conversations)
            if recent_conversations else 0
        )

        avg_response_time = (
            total_response_time / total_messages
            if total_messages > 0 else 0
        )

        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return ChatAnalyticsSummary(
            total_conversations=len(recent_conversations),
            total_messages=total_messages,
            average_conversation_length=avg_conversation_length,
            average_response_time_ms=avg_response_time,
            average_rating=avg_rating,
            total_ratings=len(ratings),
            top_rated_conversations=[],
            most_helpful_topics=[]
        )


# Global instance
conversation_service = ConversationService()
