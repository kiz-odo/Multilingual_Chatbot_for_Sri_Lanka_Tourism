"""
Security models for Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MFAMethod(str, Enum):
    """Multi-factor authentication methods"""
    SMS = "sms"
    EMAIL = "email"
    TOTP = "totp"  # Time-based One-Time Password (e.g., Google Authenticator)
    BIOMETRIC = "biometric"
    BACKUP_CODES = "backup_codes"


class AuditAction(str, Enum):
    """Audit log actions"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    PROFILE_UPDATE = "profile_update"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    PERMISSION_CHANGE = "permission_change"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"


class ThreatLevel(str, Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserMFA(Document):
    """Multi-factor authentication settings for users"""
    
    # User Reference
    user_id: Indexed(str, unique=True)
    
    # MFA Status
    mfa_enabled: bool = False
    mfa_method: Optional[MFAMethod] = None
    
    # TOTP Settings
    totp_secret: Optional[str] = None  # Encrypted
    totp_verified: bool = False
    
    # SMS Settings
    phone_number: Optional[str] = None
    phone_verified: bool = False
    
    # Email Settings
    email_verified: bool = False
    
    # Backup Codes
    backup_codes: List[str] = Field(default_factory=list)  # Encrypted, one-time use
    backup_codes_generated_at: Optional[datetime] = None
    
    # Recovery Options
    recovery_email: Optional[str] = None
    recovery_phone: Optional[str] = None
    
    # Security Questions (fallback)
    security_questions: List[Dict[str, str]] = Field(default_factory=list)  # Encrypted answers
    
    # Last Verification
    last_verification_at: Optional[datetime] = None
    last_verification_method: Optional[MFAMethod] = None
    
    # Failed Attempts
    failed_attempts: int = 0
    last_failed_attempt_at: Optional[datetime] = None
    locked_until: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "user_mfa"
        indexes = [
            "user_id",
            "mfa_enabled",
            "updated_at"
        ]


class AuditLog(Document):
    """Security audit log"""
    
    # User and Action
    user_id: Optional[Indexed(str)] = None  # Can be None for anonymous actions
    username: Optional[str] = None
    action: AuditAction
    
    # Request Information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    
    # Resource Information
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    
    # Details
    description: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None  # Before/after values
    
    # Result
    success: bool = True
    error_message: Optional[str] = None
    
    # Security Context
    threat_level: ThreatLevel = ThreatLevel.LOW
    is_suspicious: bool = False
    
    # Location
    country: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[List[float]] = None
    
    # Device Information
    device_type: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "audit_logs"
        indexes = [
            "user_id",
            "action",
            "created_at",
            "threat_level",
            "is_suspicious",
            "ip_address"
        ]


class APIKey(Document):
    """API key management"""
    
    # Key Information
    key_id: Indexed(str, unique=True)
    key_hash: str  # Hashed API key
    key_prefix: str  # First few characters for identification
    
    # Owner
    user_id: Indexed(str)
    
    # Metadata
    name: str  # Human-readable name
    description: Optional[str] = None
    
    # Permissions
    scopes: List[str] = Field(default_factory=list)  # read:attractions, write:bookings, etc.
    rate_limit: int = 1000  # Requests per hour
    
    # Status
    is_active: bool = True
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None
    
    # Usage Tracking
    total_requests: int = 0
    last_used_at: Optional[datetime] = None
    last_used_ip: Optional[str] = None
    
    # Expiration
    expires_at: Optional[datetime] = None
    
    # IP Whitelist
    allowed_ips: List[str] = Field(default_factory=list)
    
    # Referer Whitelist
    allowed_referers: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "api_keys"
        indexes = [
            "key_id",
            "key_hash",
            "user_id",
            "is_active",
            "expires_at",
            "created_at"
        ]


class SessionToken(Document):
    """User session management"""
    
    # Session Information
    session_id: Indexed(str, unique=True)
    user_id: Indexed(str)
    
    # Token
    token: str  # Access token (for backward compatibility)
    token_hash: str  # Hashed session token
    refresh_token: Optional[str] = None  # Refresh token (for backward compatibility)
    refresh_token_hash: Optional[str] = None  # For token refresh
    
    # Token Family (for rotation tracking and breach detection)
    token_family: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex)
    
    # Device and Location
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Geolocation
    country: Optional[str] = None
    city: Optional[str] = None
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    
    # Security Flags
    is_suspicious: bool = False
    requires_reauth: bool = False
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "session_tokens"
        indexes = [
            "session_id",
            "user_id",
            "token_hash",
            "refresh_token",
            "token_family",
            "is_active",
            "expires_at",
            "last_activity_at"
        ]


class SecurityAlert(Document):
    """Security alerts and incidents"""
    
    # Alert Information
    alert_id: Indexed(str, unique=True)
    alert_type: str  # brute_force, suspicious_login, data_breach, etc.
    threat_level: ThreatLevel
    
    # Affected User
    user_id: Optional[str] = None
    
    # Alert Details
    title: str
    description: str
    
    # Detection
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    detection_method: str  # rule_based, ml_model, manual, etc.
    
    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    related_requests: List[str] = Field(default_factory=list)  # Request IDs
    
    # Evidence
    evidence: Dict[str, Any] = Field(default_factory=dict)
    
    # Status
    status: str = "new"  # new, investigating, confirmed, false_positive, resolved
    
    # Response
    actions_taken: List[str] = Field(default_factory=list)
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    # Notification
    notifications_sent: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "security_alerts"
        indexes = [
            "alert_id",
            "alert_type",
            "threat_level",
            "user_id",
            "status",
            "detected_at",
            "created_at"
        ]


class RateLimitEntry(Document):
    """Rate limiting tracker"""
    
    # Identifier (user_id, ip_address, or api_key)
    identifier_type: str  # user, ip, api_key
    identifier_value: Indexed(str)
    
    # Endpoint/Resource
    endpoint: Optional[str] = None
    resource_type: Optional[str] = None
    
    # Counts
    request_count: int = 1
    window_start: datetime = Field(default_factory=datetime.utcnow)
    window_end: datetime
    
    # Limits
    limit: int
    
    # Status
    is_blocked: bool = False
    blocked_until: Optional[datetime] = None
    
    # Violation
    violations_count: int = 0
    last_violation_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "rate_limit_entries"
        indexes = [
            "identifier_value",
            [("identifier_type", 1), ("identifier_value", 1)],
            "window_end",
            "is_blocked"
        ]


class DataAccessLog(Document):
    """GDPR-compliant data access logging"""
    
    # User whose data was accessed
    user_id: Indexed(str)
    
    # Accessor
    accessed_by_user_id: Optional[str] = None
    accessed_by_system: Optional[str] = None
    
    # Access Details
    access_type: str  # read, write, delete, export
    data_type: str  # profile, conversations, preferences, etc.
    data_fields: List[str] = Field(default_factory=list)
    
    # Purpose
    purpose: str  # service_delivery, analytics, support, etc.
    legal_basis: Optional[str] = None  # consent, legitimate_interest, etc.
    
    # Request Information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Retention
    retention_until: datetime  # When this log should be deleted
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "data_access_logs"
        indexes = [
            "user_id",
            "accessed_by_user_id",
            "access_type",
            "created_at",
            "retention_until"
        ]


# Response Models
class MFASetupResponse(BaseModel):
    """MFA setup response"""
    mfa_method: MFAMethod
    qr_code_url: Optional[str] = None  # For TOTP
    backup_codes: Optional[List[str]] = None
    phone_number: Optional[str] = None  # Masked
    email: Optional[str] = None  # Masked


class AuditLogResponse(BaseModel):
    """Audit log response"""
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: AuditAction
    description: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool
    created_at: datetime


class APIKeyResponse(BaseModel):
    """API key response"""
    key_id: str
    key: Optional[str] = None  # Only returned on creation
    key_prefix: str
    name: str
    scopes: List[str]
    rate_limit: int
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None


class SecurityAlertResponse(BaseModel):
    """Security alert response"""
    alert_id: str
    alert_type: str
    threat_level: ThreatLevel
    title: str
    description: str
    status: str
    detected_at: datetime


class EmailVerificationToken(Document):
    """Email verification token storage"""
    
    # User Reference
    user_id: Indexed(str, unique=True)
    email: str
    
    # Token
    token: Indexed(str, unique=True)
    
    # Expiration
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "email_verification_tokens"
        indexes = [
            "user_id",
            "token",
            "expires_at",
            [("expires_at", 1)],  # TTL index for automatic cleanup
        ]
