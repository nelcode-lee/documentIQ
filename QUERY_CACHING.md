# Query Caching Implementation

## Overview

The RAG system now includes comprehensive caching capabilities to improve performance and reduce costs. Caching is implemented at two levels:

1. **Query Response Caching** - Caches complete query responses (saves full API calls)
2. **Embedding Caching** - Caches query embeddings (saves embedding API calls)

## Benefits

### Performance Improvements
- **Query Response Caching**: Reduces response time from ~12 seconds to < 50ms for cached queries
- **Embedding Caching**: Reduces embedding generation time from ~1-2 seconds to < 10ms
- **Overall**: Up to 99% faster response times for repeated queries

### Cost Savings
- **Reduced API Calls**: Cached queries don't call OpenAI API
- **Example Savings**: 
  - If 30% of queries are repeats (common in technical documentation)
  - With GPT-4: Saves ~$24/month on 1000 queries (30% cached = 300 fewer API calls)
  - With GPT-3.5-turbo: Saves ~$1.30/month on 1000 queries
  - Embedding savings: ~$0.01-0.05/month (minimal but consistent)

### User Experience
- Instant responses for common questions
- Consistent answers for repeated queries
- Better perceived performance

## Architecture

### Cache Backends

The system supports multiple cache backends:

#### 1. **In-Memory Cache (Default)**
- **Type**: LRU (Least Recently Used) cache
- **Storage**: Local Python dictionary
- **Pros**: 
  - No dependencies
  - Very fast (< 1ms lookup)
  - Zero configuration
- **Cons**: 
  - Lost on restart
  - Single-server only (no shared cache across instances)
  - Limited by available memory
- **Use Case**: Development, single-server deployments

#### 2. **Redis Cache (Optional)**
- **Type**: Redis key-value store
- **Storage**: Redis server (local or Azure Cache for Redis)
- **Pros**:
  - Persistent across restarts
  - Shared cache across multiple server instances
  - Configurable persistence
  - Can handle high traffic
- **Cons**:
  - Requires Redis server
  - Network latency (~1-5ms per lookup)
- **Use Case**: Production, multi-server deployments

### Cache Key Generation

Cache keys are generated using SHA-256 hashing to ensure:
- Consistent keys for same queries
- Normalized query text (lowercase, trimmed)
- Includes all relevant parameters (query, language, top_k)

**Example:**
```
Query: "What are the safety requirements?"
Language: "en"
top_k: 7

Key: query:a1b2c3d4e5f6... (SHA-256 hash)
```

### Cache TTL (Time-To-Live)

Different cache types have different TTLs:

- **Query Responses**: 1 hour (3600 seconds) - Default
  - Reason: Responses may change if documents are updated
  - Configurable via `CACHE_QUERY_TTL`
  
- **Embeddings**: 24 hours (86400 seconds) - Default
  - Reason: Embeddings for same text never change
  - Configurable via `CACHE_EMBEDDING_TTL`

## Configuration

### Environment Variables

Add to `backend/.env`:

```env
# Cache Configuration
CACHE_BACKEND=memory                    # "memory" or "redis"
CACHE_MAX_SIZE=1000                     # Max items for in-memory cache
REDIS_URL=redis://localhost:6379/0      # Redis connection URL (if using Redis)
CACHE_QUERY_TTL=3600                    # Query cache TTL in seconds (1 hour)
CACHE_EMBEDDING_TTL=86400               # Embedding cache TTL in seconds (24 hours)
ENABLE_QUERY_CACHE=true                 # Enable query response caching
ENABLE_EMBEDDING_CACHE=true             # Enable embedding caching
```

### Redis Setup (Optional)

**Local Redis:**
```bash
# Install Redis (Windows - using WSL or Docker)
docker run -d -p 6379:6379 redis:alpine

# Or install locally (Linux/Mac)
sudo apt-get install redis-server
redis-server
```

**Azure Cache for Redis:**
1. Create Azure Cache for Redis in Azure Portal
2. Get connection string from Azure Portal
3. Set `REDIS_URL=rediss://your-cache.redis.cache.windows.net:6380?ssl=true&password=your-password`

## Usage

### Automatic Caching

Caching is **automatic** and transparent. No code changes needed in your application:

```python
# First query - cache miss, full processing
response1 = await chat_service.chat(query="What is HACCP?")

# Second identical query - cache hit, instant response
response2 = await chat_service.chat(query="What is HACCP?")
```

### Cache Statistics

View cache statistics via API:

```bash
GET /api/chat/cache/stats

Response:
{
  "status": "success",
  "stats": {
    "backend": "in-memory",
    "size": 45,
    "max_size": 1000,
    "hits": 23,
    "misses": 67,
    "hit_rate": "25.56%",
    "total_requests": 90
  }
}
```

### Clear Cache

Clear all cached data:

```bash
POST /api/chat/cache/clear

Response:
{
  "status": "success",
  "message": "Cache cleared successfully"
}
```

## Performance Impact

### Before Caching
```
Query Flow:
1. Generate embedding (~1-2s)
2. Vector search (~0.2s)
3. Build context (~0.1s)
4. OpenAI API call (~6-10s)
Total: ~8-13 seconds
```

### After Caching (Cache Hit)
```
Query Flow:
1. Check cache (< 1ms) ✅
2. Return cached response (< 1ms)
Total: < 2ms (4000x faster!)
```

### Real-World Scenario

**1000 queries/month, 30% repeat rate:**

| Metric | Without Cache | With Cache | Improvement |
|--------|--------------|------------|-------------|
| Average Response Time | 12s | 8.4s* | 30% faster |
| API Calls | 1000 | 700 | 30% reduction |
| Cost (GPT-4) | $82 | $57.40 | $24.60 saved |
| Cost (GPT-3.5) | $4.40 | $3.08 | $1.32 saved |

*Weighted average: (700 × 12s + 300 × 0.002s) / 1000 = 8.4s

## Cache Invalidation

### Automatic Invalidation

- **TTL Expiration**: Cached items automatically expire after TTL
- **LRU Eviction**: In-memory cache evicts least recently used items when full

### Manual Invalidation

Clear cache when documents are updated:

```python
# After uploading new documents
cache_service.clear()  # Or use API endpoint
```

### Recommended Strategy

1. **Document Upload**: Clear query cache (responses may change)
   - Keep embedding cache (embeddings don't change)
   
2. **Bulk Document Update**: Clear entire cache
   
3. **Periodic Refresh**: Set appropriate TTL (defaults are good)

## Monitoring

### Cache Hit Rate

Monitor cache hit rate to optimize:
- **> 30% hit rate**: Excellent, caching is working well
- **10-30% hit rate**: Good, consider increasing TTL
- **< 10% hit rate**: Poor, queries are too unique

### Cache Size

Monitor cache size:
- **In-memory**: Should stay under `CACHE_MAX_SIZE`
- **Redis**: Monitor memory usage in Redis dashboard

### Logs

Look for cache hits/misses in logs:
```
[CACHE HIT] Query response cached: What are the safety requirements?...
[CACHE MISS] Generating new response for: How do I report an incident?...
[CACHE HIT] Embedding for query: What is HACCP?...
```

## Best Practices

### 1. Choose Appropriate Backend

- **Development**: Use in-memory cache (simple, fast)
- **Production (Single Server)**: Use in-memory cache (if sufficient memory)
- **Production (Multiple Servers)**: Use Redis (shared cache)

### 2. Set Appropriate TTLs

- **Query Cache**: 1-4 hours (balance freshness vs performance)
- **Embedding Cache**: 24+ hours (embeddings never change)

### 3. Monitor Hit Rate

- Target: > 20% hit rate
- If low: Analyze queries, may need different caching strategy

### 4. Clear Cache Strategically

- Clear after document updates
- Don't clear unnecessarily (hurts performance)

### 5. Consider Query Normalization

Current implementation normalizes queries (lowercase, trim). If you need case-sensitive or exact matching, modify `_generate_key()` in `cache_service.py`.

## Troubleshooting

### Cache Not Working

1. **Check Configuration**:
   ```bash
   # Verify cache is enabled
   echo $ENABLE_QUERY_CACHE  # Should be "true"
   ```

2. **Check Logs**:
   ```
   Look for [CACHE HIT] or [CACHE MISS] messages
   ```

3. **Check Statistics**:
   ```bash
   curl http://localhost:8000/api/chat/cache/stats
   ```

### Redis Connection Issues

1. **Verify Redis is Running**:
   ```bash
   redis-cli ping  # Should return "PONG"
   ```

2. **Check Connection URL**:
   ```
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Check Firewall**: Ensure Redis port is accessible

### High Memory Usage

1. **Reduce Cache Size**:
   ```env
   CACHE_MAX_SIZE=500  # Reduce from 1000
   ```

2. **Reduce TTL**:
   ```env
   CACHE_QUERY_TTL=1800  # Reduce from 3600 (30 min instead of 1 hour)
   ```

3. **Use Redis**: Move to Redis for better memory management

## Future Enhancements

### Potential Improvements

1. **Semantic Similarity Caching**
   - Cache queries with similar meaning (not just exact matches)
   - Use embedding similarity to find "near misses"

2. **Partial Cache Invalidation**
   - Invalidate only queries related to updated documents
   - Requires tracking which documents each query used

3. **Cache Warming**
   - Pre-cache common queries on startup
   - Use analytics to identify popular queries

4. **Distributed Cache**
   - Use Azure Cache for Redis for multi-region deployments
   - Automatic replication and failover

5. **Cache Analytics**
   - Track cache performance per query type
   - Identify cache optimization opportunities

## Code Examples

### Disable Caching for Specific Query

```python
# Temporarily disable cache for this query
original_setting = settings.enable_query_cache
settings.enable_query_cache = False

try:
    response = await chat_service.chat(query="test")
finally:
    settings.enable_query_cache = original_setting
```

### Custom Cache TTL

```python
# Cache with custom TTL
cache_service.set_query_response(
    query="test query",
    response={"response": "test"},
    ttl=7200  # 2 hours
)
```

### Monitor Cache in Code

```python
from app.services.cache_service import cache_service

# Get cache stats
stats = cache_service.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
print(f"Total requests: {stats['total_requests']}")
```

## Summary

Query caching provides significant performance and cost benefits:

✅ **99% faster** responses for cached queries  
✅ **20-30% cost reduction** for typical workloads  
✅ **Zero code changes** required (automatic)  
✅ **Multiple backends** (in-memory, Redis)  
✅ **Easy monitoring** via API endpoints  

**Recommendation**: Enable caching in production with Redis backend for best results.

---

**Last Updated:** January 2025
