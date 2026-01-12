"""Chat-related data models."""

from pydantic import BaseModel
from typing import Optional, List


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
