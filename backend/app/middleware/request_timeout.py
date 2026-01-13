"""
Request Timeout Middleware
Prevents long-running requests from tying up resources
"""

import asyncio
import logging
from typing import Callable
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.middleware.error_handler import ServiceUnavailableException

logger = logging.getLogger(__name__)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts"""
    
    def __init__(self, app, timeout_seconds: int = None):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds or settings.REQUEST_TIMEOUT_SECONDS
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with timeout
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
        
        Returns:
            Response or timeout error
        """
        # Skip timeout for OPTIONS (CORS preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip timeout for certain endpoints
        skip_paths = [
            "/health",
            "/health/ready",
            "/health/detailed",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Check for custom timeout in request headers
        custom_timeout = request.headers.get("X-Request-Timeout")
        if custom_timeout and custom_timeout.isdigit():
            timeout = int(custom_timeout)
        # Give chat endpoints longer timeout by default (AI responses can take time)
        elif "/api/v1/chat/" in request.url.path:
            timeout = 120  # 2 minutes for chat endpoints
        else:
            timeout = self.timeout_seconds
        
        try:
            # Execute request with timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )
            return response
            
        except asyncio.TimeoutError:
            logger.warning(
                f"Request timeout after {timeout}s: {request.method} {request.url.path}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "timeout": timeout,
                    "client_ip": request.client.host if request.client else None
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "success": False,
                    "error": {
                        "code": "REQUEST_TIMEOUT",
                        "message": f"Request exceeded maximum time limit of {timeout} seconds",
                        "timeout_seconds": timeout
                    },
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in timeout middleware: {e}", exc_info=True)
            raise


def setup_request_timeout(app, timeout_seconds: int = None):
    """
    Setup request timeout middleware
    
    Args:
        app: FastAPI application
        timeout_seconds: Timeout in seconds (defaults to config)
    """
    timeout = timeout_seconds or settings.REQUEST_TIMEOUT_SECONDS
    app.add_middleware(RequestTimeoutMiddleware, timeout_seconds=timeout)
    logger.info(f"Request timeout middleware configured: {timeout}s timeout")




