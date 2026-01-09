"""
Health check endpoint tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test basic health check endpoint"""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient):
    """Test Kubernetes liveness probe"""
    response = await client.get("/api/v1/health/live")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient):
    """Test Kubernetes readiness probe"""
    response = await client.get("/api/v1/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data
    
    # Should have checks for database, redis, rasa
    checks = data["checks"]
    assert "database" in checks
    assert "redis" in checks
    assert "rasa" in checks
    
    # Database should be healthy
    assert checks["database"]["healthy"] == True


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """Test metrics endpoint"""
    response = await client.get("/api/v1/health/metrics")
    
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "metrics" in data

