"""
Database Retry Logic Utility
Handles transient database failures with exponential backoff
"""

import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
from pymongo.errors import (
    AutoReconnect,
    ServerSelectionTimeoutError,
    NetworkTimeout,
    ConnectionFailure,
    OperationFailure
)

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Retryable MongoDB errors
RETRYABLE_ERRORS = (
    AutoReconnect,
    ServerSelectionTimeoutError,
    NetworkTimeout,
    ConnectionFailure,
)

# Type variable for generic return type
T = TypeVar('T')


def calculate_backoff_delay(attempt: int, base_delay: float, max_delay: float, exponential_base: float) -> float:
    """
    Calculate exponential backoff delay
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
    
    Returns:
        Delay in seconds
    """
    delay = base_delay * (exponential_base ** attempt)
    return min(delay, max_delay)


async def retry_db_operation(
    operation: Callable[[], T],
    max_attempts: Optional[int] = None,
    initial_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    exponential_base: Optional[float] = None,
    retryable_errors: tuple = RETRYABLE_ERRORS,
    operation_name: str = "database operation"
) -> T:
    """
    Retry a database operation with exponential backoff
    
    Args:
        operation: Async function to execute
        max_attempts: Maximum retry attempts (defaults to config)
        initial_delay: Initial delay in seconds (defaults to config)
        max_delay: Maximum delay in seconds (defaults to config)
        exponential_base: Exponential backoff base (defaults to config)
        retryable_errors: Tuple of error types to retry on
        operation_name: Name of operation for logging
    
    Returns:
        Result of the operation
    
    Raises:
        Last exception if all retries fail
    """
    max_attempts = max_attempts or settings.DB_RETRY_MAX_ATTEMPTS
    initial_delay = initial_delay or settings.DB_RETRY_INITIAL_DELAY
    max_delay = max_delay or settings.DB_RETRY_MAX_DELAY
    exponential_base = exponential_base or settings.DB_RETRY_EXPONENTIAL_BASE
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            if asyncio.iscoroutinefunction(operation):
                result = await operation()
            else:
                result = operation()
            return result
            
        except retryable_errors as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                delay = calculate_backoff_delay(attempt, initial_delay, max_delay, exponential_base)
                logger.warning(
                    f"Retryable error in {operation_name} (attempt {attempt + 1}/{max_attempts}): {type(e).__name__}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Failed {operation_name} after {max_attempts} attempts: {type(e).__name__}: {str(e)}"
                )
                raise
                
        except OperationFailure as e:
            # Some operation failures are retryable (e.g., write conflicts)
            if e.has_error_label("TransientTransactionError") or e.has_error_label("UnknownTransactionCommitResult"):
                if attempt < max_attempts - 1:
                    delay = calculate_backoff_delay(attempt, initial_delay, max_delay, exponential_base)
                    logger.warning(
                        f"Transient transaction error in {operation_name} (attempt {attempt + 1}/{max_attempts}). "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    last_exception = e
                    continue
            # Non-retryable operation failure
            logger.error(f"Non-retryable operation failure in {operation_name}: {str(e)}")
            raise
            
        except Exception as e:
            # Non-retryable error
            logger.error(f"Non-retryable error in {operation_name}: {type(e).__name__}: {str(e)}")
            raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError(f"Failed {operation_name} after {max_attempts} attempts")


def retry_db_decorator(
    max_attempts: Optional[int] = None,
    initial_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    exponential_base: Optional[float] = None,
    retryable_errors: tuple = RETRYABLE_ERRORS
):
    """
    Decorator to automatically retry database operations
    
    Usage:
        @retry_db_decorator(max_attempts=5)
        async def get_user(user_id: str):
            return await User.get(user_id)
    
    Args:
        max_attempts: Maximum retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Exponential backoff base
        retryable_errors: Tuple of error types to retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            async def operation():
                return await func(*args, **kwargs)
            
            return await retry_db_operation(
                operation,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                retryable_errors=retryable_errors,
                operation_name=func.__name__
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            def operation():
                return func(*args, **kwargs)
            
            # For sync functions, we need to run in event loop
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(
                retry_db_operation(
                    operation,
                    max_attempts=max_attempts,
                    initial_delay=initial_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    retryable_errors=retryable_errors,
                    operation_name=func.__name__
                )
            )
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator




