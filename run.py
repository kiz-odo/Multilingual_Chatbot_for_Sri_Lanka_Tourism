#!/usr/bin/env python3
"""
Sri Lanka Tourism Multilingual Chatbot - Backend Startup Script
Main entry point for running the FastAPI application
"""

import sys
import os
import uvicorn
import logging
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir.parent))

from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application"""
    logger.info("=" * 60)
    logger.info("Sri Lanka Tourism Multilingual Chatbot - Backend Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    logger.info(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)
    
    # Check critical configuration
    if settings.ENVIRONMENT == "production" and settings.DEBUG:
        logger.warning("⚠️  WARNING: Debug mode is enabled in production!")
    
    if settings.SECRET_KEY == "CHANGE-THIS-TO-A-SECURE-RANDOM-KEY-IN-PRODUCTION":
        logger.warning("⚠️  WARNING: Default SECRET_KEY detected! Change it in production!")
    
    # Start the server
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True
    )


if __name__ == "__main__":
    main()




