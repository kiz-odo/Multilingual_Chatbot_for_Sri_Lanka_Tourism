"""
Email Verification API Endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from backend.app.services.email_verification_service import EmailVerificationService

router = APIRouter()


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationResponse(BaseModel):
    success: bool
    message: str


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify user email address using token
    
    - **token**: Email verification token from email
    """
    success, error_message = await EmailVerificationService.verify_email(request.token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Email verification failed"
        )
    
    return EmailVerificationResponse(
        success=True,
        message="Email verified successfully! You can now log in."
    )


@router.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification_email(request: ResendVerificationRequest):
    """
    Resend verification email
    
    - **email**: User email address
    """
    success, error_message = await EmailVerificationService.resend_verification_email(request.email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Failed to resend verification email"
        )
    
    return EmailVerificationResponse(
        success=True,
        message="Verification email sent! Please check your inbox."
    )

