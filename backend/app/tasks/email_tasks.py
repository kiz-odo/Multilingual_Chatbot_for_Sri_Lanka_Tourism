"""
Email-related background tasks with SMTP support
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from backend.app.core.celery_app import celery_app
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


def send_email_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content
        text_content: Plain text content (fallback)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # Check if SMTP is configured
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured - email not sent")
        logger.info(f"Would send email to {to_email}: {subject}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = to_email
        
        # Add plain text version
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        # Add HTML version
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Connect to SMTP server
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email via SMTP: {e}")
        return False


@celery_app.task(name="backend.app.tasks.email_tasks.send_welcome_email")
def send_welcome_email(user_email: str, user_name: str):
    """
    Send welcome email to new user
    
    Args:
        user_email: User's email address
        user_name: User's name
    """
    try:
        logger.info(f"Sending welcome email to {user_email}")
        
        subject = f"Welcome to {settings.APP_NAME}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ padding: 8px 0; }}
                li:before {{ content: "✓ "; color: #4CAF50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Sri Lanka Tourism Chatbot!</h1>
                </div>
                <div class="content">
                    <p>Dear {user_name},</p>
                    <p>Welcome to Sri Lanka Tourism Chatbot! We're excited to help you explore the beautiful island of Sri Lanka.</p>
                    <p><strong>Get started by asking about:</strong></p>
                    <ul>
                        <li>Tourist attractions and landmarks</li>
                        <li>Hotels and accommodations</li>
                        <li>Restaurants and local cuisine</li>
                        <li>Transport options</li>
                        <li>Cultural events and festivals</li>
                        <li>Weather and travel tips</li>
                    </ul>
                    <p>Our chatbot supports multiple languages including English, Sinhala, Tamil, German, French, Chinese, and Japanese.</p>
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    <p>Happy exploring!</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Sri Lanka Tourism. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Sri Lanka Tourism Chatbot, {user_name}!
        
        We're excited to help you explore beautiful Sri Lanka.
        
        Get started by asking about:
        - Tourist attractions
        - Hotels and restaurants
        - Transport options
        - Cultural events
        
        Best regards,
        Sri Lanka Tourism Team
        """
        
        # Send email via SMTP
        success = send_email_smtp(user_email, subject, html_content, text_content)
        
        return {
            "status": "success" if success else "failed_smtp_not_configured",
            "email": user_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {e}")
        raise


@celery_app.task(name="backend.app.tasks.email_tasks.send_password_reset_email")
def send_password_reset_email(user_email: str, reset_token: str):
    """
    Send password reset email
    
    Args:
        user_email: User's email address
        reset_token: Password reset token
    """
    try:
        logger.info(f"Sending password reset email to {user_email}")
        
        # In production, replace with your actual domain
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        subject = "Password Reset Request - Sri Lanka Tourism"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF5722; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #FF5722; 
                          color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
                .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>We received a request to reset your password for Sri Lanka Tourism Chatbot.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #0066cc;">{reset_link}</p>
                    <div class="warning">
                        <p><strong>⚠️ Security Notice:</strong></p>
                        <ul style="margin: 5px 0;">
                            <li>This link will expire in 1 hour</li>
                            <li>If you didn't request this, please ignore this email</li>
                            <li>Never share this link with anyone</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Sri Lanka Tourism. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request - Sri Lanka Tourism
        
        We received a request to reset your password.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Sri Lanka Tourism Team
        """
        
        success = send_email_smtp(user_email, subject, html_content, text_content)
        
        return {
            "status": "success" if success else "failed_smtp_not_configured",
            "email": user_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        raise


@celery_app.task(name="backend.app.tasks.email_tasks.send_notification_email")
def send_notification_email(user_email: str, subject: str, message: str):
    """
    Send general notification email
    
    Args:
        user_email: Recipient email
        subject: Email subject
        message: Email message
    """
    try:
        logger.info(f"Sending notification email to {user_email}: {subject}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{subject}</h1>
                </div>
                <div class="content">
                    {message}
                </div>
                <div class="footer">
                    <p>&copy; 2025 Sri Lanka Tourism. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = message
        
        success = send_email_smtp(user_email, subject, html_content, text_content)
        
        return {
            "status": "success" if success else "failed_smtp_not_configured",
            "email": user_email,
            "subject": subject
        }
        
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")
        raise

