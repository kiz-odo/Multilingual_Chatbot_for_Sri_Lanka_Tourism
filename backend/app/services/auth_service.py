"""
Authentication Service - JWT Token Management
Handles user authentication, token generation, and password management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import logging

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.security import SessionToken, AuditLog

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for user management and JWT tokens"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Payload data to encode in token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token
        
        Args:
            data: Payload data to encode in token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JWT token (alias for verify_token)
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        return AuthService.verify_token(token)
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            True if password meets strength requirements, False otherwise
        """
        if len(password) < 8:
            return False
        
        if not any(c.isupper() for c in password):
            return False
        
        if not any(c.islower() for c in password):
            return False
        
        if not any(c.isdigit() for c in password):
            return False
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False
        
        return True
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = await User.find_one({"email": email})
        
        if not user:
            logger.warning(f"Authentication failed: User {email} not found")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed: User {email} is inactive")
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for {email}")
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await user.save()
        
        return user
    
    @staticmethod
    async def create_user_tokens(user: User, token_family: Optional[str] = None) -> Dict[str, str]:
        """
        Create access and refresh tokens for a user
        
        Args:
            user: User object
            token_family: Optional token family ID for rotation tracking
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        import uuid
        
        # Generate token family if not provided (new login)
        if not token_family:
            token_family = str(uuid.uuid4())
        
        # Create access token
        access_token = AuthService.create_access_token(
            data={
                "sub": user.email,
                "user_id": str(user.id),
                "role": user.role.value
            }
        )
        
        # Create refresh token
        refresh_token = AuthService.create_refresh_token(
            data={
                "sub": user.email,
                "user_id": str(user.id),
                "token_family": token_family
            }
        )
        
        # Store session token in database with token family
        session_token = SessionToken(
            session_id=str(uuid.uuid4()),
            user_id=str(user.id),
            token=access_token,
            token_hash=AuthService.hash_password(access_token),
            refresh_token=refresh_token,
            refresh_token_hash=AuthService.hash_password(refresh_token),
            token_family=token_family,
            expires_at=datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            is_active=True
        )
        await session_token.insert()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Generate new access token from refresh token with automatic rotation
        
        Implements refresh token rotation for enhanced security:
        - Generates new refresh token on each use
        - Invalidates old refresh token
        - Detects token reuse (potential breach)
        - Revokes all user sessions on breach detection
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            New access token data with new refresh token, or None if invalid
        """
        import uuid
        
        payload = AuthService.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            logger.warning("Invalid refresh token type")
            return None
        
        user_id = payload.get("user_id")
        token_family = payload.get("token_family")
        
        if not user_id:
            logger.warning("Missing user_id in refresh token")
            return None
        
        # Verify session token exists and is active
        session = await SessionToken.find_one({
            "refresh_token": refresh_token,
            "is_active": True
        })
        
        if not session:
            # Check for token reuse - BREACH DETECTION
            previous_session = await SessionToken.find_one({
                "refresh_token": refresh_token,
                "is_active": False
            })
            
            if previous_session:
                # Token reuse detected! This is a security breach
                logger.critical(
                    f"SECURITY BREACH: Refresh token reuse detected for user {user_id}. "
                    f"Token family: {previous_session.token_family}"
                )
                
                # Revoke ALL sessions in this token family (breach mitigation)
                if previous_session.token_family:
                    await SessionToken.update_many(
                        {
                            "token_family": previous_session.token_family,
                            "is_active": True
                        },
                        {
                            "$set": {
                                "is_active": False,
                                "revoked_at": datetime.utcnow(),
                                "is_suspicious": True
                            }
                        }
                    )
                
                # Create security alert
                from backend.app.models.security import SecurityAlert
                alert = SecurityAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type="refresh_token_reuse",
                    threat_level="critical",
                    user_id=user_id,
                    title="Refresh Token Reuse Detected",
                    description=f"Refresh token reuse detected for user {user_id}. All sessions revoked.",
                    detection_method="automatic",
                    evidence={
                        "token_family": previous_session.token_family,
                        "previous_session_id": str(previous_session.id)
                    }
                )
                await alert.insert()
                
                logger.warning(f"All sessions for user {user_id} have been revoked due to token reuse")
            
            return None
        
        # Get user
        user = await User.get(user_id)
        if not user or not user.is_active:
            logger.warning(f"User {user_id} not found or inactive")
            return None
        
        # Generate NEW refresh token (rotation)
        new_refresh_token = AuthService.create_refresh_token(
            data={
                "sub": user.email,
                "user_id": str(user.id),
                "token_family": session.token_family  # Maintain token family
            }
        )
        
        # Create new access token
        new_access_token = AuthService.create_access_token(
            data={
                "sub": user.email,
                "user_id": str(user.id),
                "role": user.role.value
            }
        )
        
        # Invalidate OLD refresh token (mark as used)
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        await session.save()
        
        # Create NEW session with rotated tokens
        new_session = SessionToken(
            session_id=str(uuid.uuid4()),
            user_id=str(user.id),
            token=new_access_token,
            token_hash=AuthService.hash_password(new_access_token),
            refresh_token=new_refresh_token,
            refresh_token_hash=AuthService.hash_password(new_refresh_token),
            token_family=session.token_family,  # Same family for breach tracking
            expires_at=datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            is_active=True,
            device_id=session.device_id,
            device_name=session.device_name,
            ip_address=session.ip_address,
            user_agent=session.user_agent
        )
        await new_session.insert()
        
        logger.info(
            f"Refresh token rotated for user {user_id}. "
            f"Old session revoked, new session created."
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,  # Return NEW refresh token
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    async def revoke_token(token: str) -> bool:
        """
        Revoke a token (logout)
        
        Args:
            token: Access or refresh token to revoke
            
        Returns:
            True if revoked successfully
        """
        session = await SessionToken.find_one({
            "$or": [
                {"token": token},
                {"refresh_token": token}
            ]
        })
        
        if session:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            await session.save()
            return True
        
        return False
    
    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate a secure random token for password reset"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def log_auth_event(
        user_id: str,
        action: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        Log authentication event for audit
        
        Args:
            user_id: User ID
            action: Action performed (login, logout, etc.)
            details: Additional details
            ip_address: Client IP address
            request_id: Request ID for tracing
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type="auth",
                resource_id=user_id,
                details=details,
                ip_address=ip_address,
                request_id=request_id,
                timestamp=datetime.utcnow()
            )
            await audit_log.insert()
        except Exception as e:
            logger.error(f"Failed to log auth event: {e}")


# Singleton instance
auth_service = AuthService()

