"""
CORS middleware configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware"""
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-API-Key"
        ],
        expose_headers=["X-Request-ID", "X-Total-Count", "X-Page", "X-Per-Page"],
        max_age=600,  # 10 minutes
    )

