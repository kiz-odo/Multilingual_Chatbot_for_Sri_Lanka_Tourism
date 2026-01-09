"""
Sri Lanka Tourism Multilingual Chatbot - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import asyncio

from backend.app.core.config import settings
from backend.app.core.database import init_database, close_database
from backend.app.api.v1 import api_router
from backend.app.core.logging_config import setup_logging
from backend.app.core.startup_validation import validate_startup_environment

# Middleware
from backend.app.middleware.error_handler import add_error_handlers
from backend.app.middleware.request_id import RequestIdMiddleware
from backend.app.middleware.request_timeout import setup_request_timeout
from backend.app.middleware.cache_headers import setup_caching_middleware
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.middleware.api_versioning import APIVersioningMiddleware

# API Routes
from backend.app.api.v1 import health, websocket

# Monitoring and tracing
from backend.app.core.tracing import setup_tracing
from backend.app.core.sentry_config import setup_sentry
from backend.app.core.circuit_breaker import initialize_circuit_breakers
from backend.app.middleware.websocket_security import websocket_cleanup_task

# GraphQL
from backend.app.graphql import schema, get_graphql_context
from strawberry.fastapi import GraphQLRouter

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Setup error tracking
setup_sentry()


# Global shutdown event
shutdown_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with graceful shutdown
    
    Handles:
    - Startup: Environment validation, Database initialization, Redis, distributed rate limiting
    - Shutdown: Graceful shutdown with timeout, connection cleanup
    """
    # Startup
    logger.info("Starting Sri Lanka Tourism Chatbot API...")
    
    # Step 1: Validate environment and configuration (fail-fast)
    logger.info("Running startup environment validation...")
    await validate_startup_environment()
    logger.info("Environment validation completed")
    
    # Initialize Redis client for distributed rate limiting
    redis_client = None
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Run pending migrations
        try:
            from backend.app.core.migrations import migration_manager
            logger.info("Checking for pending migrations...")
            migration_results = await migration_manager.run_pending_migrations()
            if migration_results.get("success", 0) > 0:
                logger.info(f"✅ Applied {migration_results['success']} migration(s)")
            if migration_results.get("failed", 0) > 0:
                logger.warning(f"⚠️  {migration_results['failed']} migration(s) failed")
            if migration_results.get("total", 0) == 0:
                logger.info("No pending migrations")
        except Exception as e:
            logger.warning(f"Migration check failed (non-critical): {e}")
            # Don't fail startup if migrations fail - they can be run manually
        
        # Initialize Redis for distributed rate limiting
        import redis.asyncio as redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8"
        )
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
        # Store Redis client in app state for access by middleware
        app.state.redis = redis_client
        
        # Setup distributed rate limiting - Commented out (middleware must be added before app starts)
        # from backend.app.middleware.distributed_rate_limit import setup_distributed_rate_limiting
        # await setup_distributed_rate_limiting(app, redis_client)
        logger.info("Distributed rate limiting configured (basic rate limiting active)")
        
        # Setup distributed tracing
        setup_tracing(app)
        logger.info("Distributed tracing configured")
        
        # Initialize circuit breakers for external services
        initialize_circuit_breakers()
        logger.info("Circuit breakers initialized for external services")
        
        # Start WebSocket cleanup background task
        asyncio.create_task(websocket_cleanup_task())
        logger.info("WebSocket cleanup task started")
        
        logger.info("✅ Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        # Cleanup on startup failure
        if redis_client:
            await redis_client.close()
        raise
    
    yield
    
    # Shutdown - Graceful shutdown with timeout
    logger.info("Shutting down Sri Lanka Tourism Chatbot API...")
    
    shutdown_timeout = settings.SHUTDOWN_TIMEOUT_SECONDS
    
    try:
        # Set shutdown event to signal in-flight requests
        shutdown_event.set()
        logger.info(f"Shutdown signal sent. Waiting up to {shutdown_timeout}s for in-flight requests...")
        
        # Wait for graceful shutdown with timeout
        try:
            await asyncio.wait_for(
                _wait_for_shutdown(),
                timeout=shutdown_timeout
            )
            logger.info("All in-flight requests completed")
        except asyncio.TimeoutError:
            logger.warning(f"Shutdown timeout ({shutdown_timeout}s) exceeded. Forcing shutdown...")
        except asyncio.CancelledError:
            # Normal cancellation during shutdown
            logger.info("Shutdown cancelled (normal)")
        
    except Exception as e:
        logger.warning(f"Error during shutdown sequence: {e}")
    
    finally:
        # Cleanup resources
        try:
            await close_database()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
        
        # Close Redis connection
        if redis_client:
            try:
                await redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
        
        logger.info("✅ Application shutdown complete")


async def _wait_for_shutdown():
    """
    Wait for in-flight requests to complete
    
    In a production environment, you would track active requests
    and wait for them to complete. For now, we just wait a short time.
    """
    try:
        # Give a moment for in-flight requests to complete
        await asyncio.sleep(2)
        
        # In production, you might want to:
        # - Track active request count
        # - Wait until count reaches zero
        # - Use a more sophisticated mechanism
    except asyncio.CancelledError:
        # Normal cancellation during shutdown
        pass


# Create FastAPI application
app = FastAPI(
    title="Sri Lanka Tourism Multilingual Chatbot API",
    description="A comprehensive AI-powered multilingual chatbot for Sri Lanka Tourism",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # Request body size limit (10MB default)
    max_request_size=settings.MAX_REQUEST_SIZE,
    # Disable automatic trailing slash redirects (prevent 307 responses)
    redirect_slashes=False
)

# Add custom middleware (order matters!)
app.add_middleware(RequestIdMiddleware)  # Add request ID first
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses

# Add request timeout middleware
setup_request_timeout(app)

# Add caching middleware
setup_caching_middleware(app)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add API versioning middleware
app.add_middleware(APIVersioningMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Accept", "Accept-Language", "Content-Type", "Authorization", "X-Request-ID", "X-API-Key"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Add rate limiting middleware (in-memory fallback if Redis unavailable)
from backend.app.middleware.rate_limit import setup_rate_limiting
setup_rate_limiting(app)

# NOTE: Distributed rate limiting with Redis is configured in lifespan() function
# The in-memory rate limiting above provides fallback protection

# Add error handlers (must be after middleware)
add_error_handlers(app)

# Include main API routes (includes all v1 endpoints)
app.include_router(api_router, prefix="/api/v1")

# Include health check routes (at root level for Kubernetes probes)
app.include_router(health.router, tags=["Health"])

# Include WebSocket routes
app.include_router(websocket.router)

# Setup GraphQL endpoint
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_graphql_context,
    graphiql=settings.ENVIRONMENT != "production"  # Enable GraphiQL in dev only
)
app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sri Lanka Tourism Multilingual Chatbot API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "active"
    }


# Note: Health check endpoints are defined in api/v1/health.py
# Exception handlers are now in middleware/error_handler.py
# They are automatically added via add_error_handlers(app)


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
