"""
Cache Decorator for Service Layer
Provides caching functionality with TTL support
"""
from functools import wraps
from typing import Optional, Callable, Any
import hashlib
import json
from datetime import datetime, timedelta

from backend.app.core.config import settings
from backend.app.services.cache_service import cache


def _generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """
    Generate a cache key based on function name and arguments.
    
    Args:
        func_name: Name of the function
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: Cache key
    """
    # Create a string representation of arguments
    args_str = json.dumps([str(arg) for arg in args], sort_keys=True)
    kwargs_str = json.dumps({k: str(v) for k, v in kwargs.items()}, sort_keys=True)
    
    # Generate hash
    key_str = f"{func_name}:{args_str}:{kwargs_str}"
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return f"cache:{func_name}:{key_hash}"


def cached(ttl: int = 300, prefix: str = ""):
    """
    Cache decorator with TTL support.
    
    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        prefix: Optional prefix for cache key
        
    Usage:
        @cached(ttl=600, prefix="qwen")
        async def get_response(self, prompt: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            func_name = f"{prefix}:{func.__name__}" if prefix else func.__name__
            cache_key = _generate_cache_key(func_name, *args, **kwargs)
            
            # Try to get from cache
            try:
                cached_value = await cache.get(cache_key)
                
                if cached_value is not None:
                    return cached_value
            except Exception as e:
                # If cache fails, continue without caching
                pass
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await cache.set(cache_key, result, ttl)
            except Exception as e:
                # If cache fails, return result anyway
                pass
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # For sync functions, don't use cache (or implement sync cache)
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_invalidate(pattern: str):
    """
    Invalidate cache entries matching the pattern.
    
    Args:
        pattern: Pattern to match cache keys (e.g., "qwen:*")
        
    Usage:
        await cache_invalidate("qwen:*")
    """
    async def invalidate():
        try:
            # This would need to be implemented in cache_service
            # For now, just pass
            pass
        except Exception:
            pass
    
    return invalidate()
