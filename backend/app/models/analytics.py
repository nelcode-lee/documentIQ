"""Analytics data models."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class QueryAnalytics(BaseModel):
    """Analytics for a single query."""
    query_id: str
    query_text: str
    timestamp: datetime
    response_time_ms: float
    sources_used: List[str]  # Document titles
    conversation_id: Optional[str] = None


class DocumentAnalytics(BaseModel):
    """Analytics for document usage."""
    document_id: str
    title: str
    query_count: int
    last_accessed: Optional[str] = None  # ISO format string
    total_chunks_retrieved: int = 0


class AnalyticsSummary(BaseModel):
    """Summary analytics data."""
    query_volume: Dict[str, int]  # daily, weekly, monthly
    top_queries: List[Dict[str, Any]]  # Most frequent queries
    top_documents: List[DocumentAnalytics]
    average_response_time: float
    total_queries: int
    time_range: Dict[str, str]  # start and end dates as ISO strings
    
    class Config:
        # Allow alias for JSON serialization (snake_case to camelCase)
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "query_volume": {"daily": 10, "weekly": 50, "monthly": 200, "total": 500},
                "top_queries": [],
                "top_documents": [],
                "average_response_time": 1200.5,
                "total_queries": 500,
                "time_range": {"start": "2024-01-01T00:00:00", "end": "2024-01-31T23:59:59"}
            }
        }


class DailyMetrics(BaseModel):
    """Daily metrics breakdown."""
    date: str
    query_count: int
    unique_conversations: int
    average_response_time: float
    documents_accessed: List[str]
