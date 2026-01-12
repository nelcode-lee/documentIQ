"""Caching service for query responses and embeddings.

Supports multiple cache backends:
- In-memory LRU cache (default, no dependencies)
- Redis (requires redis package)
- Azure Cache for Redis (uses Redis client)
"""

from typing import Optional, Any, Dict, List
import hashlib
import json
import time
from abc import ABC, abstractmethod
from app.config import settings


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (time-to-live in seconds)."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache."""
        pass


class InMemoryCacheBackend(CacheBackend):
    """In-memory LRU cache backend."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize in-memory cache with LRU eviction.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            item = self.cache[key]
            # Check if expired
            if item.get('expires_at', 0) > time.time():
                self.access_times[key] = time.time()  # Update access time
                return item.get('value')
            else:
                # Expired, remove it
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            # If cache is full, evict least recently used
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            expires_at = time.time() + ttl
            self.cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            self.access_times[key] = time.time()
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        try:
            self.cache.clear()
            self.access_times.clear()
            return True
        except Exception:
            return False
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if not self.access_times:
            return
        
        # Find least recently used
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        self.delete(lru_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'backend': 'in-memory'
        }


class RedisCacheBackend(CacheBackend):
    """Redis cache backend."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis cache backend.
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            import redis
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            self.connected = True
        except ImportError:
            print("[WARNING] redis package not installed. Install with: pip install redis")
            self.redis_client = None
            self.connected = False
        except Exception as e:
            print(f"[WARNING] Failed to connect to Redis: {e}")
            self.redis_client = None
            self.connected = False
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value to bytes."""
        return json.dumps(value).encode('utf-8')
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize value from bytes."""
        return json.loads(value.decode('utf-8'))
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.connected or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is not None:
                return self._deserialize(value)
            return None
        except Exception as e:
            print(f"Error getting from Redis cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            serialized = self._serialize(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Error setting Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False
    
    def clear(self) -> bool:
        """Clear all cache (flushes Redis database)."""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.connected or not self.redis_client:
            return {'backend': 'redis', 'connected': False}
        
        try:
            info = self.redis_client.info('memory')
            return {
                'backend': 'redis',
                'connected': True,
                'used_memory': info.get('used_memory_human', 'N/A'),
                'keys': self.redis_client.dbsize()
            }
        except Exception:
            return {'backend': 'redis', 'connected': True}


class CacheService:
    """Service for caching query responses and embeddings."""
    
    def __init__(self, backend: Optional[str] = None, **backend_kwargs):
        """Initialize cache service.
        
        Args:
            backend: Cache backend type ('memory', 'redis', or None for auto-detect)
            **backend_kwargs: Additional arguments for backend initialization
        """
        self.backend_type = backend or getattr(settings, 'cache_backend', 'memory')
        self.backend: CacheBackend = self._create_backend(backend_kwargs)
        self.stats = {'hits': 0, 'misses': 0}
    
    def _create_backend(self, kwargs: Dict) -> CacheBackend:
        """Create cache backend based on configuration."""
        if self.backend_type == 'redis':
            redis_url = kwargs.get('redis_url') or getattr(settings, 'redis_url', 'redis://localhost:6379/0')
            backend = RedisCacheBackend(redis_url=redis_url)
            if not backend.connected:
                print("[WARNING] Redis not available, falling back to in-memory cache")
                return InMemoryCacheBackend()
            return backend
        else:
            # Default to in-memory
            max_size = kwargs.get('max_size') or getattr(settings, 'cache_max_size', 1000)
            return InMemoryCacheBackend(max_size=max_size)
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments.
        
        Args:
            prefix: Key prefix (e.g., 'query', 'embedding')
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key (sorted for consistency)
        """
        # Normalize query text (lowercase, strip whitespace)
        parts = [prefix]
        
        for arg in args:
            if isinstance(arg, str):
                # Normalize string: lowercase, strip
                parts.append(arg.lower().strip())
            else:
                parts.append(str(arg))
        
        # Add kwargs in sorted order for consistency
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for key, value in sorted_kwargs:
                if isinstance(value, str):
                    parts.append(f"{key}:{value.lower().strip()}")
                else:
                    parts.append(f"{key}:{value}")
        
        # Create hash of the key parts
        key_string = "|".join(parts)
        key_hash = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_query_response(self, query: str, language: str = "en", top_k: int = 7) -> Optional[Dict]:
        """Get cached query response.
        
        Args:
            query: User query text
            language: Response language
            top_k: Number of chunks retrieved
            
        Returns:
            Cached response dict or None if not found
        """
        key = self._generate_key('query', query, language=language, top_k=top_k)
        result = self.backend.get(key)
        
        if result is not None:
            self.stats['hits'] += 1
            return result
        else:
            self.stats['misses'] += 1
            return None
    
    def set_query_response(self, query: str, response: Dict, language: str = "en", top_k: int = 7, ttl: int = 3600) -> bool:
        """Cache query response.
        
        Args:
            query: User query text
            response: Response dict with 'response', 'sources', 'conversation_id'
            language: Response language
            top_k: Number of chunks retrieved
            ttl: Time-to-live in seconds (default: 1 hour)
            
        Returns:
            True if cached successfully
        """
        key = self._generate_key('query', query, language=language, top_k=top_k)
        return self.backend.set(key, response, ttl=ttl)
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Cached embedding vector or None if not found
        """
        key = self._generate_key('embedding', text, model=getattr(settings, 'openai_embedding_model', 'text-embedding-ada-002'))
        result = self.backend.get(key)
        
        if result is not None:
            self.stats['hits'] += 1
            return result
        else:
            self.stats['misses'] += 1
            return None
    
    def set_embedding(self, text: str, embedding: List[float], ttl: int = 86400) -> bool:
        """Cache embedding.
        
        Args:
            text: Text that was embedded
            embedding: Embedding vector
            ttl: Time-to-live in seconds (default: 24 hours - embeddings rarely change)
            
        Returns:
            True if cached successfully
        """
        key = self._generate_key('embedding', text, model=getattr(settings, 'openai_embedding_model', 'text-embedding-ada-002'))
        return self.backend.set(key, embedding, ttl=ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        backend_stats = self.backend.get_stats() if hasattr(self.backend, 'get_stats') else {}
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **backend_stats,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': f"{hit_rate:.2f}%",
            'total_requests': total_requests
        }
    
    def clear(self) -> bool:
        """Clear all cache."""
        self.stats = {'hits': 0, 'misses': 0}
        return self.backend.clear()


# Global cache service instance
cache_service = CacheService()
