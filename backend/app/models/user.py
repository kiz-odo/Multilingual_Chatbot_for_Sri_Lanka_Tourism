"""
User model for the Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    """User roles - RBAC with 4 roles"""
    GUEST = "guest"  # Read public data, basic chat (rate-limited)
    USER = "user"  # Full chat, history, favorites, itinerary creation
    MODERATOR = "moderator"  # Content moderation, limited user management
    ADMIN = "admin"  # Full system access, analytics, user/role management


class UserPreferences(BaseModel):
    """User preferences model"""
    preferred_language: str = "en"
    interests: List[str] = Field(default_factory=list)
    budget_range: Optional[str] = None
    travel_style: Optional[str] = None  # adventure, cultural, relaxation, family
    dietary_restrictions: List[str] = Field(default_factory=list)
    accessibility_needs: List[str] = Field(default_factory=list)
    notification_settings: Dict[str, bool] = Field(default_factory=dict)


class UserLocation(BaseModel):
    """User location model"""
    country: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[List[float]] = None  # [longitude, latitude]
    timezone: Optional[str] = None


class UserStats(BaseModel):
    """User statistics model"""
    total_conversations: int = 0
    total_queries: int = 0
    favorite_attractions: List[str] = Field(default_factory=list)
    visited_places: List[str] = Field(default_factory=list)
    last_activity: Optional[datetime] = None


class User(Document):
    """User document model"""
    
    # Basic Information
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    nationality: Optional[str] = None
    preferred_language: str = "en"
    
    # Authentication
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    is_email_verified: bool = False
    role: UserRole = UserRole.GUEST  # Default to guest role
    
    # OAuth (Social Login)
    oauth_provider: Optional[str] = None  # google, facebook, etc.
    oauth_id: Optional[str] = None  # Provider's user ID
    profile_picture: Optional[str] = None  # Profile picture URL
    
    # Profile
    avatar_url: Optional[str] = None  # Deprecated: use profile_picture
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    
    # Preferences and Settings
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    location: Optional[UserLocation] = None
    
    # Statistics
    stats: UserStats = Field(default_factory=UserStats)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "role",
            "created_at",
            "last_login",
            "oauth_provider",
            [("oauth_provider", 1), ("oauth_id", 1)]
        ]
    
    def __str__(self):
        return f"User(username={self.username}, email={self.email})"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "preferences": self.preferences.dict(),
            "location": self.location.dict() if self.location else None,
            "stats": self.stats.dict(),
            "created_at": self.created_at,
            "last_login": self.last_login
        }


class UserCreate(BaseModel):
    """User creation model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = None
    nationality: Optional[str] = None
    preferred_language: str = "en"
    
    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password meets complexity requirements"""
        errors = []
        
        if len(v) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', v):
            errors.append("Password must contain at least one digit")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return v


class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    location: Optional[UserLocation] = None


class UserResponse(BaseModel):
    """User response model"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: UserPreferences
    location: Optional[UserLocation] = None
    stats: UserStats
    created_at: datetime
    last_login: Optional[datetime] = None
