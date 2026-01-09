"""
Integration tests for OAuth API
Tests the OAuth login endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_oauth_providers_endpoint(async_client):
    """Test getting list of OAuth providers"""
    response = await async_client.get("/api/v1/oauth/providers")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "providers" in data
    assert "total" in data
    assert isinstance(data["providers"], list)


@pytest.mark.asyncio
async def test_oauth_login_invalid_provider(async_client):
    """Test OAuth login with invalid provider"""
    payload = {
        "provider": "invalid_provider",
        "access_token": "test_token"
    }
    
    response = await async_client.post(
        "/api/v1/oauth/login",
        json=payload
    )
    
    assert response.status_code == 400  # Bad request


@pytest.mark.asyncio
async def test_oauth_login_missing_token(async_client):
    """Test OAuth login without access token"""
    payload = {
        "provider": "google"
        # Missing access_token
    }
    
    response = await async_client.post(
        "/api/v1/oauth/login",
        json=payload
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_oauth_login_google_structure(async_client):
    """Test OAuth login request structure for Google"""
    payload = {
        "provider": "google",
        "access_token": "fake_token_for_testing"
    }
    
    response = await async_client.post(
        "/api/v1/oauth/login",
        json=payload
    )
    
    # Will fail auth but should process request structure
    assert response.status_code in [401, 500]  # Unauthorized or server error


@pytest.mark.asyncio
async def test_oauth_login_facebook_structure(async_client):
    """Test OAuth login request structure for Facebook"""
    payload = {
        "provider": "facebook",
        "access_token": "fake_token_for_testing"
    }
    
    response = await async_client.post(
        "/api/v1/oauth/login",
        json=payload
    )
    
    # Will fail auth but should process request structure
    assert response.status_code in [401, 500]

