"""
OAuth2 Social Login API Endpoints
Supports Google and Facebook authentication
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import logging

from backend.app.services.oauth_service import get_oauth_service
from backend.app.middleware.error_handler import BadRequestException

router = APIRouter(prefix="/oauth", tags=["OAuth2 Social Login"])
logger = logging.getLogger(__name__)


class OAuthLoginRequest(BaseModel):
    """OAuth login request"""
    provider: str = Field(..., description="OAuth provider: google or facebook")
    access_token: str = Field(..., description="OAuth access token from provider")


class OAuthLoginResponse(BaseModel):
    """OAuth login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=OAuthLoginResponse)
async def oauth_login(request: OAuthLoginRequest):
    """
    🔐 **OAuth2 Social Login**
    
    Authenticate with Google or Facebook account.
    
    **Supported Providers:**
    - `google` - Sign in with Google
    - `facebook` - Sign in with Facebook
    
    **How it works:**
    1. Client application gets OAuth token from Google/Facebook SDK
    2. Send token to this endpoint
    3. Backend verifies token with provider
    4. Returns JWT access/refresh tokens
    5. User is logged in!
    
    **Example:**
    ```json
    {
      "provider": "google",
      "access_token": "ya29.a0AfH6SMB..."
    }
    ```
    
    **Response:**
    ```json
    {
      "access_token": "eyJ0eXAiOiJKV1Q...",
      "refresh_token": "eyJ0eXAiOiJKV1Q...",
      "token_type": "bearer",
      "user": {
        "id": "user123",
        "email": "user@example.com",
        "username": "user",
        "full_name": "John Doe",
        "profile_picture": "https://...",
        "oauth_provider": "google"
      }
    }
    ```
    
    **Client Integration Example:**
    ```python
    # 1. Use Google/Facebook SDK to get token
    # token = get_oauth_token_from_provider()
    
    # 2. Send to backend API
    import requests
    response = requests.post('/api/v1/oauth/login', 
        json={
            'provider': 'google',
            'access_token': token
        })
    
    const data = await response.json();
    
    // 3. Store JWT tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    // 4. User is logged in!
    ```
    """
    try:
        # Validate provider
        if request.provider.lower() not in ["google", "facebook"]:
            raise BadRequestException(
                f"Unsupported OAuth provider: {request.provider}. "
                "Supported providers: google, facebook"
            )
        
        # Authenticate with OAuth
        oauth_service = get_oauth_service()
        result = await oauth_service.authenticate_with_oauth(
            provider_name=request.provider.lower(),
            access_token=request.access_token
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth authentication failed. Token may be invalid or expired."
            )
        
        logger.info(f"User {result['user']['email']} logged in via {request.provider}")
        
        return OAuthLoginResponse(**result)
        
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"OAuth login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )


@router.get("/providers")
async def get_oauth_providers():
    """
    📋 **Get Available OAuth Providers**
    
    Returns list of configured OAuth providers.
    """
    from backend.app.core.config import settings
    
    providers = []
    
    if settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET:
        providers.append({
            "name": "google",
            "display_name": "Google",
            "icon": "🔵",
            "enabled": True
        })
    
    if settings.FACEBOOK_APP_ID and settings.FACEBOOK_APP_SECRET:
        providers.append({
            "name": "facebook",
            "display_name": "Facebook",
            "icon": "🔵",
            "enabled": True
        })
    
    return {
        "providers": providers,
        "total": len(providers)
    }

