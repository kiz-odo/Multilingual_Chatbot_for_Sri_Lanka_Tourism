"""
Health check endpoints for monitoring
"""

from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime
import logging

from backend.app.core.database import db
from backend.app.core.config import settings

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic health check - returns if service is alive"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe
    Returns 200 if service is alive
    """
    return {"status": "alive"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_probe() -> Dict[str, Any]:
    """
    Kubernetes readiness probe
    Returns 200 if service is ready to accept traffic
    Checks all critical dependencies
    """
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "rasa": await check_rasa(),
        "llm": await check_llm_service(),
    }
    
    # Critical services that must be healthy
    critical_services = ["database"]
    critical_healthy = all(
        checks[service]["healthy"] 
        for service in critical_services 
        if service in checks
    )
    
    # Optional services (warn if unhealthy but still ready)
    optional_services = ["redis", "rasa", "llm"]
    optional_status = {
        service: checks[service]["healthy"]
        for service in optional_services
        if service in checks
    }
    
    return {
        "status": "ready" if critical_healthy else "not_ready",
        "critical_services_healthy": critical_healthy,
        "checks": checks,
        "optional_services": optional_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check including external APIs
    For monitoring and debugging purposes
    """
    checks = {
        "core_services": {
            "database": await check_database(),
            "redis": await check_redis(),
            "rasa": await check_rasa(),
            "llm": await check_llm_service(),
        },
        "external_apis": {
            "google_translate": check_api_configured("GOOGLE_TRANSLATE_API_KEY"),
            "google_maps": check_api_configured("GOOGLE_MAPS_API_KEY"),
            "openweather": check_api_configured("OPENWEATHER_API_KEY"),
            "currencylayer": check_api_configured("CURRENCYLAYER_API_KEY"),
        },
        "configuration": {
            "debug_mode": settings.DEBUG,
            "environment": "development" if settings.DEBUG else "production",
            "supported_languages": settings.SUPPORTED_LANGUAGES,
            "llm_enabled": settings.LLM_ENABLED,
        }
    }
    
    # Overall health status
    core_healthy = all(
        check["healthy"] 
        for check in checks["core_services"].values()
        if isinstance(check, dict) and "healthy" in check
    )
    
    return {
        "status": "healthy" if core_healthy else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_database() -> Dict[str, Any]:
    """Check MongoDB connection"""
    try:
        if db.client:
            # Ping database
            await db.client.admin.command('ping')
            return {
                "healthy": True,
                "message": "Database connection OK",
                "latency_ms": 0  # Could measure actual latency
            }
        else:
            return {
                "healthy": False,
                "message": "Database client not initialized"
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "healthy": False,
            "message": f"Database error: {str(e)}"
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis connection"""
    try:
        # Try to import redis
        import redis
        from backend.app.core.config import settings
        
        # Create Redis client
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        
        return {
            "healthy": True,
            "message": "Redis connection OK"
        }
    except ImportError:
        return {
            "healthy": False,
            "message": "Redis library not installed"
        }
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return {
            "healthy": False,
            "message": f"Redis error: {str(e)}"
        }


async def check_rasa() -> Dict[str, Any]:
    """Check Rasa server connection"""
    try:
        import httpx
        from backend.app.core.config import settings
        
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{settings.RASA_SERVER_URL}/status")
            
            if response.status_code == 200:
                return {
                    "healthy": True,
                    "message": "Rasa server OK"
                }
            else:
                return {
                    "healthy": False,
                    "message": f"Rasa server returned {response.status_code}"
                }
    except Exception as e:
        logger.warning(f"Rasa health check failed: {e}")
        return {
            "healthy": False,
            "message": f"Rasa error: {str(e)}"
        }


async def check_llm_service() -> Dict[str, Any]:
    """Check LLM service availability"""
    try:
        if not settings.LLM_ENABLED:
            return {
                "healthy": True,
                "message": "LLM service disabled by configuration",
                "enabled": False
            }
        
        from backend.app.services.llm_service import get_llm_service
        llm_service = get_llm_service()
        
        if llm_service.enabled:
            return {
                "healthy": True,
                "message": "LLM service initialized and ready",
                "enabled": True,
                "model": llm_service.model_name
            }
        else:
            return {
                "healthy": True,
                "message": "LLM service available but not initialized (lazy loading)",
                "enabled": False
            }
    except Exception as e:
        logger.warning(f"LLM health check failed: {e}")
        return {
            "healthy": False,
            "message": f"LLM error: {str(e)}",
            "enabled": False
        }


def check_api_configured(api_key_name: str) -> Dict[str, Any]:
    """Check if an external API key is configured"""
    try:
        api_key = getattr(settings, api_key_name, None)
        is_configured = bool(api_key and api_key.strip())
        
        return {
            "configured": is_configured,
            "message": "API key configured" if is_configured else "API key not configured"
        }
    except Exception as e:
        return {
            "configured": False,
            "message": f"Error checking API key: {str(e)}"
        }


@router.get("/health/metrics", status_code=status.HTTP_200_OK)
async def metrics() -> Dict[str, Any]:
    """Basic metrics endpoint (can be enhanced with Prometheus)"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "uptime_seconds": 0,  # Would need to track actual uptime
            "requests_total": 0,   # Would need counter
            "requests_failed": 0,  # Would need counter
        }
    }

