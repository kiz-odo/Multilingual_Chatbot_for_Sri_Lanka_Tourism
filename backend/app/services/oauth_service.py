"""
OAuth2 Social Login Service
Supports Google and Facebook authentication
"""

import logging
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from backend.app.core.config import settings
from backend.app.models.user import User, UserRole
from backend.app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class OAuthProvider:
    """Base OAuth provider class"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from OAuth provider"""
        raise NotImplementedError
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify OAuth token"""
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth2 provider"""
    
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    
    def __init__(self):
        super().__init__("google")
        self.client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        self.client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google OAuth token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.TOKENINFO_URL,
                    params={"id_token": token}
                )
                
                if response.status_code != 200:
                    logger.warning(f"Google token verification failed: {response.status_code}")
                    return None
                
                token_info = response.json()
                
                # Verify audience (client ID)
                if token_info.get("aud") != self.client_id:
                    logger.warning("Google token audience mismatch")
                    return None
                
                # Check if token is expired
                exp = int(token_info.get("exp", 0))
                if exp < datetime.utcnow().timestamp():
                    logger.warning("Google token expired")
                    return None
                
                return token_info
                
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get Google user info: {response.status_code}")
                    return {}
                
                user_info = response.json()
                
                return {
                    "email": user_info.get("email"),
                    "email_verified": user_info.get("verified_email", False),
                    "name": user_info.get("name"),
                    "given_name": user_info.get("given_name"),
                    "family_name": user_info.get("family_name"),
                    "picture": user_info.get("picture"),
                    "locale": user_info.get("locale"),
                    "provider_id": user_info.get("id")
                }
                
        except Exception as e:
            logger.error(f"Error getting Google user info: {e}")
            return {}


class FacebookOAuthProvider(OAuthProvider):
    """Facebook OAuth2 provider"""
    
    USERINFO_URL = "https://graph.facebook.com/v18.0/me"
    DEBUG_TOKEN_URL = "https://graph.facebook.com/debug_token"
    
    def __init__(self):
        super().__init__("facebook")
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Facebook access token"""
        try:
            # Get app access token
            app_token = f"{self.app_id}|{self.app_secret}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.DEBUG_TOKEN_URL,
                    params={
                        "input_token": token,
                        "access_token": app_token
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Facebook token verification failed: {response.status_code}")
                    return None
                
                data = response.json()
                token_data = data.get("data", {})
                
                # Check if token is valid
                if not token_data.get("is_valid"):
                    logger.warning("Facebook token is invalid")
                    return None
                
                # Verify app ID
                if token_data.get("app_id") != self.app_id:
                    logger.warning("Facebook token app ID mismatch")
                    return None
                
                # Check expiration
                expires_at = token_data.get("expires_at", 0)
                if expires_at > 0 and expires_at < datetime.utcnow().timestamp():
                    logger.warning("Facebook token expired")
                    return None
                
                return token_data
                
        except Exception as e:
            logger.error(f"Error verifying Facebook token: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Facebook"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.USERINFO_URL,
                    params={
                        "fields": "id,name,email,first_name,last_name,picture",
                        "access_token": access_token
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get Facebook user info: {response.status_code}")
                    return {}
                
                user_info = response.json()
                
                return {
                    "email": user_info.get("email"),
                    "email_verified": True,  # Facebook emails are verified
                    "name": user_info.get("name"),
                    "given_name": user_info.get("first_name"),
                    "family_name": user_info.get("last_name"),
                    "picture": user_info.get("picture", {}).get("data", {}).get("url"),
                    "locale": None,
                    "provider_id": user_info.get("id")
                }
                
        except Exception as e:
            logger.error(f"Error getting Facebook user info: {e}")
            return {}


class OAuthService:
    """OAuth service for social login"""
    
    def __init__(self):
        self.providers = {
            "google": GoogleOAuthProvider(),
            "facebook": FacebookOAuthProvider()
        }
    
    def get_provider(self, provider_name: str) -> Optional[OAuthProvider]:
        """Get OAuth provider by name"""
        return self.providers.get(provider_name.lower())
    
    async def authenticate_with_oauth(
        self,
        provider_name: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with OAuth token
        
        Args:
            provider_name: OAuth provider (google, facebook)
            access_token: OAuth access token
        
        Returns:
            Dict with user info and JWT tokens
        """
        provider = self.get_provider(provider_name)
        
        if not provider:
            logger.error(f"Unknown OAuth provider: {provider_name}")
            return None
        
        try:
            # Verify token
            token_info = await provider.verify_token(access_token)
            if not token_info:
                logger.warning(f"Token verification failed for {provider_name}")
                return None
            
            # Get user info
            user_info = await provider.get_user_info(access_token)
            if not user_info or not user_info.get("email"):
                logger.error(f"Failed to get user info from {provider_name}")
                return None
            
            # Check if user exists
            user = await User.find_one(User.email == user_info["email"])
            
            if user:
                # Update OAuth info
                if not user.oauth_provider:
                    user.oauth_provider = provider_name
                    user.oauth_id = user_info.get("provider_id")
                
                # Update profile info if missing
                if not user.full_name and user_info.get("name"):
                    user.full_name = user_info["name"]
                
                if not user.profile_picture and user_info.get("picture"):
                    user.profile_picture = user_info["picture"]
                
                # Mark email as verified
                if user_info.get("email_verified") and not user.is_email_verified:
                    user.is_email_verified = True
                
                user.last_login = datetime.utcnow()
                await user.save()
                
                logger.info(f"Existing user logged in via {provider_name}: {user.email}")
            else:
                # Create new user
                username = user_info["email"].split("@")[0]
                
                # Check if username exists, append number if needed
                existing = await User.find_one(User.username == username)
                if existing:
                    import random
                    username = f"{username}{random.randint(100, 999)}"
                
                user = User(
                    email=user_info["email"],
                    username=username,
                    full_name=user_info.get("name", ""),
                    hashed_password="",  # No password for OAuth users
                    is_email_verified=user_info.get("email_verified", False),
                    oauth_provider=provider_name,
                    oauth_id=user_info.get("provider_id"),
                    profile_picture=user_info.get("picture"),
                    role=UserRole.USER,
                    is_active=True,
                    preferences={
                        "language": user_info.get("locale", "en")[:2] if user_info.get("locale") else "en"
                    }
                )
                
                await user.insert()
                
                logger.info(f"New user created via {provider_name}: {user.email}")
            
            # Generate JWT tokens
            access_token_jwt = AuthService.create_access_token(
                data={"user_id": str(user.id), "email": user.email}
            )
            
            refresh_token_jwt = AuthService.create_refresh_token(
                data={"user_id": str(user.id)}
            )
            
            return {
                "access_token": access_token_jwt,
                "refresh_token": refresh_token_jwt,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "profile_picture": user.profile_picture,
                    "oauth_provider": user.oauth_provider
                }
            }
            
        except Exception as e:
            logger.error(f"OAuth authentication error: {e}", exc_info=True)
            return None


# Singleton instance
_oauth_service = None

def get_oauth_service() -> OAuthService:
    """Get OAuth service singleton"""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = OAuthService()
    return _oauth_service

