"""Analytics service for tracking usage metrics."""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from app.models.analytics import (
    QueryAnalytics,
    DocumentAnalytics,
    AnalyticsSummary,
    DailyMetrics
)
import uuid


class AnalyticsService:
    """Service to track and analyze usage metrics."""
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalyticsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize analytics storage."""
        if self._initialized:
            return
        
        # In-memory storage (can be replaced with database later)
        self.queries: List[QueryAnalytics] = []
        self.document_access: Dict[str, int] = defaultdict(int)  # document_id -> count
        self.document_last_access: Dict[str, datetime] = {}  # document_id -> last access time
        self.document_chunks_retrieved: Dict[str, int] = defaultdict(int)  # document_id -> chunks
        self._initialized = True
        
    def track_query(
        self,
        query_text: str,
        response_time_ms: float,
        sources_used: List[str],
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Track a query event.
        
        Args:
            query_text: The user's query
            response_time_ms: Response time in milliseconds
            sources_used: List of document titles used in response
            conversation_id: Optional conversation ID
            
        Returns:
            Query ID
        """
        query_id = str(uuid.uuid4())
        
        query_analytics = QueryAnalytics(
            query_id=query_id,
            query_text=query_text,
            timestamp=datetime.utcnow(),
            response_time_ms=response_time_ms,
            sources_used=sources_used,
            conversation_id=conversation_id
        )
        
        self.queries.append(query_analytics)
        
        # Track document access
        for source in sources_used:
            # Try to find document ID from source (could be title or ID)
            # For now, we'll track by title
            self.document_access[source] += 1
            self.document_last_access[source] = datetime.utcnow()
            # Increment chunks retrieved (assuming 1 chunk per document per query)
            self.document_chunks_retrieved[source] += 1
        
        return query_id
    
    def get_query_volume(
        self,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get query volume for different time periods.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with daily, weekly, monthly counts
        """
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=days)
        
        # Filter queries within time range
        recent_queries = [
            q for q in self.queries
            if q.timestamp >= cutoff_date
        ]
        
        # Daily (last 7 days)
        daily_cutoff = now - timedelta(days=7)
        daily_queries = [q for q in recent_queries if q.timestamp >= daily_cutoff]
        
        # Weekly (last 30 days, grouped by week)
        weekly_cutoff = now - timedelta(days=30)
        weekly_queries = [q for q in recent_queries if q.timestamp >= weekly_cutoff]
        
        # Monthly (all in range)
        monthly_queries = recent_queries
        
        return {
            "daily": len([q for q in daily_queries if q.timestamp.date() == now.date()]),
            "weekly": len(weekly_queries),
            "monthly": len(monthly_queries),
            "total": len(self.queries)
        }
    
    def get_top_queries(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get most frequent queries.
        
        Args:
            limit: Number of top queries to return
            days: Number of days to look back
            
        Returns:
            List of query dictionaries with count
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_queries = [
            q.query_text for q in self.queries
            if q.timestamp >= cutoff_date
        ]
        
        # Count query frequency
        query_counts = Counter(recent_queries)
        
        # Return top queries
        top_queries = []
        for query_text, count in query_counts.most_common(limit):
            # Get average response time for this query
            query_times = [
                q.response_time_ms for q in self.queries
                if q.query_text == query_text and q.timestamp >= cutoff_date
            ]
            avg_time = sum(query_times) / len(query_times) if query_times else 0
            
            top_queries.append({
                "query": query_text,
                "count": count,
                "average_response_time_ms": round(avg_time, 2)
            })
        
        return top_queries
    
    def get_top_documents(
        self,
        limit: int = 10,
        days: int = 30
    ) -> List[DocumentAnalytics]:
        """
        Get most accessed documents.
        
        Args:
            limit: Number of top documents to return
            days: Number of days to look back
            
        Returns:
            List of DocumentAnalytics objects
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter queries in time range and extract document access
        document_access_counts = defaultdict(int)
        document_last_access = {}
        document_chunks = defaultdict(int)
        
        for query in self.queries:
            if query.timestamp >= cutoff_date:
                for source in query.sources_used:
                    document_access_counts[source] += 1
                    if source not in document_last_access or query.timestamp > document_last_access[source]:
                        document_last_access[source] = query.timestamp
                    document_chunks[source] += 1
        
        # Create DocumentAnalytics objects
        top_documents = []
        for doc_title, count in sorted(
            document_access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]:
            last_accessed_dt = document_last_access.get(doc_title)
            doc_analytics = DocumentAnalytics(
                document_id=doc_title,  # Using title as ID for now
                title=doc_title,
                query_count=count,
                last_accessed=last_accessed_dt.isoformat() if last_accessed_dt else None,
                total_chunks_retrieved=document_chunks.get(doc_title, 0)
            )
            top_documents.append(doc_analytics)
        
        return top_documents
    
    def get_average_response_time(
        self,
        days: int = 30
    ) -> float:
        """
        Get average response time.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Average response time in milliseconds
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_queries = [
            q for q in self.queries
            if q.timestamp >= cutoff_date
        ]
        
        if not recent_queries:
            return 0.0
        
        total_time = sum(q.response_time_ms for q in recent_queries)
        return round(total_time / len(recent_queries), 2)
    
    def get_daily_metrics(
        self,
        days: int = 30
    ) -> List[DailyMetrics]:
        """
        Get daily metrics breakdown.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of DailyMetrics objects
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_queries = [
            q for q in self.queries
            if q.timestamp >= cutoff_date
        ]
        
        # Group by date
        daily_data = defaultdict(lambda: {
            "queries": [],
            "conversations": set(),
            "documents": set()
        })
        
        for query in recent_queries:
            date_key = query.timestamp.date().isoformat()
            daily_data[date_key]["queries"].append(query)
            if query.conversation_id:
                daily_data[date_key]["conversations"].add(query.conversation_id)
            daily_data[date_key]["documents"].update(query.sources_used)
        
        # Convert to DailyMetrics
        daily_metrics = []
        for date_str in sorted(daily_data.keys()):
            data = daily_data[date_str]
            queries = data["queries"]
            
            avg_response_time = (
                sum(q.response_time_ms for q in queries) / len(queries)
                if queries else 0
            )
            
            metrics = DailyMetrics(
                date=date_str,
                query_count=len(queries),
                unique_conversations=len(data["conversations"]),
                average_response_time=round(avg_response_time, 2),
                documents_accessed=list(data["documents"])
            )
            daily_metrics.append(metrics)
        
        return daily_metrics
    
    def get_analytics_summary(
        self,
        days: int = 30
    ) -> AnalyticsSummary:
        """
        Get comprehensive analytics summary.
        
        Args:
            days: Number of days to look back
            
        Returns:
            AnalyticsSummary object
        """
        query_volume = self.get_query_volume(days)
        top_queries = self.get_top_queries(limit=10, days=days)
        top_documents = self.get_top_documents(limit=10, days=days)
        avg_response_time = self.get_average_response_time(days)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return AnalyticsSummary(
            query_volume=query_volume,
            top_queries=top_queries,
            top_documents=top_documents,
            average_response_time=avg_response_time,
            total_queries=query_volume.get("total", 0),
            time_range={
                "start": cutoff_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        )
