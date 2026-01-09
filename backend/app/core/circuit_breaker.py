"""
Circuit Breaker Pattern Implementation
Prevents cascading failures from external API timeouts
"""

import asyncio
import logging
from typing import Any, Callable, Optional, Dict
from datetime import datetime, timedelta
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import httpx

logger = logging.getLogger(__name__)


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for external API calls
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, block all requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should move to HALF_OPEN state"""
        if self.state == "OPEN" and self.last_failure_time:
            time_since_failure = datetime.utcnow() - self.last_failure_time
            return time_since_failure.total_seconds() >= self.recovery_timeout
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check if we should attempt reset
        if self._should_attempt_reset():
            self.state = "HALF_OPEN"
            logger.info("Circuit breaker entering HALF_OPEN state for testing")
        
        # Block requests if circuit is open
        if self.state == "OPEN":
            logger.warning("Circuit breaker is OPEN, blocking request")
            raise CircuitBreakerError("Circuit breaker is open, service unavailable")
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker test successful, moving to CLOSED state")
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            # Increment failure count
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            logger.error(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}: {e}"
            )
            
            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.critical(
                    f"Circuit breaker opened after {self.failure_count} failures. "
                    f"Will retry in {self.recovery_timeout}s"
                )
            
            raise


# Global circuit breakers for different services
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for a service"""
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )
    return _circuit_breakers[service_name]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    after=after_log(logger, logging.INFO)
)
async def call_external_api_with_retry(
    url: str,
    method: str = "GET",
    timeout: int = 10,
    **kwargs
) -> dict:
    """
    Call external API with retry logic and exponential backoff
    
    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
        **kwargs: Additional httpx client arguments
        
    Returns:
        JSON response from API
        
    Raises:
        httpx.HTTPError: If request fails after retries
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()


async def call_external_api_with_circuit_breaker(
    service_name: str,
    url: str,
    method: str = "GET",
    timeout: int = 10,
    **kwargs
) -> Optional[dict]:
    """
    Call external API with circuit breaker pattern and retry logic
    
    Combines circuit breaker protection with exponential backoff retries
    
    Args:
        service_name: Name of the service (for circuit breaker tracking)
        url: API endpoint URL
        method: HTTP method
        timeout: Request timeout in seconds
        **kwargs: Additional httpx arguments
        
    Returns:
        JSON response or None if circuit is open
        
    Example:
        result = await call_external_api_with_circuit_breaker(
            "google_maps",
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": "Colombo"}
        )
    """
    circuit_breaker = get_circuit_breaker(service_name)
    
    try:
        return await circuit_breaker.call(
            call_external_api_with_retry,
            url=url,
            method=method,
            timeout=timeout,
            **kwargs
        )
    except CircuitBreakerError as e:
        logger.error(f"Circuit breaker open for {service_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"External API call failed for {service_name}: {e}")
        return None


async def call_with_fallback(
    primary_func: Callable,
    fallback_func: Optional[Callable] = None,
    fallback_value: Any = None,
    *args,
    **kwargs
) -> Any:
    """
    Call function with automatic fallback on failure
    
    Args:
        primary_func: Primary function to call
        fallback_func: Optional fallback function
        fallback_value: Default fallback value
        *args, **kwargs: Arguments for primary function
        
    Returns:
        Result from primary function, fallback function, or fallback value
    """
    try:
        return await primary_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary function failed: {e}. Using fallback.")
        
        if fallback_func:
            try:
                return await fallback_func(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback function also failed: {fallback_error}")
        
        return fallback_value


# Export commonly used functions
__all__ = [
    'CircuitBreaker',
    'CircuitBreakerError',
    'get_circuit_breaker',
    'call_external_api_with_retry',
    'call_external_api_with_circuit_breaker',
    'call_with_fallback',
    'with_circuit_breaker'
]


def with_circuit_breaker(service_name: str, fallback_value: Any = None):
    """
    Decorator to wrap any async function with circuit breaker protection
    
    Usage:
        @with_circuit_breaker("gemini", fallback_value={"error": "Service unavailable"})
        async def get_gemini_response(message: str) -> dict:
            ...
    
    Args:
        service_name: Name of the service for circuit breaker tracking
        fallback_value: Value to return if circuit is open or call fails
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            circuit_breaker = get_circuit_breaker(service_name)
            
            try:
                return await circuit_breaker.call(func, *args, **kwargs)
            except CircuitBreakerError as e:
                logger.warning(f"Circuit breaker open for {service_name}: {e}")
                return fallback_value
            except Exception as e:
                logger.error(f"Error in {service_name} call: {e}")
                return fallback_value
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


# Pre-configured circuit breakers for known external services
EXTERNAL_SERVICES = {
    "gemini": {"failure_threshold": 3, "recovery_timeout": 120},
    "openai": {"failure_threshold": 3, "recovery_timeout": 120},
    "mistral": {"failure_threshold": 3, "recovery_timeout": 120},
        "openweather": {"failure_threshold": 5, "recovery_timeout": 60},
    "currencylayer": {"failure_threshold": 5, "recovery_timeout": 300},
    "google_maps": {"failure_threshold": 5, "recovery_timeout": 60},
    "tavily_search": {"failure_threshold": 5, "recovery_timeout": 60},
    "rasa": {"failure_threshold": 5, "recovery_timeout": 30},
    "translation": {"failure_threshold": 5, "recovery_timeout": 60},
    "speech": {"failure_threshold": 5, "recovery_timeout": 120},
}


def initialize_circuit_breakers():
    """
    Initialize circuit breakers for all known external services
    Call this during application startup
    """
    for service_name, config in EXTERNAL_SERVICES.items():
        _circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=config["failure_threshold"],
            recovery_timeout=config["recovery_timeout"],
            expected_exception=Exception
        )
    logger.info(f"Initialized {len(EXTERNAL_SERVICES)} circuit breakers")


def get_all_circuit_breaker_status() -> Dict[str, Dict[str, Any]]:
    """
    Get status of all circuit breakers
    
    Returns:
        Dictionary with status of each circuit breaker
    """
    status = {}
    for name, cb in _circuit_breakers.items():
        status[name] = {
            "state": cb.state,
            "failure_count": cb.failure_count,
            "last_failure": cb.last_failure_time.isoformat() if cb.last_failure_time else None,
            "failure_threshold": cb.failure_threshold,
            "recovery_timeout": cb.recovery_timeout
        }
    return status


def reset_circuit_breaker(service_name: str) -> bool:
    """
    Manually reset a circuit breaker to CLOSED state
    
    Args:
        service_name: Name of the service
        
    Returns:
        True if reset successful, False if service not found
    """
    if service_name in _circuit_breakers:
        cb = _circuit_breakers[service_name]
        cb.state = "CLOSED"
        cb.failure_count = 0
        cb.last_failure_time = None
        logger.info(f"Circuit breaker for {service_name} manually reset")
        return True
    return False

