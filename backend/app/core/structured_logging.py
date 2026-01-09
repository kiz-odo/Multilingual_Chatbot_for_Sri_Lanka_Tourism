"""
Structured Logging Configuration
JSON-formatted logging with request tracing
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from backend.app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add application context
        log_record['app'] = settings.APP_NAME
        log_record['version'] = settings.APP_VERSION
        log_record['environment'] = getattr(settings, 'ENVIRONMENT', 'development')
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        # Add trace ID for distributed tracing
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id


def setup_structured_logging():
    """Configure structured JSON logging"""
    
    # Determine log format
    use_json = settings.LOG_FORMAT.lower() == 'json'
    
    # Create formatter
    if use_json:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return root_logger


# Request context filter
class RequestContextFilter(logging.Filter):
    """Add request context to log records"""
    
    def __init__(self, request_id: str = None, user_id: str = None):
        super().__init__()
        self.request_id = request_id
        self.user_id = user_id
    
    def filter(self, record):
        if self.request_id:
            record.request_id = self.request_id
        if self.user_id:
            record.user_id = self.user_id
        return True


# Utility functions for structured logging
def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    request_id: str = None,
    user_id: str = None,
    **kwargs
):
    """Log message with structured context"""
    extra = {
        'request_id': request_id,
        'user_id': user_id,
        **kwargs
    }
    
    log_method = getattr(logger, level.lower())
    log_method(message, extra=extra)


def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: str = None,
    user_id: str = None
):
    """Log API request with metrics"""
    log_with_context(
        logger,
        'info',
        f"{method} {path} - {status_code}",
        request_id=request_id,
        user_id=user_id,
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        event_type='api_request'
    )


def log_error_with_trace(
    logger: logging.Logger,
    error: Exception,
    request_id: str = None,
    user_id: str = None,
    **context
):
    """Log error with full context and stack trace"""
    import traceback
    
    log_with_context(
        logger,
        'error',
        str(error),
        request_id=request_id,
        user_id=user_id,
        error_type=type(error).__name__,
        stack_trace=traceback.format_exc(),
        event_type='error',
        **context
    )
