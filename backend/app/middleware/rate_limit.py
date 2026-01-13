"""
Rate limiting middleware
Protects API from abuse
"""

import time
from typing import Dict, Tuple
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.app.middleware.error_handler import RateLimitException
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.limits = {
            "default": (100, 60),  # 100 requests per 60 seconds
            "chat": (50, 60),      # 50 chat requests per minute
            "auth": (10, 60),      # 10 auth requests per minute
            "upload": (20, 60),    # 20 uploads per minute
        }
    
    def _get_limit_for_path(self, path: str) -> Tuple[int, int]:
        """Get rate limit for specific path"""
        if "/chat" in path:
            return self.limits["chat"]
        elif "/auth" in path:
            return self.limits["auth"]
        elif "/upload" in path or "/landmarks/recognize" in path:
            return self.limits["upload"]
        else:
            return self.limits["default"]
    
    def is_allowed(self, identifier: str, path: str) -> bool:
        """Check if request is allowed"""
        max_requests, window = self._get_limit_for_path(path)
        current_time = time.time()
        
        # Get or create request list for identifier
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests outside window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(current_time)
        return True
    
    def get_remaining(self, identifier: str, path: str) -> Tuple[int, int]:
        """Get remaining requests and reset time"""
        max_requests, window = self._get_limit_for_path(path)
        
        if identifier not in self.requests:
            return max_requests, window
        
        current_time = time.time()
        recent_requests = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < window
        ]
        
        remaining = max(0, max_requests - len(recent_requests))
        
        # Calculate reset time
        if recent_requests:
            oldest_request = min(recent_requests)
            reset_time = int(window - (current_time - oldest_request))
        else:
            reset_time = window
        
        return remaining, reset_time


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app, limiter: RateLimiter = None):
        super().__init__(app)
        self.limiter = limiter or rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for OPTIONS (CORS preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/health/live", "/health/ready", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Get identifier (user ID or IP)
        identifier = self._get_identifier(request)
        path = request.url.path
        
        # Check rate limit
        if not self.limiter.is_allowed(identifier, path):
            remaining, reset_time = self.limiter.get_remaining(identifier, path)
            
            logger.warning(
                f"Rate limit exceeded for {identifier}",
                extra={
                    "identifier": identifier,
                    "path": path,
                    "method": request.method
                }
            )
            
            raise RateLimitException(
                message=f"Rate limit exceeded. Try again in {reset_time} seconds."
            )
        
        # Add rate limit headers
        response: Response = await call_next(request)
        remaining, reset_time = self.limiter.get_remaining(identifier, path)
        
        response.headers["X-RateLimit-Limit"] = str(self.limiter._get_limit_for_path(path)[0])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get user ID from auth
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"


def setup_rate_limiting(app: FastAPI) -> None:
    """Setup rate limiting middleware"""
    app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)

