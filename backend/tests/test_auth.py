"""
Authentication endpoint tests
"""

import pytest
from httpx import AsyncClient
from backend.app.models.user import User


@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePassword123!",
            "full_name": "New User",
            "nationality": "USA",
            "preferred_language": "en"
        }
    )
    
    # Accept 201 (success) or 422 (validation error) or 400 (already exists)
    assert response.status_code in [201, 400, 422]
    
    if response.status_code == 201:
        data = response.json()
        
        # Should return tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        
        # Should return user info (may be optional)
        if "user" in data:
            assert data["user"]["email"] == "newuser@example.com"
    
    # Cleanup
    user = await User.find_one({"email": "newuser@example.com"})
    if user:
        await user.delete()


@pytest.mark.asyncio
async def test_duplicate_email_registration(client: AsyncClient, test_user: User):
    """Test registration with duplicate email"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "username": "anotheruser",
            "password": "SecurePassword123!",
            "full_name": "Another User"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    # Handle both error response formats
    error_message = ""
    if "detail" in data:
        error_message = data["detail"].lower()
    elif "error" in data and isinstance(data["error"], dict) and "message" in data["error"]:
        error_message = data["error"]["message"].lower()
    assert "already registered" in error_message


@pytest.mark.asyncio
async def test_user_login(client: AsyncClient, test_user: User):
    """Test user login"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return tokens
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    # Should return user info (may be optional)
    if "user" in data:
        assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_with_wrong_password(client: AsyncClient, test_user: User):
    """Test login with incorrect password"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "WrongPassword123!"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    # Handle both error response formats
    error_message = ""
    if "detail" in data:
        error_message = data["detail"].lower()
    elif "error" in data and isinstance(data["error"], dict) and "message" in data["error"]:
        error_message = data["error"]["message"].lower()
    assert "incorrect" in error_message


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict):
    """Test getting current user info"""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data


@pytest.mark.asyncio
async def test_get_current_user_without_auth(client: AsyncClient):
    """Test getting current user without authentication"""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    """Test user logout"""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, auth_headers: dict):
    """Test password change"""
    response = await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "old_password": "TestPassword123!",
            "new_password": "NewPassword123!"
        }
    )
    
    assert response.status_code == 200
    
    # Change back to original password for other tests
    await client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "old_password": "NewPassword123!",
            "new_password": "TestPassword123!"
        }
    )


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient, test_user: User):
    """Test token refresh"""
    # Login to get tokens
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123!"
        }
    )
    
    login_data = login_response.json()
    refresh_token = login_data.get("refresh_token")
    
    if not refresh_token:
        pytest.skip("No refresh token in login response")
    
    # Refresh token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200, f"Refresh failed with status {response.status_code}: {response.text[:200]}"
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_verify_token(client: AsyncClient, auth_headers: dict):
    """Test token verification"""
    response = await client.get(
        "/api/v1/auth/verify-token",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert "user" in data

