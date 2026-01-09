"""
Application Metrics and Monitoring
Prometheus metrics for business and technical monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# ==================================================
# BUSINESS METRICS
# ==================================================

# Chat and Conversation Metrics
chat_requests_total = Counter(
    'chat_requests_total',
    'Total number of chat requests',
    ['language', 'intent']
)

chat_response_time = Histogram(
    'chat_response_time_seconds',
    'Chat response time in seconds',
    ['language']
)

conversations_active = Gauge(
    'conversations_active',
    'Number of active conversations'
)

# User Metrics
users_registered_total = Counter(
    'users_registered_total',
    'Total number of registered users',
    ['source']  # oauth, email, etc.
)

users_active = Gauge(
    'users_active',
    'Number of active users'
)

user_sessions_total = Counter(
    'user_sessions_total',
    'Total number of user sessions',
    ['user_type']  # tourist, local, admin
)

# Attraction Metrics
attractions_viewed_total = Counter(
    'attractions_viewed_total',
    'Total number of attraction views',
    ['category', 'city']
)

attractions_bookmarked_total = Counter(
    'attractions_bookmarked_total',
    'Total number of bookmarks',
    ['category']
)

# Search Metrics
searches_total = Counter(
    'searches_total',
    'Total number of searches',
    ['search_type', 'language']  # text, voice, image
)

search_results = Histogram(
    'search_results_count',
    'Number of search results returned',
    ['search_type']
)

# Recommendation Metrics
recommendations_generated_total = Counter(
    'recommendations_generated_total',
    'Total recommendations generated',
    ['algorithm']  # collaborative, content_based, hybrid
)

recommendations_clicked_total = Counter(
    'recommendations_clicked_total',
    'Total recommendations clicked'
)

# Itinerary Metrics
itineraries_created_total = Counter(
    'itineraries_created_total',
    'Total itineraries created'
)

itinerary_exports_total = Counter(
    'itinerary_exports_total',
    'Total itinerary exports',
    ['format']  # pdf, calendar, etc.
)

# ==================================================
# TECHNICAL METRICS
# ==================================================

# API Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database Metrics
db_operations_total = Counter(
    'db_operations_total',
    'Total database operations',
    ['operation', 'collection']  # find, insert, update, delete
)

db_operation_duration = Histogram(
    'db_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'collection']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Cache Metrics
cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'status']  # get/set, hit/miss
)

cache_hit_ratio = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio'
)

# External API Metrics
external_api_calls_total = Counter(
    'external_api_calls_total',
    'Total external API calls',
    ['service', 'status']  # google_maps, weather, etc.
)

external_api_duration = Histogram(
    'external_api_duration_seconds',
    'External API call duration',
    ['service']
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Rate Limit Metrics
rate_limit_exceeded_total = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit violations',
    ['endpoint', 'identifier_type']  # ip, user, api_key
)

# Background Task Metrics
tasks_executed_total = Counter(
    'tasks_executed_total',
    'Total background tasks executed',
    ['task_name', 'status']  # success, failed
)

tasks_duration = Histogram(
    'tasks_duration_seconds',
    'Task execution duration',
    ['task_name']
)

# LLM Metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

llm_tokens_used = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['model', 'type']  # input, output
)

llm_response_time = Histogram(
    'llm_response_time_seconds',
    'LLM response time in seconds',
    ['model']
)

# System Metrics
app_info = Info(
    'app',
    'Application information'
)


# ==================================================
# METRIC DECORATORS
# ==================================================

def track_time(metric: Histogram, labels: dict = None):
    """Decorator to track execution time"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def track_errors(error_counter: Counter, labels: dict = None):
    """Decorator to track errors"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_labels = labels or {}
                error_labels['error_type'] = type(e).__name__
                error_counter.labels(**error_labels).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_labels = labels or {}
                error_labels['error_type'] = type(e).__name__
                error_counter.labels(**error_labels).inc()
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def initialize_metrics():
    """Initialize application metrics"""
    from backend.app.core.config import settings
    
    app_info.info({
        'version': settings.APP_VERSION,
        'environment': getattr(settings, 'ENVIRONMENT', 'development')
    })
    
    logger.info("Metrics initialized successfully")


def record_http_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics"""
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)
    ).inc()
    
    http_request_duration.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


def record_db_operation(operation: str, collection: str, duration: float):
    """Record database operation metrics"""
    db_operations_total.labels(
        operation=operation,
        collection=collection
    ).inc()
    
    db_operation_duration.labels(
        operation=operation,
        collection=collection
    ).observe(duration)


def record_cache_operation(operation: str, hit: bool):
    """Record cache operation metrics"""
    status = 'hit' if hit else 'miss'
    cache_operations_total.labels(
        operation=operation,
        status=status
    ).inc()
