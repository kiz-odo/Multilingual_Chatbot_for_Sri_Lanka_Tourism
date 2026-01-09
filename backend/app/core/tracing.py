"""
OpenTelemetry Distributed Tracing Configuration
Instruments FastAPI, MongoDB, Redis, and external HTTP requests
"""

import logging

logger = logging.getLogger(__name__)

# Try to import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logger.warning("OpenTelemetry SDK not available. Tracing will be disabled.")

# Try to import Jaeger exporter (deprecated in newer versions)
try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    JAEGER_AVAILABLE = True
except ImportError:
    JAEGER_AVAILABLE = False
    logger.info("Jaeger exporter not available. Using OTLP exporter if available.")

# Try to import OTLP exporter as alternative
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False

# Try to import instrumentors
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FASTAPI_INSTRUMENTATION = True
except ImportError:
    FASTAPI_INSTRUMENTATION = False

try:
    from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
    PYMONGO_INSTRUMENTATION = True
except ImportError:
    PYMONGO_INSTRUMENTATION = False

try:
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    REDIS_INSTRUMENTATION = True
except ImportError:
    REDIS_INSTRUMENTATION = False

try:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    REQUESTS_INSTRUMENTATION = True
except ImportError:
    REQUESTS_INSTRUMENTATION = False

try:
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    LOGGING_INSTRUMENTATION = True
except ImportError:
    LOGGING_INSTRUMENTATION = False

from backend.app.core.config import settings


def setup_tracing(app):
    """Setup OpenTelemetry distributed tracing"""
    
    if not settings.ENABLE_TRACING:
        logger.info("Distributed tracing is disabled")
        return
    
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available. Skipping tracing setup.")
        return
    
    try:
        # Create resource with service information
        resource = Resource(attributes={
            SERVICE_NAME: settings.OTEL_SERVICE_NAME or "tourism-chatbot",
            "service.version": settings.APP_VERSION,
            "deployment.environment": settings.ENVIRONMENT
        })
        
        # Create tracer provider
        provider = TracerProvider(resource=resource)
        
        # Configure exporter (prefer OTLP, fallback to Jaeger)
        if OTLP_AVAILABLE:
            exporter = OTLPSpanExporter()
            logger.info("Using OTLP exporter for tracing")
        elif JAEGER_AVAILABLE:
            exporter = JaegerExporter(
                agent_host_name=settings.JAEGER_AGENT_HOST or "localhost",
                agent_port=int(settings.JAEGER_AGENT_PORT or 6831),
            )
            logger.info("Using Jaeger exporter for tracing")
        else:
            logger.warning("No trace exporter available. Tracing will be limited.")
            return
        
        # Add span processor
        provider.add_span_processor(BatchSpanProcessor(exporter))
        
        # Set as global tracer provider
        trace.set_tracer_provider(provider)
        
        # Instrument FastAPI
        if FASTAPI_INSTRUMENTATION:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumented for tracing")
        
        # Instrument MongoDB
        if PYMONGO_INSTRUMENTATION:
            PymongoInstrumentor().instrument()
            logger.info("MongoDB instrumented for tracing")
        
        # Instrument Redis
        if REDIS_INSTRUMENTATION:
            RedisInstrumentor().instrument()
            logger.info("Redis instrumented for tracing")
        
        # Instrument HTTP requests
        if REQUESTS_INSTRUMENTATION:
            RequestsInstrumentor().instrument()
            logger.info("HTTP requests instrumented for tracing")
        
        # Instrument logging
        if LOGGING_INSTRUMENTATION:
            LoggingInstrumentor().instrument(set_logging_format=True)
            logger.info("Logging instrumented for tracing")
        
        logger.info("✅ Distributed tracing setup complete")
        
    except Exception as e:
        logger.error(f"Failed to setup distributed tracing: {e}", exc_info=True)


def get_tracer(name: str):
    """Get a tracer instance"""
    if OTEL_AVAILABLE:
        return trace.get_tracer(name)
    return None


def create_span(tracer, name: str, attributes: dict = None):
    """Create a new span with optional attributes"""
    if tracer is None:
        return None
    span = tracer.start_span(name)
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    return span
