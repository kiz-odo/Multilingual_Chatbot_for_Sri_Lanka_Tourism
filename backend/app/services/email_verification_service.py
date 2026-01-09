"""
Email Verification Service
Handles email verification workflow for user registration
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.tasks.email_tasks import send_notification_email

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """Service for email verification"""
    
    TOKEN_EXPIRY_HOURS = 24
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    async def send_verification_email(user: User) -> bool:
        """
        Send verification email to user
        
        Args:
            user: User object
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Generate verification token
            token = EmailVerificationService.generate_verification_token()
            expiry = datetime.utcnow() + timedelta(hours=EmailVerificationService.TOKEN_EXPIRY_HOURS)
            
            # Store token in user document
            user.email_verification_token = token
            user.email_verification_token_expiry = expiry
            await user.save()
            
            # Generate verification token (to be used by future frontend)
            verification_link = f"Verification Token: {token}"
            
            # Prepare email content
            subject = f"Verify Your Email - {settings.APP_NAME}"
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background-color: #4CAF50; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 4px; 
                        margin: 20px 0;
                    }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
                    .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Verify Your Email Address</h1>
                    </div>
                    <div class="content">
                        <p>Dear {user.full_name or user.username},</p>
                        <p>Thank you for registering with {settings.APP_NAME}!</p>
                        <p>To complete your registration and activate your account, please verify your email address by clicking the button below:</p>
                        <p style="text-align: center;">
                            <a href="{verification_link}" class="button">Verify Email Address</a>
                        </p>
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #0066cc;">{verification_link}</p>
                        <div class="warning">
                            <p><strong>⚠️ Important:</strong></p>
                            <ul style="margin: 5px 0;">
                                <li>This link will expire in {EmailVerificationService.TOKEN_EXPIRY_HOURS} hours</li>
                                <li>If you didn't create an account, please ignore this email</li>
                                <li>Never share this link with anyone</li>
                            </ul>
                        </div>
                        <p>If you have any questions, feel free to contact our support team.</p>
                        <p>Welcome aboard!</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 {settings.APP_NAME}. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email (async task)
            from backend.app.tasks.email_tasks import send_notification_email
            send_notification_email.delay(
                user_email=user.email,
                subject=subject,
                message=html_message
            )
            
            logger.info(f"Verification email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            return False
    
    @staticmethod
    async def verify_email(token: str) -> tuple[bool, Optional[str]]:
        """
        Verify email using token
        
        Args:
            token: Verification token
        
        Returns:
            tuple: (success, error_message)
        """
        try:
            # Find user with this token
            user = await User.find_one(User.email_verification_token == token)
            
            if not user:
                return False, "Invalid or expired verification token"
            
            # Check if token is expired
            if user.email_verification_token_expiry < datetime.utcnow():
                return False, "Verification token has expired. Please request a new one."
            
            # Mark email as verified
            user.is_email_verified = True
            user.email_verified_at = datetime.utcnow()
            user.email_verification_token = None
            user.email_verification_token_expiry = None
            await user.save()
            
            logger.info(f"Email verified successfully for user {user.email}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False, "An error occurred during verification"
    
    @staticmethod
    async def resend_verification_email(email: str) -> tuple[bool, Optional[str]]:
        """
        Resend verification email
        
        Args:
            email: User email
        
        Returns:
            tuple: (success, error_message)
        """
        try:
            user = await User.find_one(User.email == email)
            
            if not user:
                return False, "User not found"
            
            if user.is_email_verified:
                return False, "Email is already verified"
            
            # Send new verification email
            success = await EmailVerificationService.send_verification_email(user)
            
            if success:
                return True, None
            else:
                return False, "Failed to send verification email"
                
        except Exception as e:
            logger.error(f"Error resending verification email: {e}")
            return False, "An error occurred"

