"""Conversation service for storing and managing chat conversations."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient
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
        """Initialize conversation service with Azure Blob Storage."""
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self.conversations_container = "conversations"
        self.messages_container = "conversation-messages"
        self.ratings_container = "conversation-ratings"
        self.feedback_container = "conversation-feedback"

        # Ensure containers exist
        self._ensure_containers()

    def _ensure_containers(self):
        """Ensure required blob containers exist."""
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

        conversation = Conversation(
            id=conversation_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            message_count=0,
            language=language,
            total_response_time_ms=0.0,
            average_response_time_ms=0.0,
            total_queries=0,
            is_active=True
        )

        self._save_to_blob(self.conversations_container, conversation_id, conversation.dict())
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        data = self._load_from_blob(self.conversations_container, conversation_id)
        if data and "_metadata" in data:
            del data["_metadata"]  # Remove metadata before converting

        if data:
            # Convert string dates back to datetime
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            return Conversation(**data)
        return None

    def update_conversation(self, conversation: Conversation):
        """Update conversation metadata."""
        self._save_to_blob(self.conversations_container, conversation.id, conversation.dict())

    def list_conversations(self, limit: int = 50) -> List[Conversation]:
        """List recent conversations."""
        blob_names = self._list_blobs(self.conversations_container)

        conversations = []
        for blob_name in blob_names[-limit:]:  # Get most recent
            conversation_id = blob_name.replace(f"{self.conversations_container}/", "").replace(".json", "")
            conversation = self.get_conversation(conversation_id)
            if conversation:
                conversations.append(conversation)

        # Sort by updated_at descending
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        return conversations

    # Message Management
    def add_message(self, message: ConversationMessage):
        """Add a message to a conversation."""
        # Store message with conversation_id prefix for easier retrieval
        message_blob_id = f"{message.conversation_id}-{message.id}"
        self._save_to_blob(self.messages_container, message_blob_id, message.dict())

        # Update conversation metadata
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
                print(f"[ANALYTICS] Updated conversation {conversation.id}: total_time={conversation.total_response_time_ms:.2f}ms, avg_time={conversation.average_response_time_ms:.2f}ms, queries={conversation.total_queries}")

            self.update_conversation(conversation)

    def get_conversation_messages(self, conversation_id: str) -> List[ConversationMessage]:
        """Get all messages for a conversation."""
        prefix = f"{self.messages_container}/{conversation_id}-"
        blob_names = self._list_blobs(self.messages_container, prefix)

        messages = []
        # Fallback for legacy messages saved without conversation_id prefix
        if not blob_names:
            # List all blobs in the container (no prefix) and filter by conversation_id
            blob_names = self._list_blobs(self.messages_container, "")

        for blob_name in blob_names:
            # Extract message blob ID (conversation_id-message_id or legacy message_id)
            message_blob_id = blob_name.replace(f"{self.messages_container}/", "").replace(".json", "")
            data = self._load_from_blob(self.messages_container, message_blob_id)

            if data and "_metadata" in data:
                del data["_metadata"]

            if data:
                # Convert timestamp back to datetime
                if isinstance(data.get("timestamp"), str):
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                # Ensure conversation_id matches (safety check)
                if data.get("conversation_id") == conversation_id:
                    messages.append(ConversationMessage(**data))

        # If no messages were found using prefix, but we had blobs, try a full scan once
        if not messages and blob_names:
            all_blob_names = self._list_blobs(self.messages_container, "")
            for blob_name in all_blob_names:
                message_blob_id = blob_name.replace(f"{self.messages_container}/", "").replace(".json", "")
                data = self._load_from_blob(self.messages_container, message_blob_id)
                if data and "_metadata" in data:
                    del data["_metadata"]
                if data:
                    if isinstance(data.get("timestamp"), str):
                        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    if data.get("conversation_id") == conversation_id:
                        messages.append(ConversationMessage(**data))

        # Sort by timestamp
        messages.sort(key=lambda x: x.timestamp)
        return messages

    # Rating System
    def add_rating(self, rating: ChatRating):
        """Add a rating for a message."""
        self._save_to_blob(self.ratings_container, rating.id, rating.dict())

    def get_message_ratings(self, message_id: str) -> List[ChatRating]:
        """Get all ratings for a message."""
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

    def get_average_rating(self, conversation_id: Optional[str] = None, days: int = 30) -> float:
        """Get average rating, optionally filtered by conversation or time."""
        blob_names = self._list_blobs(self.ratings_container)
        ratings = []

        cutoff_date = datetime.utcnow() - timedelta(days=days)

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

    # Feedback System
    def add_feedback(self, feedback: ChatFeedback):
        """Add detailed feedback for a message."""
        self._save_to_blob(self.feedback_container, feedback.id, feedback.dict())

    def get_message_feedback(self, message_id: str) -> List[ChatFeedback]:
        """Get all feedback for a message."""
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

    # Analytics
    def get_chat_analytics(self, days: int = 30) -> ChatAnalyticsSummary:
        """Get comprehensive chat analytics."""
        conversations = self.list_conversations(limit=1000)
        total_messages = 0
        total_response_time = 0
        ratings = []

        # Filter by time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_conversations = [c for c in conversations if c.updated_at >= cutoff_date]

        for conv in recent_conversations:
            total_messages += conv.message_count
            total_response_time += conv.total_response_time_ms

            # Get ratings for this conversation
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
            top_rated_conversations=[],  # TODO: Implement
            most_helpful_topics=[]  # TODO: Implement
        )


# Global instance
conversation_service = ConversationService()