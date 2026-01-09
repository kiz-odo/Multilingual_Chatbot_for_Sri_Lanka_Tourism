"""
Redis Caching Service
Provides caching functionality for expensive operations
"""

import redis
import pickle
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import logging
from datetime import timedelta

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            serialized = pickle.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL for key in seconds"""
        if not self.enabled:
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return -1
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter
        
        Args:
            key: Counter key
            amount: Amount to increment
            
        Returns:
            New value or None on error
        """
        if not self.enabled:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache incr error for key {key}: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on existing key"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """Flush all cache (use with caution!)"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.flushdb()
            logger.warning("Cache flushed!")
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False


# Global cache instance
cache = CacheService()


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        MD5 hash of arguments
    """
    key_data = json.dumps({
        "args": [str(arg) for arg in args],
        "kwargs": {k: str(v) for k, v in sorted(kwargs.items())}
    }, sort_keys=True)
    
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(
    ttl: int = 3600,
    prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results
    
    Usage:
        @cached(ttl=3600, prefix="attractions")
        async def get_popular_attractions():
            # Expensive operation
            return attractions
    
    Args:
        ttl: Cache time-to-live in seconds
        prefix: Prefix for cache key
        key_builder: Custom function to build cache key
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not cache.enabled:
                return await func(*args, **kwargs)
            
            # Build cache key
            if key_builder:
                cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                args_key = generate_cache_key(*args, **kwargs)
                cache_key = f"{prefix}:{func.__name__}:{args_key}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: cache.delete_pattern(f"{prefix}:*")
        wrapper.cache_key_prefix = prefix
        
        return wrapper
    return decorator


def cache_invalidate(key_patterns: list[str]):
    """
    Decorator to invalidate cache after function execution
    
    Usage:
        @cache_invalidate(["attractions:*", "popular:*"])
        async def update_attraction(id, data):
            # Update operation
            return result
    
    Args:
        key_patterns: List of key patterns to invalidate
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache patterns
            if cache.enabled:
                for pattern in key_patterns:
                    deleted = cache.delete_pattern(pattern)
                    logger.debug(f"Cache invalidated: {pattern} ({deleted} keys)")
            
            return result
        return wrapper
    return decorator


class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self, cache_service: CacheService = cache):
        self.cache = cache_service
    
    def is_allowed(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if allowed, False if rate limited
        """
        if not self.cache.enabled:
            return True  # Allow if Redis is down
        
        key = f"ratelimit:{identifier}"
        
        try:
            current = self.cache.incr(key)
            
            if current == 1:
                # First request in window
                self.cache.expire(key, window_seconds)
            
            return current <= max_requests
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True  # Allow on error
    
    def reset(self, identifier: str):
        """Reset rate limit for identifier"""
        key = f"ratelimit:{identifier}"
        self.cache.delete(key)


# Global rate limiter instance
rate_limiter = RateLimiter(cache)

