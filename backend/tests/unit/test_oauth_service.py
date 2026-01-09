"""
Unit tests for OAuth Service
Tests Google and Facebook OAuth authentication
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from backend.app.services.oauth_service import (
    OAuthService,
    GoogleOAuthProvider,
    FacebookOAuthProvider
)


@pytest.fixture
def oauth_service():
    """Create OAuthService instance"""
    return OAuthService()


@pytest.fixture
def mock_google_token_info():
    """Mock Google token info response"""
    return {
        "aud": "test_client_id",
        "exp": (datetime.utcnow().timestamp() + 3600),  # 1 hour from now
        "email": "test@gmail.com",
        "email_verified": True
    }


@pytest.fixture
def mock_google_user_info():
    """Mock Google user info response"""
    return {
        "email": "test@gmail.com",
        "verified_email": True,
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/photo.jpg",
        "locale": "en",
        "id": "google123"
    }


def test_oauth_service_has_providers(oauth_service):
    """Test that OAuth service has configured providers"""
    assert "google" in oauth_service.providers
    assert "facebook" in oauth_service.providers


def test_get_provider(oauth_service):
    """Test getting provider by name"""
    google = oauth_service.get_provider("google")
    facebook = oauth_service.get_provider("facebook")
    
    assert isinstance(google, GoogleOAuthProvider)
    assert isinstance(facebook, FacebookOAuthProvider)
    
    # Test case insensitivity
    google2 = oauth_service.get_provider("GOOGLE")
    assert isinstance(google2, GoogleOAuthProvider)


def test_get_unknown_provider(oauth_service):
    """Test getting unknown provider returns None"""
    unknown = oauth_service.get_provider("twitter")
    assert unknown is None


@pytest.mark.asyncio
async def test_authenticate_with_oauth_google_new_user(
    oauth_service,
    mock_google_token_info,
    mock_google_user_info
):
    """Test OAuth authentication with Google for new user"""
    # Create mock user that will be returned after insert
    new_user = Mock()
    new_user.id = "new_user_123"
    new_user.email = "test@gmail.com"
    new_user.username = "test"
    new_user.full_name = "Test User"
    new_user.oauth_provider = "google"
    new_user.oauth_id = "google_user_123"
    new_user.is_email_verified = True
    
    # Mock insert to be async
    async def mock_insert():
        return new_user
    new_user.insert = mock_insert
    
    with patch.object(
        GoogleOAuthProvider,
        'verify_token',
        return_value=mock_google_token_info
    ):
        with patch.object(
            GoogleOAuthProvider,
            'get_user_info',
            return_value=mock_google_user_info
        ):
            # Mock User.find_one to return None (user doesn't exist)
            # Create mock for User.find_one that returns awaitable
            mock_find_one = AsyncMock(return_value=None)
            
            with patch('backend.app.services.oauth_service.User') as MockUser:
                MockUser.find_one = mock_find_one
                MockUser.return_value = new_user
                
                with patch('backend.app.services.auth_service.AuthService.create_access_token') as mock_access:
                    with patch('backend.app.services.auth_service.AuthService.create_refresh_token') as mock_refresh:
                        mock_access.return_value = "access_token_123"
                        mock_refresh.return_value = "refresh_token_123"
                        
                        result = await oauth_service.authenticate_with_oauth(
                            provider_name="google",
                            access_token="google_token_123"
                        )
                        
                        assert result is not None
                        assert result["access_token"] == "access_token_123"
                        assert result["refresh_token"] == "refresh_token_123"
                        assert result["user"]["email"] == "test@gmail.com"
                        assert result["user"]["oauth_provider"] == "google"


@pytest.mark.asyncio
async def test_authenticate_with_oauth_google_existing_user(
    oauth_service,
    mock_google_token_info,
    mock_google_user_info
):
    """Test OAuth authentication with Google for existing user"""
    existing_user = Mock()
    existing_user.id = "user123"
    existing_user.email = "test@gmail.com"
    existing_user.username = "testuser"
    existing_user.full_name = "Test User"
    existing_user.oauth_provider = None
    existing_user.profile_picture = None
    existing_user.is_email_verified = False
    
    # Create AsyncMock for save that updates the field
    async def mock_save():
        existing_user.is_email_verified = True
    
    existing_user.save = AsyncMock(side_effect=mock_save)
    
    with patch.object(
        GoogleOAuthProvider,
        'verify_token',
        return_value=mock_google_token_info
    ):
        with patch.object(
            GoogleOAuthProvider,
            'get_user_info',
            return_value=mock_google_user_info
        ):
            with patch('backend.app.models.user.User.find_one', new_callable=AsyncMock) as mock_find:
                mock_find.return_value = existing_user
                
                with patch('backend.app.services.auth_service.AuthService.create_access_token') as mock_access:
                    with patch('backend.app.services.auth_service.AuthService.create_refresh_token') as mock_refresh:
                        mock_access.return_value = "access_token_123"
                        mock_refresh.return_value = "refresh_token_123"
                        
                        result = await oauth_service.authenticate_with_oauth(
                            provider_name="google",
                            access_token="google_token_123"
                        )
                        
                        assert result is not None
                        # Verify user was updated
                        assert existing_user.oauth_provider == "google"
                        assert existing_user.profile_picture == "https://example.com/photo.jpg"
                        assert existing_user.is_email_verified == True  # Should be updated from False to True
                        existing_user.save.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_with_invalid_token(oauth_service):
    """Test OAuth authentication with invalid token"""
    with patch.object(
        GoogleOAuthProvider,
        'verify_token',
        return_value=None  # Invalid token
    ):
        result = await oauth_service.authenticate_with_oauth(
            provider_name="google",
            access_token="invalid_token"
        )
        
        assert result is None


@pytest.mark.asyncio
async def test_authenticate_with_unknown_provider(oauth_service):
    """Test OAuth authentication with unknown provider"""
    result = await oauth_service.authenticate_with_oauth(
        provider_name="unknown_provider",
        access_token="some_token"
    )
    
    assert result is None


@pytest.mark.asyncio
async def test_google_provider_verify_expired_token():
    """Test Google provider rejects expired token"""
    provider = GoogleOAuthProvider()
    provider.client_id = "test_client_id"
    
    expired_token_info = {
        "aud": "test_client_id",
        "exp": datetime.utcnow().timestamp() - 3600,  # Expired 1 hour ago
    }
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expired_token_info
        mock_get.return_value = mock_response
        
        result = await provider.verify_token("expired_token")
        
        assert result is None  # Expired token should be rejected

