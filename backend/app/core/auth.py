"""
Authentication Dependencies and Utilities
FastAPI dependencies for route protection and user authentication
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
import logging

from backend.app.services.auth_service import AuthService
from backend.app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT"
)

# HTTP Bearer scheme for custom auth
security = HTTPBearer()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    request: Request = None
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
        request: FastAPI request object (optional)
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    payload = AuthService.verify_token(token)
    
    if payload is None:
        logger.warning("Invalid token provided")
        raise credentials_exception
    
    # Check token type
    if payload.get("type") != "access":
        logger.warning("Wrong token type provided")
        raise credentials_exception
    
    # Get user ID from payload
    user_id: str = payload.get("user_id")
    if user_id is None:
        logger.warning("Token payload missing user_id")
        raise credentials_exception
    
    # Get user from database
    try:
        user = await User.get(user_id)
        if user is None:
            logger.warning(f"User {user_id} not found")
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Attach request info to user for logging
        if request:
            user._request_id = getattr(request.state, "request_id", None)
            user._ip_address = request.client.host if request.client else None
        
        return user
        
    except Exception as e:
        logger.error(f"Error retrieving user: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is active
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Dependency to get user if authenticated, None otherwise
    Useful for endpoints that work with or without authentication
    
    Args:
        request: FastAPI request
        credentials: Optional HTTP credentials (auto_error=False allows missing credentials)
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        
        if payload and payload.get("type") == "access":
            user_id = payload.get("user_id")
            if user_id:
                user = await User.get(user_id)
                if user and user.is_active:
                    return user
    except Exception as e:
        logger.debug(f"Optional auth failed: {e}")
    
    return None


class RoleChecker:
    """
    Dependency class to check user roles
    Usage: dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]
    """
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            logger.warning(
                f"User {current_user.email} attempted to access resource requiring "
                f"{self.allowed_roles} but has role {current_user.role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_user


# Convenience role checkers
require_admin = RoleChecker([UserRole.ADMIN])
require_moderator = RoleChecker([UserRole.ADMIN, UserRole.MODERATOR])
# Note: OPERATOR and PREMIUM roles not yet implemented in UserRole enum


def require_roles(*roles: UserRole):
    """
    Function to create a role checker for specific roles
    
    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(user: User = Depends(require_roles(UserRole.ADMIN))):
            pass
    """
    return RoleChecker(list(roles))

