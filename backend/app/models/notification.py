"""
Notification models for Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification types"""
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationCategory(str, Enum):
    """Notification categories"""
    SYSTEM = "system"
    MARKETING = "marketing"
    TRANSACTIONAL = "transactional"
    ALERT = "alert"
    REMINDER = "reminder"
    SOCIAL = "social"
    PROMOTIONAL = "promotional"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationTemplate(Document):
    """Notification template"""
    
    # Template Information
    template_id: Indexed(str, unique=True)
    template_name: str
    description: Optional[str] = None
    
    # Classification
    notification_type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority
    
    # Content (Multilingual)
    title: Dict[str, str]  # Language -> title
    body: Dict[str, str]  # Language -> body
    
    # Push Notification Specific
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    sound: Optional[str] = None
    badge_count: Optional[int] = None
    
    # Action
    action_url: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    
    # Email Specific
    email_subject: Optional[Dict[str, str]] = None
    email_html_template: Optional[str] = None
    email_text_template: Optional[str] = None
    
    # SMS Specific
    sms_template: Optional[Dict[str, str]] = None
    
    # Variables/Placeholders
    variables: List[str] = Field(default_factory=list)  # {user_name}, {attraction_name}, etc.
    
    # Scheduling
    can_be_scheduled: bool = True
    default_schedule_offset_minutes: int = 0
    
    # Throttling
    throttle_per_user_minutes: Optional[int] = None  # Min time between same notifications
    max_per_day_per_user: Optional[int] = None
    
    # Status
    is_active: bool = True
    
    # A/B Testing
    ab_test_variant: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "notification_templates"
        indexes = [
            "template_id",
            "notification_type",
            "category",
            "is_active"
        ]


class Notification(Document):
    """Individual notification"""
    
    # Recipient
    user_id: Indexed(str)
    
    # Notification Details
    notification_type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority
    
    # Template Reference
    template_id: Optional[str] = None
    
    # Content
    title: str
    body: str
    language: str = "en"
    
    # Rich Content
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    sound: Optional[str] = None
    
    # Action
    action_url: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    
    # Delivery Information
    device_tokens: List[str] = Field(default_factory=list)  # For push notifications
    email_address: Optional[str] = None  # For email
    phone_number: Optional[str] = None  # For SMS
    
    # Status
    status: NotificationStatus = NotificationStatus.PENDING
    
    # Delivery Tracking
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Engagement
    clicked: bool = False
    clicked_at: Optional[datetime] = None
    dismissed: bool = False
    dismissed_at: Optional[datetime] = None
    
    # Scheduling
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Grouping
    group_id: Optional[str] = None  # For related notifications
    thread_id: Optional[str] = None  # For conversation threads
    
    # Provider Response
    provider_response: Optional[Dict[str, Any]] = None
    provider_message_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "notification_type",
            "category",
            "status",
            "priority",
            "scheduled_for",
            "created_at",
            "sent_at",
            "read_at"
        ]


class UserNotificationPreferences(Document):
    """User notification preferences"""
    
    # User Reference
    user_id: Indexed(str, unique=True)
    
    # Global Settings
    notifications_enabled: bool = True
    
    # Channel Preferences
    push_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    
    # Category Preferences
    marketing_notifications: bool = True
    transactional_notifications: bool = True
    alert_notifications: bool = True
    reminder_notifications: bool = True
    social_notifications: bool = True
    promotional_notifications: bool = True
    
    # Timing Preferences
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[int] = 22  # Hour of day (0-23)
    quiet_hours_end: Optional[int] = 8  # Hour of day (0-23)
    
    # Frequency Preferences
    max_notifications_per_day: Optional[int] = None
    digest_mode: bool = False  # Batch notifications into digest
    digest_frequency: Optional[str] = None  # daily, weekly
    
    # Language
    preferred_language: str = "en"
    
    # Device Tokens (for push notifications)
    device_tokens: List[Dict[str, Any]] = Field(default_factory=list)  # {token, platform, registered_at}
    
    # Contact Information
    email_addresses: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    
    # Unsubscribe Tokens
    unsubscribe_tokens: Dict[str, str] = Field(default_factory=dict)  # category -> token
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "user_notification_preferences"
        indexes = [
            "user_id",
            "updated_at"
        ]


class NotificationCampaign(Document):
    """Notification campaign for mass notifications"""
    
    # Campaign Information
    campaign_id: Indexed(str, unique=True)
    campaign_name: str
    description: Optional[str] = None
    
    # Template
    template_id: str
    
    # Target Audience
    target_type: str  # all_users, segment, specific_users
    target_segment: Optional[str] = None
    target_user_ids: List[str] = Field(default_factory=list)
    
    # Filters
    user_filters: Dict[str, Any] = Field(default_factory=dict)  # location, language, interests, etc.
    
    # Scheduling
    scheduled_for: Optional[datetime] = None
    timezone: str = "UTC"
    
    # Status
    status: str = "draft"  # draft, scheduled, in_progress, completed, cancelled
    
    # Progress
    total_recipients: int = 0
    notifications_sent: int = 0
    notifications_delivered: int = 0
    notifications_read: int = 0
    notifications_failed: int = 0
    
    # Engagement Metrics
    click_through_rate: float = 0.0
    conversion_rate: float = 0.0
    
    # A/B Testing
    ab_test_enabled: bool = False
    ab_test_variants: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "notification_campaigns"
        indexes = [
            "campaign_id",
            "status",
            "scheduled_for",
            "created_at"
        ]


# Response Models
class NotificationRequest(BaseModel):
    """Create notification request"""
    user_id: str
    template_id: Optional[str] = None
    notification_type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    body: str
    language: str = "en"
    action_url: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None
    scheduled_for: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    user_id: str
    notification_type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    body: str
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences"""
    notifications_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    marketing_notifications: Optional[bool] = None
    transactional_notifications: Optional[bool] = None
    alert_notifications: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[int] = None
    quiet_hours_end: Optional[int] = None

