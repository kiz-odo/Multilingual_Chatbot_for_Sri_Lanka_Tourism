"""
Unit tests for the circuit breaker utilities (backend/app/core/circuit_breaker.py).

Pure, deterministic logic — no external services required.
"""

from datetime import datetime, timedelta

import pytest

from backend.app.core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    get_circuit_breaker,
    call_with_fallback,
    with_circuit_breaker,
    initialize_circuit_breakers,
    get_all_circuit_breaker_status,
    reset_circuit_breaker,
    EXTERNAL_SERVICES,
)


async def _ok(value="ok"):
    return value


async def _boom():
    raise ValueError("boom")


class TestCircuitBreakerStateMachine:
    async def test_closed_allows_calls(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        result = await cb.call(_ok, "hello")
        assert result == "hello"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    async def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(_boom)
        assert cb.state == "OPEN"
        assert cb.failure_count == 2

    async def test_open_blocks_requests(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=60)
        with pytest.raises(ValueError):
            await cb.call(_boom)
        assert cb.state == "OPEN"
        # Now the circuit is open and should block without calling the function
        with pytest.raises(CircuitBreakerError):
            await cb.call(_ok)

    async def test_should_attempt_reset_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        with pytest.raises(ValueError):
            await cb.call(_boom)
        assert cb.state == "OPEN"
        # Pretend enough time has passed
        cb.last_failure_time = datetime.utcnow() - timedelta(seconds=5)
        assert cb._should_attempt_reset() is True

    async def test_half_open_success_closes_circuit(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        with pytest.raises(ValueError):
            await cb.call(_boom)
        cb.last_failure_time = datetime.utcnow() - timedelta(seconds=5)
        # Successful call in HALF_OPEN should close the circuit and reset count
        result = await cb.call(_ok, "recovered")
        assert result == "recovered"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    async def test_should_not_reset_when_closed(self):
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=1)
        assert cb._should_attempt_reset() is False


class TestCircuitBreakerRegistry:
    def test_get_circuit_breaker_creates_and_reuses(self):
        cb1 = get_circuit_breaker("unit-test-service")
        cb2 = get_circuit_breaker("unit-test-service")
        assert cb1 is cb2
        assert isinstance(cb1, CircuitBreaker)

    def test_initialize_and_status_and_reset(self):
        initialize_circuit_breakers()
        status = get_all_circuit_breaker_status()
        # Every pre-configured service should have a status entry
        for name in EXTERNAL_SERVICES:
            assert name in status
            assert status[name]["state"] == "CLOSED"
            assert status[name]["failure_count"] == 0

        # Drive one into a failed state, then reset it
        cb = get_circuit_breaker("gemini")
        cb.state = "OPEN"
        cb.failure_count = 9
        cb.last_failure_time = datetime.utcnow()
        assert reset_circuit_breaker("gemini") is True
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
        assert cb.last_failure_time is None

    def test_reset_unknown_service_returns_false(self):
        assert reset_circuit_breaker("does-not-exist-xyz") is False


class TestCallWithFallback:
    async def test_primary_success(self):
        result = await call_with_fallback(_ok)
        assert result == "ok"

    async def test_uses_fallback_func_on_primary_failure(self):
        async def fallback():
            return "fallback-func"

        result = await call_with_fallback(_boom, fallback)
        assert result == "fallback-func"

    async def test_uses_fallback_value_when_all_fail(self):
        result = await call_with_fallback(_boom, _boom, "default-value")
        assert result == "default-value"

    async def test_no_fallback_func_returns_value(self):
        result = await call_with_fallback(_boom, None, "just-value")
        assert result == "just-value"


class TestWithCircuitBreakerDecorator:
    async def test_decorator_returns_result_on_success(self):
        @with_circuit_breaker("decorated-ok")
        async def op(x):
            return x * 2

        assert await op(21) == 42

    async def test_decorator_returns_fallback_when_open(self):
        @with_circuit_breaker("decorated-open", fallback_value={"error": "unavailable"})
        async def op():
            raise RuntimeError("fail")

        # Force the underlying breaker open
        cb = get_circuit_breaker("decorated-open")
        cb.state = "OPEN"
        cb.last_failure_time = datetime.utcnow()

        assert await op() == {"error": "unavailable"}

    async def test_decorator_preserves_name(self):
        @with_circuit_breaker("decorated-name")
        async def my_named_op():
            return 1

        assert my_named_op.__name__ == "my_named_op"
