"""
Response Caching Middleware
Adds Cache-Control, ETag, and other caching headers for performance
"""

import logging
import hashlib
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

logger = logging.getLogger(__name__)


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds appropriate caching headers to responses
    Implements ETags for conditional requests
    """
    
    def __init__(
        self,
        app,
        default_cache_control: str = "no-cache",
        enable_etag: bool = True
    ):
        super().__init__(app)
        self.default_cache_control = default_cache_control
        self.enable_etag = enable_etag
        
        # Define caching strategies for different paths
        self.cache_policies = {
            # Static and rarely changing data - cache heavily
            "/api/v1/attractions": "public, max-age=300",  # 5 minutes
            "/api/v1/hotels": "public, max-age=300",
            "/api/v1/restaurants": "public, max-age=300",
            "/api/v1/events": "public, max-age=180",  # 3 minutes
            "/api/v1/transport": "public, max-age=600",  # 10 minutes
            "/api/v1/emergency": "public, max-age=3600",  # 1 hour
            
            # Weather and currency - moderate caching
            "/api/v1/weather": "public, max-age=600",  # 10 minutes
            "/api/v1/currency": "public, max-age=1800",  # 30 minutes
            
            # User-specific data - private, short cache
            "/api/v1/users/me": "private, max-age=60",
            "/api/v1/conversations": "private, no-store",
            
            # Chat - no cache
            "/api/v1/chat": "no-cache, no-store, must-revalidate",
            
            # Health checks - short cache
            "/health": "public, max-age=30",
            
            # API documentation - cache for 1 hour
            "/docs": "public, max-age=3600",
            "/redoc": "public, max-age=3600",
            "/openapi.json": "public, max-age=3600",
        }
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and add caching headers"""
        
        # Check if client sent If-None-Match header (ETag validation)
        if_none_match = request.headers.get("if-none-match")
        
        # Call the actual endpoint
        response = await call_next(request)
        
        # Only add caching headers to successful GET requests
        if request.method == "GET" and response.status_code == 200:
            # Determine cache policy for this path
            cache_control = self._get_cache_policy(request.url.path)
            response.headers["Cache-Control"] = cache_control
            
            # Add Vary header for content negotiation
            response.headers["Vary"] = "Accept, Accept-Language, Accept-Encoding"
            
            # Generate and add ETag if enabled and response has body
            if self.enable_etag and hasattr(response, 'body'):
                try:
                    etag = self._generate_etag(response.body)
                    response.headers["ETag"] = etag
                    
                    # If client's ETag matches, return 304 Not Modified
                    if if_none_match and if_none_match == etag:
                        return Response(
                            status_code=304,
                            headers={
                                "ETag": etag,
                                "Cache-Control": cache_control
                            }
                        )
                except Exception as e:
                    logger.debug(f"Could not generate ETag: {e}")
        
        # For POST, PUT, DELETE - no caching
        elif request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response
    
    def _get_cache_policy(self, path: str) -> str:
        """Get cache policy for the given path"""
        # Check for exact match
        if path in self.cache_policies:
            return self.cache_policies[path]
        
        # Check for prefix match
        for policy_path, policy in self.cache_policies.items():
            if path.startswith(policy_path):
                return policy
        
        # Default policy
        return self.default_cache_control
    
    def _generate_etag(self, content: bytes) -> str:
        """Generate ETag from response content"""
        # Use MD5 hash (fast, good enough for ETags)
        hash_md5 = hashlib.md5(content)
        return f'"{hash_md5.hexdigest()}"'


class ConditionalGetMiddleware(BaseHTTPMiddleware):
    """
    Handles conditional GET requests (If-Modified-Since)
    Works in conjunction with Last-Modified headers
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process conditional GET requests"""
        
        response = await call_next(request)
        
        # For GET requests, add Last-Modified if not present
        if request.method == "GET" and response.status_code == 200:
            if "Last-Modified" not in response.headers:
                # You can implement logic to add Last-Modified based on resource
                # For now, we'll let individual endpoints handle this
                pass
            
            # Handle If-Modified-Since
            if_modified_since = request.headers.get("if-modified-since")
            last_modified = response.headers.get("last-modified")
            
            if if_modified_since and last_modified:
                if if_modified_since == last_modified:
                    return Response(
                        status_code=304,
                        headers={
                            "Last-Modified": last_modified,
                            "Cache-Control": response.headers.get("cache-control", "")
                        }
                    )
        
        return response


def setup_caching_middleware(app):
    """Setup caching middleware for the application"""
    # Add cache headers middleware
    app.add_middleware(
        CacheHeadersMiddleware,
        default_cache_control="no-cache",
        enable_etag=True
    )
    
    # Add conditional GET middleware
    app.add_middleware(ConditionalGetMiddleware)
    
    logger.info("Response caching middleware configured")

