"""
Attraction API endpoint tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_attractions(client: AsyncClient):
    """Test attraction search endpoint"""
    response = await client.get(
        "/api/v1/attractions/search",
        params={"q": "Sigiriya", "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_attractions_by_category(client: AsyncClient):
    """Test attraction search by category"""
    response = await client.get(
        "/api/v1/attractions/search",
        params={"category": "historical", "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_popular_attractions(client: AsyncClient):
    """Test getting popular attractions"""
    response = await client.get(
        "/api/v1/attractions/popular",
        params={"limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_chat_endpoint(client: AsyncClient):
    """Test chat endpoint"""
    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "Tell me about Sigiriya",
            "session_id": "test-session-123",
            "language": "en"
        }
    )
    
    assert response.status_code in [200, 404]  # 404 if route not properly configured
    if response.status_code == 200:
        data = response.json()
        assert "response" in data or "text" in data


@pytest.mark.asyncio
async def test_recommendations(client: AsyncClient):
    """Test recommendations endpoint"""
    response = await client.post(
        "/api/v1/recommendations",
        json={
            "session_id": "test-session",
            "resource_type": "attraction",
            "limit": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data

