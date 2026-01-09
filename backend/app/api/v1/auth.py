"""
Authentication API endpoints - Complete Implementation with JWT
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import logging

from backend.app.models.user import User, UserCreate, UserResponse, UserRole
from backend.app.services.user_service import UserService
from backend.app.services.auth_service import AuthService
from backend.app.core.auth import get_current_user, get_current_active_user
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


# ============ AUTHENTICATION ENDPOINTS ============

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request):
    """
    Register a new user
    
    - Creates new user account
    - Returns access token and refresh token for immediate login
    - Logs the registration event
    - Password validation is enforced via UserCreate model validator
    """
    user_service = UserService()
    
    # Check if email already exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Password validation is automatically enforced by UserCreate.field_validator
    # Additional validation for extra security
    if not AuthService.validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet complexity requirements. Must contain: uppercase, lowercase, digit, and special character"
        )
    
    # Hash password
    hashed_password = AuthService.hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        nationality=user_data.nationality,
        preferred_language=user_data.preferred_language,
        role=UserRole.USER,  # New users get USER role (not GUEST)
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    await user.insert()
    
    # Create tokens for automatic login
    tokens = await AuthService.create_user_tokens(user)
    
    # Log registration event
    await AuthService.log_auth_event(
        user_id=str(user.id),
        action="register",
        details={"email": user.email, "username": user.username},
        ip_address=request.client.host if request.client else None,
        request_id=getattr(request.state, "request_id", None)
    )
    
    return Token(
        **tokens,
        user=UserResponse(**user.dict())
    )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """
    Login user with email/username and password
    
    - Authenticates user
    - Returns access token and refresh token
    - Logs login event
    """
    # Authenticate user (form_data.username can be email or username)
    user = await AuthService.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        # Log failed login attempt
        await AuthService.log_auth_event(
            user_id="unknown",
            action="login_failed",
            details={"username": form_data.username},
            ip_address=request.client.host if request and request.client else None,
            request_id=getattr(request.state, "request_id", None) if request else None
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = await AuthService.create_user_tokens(user)
    
    # Log successful login
    await AuthService.log_auth_event(
        user_id=str(user.id),
        action="login",
        details={"email": user.email},
        ip_address=request.client.host if request and request.client else None,
        request_id=getattr(request.state, "request_id", None) if request else None
    )
    
    return Token(
        **tokens,
        user=UserResponse(**user.dict())
    )


@router.post("/refresh")
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Issues new access token
    - Keeps same refresh token
    """
    new_tokens = await AuthService.refresh_access_token(token_data.refresh_token)
    
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return new_tokens


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Logout user
    
    - Revokes current token
    - Logs logout event
    """
    # Get token from request
    auth_header = request.headers.get("Authorization") if request else None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        await AuthService.revoke_token(token)
    
    # Log logout
    await AuthService.log_auth_event(
        user_id=str(current_user.id),
        action="logout",
        details={"email": current_user.email},
        ip_address=request.client.host if request and request.client else None,
        request_id=getattr(request.state, "request_id", None) if request else None
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Returns authenticated user's profile
    """
    return UserResponse(**current_user.dict())


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's profile
    
    Allowed fields: full_name, preferred_language, nationality
    """
    allowed_fields = ["full_name", "preferred_language", "nationality"]
    
    for field, value in user_update.items():
        if field in allowed_fields and value is not None:
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return UserResponse(**current_user.dict())


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    request: Request = None
):
    """
    Change user password
    
    - Verifies old password
    - Updates to new password
    - Logs password change event
    """
    # Verify old password
    if not AuthService.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash and save new password
    current_user.hashed_password = AuthService.hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    # Log password change
    await AuthService.log_auth_event(
        user_id=str(current_user.id),
        action="password_change",
        details={"email": current_user.email},
        ip_address=request.client.host if request and request.client else None,
        request_id=getattr(request.state, "request_id", None) if request else None
    )
    
    return {"message": "Password changed successfully"}


@router.post("/password-reset-request")
async def request_password_reset(reset_data: PasswordReset):
    """
    Request password reset
    
    - Generates reset token
    - Sends email with reset link
    """
    user_service = UserService()
    user = await user_service.get_user_by_email(reset_data.email)
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If email exists, password reset link has been sent"}
    
    # Generate reset token
    reset_token = AuthService.generate_password_reset_token()
    
    # Store reset token with expiration (1 hour)
    from backend.app.models.security import EmailVerificationToken
    from datetime import timedelta
    
    token_entry = EmailVerificationToken(
        user_id=str(user.id),
        email=user.email,
        token=reset_token,
        token_type="password_reset",
        expires_at=datetime.utcnow() + timedelta(hours=1),
        is_used=False
    )
    await token_entry.insert()
    
    # Send password reset email
    try:
        from backend.app.tasks.email_tasks import send_password_reset_email
        send_password_reset_email.delay(
            email=user.email,
            reset_token=reset_token,
            user_name=user.full_name or user.username
        )
    except Exception as e:
        logger.warning(f"Failed to send password reset email: {e}")
        # Don't fail the request if email sending fails
    
    return {"message": "Password reset link has been sent to your email"}


@router.get("/verify-token")
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """
    Verify if token is valid
    
    Returns user info if token is valid, 401 otherwise
    """
    return {
        "valid": True,
        "user": UserResponse(**current_user.dict())
    }


# ============ MFA ENDPOINTS ============

class MFAVerifyRequest(BaseModel):
    """MFA verification request"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")


class MFASetupRequest(BaseModel):
    """MFA setup request"""
    method: str = Field(default="totp", description="MFA method: totp")


@router.post("/enable-mfa", status_code=status.HTTP_200_OK)
async def enable_mfa(
    request: MFASetupRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Enable MFA with TOTP and QR code
    
    - Generates TOTP secret
    - Creates QR code for authenticator app
    - Returns QR code URL and backup codes
    """
    try:
        from backend.app.models.security import UserMFA, MFAMethod, MFASetupResponse
        import pyotp
        import qrcode
        import io
        import base64
        
        # Check if MFA already enabled
        existing_mfa = await UserMFA.find_one(UserMFA.user_id == str(current_user.id))
        if existing_mfa and existing_mfa.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled for this account"
            )
        
        # Generate TOTP secret
        totp_secret = pyotp.random_base32()
        
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
            name=current_user.email,
            issuer_name=settings.APP_NAME
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_data}"
        
        # Generate backup codes
        import secrets
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        # Create or update MFA record
        if existing_mfa:
            existing_mfa.mfa_enabled = False  # Not enabled until verified
            existing_mfa.mfa_method = MFAMethod.TOTP
            existing_mfa.totp_secret = totp_secret  # Should be encrypted in production
            existing_mfa.totp_verified = False
            existing_mfa.backup_codes = backup_codes  # Should be encrypted in production
            existing_mfa.backup_codes_generated_at = datetime.utcnow()
            existing_mfa.updated_at = datetime.utcnow()
            await existing_mfa.save()
            mfa_record = existing_mfa
        else:
            mfa_record = UserMFA(
                user_id=str(current_user.id),
                mfa_enabled=False,  # Not enabled until verified
                mfa_method=MFAMethod.TOTP,
                totp_secret=totp_secret,  # Should be encrypted in production
                totp_verified=False,
                backup_codes=backup_codes,  # Should be encrypted in production
                backup_codes_generated_at=datetime.utcnow()
            )
            await mfa_record.insert()
        
        return MFASetupResponse(
            mfa_method=MFAMethod.TOTP,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )
        
    except ImportError:
        logger.error("pyotp or qrcode not installed. Install with: pip install pyotp qrcode[pil]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA service not available. Required packages not installed."
        )
    except Exception as e:
        logger.error(f"Failed to enable MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable MFA"
        )


@router.post("/verify-mfa", status_code=status.HTTP_200_OK)
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify MFA code during login
    
    - Verifies TOTP code or backup code
    - Enables MFA if this is the first verification after setup
    - Returns success status
    """
    try:
        from backend.app.models.security import UserMFA, MFAMethod
        import pyotp
        
        mfa_record = await UserMFA.find_one(UserMFA.user_id == str(current_user.id))
        if not mfa_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA not set up for this account"
            )
        
        # Check if locked
        if mfa_record.locked_until and mfa_record.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"MFA is locked until {mfa_record.locked_until}"
            )
        
        verified = False
        
        # Verify TOTP code
        if mfa_record.totp_secret:
            totp = pyotp.TOTP(mfa_record.totp_secret)
            if totp.verify(request.code, valid_window=1):
                verified = True
                mfa_record.totp_verified = True
                mfa_record.last_verification_method = MFAMethod.TOTP
        
        # Verify backup code if TOTP failed
        if not verified and mfa_record.backup_codes:
            if request.code.upper() in mfa_record.backup_codes:
                verified = True
                # Remove used backup code
                mfa_record.backup_codes.remove(request.code.upper())
                mfa_record.last_verification_method = MFAMethod.BACKUP_CODES
        
        if not verified:
            mfa_record.failed_attempts += 1
            mfa_record.last_failed_attempt_at = datetime.utcnow()
            
            # Lock after 5 failed attempts
            if mfa_record.failed_attempts >= 5:
                from datetime import timedelta
                mfa_record.locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            await mfa_record.save()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code"
            )
        
        # Enable MFA if this is first verification
        if not mfa_record.mfa_enabled:
            mfa_record.mfa_enabled = True
        
        # Reset failed attempts on success
        mfa_record.failed_attempts = 0
        mfa_record.last_verification_at = datetime.utcnow()
        mfa_record.updated_at = datetime.utcnow()
        await mfa_record.save()
        
        return {"message": "MFA verified successfully", "mfa_enabled": mfa_record.mfa_enabled}
        
    except HTTPException:
        raise
    except ImportError:
        logger.error("pyotp not installed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA service not available"
        )
    except Exception as e:
        logger.error(f"Failed to verify MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify MFA"
        )


@router.post("/disable-mfa", status_code=status.HTTP_200_OK)
async def disable_mfa(
    password: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Disable MFA for user account
    
    - Requires password verification for security
    - Disables MFA and clears TOTP secret
    """
    from backend.app.models.security import UserMFA
    from backend.app.services.auth_service import AuthService
    
    # Verify password
    if not AuthService.verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    
    mfa_record = await UserMFA.find_one(UserMFA.user_id == str(current_user.id))
    if not mfa_record or not mfa_record.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this account"
        )
    
    # Disable MFA
    mfa_record.mfa_enabled = False
    mfa_record.totp_secret = None
    mfa_record.totp_verified = False
    mfa_record.backup_codes = []
    mfa_record.updated_at = datetime.utcnow()
    await mfa_record.save()
    
    # Log event
    await AuthService.log_auth_event(
        user_id=str(current_user.id),
        action="mfa_disabled",
        details={"email": current_user.email},
        ip_address=None,
        request_id=None
    )
    
    return {"message": "MFA disabled successfully"}


@router.post("/forgot-password")
async def forgot_password(reset_data: PasswordReset):
    """
    Request password reset (alias for password-reset-request)
    
    - Generates reset token
    - Sends email with reset link
    """
    return await request_password_reset(reset_data)


@router.post("/reset-password")
async def reset_password(
    token: str = None,
    new_password: str = None
):
    """
    Reset password with token
    
    - Validates reset token
    - Updates password
    """
    from backend.app.models.security import EmailVerificationToken
    from backend.app.services.auth_service import AuthService
    
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and new_password are required"
        )
    
    # Validate password strength
    if len(new_password) < settings.PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        )
    
    # Find token
    token_entry = await EmailVerificationToken.find_one({
        "token": token,
        "token_type": "password_reset",
        "is_used": False,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if not token_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user = await User.get(token_entry.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = AuthService.hash_password(new_password)
    user.updated_at = datetime.utcnow()
    await user.save()
    
    # Mark token as used
    token_entry.is_used = True
    await token_entry.save()
    
    # Log event
    await AuthService.log_auth_event(
        user_id=str(user.id),
        action="password_reset",
        details={"email": user.email},
        ip_address=None,
        request_id=None
    )
    
    return {"message": "Password reset successfully"}