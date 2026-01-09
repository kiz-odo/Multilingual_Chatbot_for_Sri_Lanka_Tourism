# 🛡️ Middleware Documentation

Complete documentation of all middleware components in the backend.

## Overview

Middleware components process requests and responses in the FastAPI application. They are executed in a specific order and can modify requests, responses, or handle errors.

## Middleware Execution Order

```
1. RequestIdMiddleware        # Add unique request ID
2. GZipMiddleware            # Response compression
3. RequestTimeoutMiddleware  # Request timeout handling
4. CacheHeadersMiddleware    # HTTP caching headers
5. SecurityHeadersMiddleware # Security headers
6. APIVersioningMiddleware   # API versioning
7. CORSMiddleware            # CORS handling
8. RateLimitMiddleware       # Rate limiting
9. ErrorHandlerMiddleware    # Error handling (after routes)
```

## Core Middleware

### 1. RequestIdMiddleware

**Location**: `backend/app/middleware/request_id.py`

**Purpose**: Adds a unique request ID to every request for tracing and debugging.

**Features**:
- Generates UUID for each request
- Adds `X-Request-ID` header to responses
- Includes request ID in logs

**Configuration**:
```python
app.add_middleware(RequestIdMiddleware)
```

**Headers**:
- `X-Request-ID`: Unique request identifier

**Usage in Logs**:
```python
logger.info("Processing request", extra={"request_id": request.state.request_id})
```

### 2. GZipMiddleware

**Location**: FastAPI built-in middleware

**Purpose**: Compresses responses using GZip for better performance.

**Configuration**:
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Features**:
- Compresses responses larger than 1000 bytes
- Automatically handles `Accept-Encoding` header
- Reduces bandwidth usage

### 3. RequestTimeoutMiddleware

**Location**: `backend/app/middleware/request_timeout.py`

**Purpose**: Enforces request timeout limits to prevent long-running requests.

**Configuration**:
```python
from backend.app.middleware.request_timeout import setup_request_timeout

setup_request_timeout(app, timeout_seconds=30)
```

**Features**:
- Default timeout: 30 seconds
- Configurable per route
- Returns 504 Gateway Timeout on timeout

**Timeout Configuration**:
```python
@router.get("/endpoint", timeout=60)  # 60 seconds for this route
async def endpoint():
    pass
```

### 4. CacheHeadersMiddleware

**Location**: `backend/app/middleware/cache_headers.py`

**Purpose**: Adds HTTP caching headers to responses.

**Configuration**:
```python
from backend.app.middleware.cache_headers import setup_caching_middleware

setup_caching_middleware(app)
```

**Headers Added**:
- `Cache-Control`: Cache control directives
- `ETag`: Entity tag for cache validation
- `Last-Modified`: Last modification time

**Cache Strategies**:
- Static resources: Long cache (1 year)
- Dynamic content: Short cache (5 minutes)
- User-specific: No cache

### 5. SecurityHeadersMiddleware

**Location**: `backend/app/middleware/security_headers.py`

**Purpose**: Adds security headers to prevent common attacks.

**Configuration**:
```python
from backend.app.middleware.security_headers import SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
```

**Headers Added**:
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Strict-Transport-Security` - HSTS (HTTPS only)
- `Content-Security-Policy` - CSP policy
- `Referrer-Policy: strict-origin-when-cross-origin`

**Security Features**:
- XSS protection
- Clickjacking protection
- MIME type sniffing prevention
- HTTPS enforcement

### 6. APIVersioningMiddleware

**Location**: `backend/app/middleware/api_versioning.py`

**Purpose**: Handles API versioning and deprecation warnings.

**Configuration**:
```python
from backend.app.middleware.api_versioning import APIVersioningMiddleware

app.add_middleware(APIVersioningMiddleware)
```

**Features**:
- Version detection from URL (`/api/v1/`)
- Deprecation warnings for old versions
- Version header in responses

**Headers**:
- `X-API-Version`: Current API version
- `X-API-Deprecated`: Warning if using deprecated version

### 7. CORSMiddleware

**Location**: FastAPI built-in middleware

**Purpose**: Handles Cross-Origin Resource Sharing (CORS).

**Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Accept", "Accept-Language", "Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
)
```

**Features**:
- Configurable allowed origins
- Credential support
- Method and header whitelisting
- Preflight request handling

**Security**:
- Only allows configured origins
- Validates credentials
- Prevents unauthorized cross-origin requests

### 8. RateLimitMiddleware

**Location**: `backend/app/middleware/rate_limit.py`

**Purpose**: Enforces rate limiting to prevent abuse.

**Configuration**:
```python
from backend.app.middleware.rate_limit import setup_rate_limiting

setup_rate_limiting(app)
```

**Rate Limits**:
- **Default**: 100 requests per minute per IP
- **Authenticated**: 200 requests per minute per user
- **Admin**: 1000 requests per minute

**Features**:
- IP-based rate limiting
- User-based rate limiting (authenticated)
- Redis-backed distributed rate limiting
- In-memory fallback if Redis unavailable

**Headers**:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time (Unix timestamp)

**Response on Limit Exceeded**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later."
  },
  "status": "error"
}
```

**Status Code**: `429 Too Many Requests`

### 9. DistributedRateLimitMiddleware

**Location**: `backend/app/middleware/distributed_rate_limit.py`

**Purpose**: Distributed rate limiting using Redis.

**Features**:
- Redis-backed rate limiting
- Works across multiple server instances
- Sliding window algorithm
- Configurable time windows

**Configuration**:
```python
from backend.app.middleware.distributed_rate_limit import DistributedRateLimitMiddleware

app.add_middleware(DistributedRateLimitMiddleware)
```

### 10. ErrorHandlerMiddleware

**Location**: `backend/app/middleware/error_handler.py`

**Purpose**: Centralized error handling and formatting.

**Configuration**:
```python
from backend.app.middleware.error_handler import add_error_handlers

add_error_handlers(app)
```

**Error Types Handled**:
- `ValidationError` (400): Invalid input
- `AuthenticationError` (401): Missing/invalid token
- `AuthorizationError` (403): Insufficient permissions
- `NotFoundError` (404): Resource not found
- `RateLimitError` (429): Rate limit exceeded
- `InternalServerError` (500): Server errors
- `ServiceUnavailableError` (503): External service down

**Error Response Format**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "validation error details"
    }
  },
  "status": "error",
  "request_id": "unique-request-id"
}
```

**Features**:
- Consistent error format
- Request ID in error responses
- Detailed error logging
- Security: Hides sensitive error details in production

### 11. WebSocketSecurityMiddleware

**Location**: `backend/app/middleware/websocket_security.py`

**Purpose**: Security and cleanup for WebSocket connections.

**Features**:
- WebSocket authentication
- Connection tracking
- Automatic cleanup of stale connections
- Rate limiting for WebSocket messages

**Configuration**:
```python
from backend.app.middleware.websocket_security import websocket_cleanup_task

# Cleanup task runs periodically
```

## Custom Middleware Creation

### Example: Custom Logging Middleware

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "request_id": request.state.request_id
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} ({process_time:.3f}s)",
            extra={
                "status_code": response.status_code,
                "process_time": process_time,
                "request_id": request.state.request_id
            }
        )
        
        return response

# Add to app
app.add_middleware(LoggingMiddleware)
```

## Middleware Best Practices

### 1. Order Matters

Middleware is executed in the order it's added. Add middleware in the correct order:

```python
# 1. Request ID (first)
app.add_middleware(RequestIdMiddleware)

# 2. Compression
app.add_middleware(GZipMiddleware)

# 3. Security
app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS
app.add_middleware(CORSMiddleware)

# 5. Rate limiting
setup_rate_limiting(app)

# 6. Error handling (last, but added via function)
add_error_handlers(app)
```

### 2. Performance

- Keep middleware lightweight
- Use async operations
- Cache expensive operations
- Avoid blocking operations

### 3. Error Handling

- Catch and handle errors gracefully
- Log errors with context
- Return appropriate status codes
- Don't expose sensitive information

### 4. Security

- Validate all inputs
- Sanitize outputs
- Use secure headers
- Implement rate limiting
- Log security events

## Testing Middleware

### Unit Testing

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_rate_limiting():
    # Make many requests
    for _ in range(101):
        response = client.get("/api/v1/attractions")
    
    # 101st request should be rate limited
    assert response.status_code == 429

def test_cors_headers():
    response = client.options("/api/v1/attractions")
    assert "Access-Control-Allow-Origin" in response.headers
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_request_id_middleware():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert "X-Request-ID" in response.headers
```

## Monitoring Middleware

### Metrics

Middleware can expose metrics:

```python
from backend.app.core.metrics import increment_counter

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Increment request counter
        increment_counter("http_requests_total", {
            "method": request.method,
            "status": response.status_code
        })
        
        return response
```

### Logging

Middleware should log important events:

```python
logger.info(
    "Rate limit exceeded",
    extra={
        "ip": request.client.host,
        "user_id": getattr(request.state, "user_id", None),
        "request_id": request.state.request_id
    }
)
```

## Configuration

Middleware configuration is in `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_AUTHENTICATED: int = 200
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Timeout
    REQUEST_TIMEOUT_SECONDS: int = 30
```

## Troubleshooting

### Middleware Not Executing

- Check middleware order
- Verify middleware is added to app
- Check for exceptions in middleware

### Rate Limiting Issues

- Check Redis connection
- Verify rate limit configuration
- Check IP detection (behind proxy)

### CORS Issues

- Verify allowed origins
- Check preflight requests
- Verify credentials configuration

### Performance Issues

- Profile middleware execution time
- Check for blocking operations
- Optimize database queries in middleware

## Future Enhancements

1. **Request/Response Transformation**: Transform requests/responses
2. **API Key Middleware**: API key authentication
3. **Request Validation**: Pre-route validation
4. **Response Compression**: Advanced compression
5. **Request Logging**: Detailed request logging

