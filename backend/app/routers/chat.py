"""Chat API endpoints."""

from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.analytics import AnalyticsService
from app.services.cache_service import cache_service
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
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
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
