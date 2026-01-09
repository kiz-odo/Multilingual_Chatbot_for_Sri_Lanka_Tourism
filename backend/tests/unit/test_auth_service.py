"""
Unit tests for authentication service
"""

import pytest
from datetime import datetime, timedelta
from backend.app.services.auth_service import AuthService
from backend.app.models.user import User, UserRole


class TestAuthService:
    """Test authentication service methods"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password("WrongPassword", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT access token creation"""
        data = {"sub": "test_user_123"}
        token = AuthService.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test JWT token with custom expiry"""
        data = {"sub": "test_user_123"}
        expires_delta = timedelta(minutes=5)
        token = AuthService.create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_decode_token_valid(self):
        """Test decoding valid JWT token"""
        data = {"sub": "test_user_123"}
        token = AuthService.create_access_token(data)
        
        decoded = AuthService.decode_token(token)
        assert decoded is not None
        assert decoded.get("sub") == "test_user_123"
    
    def test_decode_token_expired(self):
        """Test decoding expired JWT token"""
        data = {"sub": "test_user_123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = AuthService.create_access_token(data, expires_delta)
        
        decoded = AuthService.decode_token(token)
        assert decoded is None
    
    def test_decode_token_invalid(self):
        """Test decoding invalid JWT token"""
        invalid_token = "invalid.token.here"
        
        decoded_user_id = AuthService.decode_token(invalid_token)
        assert decoded_user_id is None
    
    def test_validate_password_strength_valid(self):
        """Test password strength validation with valid password"""
        valid_passwords = [
            "TestPassword123!",
            "MyP@ssw0rd",
            "Secure#Pass1",
            "C0mpl3x!Pass"
        ]
        
        for password in valid_passwords:
            assert AuthService.validate_password_strength(password) is True
    
    def test_validate_password_strength_too_short(self):
        """Test password strength validation with short password"""
        short_password = "Abc1!"
        assert AuthService.validate_password_strength(short_password) is False
    
    def test_validate_password_strength_no_uppercase(self):
        """Test password strength validation without uppercase"""
        password = "testpassword123!"
        assert AuthService.validate_password_strength(password) is False
    
    def test_validate_password_strength_no_lowercase(self):
        """Test password strength validation without lowercase"""
        password = "TESTPASSWORD123!"
        assert AuthService.validate_password_strength(password) is False
    
    def test_validate_password_strength_no_digit(self):
        """Test password strength validation without digit"""
        password = "TestPassword!"
        assert AuthService.validate_password_strength(password) is False
    
    def test_validate_password_strength_no_special(self):
        """Test password strength validation without special character"""
        password = "TestPassword123"
        assert AuthService.validate_password_strength(password) is False


@pytest.mark.asyncio
class TestAuthServiceAsync:
    """Test async authentication service methods"""
    
    async def test_authenticate_user_valid(self, test_user):
        """Test user authentication with valid credentials"""
        user = await AuthService.authenticate_user(
            test_user.email,
            "TestPassword123!"
        )
        
        assert user is not None
        assert user.email == test_user.email
        assert user.username == test_user.username
    
    async def test_authenticate_user_invalid_email(self):
        """Test user authentication with invalid email"""
        user = await AuthService.authenticate_user(
            "nonexistent@example.com",
            "TestPassword123!"
        )
        
        assert user is None
    
    async def test_authenticate_user_invalid_password(self, test_user):
        """Test user authentication with invalid password"""
        user = await AuthService.authenticate_user(
            test_user.email,
            "WrongPassword123!"
        )
        
        assert user is None
    
    async def test_authenticate_user_inactive(self, test_user):
        """Test authentication with inactive user"""
        # Temporarily deactivate user
        original_status = test_user.is_active
        test_user.is_active = False
        await test_user.save()
        
        user = await AuthService.authenticate_user(
            test_user.email,
            "TestPassword123!"
        )
        
        # Restore user status
        test_user.is_active = original_status
        await test_user.save()
        
        assert user is None
