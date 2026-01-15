"""Chat-related data models."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = "en"  # Language code: "en", "pl", "ro"


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    sources: List[str] = []
    conversation_id: str


class ConversationMessage(BaseModel):
    """Model for individual chat messages."""
    id: str
    conversation_id: str
    role: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[str]] = None
    response_time_ms: Optional[float] = None


class Conversation(BaseModel):
    """Model for chat conversations."""
    id: str
    user_id: Optional[str] = None  # For future user auth
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    language: str
    total_response_time_ms: float
    average_response_time_ms: float
    total_queries: int
    is_active: bool = True


class ChatRating(BaseModel):
    """Model for chat message ratings."""
    id: str
    message_id: str
    conversation_id: str
    rating: int  # 1-5 stars
    feedback: Optional[str] = None
    timestamp: datetime
    user_id: Optional[str] = None  # For future user auth


class ChatFeedback(BaseModel):
    """Model for detailed chat feedback."""
    id: str
    message_id: str
    conversation_id: str
    helpfulness_rating: int  # 1-5 (very unhelpful to very helpful)
    accuracy_rating: int  # 1-5 (very inaccurate to very accurate)
    clarity_rating: int  # 1-5 (very unclear to very clear)
    completeness_rating: int  # 1-5 (very incomplete to very complete)
    additional_feedback: Optional[str] = None
    timestamp: datetime
    user_id: Optional[str] = None  # For future user auth


class ChatAnalyticsSummary(BaseModel):
    """Summary of chat analytics."""
    total_conversations: int
    total_messages: int
    average_conversation_length: float
    average_response_time_ms: float
    average_rating: Optional[float] = None
    total_ratings: int
    top_rated_conversations: List[dict]
    most_helpful_topics: List[dict]


class QuickRatingRequest(BaseModel):
    """Request model for quick 1-5 star rating."""
    message_id: str
    conversation_id: str
    rating: int  # 1-5 stars
    feedback: Optional[str] = None


class DetailedFeedbackRequest(BaseModel):
    """Request model for detailed feedback."""
    message_id: str
    conversation_id: str
    helpfulness_rating: int
    accuracy_rating: int
    clarity_rating: int
    completeness_rating: int
    additional_feedback: Optional[str] = None
