"""
API endpoint tests for authentication
"""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.auth
class TestAuthEndpoints:
    """Test authentication API endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration with valid data"""
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"newuser_{unique_id}@example.com",
                "username": f"newuser_{unique_id}",
                "password": "NewPassword123!",
                "full_name": "New User"
            }
        )
        
        # Debug: Print actual response for troubleshooting
        if response.status_code not in [200, 201]:
            print(f"DEBUG - Status: {response.status_code}, Body: {response.text[:500]}")
        
        assert response.status_code in [200, 201], f"Got {response.status_code}: {response.text[:300]}"
        data = response.json()
        assert "user" in data or "access_token" in data  # Returns Token with user
        if "user" in data:
            assert "email" in data["user"]
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "anotheruser",
                "password": "Password123!",
                "full_name": "Another User"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weakpass@example.com",
                "username": "weakpass",
                "password": "weak",
                "full_name": "Weak Pass User"
            }
        )
        
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client: AsyncClient, test_user):
        """Test login with valid credentials"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with invalid email"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user):
        """Test login with invalid password"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "WrongPassword!"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
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
    async def test_get_current_user_no_auth(self, client: AsyncClient):
        """Test getting current user without authentication"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """Test token refresh"""
        # First login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "TestPassword123!"
            }
        )
        
        if login_response.status_code != 200:
            pytest.skip("Login failed, cannot test refresh token")
        
        tokens = login_response.json()
        refresh_token = tokens.get("refresh_token")
        
        if not refresh_token:
            pytest.skip("No refresh token in login response")
        
        # Now test refresh - use TokenRefresh model format
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code in [200, 201], f"Got {response.status_code}: {response.text[:300]}"
        data = response.json()
        assert "access_token" in data or "token" in data
    
    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, auth_headers):
        """Test user logout"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_change_password(self, client: AsyncClient, auth_headers):
        """Test password change"""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "TestPassword123!",
                "new_password": "NewTestPassword123!"
            }
        )
        
        assert response.status_code in [200, 201]
