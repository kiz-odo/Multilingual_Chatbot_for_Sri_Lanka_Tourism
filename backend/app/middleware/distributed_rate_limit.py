"""
Distributed Rate Limiting using Redis
Industry-standard rate limiting for multi-instance deployments
"""

import time
import hashlib
from typing import Tuple, Optional
from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import redis.asyncio as redis

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class DistributedRateLimiter:
    """Redis-based distributed rate limiter using sliding window algorithm"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.enabled = settings.RATE_LIMIT_ENABLED
        
        # Rate limit configurations (requests, window_seconds)
        # Fixed: Use RATE_LIMIT_CHAT_PER_MINUTE instead of non-existent RATE_LIMIT_CHAT
        self.limits = {
            "default": (settings.RATE_LIMIT_DEFAULT, settings.RATE_LIMIT_WINDOW),
            "chat": (settings.RATE_LIMIT_CHAT_PER_MINUTE, 60),
            "auth": (settings.RATE_LIMIT_AUTH, 60),
            "upload": (settings.RATE_LIMIT_UPLOAD, 60),
        }
    
    def _get_limit_for_path(self, path: str) -> Tuple[int, int]:
        """Get rate limit configuration for specific path"""
        if "/chat" in path or "/api/v1/chat" in path:
            return self.limits["chat"]
        elif "/auth" in path or "/login" in path or "/register" in path:
            return self.limits["auth"]
        elif "/upload" in path or "/landmarks/recognize" in path:
            return self.limits["upload"]
        else:
            return self.limits["default"]
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for the request (IP + User ID if authenticated)"""
        # Try to get real IP from proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # If user is authenticated, include user ID
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            identifier = f"{ip}:{user_id}"
        else:
            identifier = ip
        
        # Hash for privacy
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    async def is_allowed(self, request: Request) -> Tuple[bool, dict]:
        """
        Check if request is allowed using sliding window algorithm
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        if not self.enabled:
            return True, {}
        
        identifier = self._get_identifier(request)
        path = request.url.path
        max_requests, window = self._get_limit_for_path(path)
        
        # Create Redis key
        key = f"ratelimit:{identifier}:{path}"
        current_time = time.time()
        window_start = current_time - window
        
        # Use Redis transaction for atomic operations
        pipe = self.redis.pipeline()
        
        try:
            # Remove old requests outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(key, window)
            
            # Execute transaction
            results = await pipe.execute()
            request_count = results[1]  # Count from zcard
            
            # Calculate rate limit info
            remaining = max(0, max_requests - request_count - 1)
            reset_time = int(current_time + window)
            
            rate_limit_info = {
                "limit": max_requests,
                "remaining": remaining,
                "reset": reset_time,
                "window": window
            }
            
            # Check if limit exceeded
            if request_count >= max_requests:
                return False, rate_limit_info
            
            return True, rate_limit_info
            
        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            # Fail open - allow request if Redis is down
            return True, {}
    
    async def cleanup_old_entries(self):
        """Cleanup old rate limit entries (run periodically)"""
        try:
            # This would be called by a background task
            # Scan for all rate limit keys and clean old entries
            cursor = 0
            pattern = "ratelimit:*"
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                
                for key in keys:
                    # Remove entries older than 1 hour
                    cutoff = time.time() - 3600
                    await self.redis.zremrangebyscore(key, 0, cutoff)
                
                if cursor == 0:
                    break
                    
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


class DistributedRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce distributed rate limiting"""
    
    def __init__(self, app: FastAPI, rate_limiter: DistributedRateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Check rate limit
        allowed, rate_limit_info = await self.rate_limiter.is_allowed(request)
        
        # Add rate limit headers to response
        response = None
        if allowed:
            response = await call_next(request)
        else:
            response = Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
        
        # Add rate limit headers
        if rate_limit_info:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info.get("reset", 0))
            response.headers["X-RateLimit-Window"] = str(rate_limit_info.get("window", 0))
        
        return response


async def setup_distributed_rate_limiting(app: FastAPI, redis_client: redis.Redis):
    """Setup distributed rate limiting with Redis"""
    try:
        rate_limiter = DistributedRateLimiter(redis_client)
        app.add_middleware(DistributedRateLimitMiddleware, rate_limiter=rate_limiter)
        logger.info("Distributed rate limiting configured successfully")
        return rate_limiter
    except Exception as e:
        logger.error(f"Failed to setup rate limiting: {e}")
        raise
