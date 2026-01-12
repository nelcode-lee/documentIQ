"""Analytics API endpoints."""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.analytics import AnalyticsService
from app.models.analytics import AnalyticsSummary, DailyMetrics

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back")
) -> AnalyticsSummary:
    """
    Get comprehensive analytics summary.
    
    Args:
        days: Number of days to look back (1-365)
        
    Returns:
        AnalyticsSummary with query volume, top queries, top documents, etc.
    """
    try:
        return analytics_service.get_analytics_summary(days=days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving analytics summary: {str(e)}"
        )


@router.get("/query-volume")
async def get_query_volume(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get query volume metrics.
    
    Returns:
        Dictionary with daily, weekly, monthly, and total query counts
    """
    try:
        return analytics_service.get_query_volume(days=days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving query volume: {str(e)}"
        )


@router.get("/top-queries")
async def get_top_queries(
    limit: int = Query(default=10, ge=1, le=50, description="Number of top queries to return"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get most frequent queries.
    
    Returns:
        List of top queries with counts and average response times
    """
    try:
        return analytics_service.get_top_queries(limit=limit, days=days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving top queries: {str(e)}"
        )


@router.get("/top-documents")
async def get_top_documents(
    limit: int = Query(default=10, ge=1, le=50, description="Number of top documents to return"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get most accessed documents.
    
    Returns:
        List of top documents with access counts
    """
    try:
        return analytics_service.get_top_documents(limit=limit, days=days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving top documents: {str(e)}"
        )


@router.get("/response-time")
async def get_average_response_time(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get average response time.
    
    Returns:
        Average response time in milliseconds
    """
    try:
        avg_time = analytics_service.get_average_response_time(days=days)
        return {"average_response_time_ms": avg_time}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving response time: {str(e)}"
        )


@router.get("/daily-metrics")
async def get_daily_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back")
) -> List[DailyMetrics]:
    """
    Get daily metrics breakdown.
    
    Returns:
        List of daily metrics for the specified period
    """
    try:
        return analytics_service.get_daily_metrics(days=days)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving daily metrics: {str(e)}"
        )
