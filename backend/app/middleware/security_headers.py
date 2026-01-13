"""
Security Headers Middleware
Adds comprehensive security headers to all responses
"""

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip security headers for OPTIONS (CORS preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Strict Transport Security (HTTPS only)
        if settings.ENABLE_HSTS:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy
        if settings.ENABLE_CSP:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https: blob:",
                "connect-src 'self' ws: wss:",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Permissions Policy (formerly Feature Policy)
        permissions = [
            "geolocation=(self)",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server header for security
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Add custom security header
        response.headers["X-Security-Policy"] = "enabled"
        
        return response


def setup_security_middleware(app: FastAPI):
    """Setup all security-related middleware"""
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Enforce HTTPS in production
    if settings.ENABLE_HTTPS_REDIRECT and not settings.DEBUG:
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted host middleware
    if settings.ALLOWED_HOSTS:
        allowed_hosts = settings.ALLOWED_HOSTS.split(",")
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    logger.info("Security middleware configured successfully")
