"""
Sentry Error Tracking Integration
Captures errors, performance data, and user feedback
"""

import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.pymongo import PyMongoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def setup_sentry():
    """Initialize Sentry error tracking"""
    
    if not settings.SENTRY_DSN:
        logger.info("Sentry is not configured (SENTRY_DSN not set)")
        return
    
    try:
        # Configure logging integration
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
            release=f"tourism-chatbot@{settings.APP_VERSION}",
            
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                StarletteIntegration(transaction_style="endpoint"),
                AsyncioIntegration(),
                PyMongoIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
                sentry_logging,
            ],
            
            # Performance monitoring
            traces_sample_rate=float(settings.SENTRY_TRACES_SAMPLE_RATE or 0.1),
            profiles_sample_rate=float(settings.SENTRY_PROFILES_SAMPLE_RATE or 0.1),
            
            # Data scrubbing
            send_default_pii=False,
            
            # Error sampling
            sample_rate=1.0,
            
            # Before send hook for custom filtering
            before_send=before_send_hook,
            before_breadcrumb=before_breadcrumb_hook,
            
            # Additional options
            attach_stacktrace=True,
            debug=settings.DEBUG,
            max_breadcrumbs=50,
            
            # Request body
            request_bodies="medium",
        )
        
        logger.info("✅ Sentry error tracking initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}", exc_info=True)


def before_send_hook(event, hint):
    """Filter events before sending to Sentry"""
    
    # Don't send health check errors
    if event.get("request", {}).get("url", "").endswith("/health"):
        return None
    
    # Add custom context
    event.setdefault("tags", {})
    event["tags"]["app_version"] = settings.APP_VERSION
    event["tags"]["environment"] = settings.ENVIRONMENT
    
    return event


def before_breadcrumb_hook(crumb, hint):
    """Filter breadcrumbs before adding to Sentry"""
    
    # Skip health check breadcrumbs
    if crumb.get("category") == "httplib" and "/health" in crumb.get("data", {}).get("url", ""):
        return None
    
    return crumb


def capture_exception(error: Exception, context: dict = None):
    """Manually capture an exception with optional context"""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture a message with optional context"""
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        sentry_sdk.capture_message(message, level=level)


def set_user(user_id: str, email: str = None, username: str = None):
    """Set user context for error tracking"""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })


def set_tag(key: str, value: str):
    """Set a tag for the current scope"""
    sentry_sdk.set_tag(key, value)


def set_context(key: str, value: dict):
    """Set additional context"""
    sentry_sdk.set_context(key, value)
