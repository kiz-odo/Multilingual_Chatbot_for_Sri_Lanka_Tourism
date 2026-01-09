"""
GraphQL Context
Handles authentication and request context for GraphQL
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

from backend.app.core.config import settings
from backend.app.models.user import User

logger = logging.getLogger(__name__)


async def get_graphql_context(request: Request) -> dict:
    """
    Get GraphQL context from request
    Extracts and validates JWT token if present
    """
    context = {
        "request": request,
        "user": None
    }
    
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("user_id")
            
            if user_id:
                # Get user from database
                user = await User.get(user_id)
                
                if user and user.is_active:
                    context["user"] = user
                    logger.debug(f"GraphQL request authenticated: {user.email}")
                else:
                    logger.warning(f"User {user_id} not found or inactive")
            
        except JWTError as e:
            logger.warning(f"Invalid JWT token in GraphQL request: {e}")
        except Exception as e:
            logger.error(f"Error processing GraphQL auth: {e}")
    
    return context


def require_auth(context: dict) -> User:
    """
    Helper to require authentication in resolvers
    Raises exception if user is not authenticated
    """
    user = context.get("user")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return user

