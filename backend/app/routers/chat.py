"""Chat API endpoints."""

from fastapi import APIRouter, HTTPException
from app.models.chat import (
    ChatRequest, ChatResponse, Conversation, ConversationMessage,
    QuickRatingRequest, DetailedFeedbackRequest, ChatRating, ChatFeedback
)
from app.services.chat_service import ChatService
from app.services.analytics import AnalyticsService
from app.services.conversation_service import conversation_service
from app.services.cache_service import cache_service
from typing import List
from datetime import datetime
import uuid
import time

router = APIRouter()
chat_service = ChatService()
analytics_service = AnalyticsService()


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle chat queries with RAG.

    Uses OpenAI API for embeddings and chat completions,
    and Azure AI Search for vector storage and retrieval.
    """
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or conversation_service.create_conversation(
            title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            language=request.language or "en"
        )

        # Ensure conversation exists
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            conversation_id = conversation_service.create_conversation(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                language=request.language or "en"
            )

        # Track start time for analytics
        start_time = time.time()

        # Get response from chat service
        selected_language = request.language or "en"
        print(f"[DEBUG] Chat request - Language: {selected_language}, Message: {request.message[:50]}...")

        result = await chat_service.chat(
            query=request.message,
            conversation_id=conversation_id,
            language=selected_language
        )

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        print(f"[ANALYTICS] Response time: {response_time_ms:.2f}ms for query: {request.message[:50]}...")

        # Save user message to conversation
        user_message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        conversation_service.add_message(user_message)

        # Save assistant message to conversation
        assistant_message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"],
            timestamp=datetime.utcnow(),
            sources=result["sources"],
            response_time_ms=response_time_ms
        )
        conversation_service.add_message(assistant_message)

        # Track query in analytics
        analytics_service.track_query(
            query_text=request.message,
            response_time_ms=response_time_ms,
            sources_used=result["sources"],
            conversation_id=conversation_id
        )

        response = ChatResponse(
            response=result["response"],
            sources=result["sources"],
            conversation_id=result["conversation_id"]
        )

        return response
    except Exception as e:
        import traceback
        error_details = str(e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {error_details}"
        )


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics.
    
    Returns cache hit rate, backend type, and usage statistics.
    """
    try:
        stats = cache_service.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving cache stats: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear all cached data.

    Use with caution - this will invalidate all cached queries and embeddings.
    """
    try:
        success = cache_service.clear()
        return {
            "status": "success" if success else "failed",
            "message": "Cache cleared successfully" if success else "Failed to clear cache"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


# Conversation Management Endpoints
@router.get("/conversations", response_model=List[Conversation])
async def list_conversations(limit: int = 20):
    """List recent conversations."""
    try:
        conversations = conversation_service.list_conversations(limit=limit)
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Get a specific conversation."""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[ConversationMessage])
async def get_conversation_messages(conversation_id: str):
    """Get messages for a conversation."""
    try:
        messages = conversation_service.get_conversation_messages(conversation_id)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting conversation messages: {str(e)}"
        )


# Rating and Feedback Endpoints
@router.post("/rating/quick")
async def submit_quick_rating(request: QuickRatingRequest):
    """Submit a quick 1-5 star rating for a message."""
    try:
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        rating = ChatRating(
            id=str(uuid.uuid4()),
            message_id=request.message_id,
            conversation_id=request.conversation_id,
            rating=request.rating,
            feedback=request.feedback,
            timestamp=datetime.utcnow()
        )

        conversation_service.add_rating(rating)

        return {
            "status": "success",
            "message": "Rating submitted successfully",
            "rating_id": rating.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting rating: {str(e)}"
        )


@router.post("/feedback/detailed")
async def submit_detailed_feedback(request: DetailedFeedbackRequest):
    """Submit detailed feedback for a message."""
    try:
        # Validate ratings are between 1-5
        ratings = [
            request.helpfulness_rating,
            request.accuracy_rating,
            request.clarity_rating,
            request.completeness_rating
        ]

        if not all(1 <= rating <= 5 for rating in ratings):
            raise HTTPException(status_code=400, detail="All ratings must be between 1 and 5")

        feedback = ChatFeedback(
            id=str(uuid.uuid4()),
            message_id=request.message_id,
            conversation_id=request.conversation_id,
            helpfulness_rating=request.helpfulness_rating,
            accuracy_rating=request.accuracy_rating,
            clarity_rating=request.clarity_rating,
            completeness_rating=request.completeness_rating,
            additional_feedback=request.additional_feedback,
            timestamp=datetime.utcnow()
        )

        conversation_service.add_feedback(feedback)

        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/analytics/chat")
async def get_chat_analytics(days: int = 30):
    """Get chat analytics summary."""
    try:
        analytics = conversation_service.get_chat_analytics(days=days)
        return analytics.dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting chat analytics: {str(e)}"
        )
