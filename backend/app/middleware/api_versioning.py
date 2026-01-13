"""
API Versioning Middleware
Provides API version deprecation warnings and version-based routing
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException

logger = logging.getLogger(__name__)


# API Version Configuration
API_VERSIONS = {
    "v1": {
        "status": "stable",
        "released": "2024-01-01",
        "deprecated": None,
        "sunset": None,
        "documentation": "/docs"
    },
    "v2": {
        "status": "planned",
        "released": None,
        "deprecated": None,
        "sunset": None,
        "documentation": None
    }
}

# Current default version
DEFAULT_VERSION = "v1"

# Deprecated endpoints tracking
DEPRECATED_ENDPOINTS = {
    # Example: "/api/v1/old-endpoint": {
    #     "deprecated_at": "2024-06-01",
    #     "sunset_at": "2024-12-01",
    #     "replacement": "/api/v1/new-endpoint",
    #     "message": "Use /api/v1/new-endpoint instead"
    # }
}


class APIVersioningMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API versioning with deprecation warnings
    
    Features:
    - Adds API version headers to responses
    - Warns about deprecated versions/endpoints
    - Provides sunset dates for deprecated APIs
    - Supports version negotiation via headers
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip versioning for OPTIONS (CORS preflight) requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Extract requested version
        path = request.url.path
        requested_version = self._extract_version(path)
        
        # Get version from header if not in path
        if not requested_version:
            requested_version = request.headers.get("X-API-Version", DEFAULT_VERSION)
        
        # Validate version
        version_info = API_VERSIONS.get(requested_version)
        
        # Process request
        response = await call_next(request)
        
        # Add version headers
        response.headers["X-API-Version"] = requested_version or DEFAULT_VERSION
        response.headers["X-API-Versions-Available"] = ", ".join(
            v for v, info in API_VERSIONS.items() 
            if info["status"] in ("stable", "deprecated")
        )
        
        # Add deprecation warnings if applicable
        if version_info and version_info.get("deprecated"):
            response.headers["Deprecation"] = version_info["deprecated"]
            response.headers["Sunset"] = version_info.get("sunset", "")
            response.headers["Link"] = f'</api/{self._get_latest_version()}>; rel="successor-version"'
            
            # Add deprecation warning in body for JSON responses
            logger.warning(f"Deprecated API version {requested_version} accessed: {path}")
        
        # Check for deprecated endpoints
        endpoint_key = path.split("?")[0]  # Remove query params
        if endpoint_key in DEPRECATED_ENDPOINTS:
            deprecation_info = DEPRECATED_ENDPOINTS[endpoint_key]
            response.headers["Deprecation"] = deprecation_info["deprecated_at"]
            response.headers["Sunset"] = deprecation_info.get("sunset_at", "")
            
            if deprecation_info.get("replacement"):
                response.headers["Link"] = f'<{deprecation_info["replacement"]}>; rel="successor"'
            
            # Log deprecation access
            logger.warning(
                f"Deprecated endpoint accessed: {endpoint_key}. "
                f"Replacement: {deprecation_info.get('replacement', 'none')}"
            )
        
        return response
    
    def _extract_version(self, path: str) -> Optional[str]:
        """Extract API version from path"""
        parts = path.strip("/").split("/")
        
        if len(parts) >= 2 and parts[0] == "api":
            potential_version = parts[1]
            if potential_version in API_VERSIONS:
                return potential_version
        
        return None
    
    def _get_latest_version(self) -> str:
        """Get the latest stable API version"""
        stable_versions = [
            v for v, info in API_VERSIONS.items()
            if info["status"] == "stable"
        ]
        return sorted(stable_versions)[-1] if stable_versions else DEFAULT_VERSION


def deprecate_endpoint(
    path: str,
    deprecated_at: str,
    sunset_at: str,
    replacement: Optional[str] = None,
    message: Optional[str] = None
):
    """
    Mark an endpoint as deprecated
    
    Args:
        path: The endpoint path (e.g., "/api/v1/old-endpoint")
        deprecated_at: ISO date when deprecated (e.g., "2024-06-01")
        sunset_at: ISO date when endpoint will be removed
        replacement: New endpoint path to use instead
        message: Custom deprecation message
    """
    DEPRECATED_ENDPOINTS[path] = {
        "deprecated_at": deprecated_at,
        "sunset_at": sunset_at,
        "replacement": replacement,
        "message": message or f"This endpoint is deprecated. Use {replacement} instead."
    }
    
    logger.info(f"Endpoint {path} marked as deprecated. Sunset: {sunset_at}")


def get_version_info(version: str = None) -> Dict[str, Any]:
    """Get information about an API version"""
    if version is None:
        return {
            "current_version": DEFAULT_VERSION,
            "available_versions": API_VERSIONS,
            "deprecated_endpoints": len(DEPRECATED_ENDPOINTS)
        }
    
    return API_VERSIONS.get(version, {"error": "Version not found"})


def check_sunset_dates():
    """
    Check for endpoints past their sunset date
    Called during startup or scheduled task
    """
    today = date.today()
    
    for path, info in list(DEPRECATED_ENDPOINTS.items()):
        sunset = info.get("sunset_at")
        if sunset:
            sunset_date = datetime.strptime(sunset, "%Y-%m-%d").date()
            if sunset_date <= today:
                logger.error(
                    f"Endpoint {path} is past its sunset date ({sunset}). "
                    "Consider removing it."
                )
