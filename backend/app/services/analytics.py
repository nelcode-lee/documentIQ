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
from app.services.conversation_service import conversation_service
from app.services.cache_service import cache_service
import uuid
import time


class AnalyticsService:
    """Service to track and analyze usage metrics with blob storage persistence."""

    # Singleton instance
    _instance = None
    
    # Cache TTL in seconds (60 seconds = analytics refresh every minute max)
    CACHE_TTL = 60

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalyticsService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize analytics storage."""
        if self._initialized:
            return

        # Analytics data is now stored in blob storage via conversation_service
        # Keep some in-memory caches for performance
        self._query_cache: List[QueryAnalytics] = []
        self._cache_size_limit = 1000  # Keep last 1000 queries in memory
        self._analytics_cache: Dict[str, Any] = {}  # In-memory analytics cache
        self._cache_timestamps: Dict[str, float] = {}  # Cache timestamps
        self._initialized = True
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached analytics data if still valid."""
        if key in self._analytics_cache and key in self._cache_timestamps:
            if time.time() - self._cache_timestamps[key] < self.CACHE_TTL:
                return self._analytics_cache[key]
        return None
    
    def _set_cached(self, key: str, value: Any):
        """Cache analytics data."""
        self._analytics_cache[key] = value
        self._cache_timestamps[key] = time.time()
    
    def _get_conversations_cached(self, days: int) -> tuple:
        """Get conversations with caching - returns (all_conversations, recent_conversations)."""
        cache_key = f"conversations_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        conversations = conversation_service.list_conversations(limit=1000)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent = [c for c in conversations if c.updated_at >= cutoff_date]
        
        result = (conversations, recent, cutoff_date)
        self._set_cached(cache_key, result)
        return result
        
    def track_query(
        self,
        query_text: str,
        response_time_ms: float,
        sources_used: List[str],
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Track a query event.

        Note: Analytics are now stored via conversation service in blob storage.
        This method is kept for backward compatibility but primary tracking
        is now done in the chat endpoint with conversation persistence.

        Args:
            query_text: The user's query
            response_time_ms: Response time in milliseconds
            sources_used: List of document titles used in response
            conversation_id: Optional conversation ID

        Returns:
            Query ID
        """
        query_id = str(uuid.uuid4())

        # Keep in-memory cache for backward compatibility
        query_analytics = QueryAnalytics(
            query_id=query_id,
            query_text=query_text,
            timestamp=datetime.utcnow(),
            response_time_ms=response_time_ms,
            sources_used=sources_used,
            conversation_id=conversation_id
        )

        # Maintain cache with size limit
        self._query_cache.append(query_analytics)
        if len(self._query_cache) > self._cache_size_limit:
            self._query_cache.pop(0)  # Remove oldest

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
        # Check cache first
        cache_key = f"query_volume_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        now = datetime.utcnow()
        conversations, recent_conversations, cutoff_date = self._get_conversations_cached(days)

        # Calculate query volume from conversations
        total_queries = sum(c.total_queries for c in conversations)
        recent_queries_total = sum(c.total_queries for c in recent_conversations)

        # Daily (today)
        today_conversations = [
            c for c in recent_conversations
            if c.updated_at.date() == now.date()
        ]
        daily_queries = sum(c.total_queries for c in today_conversations)

        # Weekly (last 7 days)
        weekly_cutoff = now - timedelta(days=7)
        weekly_conversations = [
            c for c in conversations
            if c.updated_at >= weekly_cutoff
        ]
        weekly_queries = sum(c.total_queries for c in weekly_conversations)

        # Monthly (all in range)
        monthly_queries = recent_queries_total

        result = {
            "daily": daily_queries,
            "weekly": weekly_queries,
            "monthly": monthly_queries,
            "total": total_queries
        }
        self._set_cached(cache_key, result)
        return result
    
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
        # Check cache first (use max limit for cache key to reuse for smaller limits)
        cache_key = f"top_queries_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached[:limit]  # Return only requested limit
        
        from collections import Counter

        # Get conversations and messages from blob storage
        conversations, recent_conversations, cutoff_date = self._get_conversations_cached(days)
        
        print(f"[ANALYTICS] get_top_queries: Found {len(conversations)} conversations, cutoff_date={cutoff_date}")

        # Collect query texts and response times
        query_data = {}
        total_messages_found = 0
        total_user_messages = 0
        
        for conversation in recent_conversations:
            messages = conversation_service.get_conversation_messages(conversation.id)
            total_messages_found += len(messages)
            
            print(f"[ANALYTICS] Conversation {conversation.id}: {len(messages)} messages")
            
            # Pair user messages with their corresponding assistant responses
            for i, message in enumerate(messages):
                if message.role == "user" and message.timestamp >= cutoff_date:
                    query_text = message.content.strip()
                    total_user_messages += 1
                    
                    if not query_text:
                        continue
                    
                    # Find the next assistant message for this query
                    response_time = 0
                    if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                        response_time = messages[i + 1].response_time_ms or 0

                    if query_text not in query_data:
                        query_data[query_text] = {"count": 0, "response_times": []}

                    query_data[query_text]["count"] += 1
                    if response_time > 0:
                        query_data[query_text]["response_times"].append(response_time)

        print(f"[ANALYTICS] Found {total_messages_found} total messages, {total_user_messages} user messages, {len(query_data)} unique queries")

        # Process into top queries (cache more than needed)
        all_top_queries = []
        for query_text, data in sorted(
            query_data.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:20]:  # Cache top 20 for reuse
            response_times = data["response_times"]
            avg_time = sum(response_times) / len(response_times) if response_times else 0

            all_top_queries.append({
                "query": query_text,
                "count": data["count"],
                "average_response_time_ms": round(avg_time, 2)
            })
        
        # Cache the result
        self._set_cached(cache_key, all_top_queries)
        
        top_queries = all_top_queries[:limit]
        print(f"[ANALYTICS] Returning {len(top_queries)} top queries: {[q['query'][:50] for q in top_queries]}")

        return top_queries if top_queries else []
    
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
        # Check cache first
        cache_key = f"top_documents_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached[:limit]
        
        from collections import defaultdict

        conversations, recent_conversations, cutoff_date = self._get_conversations_cached(days)

        # Filter conversations in time range and extract document access
        document_access_counts = defaultdict(int)
        document_last_access = {}
        document_chunks = defaultdict(int)

        for conversation in recent_conversations:
            messages = conversation_service.get_conversation_messages(conversation.id)
            for message in messages:
                if message.role == "assistant" and message.timestamp >= cutoff_date:
                    if message.sources:
                        for source in message.sources:
                            document_access_counts[source] += 1
                            if source not in document_last_access or message.timestamp > document_last_access[source]:
                                document_last_access[source] = message.timestamp
                            # Estimate chunks retrieved (could be improved)
                            document_chunks[source] += 1

        # Create DocumentAnalytics objects (cache more than needed)
        all_documents = []
        for doc_title, count in sorted(
            document_access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]:  # Cache top 20
            last_accessed_dt = document_last_access.get(doc_title)
            doc_analytics = DocumentAnalytics(
                document_id=doc_title,  # Using title as ID for now
                title=doc_title,
                query_count=count,
                last_accessed=last_accessed_dt.isoformat() if last_accessed_dt else None,
                total_chunks_retrieved=document_chunks.get(doc_title, 0)
            )
            all_documents.append(doc_analytics)

        self._set_cached(cache_key, all_documents)
        return all_documents[:limit]
    
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
        # Check cache first
        cache_key = f"avg_response_time_{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Get conversations from cache
        conversations, recent_conversations, cutoff_date = self._get_conversations_cached(days)

        total_time = sum(c.total_response_time_ms for c in recent_conversations)
        total_queries = sum(c.total_queries for c in recent_conversations)

        print(f"[ANALYTICS] get_average_response_time: {len(recent_conversations)} conversations, {total_queries} queries, {total_time:.2f}ms total")

        if total_queries == 0:
            self._set_cached(cache_key, 0.0)
            return 0.0

        avg_time = round(total_time / total_queries, 2)
        print(f"[ANALYTICS] Average response time: {avg_time}ms")
        self._set_cached(cache_key, avg_time)
        return avg_time
    
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
        # Check cache first
        cache_key = f"daily_metrics_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        from collections import defaultdict

        conversations, recent_conversations, cutoff_date = self._get_conversations_cached(days)

        # Group by date
        daily_data = defaultdict(lambda: {
            "query_count": 0,
            "conversations": set(),
            "documents": set(),
            "response_times": []
        })

        for conversation in recent_conversations:
            # Count queries and collect response times from actual messages
            messages = conversation_service.get_conversation_messages(conversation.id)
            
            # Group messages by their actual date (not conversation updated_at)
            for message in messages:
                if message.timestamp >= cutoff_date:
                    date_key = message.timestamp.date().isoformat()
                    
                    if message.role == "user":
                        daily_data[date_key]["query_count"] += 1
                        daily_data[date_key]["conversations"].add(conversation.id)
                    elif message.role == "assistant":
                        daily_data[date_key]["conversations"].add(conversation.id)
                        if message.response_time_ms and message.response_time_ms > 0:
                            daily_data[date_key]["response_times"].append(message.response_time_ms)
                        if message.sources:
                            daily_data[date_key]["documents"].update(message.sources)

        # Convert to DailyMetrics
        daily_metrics = []
        for date_str in sorted(daily_data.keys()):
            data = daily_data[date_str]
            response_times = data["response_times"]

            avg_response_time = (
                sum(response_times) / len(response_times)
                if response_times else 0
            )

            metrics = DailyMetrics(
                date=date_str,
                query_count=data["query_count"],
                unique_conversations=len(data["conversations"]),
                average_response_time=round(avg_response_time, 2),
                documents_accessed=list(data["documents"])
            )
            daily_metrics.append(metrics)

        self._set_cached(cache_key, daily_metrics)
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
        # Check cache first for the complete summary
        cache_key = f"analytics_summary_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Individual methods will also use caching
        query_volume = self.get_query_volume(days)
        top_queries = self.get_top_queries(limit=10, days=days)
        top_documents = self.get_top_documents(limit=10, days=days)
        avg_response_time = self.get_average_response_time(days)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        summary = AnalyticsSummary(
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
        
        self._set_cached(cache_key, summary)
        return summary