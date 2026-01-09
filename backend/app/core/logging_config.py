"""
Enhanced logging configuration with structured logging and monitoring
"""

import logging
import logging.config
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict
from backend.app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging in production"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for better console readability in development"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging():
    """Setup logging configuration with environment-based formatting"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Use JSON logging in production, colored logging in development
    is_production = not settings.DEBUG
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": ColoredFormatter if not is_production else logging.Formatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "()": ColoredFormatter if not is_production else logging.Formatter,
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "detailed" if not is_production else "json",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "json" if is_production else "detailed",
                "filename": settings.LOG_FILE,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json" if is_production else "detailed",
                "filename": settings.LOG_FILE.replace(".log", "_errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "backend": {  # Application logger
                "handlers": ["console", "file", "error_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "file", "error_file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "WARNING" if is_production else "INFO",
                "propagate": False,
            },
            # Suppress noisy third-party loggers
            "httpx": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False,
            },
            "httpcore": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}, Mode: {'Production' if is_production else 'Development'}")
    logger.info(f"Log file: {settings.LOG_FILE}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
