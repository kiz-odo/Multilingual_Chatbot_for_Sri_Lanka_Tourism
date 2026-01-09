"""
Feedback model for Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class FeedbackType(str, Enum):
    """Feedback types"""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL_FEEDBACK = "general_feedback"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    PRAISE = "praise"
    CONTENT_CORRECTION = "content_correction"
    TRANSLATION_ISSUE = "translation_issue"


class FeedbackStatus(str, Enum):
    """Feedback status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackCategory(str, Enum):
    """Feedback categories"""
    CHATBOT_RESPONSE = "chatbot_response"
    USER_INTERFACE = "user_interface"
    CONTENT_ACCURACY = "content_accuracy"
    TRANSLATION_QUALITY = "translation_quality"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    MOBILE_APP = "mobile_app"
    WEB_APP = "web_app"
    API = "api"
    CHAT = "chat"
    OTHER = "other"


class Response(BaseModel):
    """Admin response model"""
    admin_id: str
    admin_name: str
    response_text: str
    response_date: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = True


class Feedback(Document):
    """Feedback document model"""
    
    # Basic Information
    title: str
    description: str
    feedback_type: FeedbackType
    category: FeedbackCategory
    
    # User Information
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    is_anonymous: bool = False
    
    # Rating and Sentiment
    rating: Optional[int] = Field(None, ge=1, le=5)
    sentiment: Optional[str] = None  # positive, negative, neutral
    
    # Context Information
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    language: str = "en"
    
    # Technical Details
    browser_info: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Status and Priority
    status: FeedbackStatus = FeedbackStatus.NEW
    priority: Priority = Priority.MEDIUM
    assigned_to: Optional[str] = None
    
    # Content Related (for content corrections)
    content_type: Optional[str] = None  # attraction, restaurant, hotel, etc.
    content_id: Optional[str] = None
    suggested_correction: Optional[str] = None
    
    # Admin Response
    admin_responses: List[Response] = Field(default_factory=list)
    resolution_notes: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)  # file URLs
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "feedback"
        indexes = [
            "user_id",
            "feedback_type",
            "category",
            "status",
            "priority",
            "rating",
            "created_at",
            "language"
        ]
    
    def add_admin_response(self, admin_id: str, admin_name: str, response_text: str, is_public: bool = True):
        """Add admin response to feedback"""
        response = Response(
            admin_id=admin_id,
            admin_name=admin_name,
            response_text=response_text,
            is_public=is_public
        )
        self.admin_responses.append(response)
        self.updated_at = datetime.utcnow()
    
    def resolve(self, resolution_notes: Optional[str] = None):
        """Mark feedback as resolved"""
        self.status = FeedbackStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if resolution_notes:
            self.resolution_notes = resolution_notes
    
    def close(self):
        """Close feedback"""
        self.status = FeedbackStatus.CLOSED
        self.updated_at = datetime.utcnow()


class FeedbackCreate(BaseModel):
    """Feedback creation model"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    feedback_type: FeedbackType
    category: FeedbackCategory
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    is_anonymous: bool = False
    rating: Optional[int] = Field(None, ge=1, le=5)
    page_url: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    language: str = "en"
    content_type: Optional[str] = None
    content_id: Optional[str] = None
    suggested_correction: Optional[str] = None


class FeedbackUpdate(BaseModel):
    """Feedback update model"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    feedback_type: Optional[FeedbackType] = None
    category: Optional[FeedbackCategory] = None
    status: Optional[FeedbackStatus] = None
    priority: Optional[Priority] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class FeedbackResponse(BaseModel):
    """Feedback response model"""
    id: str
    title: str
    description: str
    feedback_type: FeedbackType
    category: FeedbackCategory
    user_name: Optional[str] = None
    is_anonymous: bool
    rating: Optional[int] = None
    sentiment: Optional[str] = None
    status: FeedbackStatus
    priority: Priority
    language: str
    admin_responses: List[Response]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


class FeedbackStats(BaseModel):
    """Feedback statistics model"""
    total_feedback: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)
    by_category: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    by_priority: Dict[str, int] = Field(default_factory=dict)
    average_rating: float = 0.0
    resolution_rate: float = 0.0
    average_resolution_time_hours: float = 0.0


class AdminResponse(BaseModel):
    """Admin response creation model"""
    response_text: str = Field(..., min_length=5, max_length=1000)
    is_public: bool = True
