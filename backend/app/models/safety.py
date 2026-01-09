"""
Safety & Emergency Features Models
Real-time safety tracking and emergency assistance
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field, BaseModel
from beanie import Document


class EmergencyType(str, Enum):
    """Type of emergency"""
    MEDICAL = "medical"
    ACCIDENT = "accident"
    THEFT = "theft"
    LOST = "lost"
    NATURAL_DISASTER = "natural_disaster"
    HARASSMENT = "harassment"
    OTHER = "other"


class EmergencyStatus(str, Enum):
    """Status of emergency"""
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class SafetyLevel(str, Enum):
    """Safety level for areas"""
    VERY_SAFE = "very_safe"
    SAFE = "safe"
    MODERATE = "moderate"
    CAUTION = "caution"
    UNSAFE = "unsafe"


class AlertType(str, Enum):
    """Type of travel alert"""
    WEATHER = "weather"
    PROTEST = "protest"
    STRIKE = "strike"
    ROAD_CLOSURE = "road_closure"
    HEALTH = "health"
    SECURITY = "security"
    EVENT = "event"


class Location(BaseModel):
    """Geographic location"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Sri Lanka"


class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str
    phone: str
    email: Optional[str] = None
    relationship: str


class SOSAlert(Document):
    """SOS emergency alert"""
    
    # User info
    user_id: str
    user_name: str
    user_phone: Optional[str] = None
    
    # Emergency details
    emergency_type: EmergencyType
    description: str
    severity: int = Field(..., ge=1, le=5, description="1=minor, 5=critical")
    
    # Location
    location: Location
    location_shared: bool = True
    
    # Status
    status: EmergencyStatus = EmergencyStatus.ACTIVE
    
    # Response
    responders_notified: List[str] = Field(default_factory=list)
    response_time_seconds: Optional[int] = None
    resolution_notes: Optional[str] = None
    
    # Contacts
    emergency_contacts_notified: List[str] = Field(default_factory=list)
    
    # Media
    photos: List[str] = Field(default_factory=list)
    voice_message_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    class Settings:
        name = "sos_alerts"
        indexes = [
            "user_id",
            "status",
            "emergency_type",
            "created_at",
            [("status", 1), ("created_at", -1)],
            [("location.city", 1), ("status", 1)],
        ]


class LocationSharing(Document):
    """Real-time location sharing with family/friends"""
    
    # User sharing location
    user_id: str
    user_name: str
    
    # Location
    current_location: Location
    location_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Sharing settings
    shared_with: List[str] = Field(..., description="Phone numbers or user IDs")
    share_token: str = Field(..., description="Public token for tracking link")
    
    # Duration
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = True
    
    # Updates
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    update_interval_minutes: int = 5
    
    # Trip info
    trip_description: Optional[str] = None
    expected_return: Optional[datetime] = None
    
    # Safety features
    auto_check_in_enabled: bool = False
    check_in_interval_hours: int = 12
    last_check_in: Optional[datetime] = None
    missed_check_ins: int = 0
    
    class Settings:
        name = "location_sharing"
        indexes = [
            "user_id",
            "share_token",
            "is_active",
            [("is_active", 1), ("last_updated", -1)],
        ]


class SafetyScore(Document):
    """Safety score for areas/locations"""
    
    # Location
    area_name: str
    city: str
    coordinates: Location
    
    # Score
    safety_level: SafetyLevel
    safety_score: float = Field(..., ge=0, le=100)
    
    # Breakdown
    crime_score: float = Field(..., ge=0, le=100)
    tourist_safety_score: float = Field(..., ge=0, le=100)
    infrastructure_score: float = Field(..., ge=0, le=100)
    health_safety_score: float = Field(..., ge=0, le=100)
    
    # Data sources
    police_reports_count: int = 0
    user_reports_count: int = 0
    official_rating: Optional[str] = None
    
    # Time-based
    day_score: float = Field(..., ge=0, le=100)
    night_score: float = Field(..., ge=0, le=100)
    
    # Tips
    safety_tips: List[str] = Field(default_factory=list)
    common_issues: List[str] = Field(default_factory=list)
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_quality_score: float = Field(50, ge=0, le=100)
    
    class Settings:
        name = "safety_scores"
        indexes = [
            "city",
            "area_name",
            "safety_level",
            [("city", 1), ("safety_score", -1)],
        ]


class TravelAlert(Document):
    """Real-time travel alerts and warnings"""
    
    # Alert info
    title: str
    description: str
    alert_type: AlertType
    severity: int = Field(..., ge=1, le=5)
    
    # Affected area
    affected_cities: List[str] = Field(default_factory=list)
    affected_areas: List[str] = Field(default_factory=list)
    coordinates: Optional[Location] = None
    radius_km: Optional[float] = None
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    is_ongoing: bool = True
    
    # Actions
    recommended_actions: List[str] = Field(default_factory=list)
    avoid_areas: List[str] = Field(default_factory=list)
    alternative_routes: List[str] = Field(default_factory=list)
    
    # Source
    source: str = Field(..., description="police, weather_service, user_report, etc.")
    verified: bool = False
    
    # Engagement
    views: int = 0
    users_affected: int = 0
    users_notified: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    class Settings:
        name = "travel_alerts"
        indexes = [
            "alert_type",
            "is_ongoing",
            "severity",
            "affected_cities",
            [("is_ongoing", 1), ("severity", -1), ("created_at", -1)],
        ]


class UserSafetyProfile(Document):
    """User's safety settings and preferences"""
    
    user_id: str
    
    # Emergency contacts
    emergency_contacts: List[EmergencyContact] = Field(default_factory=list)
    
    # Medical info
    blood_type: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)
    
    # Insurance
    travel_insurance_provider: Optional[str] = None
    policy_number: Optional[str] = None
    insurance_contact: Optional[str] = None
    
    # Embassy
    home_country: str
    embassy_contact_saved: bool = False
    
    # Preferences
    auto_share_location_emergency: bool = True
    notify_contacts_on_sos: bool = True
    enable_safety_check_ins: bool = False
    check_in_frequency_hours: int = 24
    
    # Alert preferences
    receive_weather_alerts: bool = True
    receive_security_alerts: bool = True
    alert_radius_km: float = 50
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_safety_profiles"
        indexes = [
            "user_id",
        ]


class SafetyCheckIn(Document):
    """Safety check-in records"""
    
    user_id: str
    location: Location
    
    status: str = Field(..., description="safe, needs_help, emergency")
    message: Optional[str] = None
    
    # Auto check-in
    is_automatic: bool = False
    location_sharing_id: Optional[str] = None
    
    check_in_time: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "safety_check_ins"
        indexes = [
            "user_id",
            "check_in_time",
            [("user_id", 1), ("check_in_time", -1)],
        ]


# API Request/Response Models

class SOSRequest(BaseModel):
    """SOS alert request"""
    emergency_type: EmergencyType
    description: str
    severity: int = Field(3, ge=1, le=5)
    location: Location
    photo_urls: Optional[List[str]] = None


class LocationSharingRequest(BaseModel):
    """Start location sharing"""
    shared_with: List[str] = Field(..., description="Phone numbers")
    duration_hours: int = Field(24, ge=1, le=168)
    trip_description: Optional[str] = None
    enable_auto_check_in: bool = False


class SafetyScoreResponse(BaseModel):
    """Safety score response"""
    area_name: str
    city: str
    safety_level: SafetyLevel
    safety_score: float
    safety_tips: List[str]
    day_score: float
    night_score: float


class TravelAlertResponse(BaseModel):
    """Travel alert response"""
    title: str
    description: str
    alert_type: AlertType
    severity: int
    affected_cities: List[str]
    recommended_actions: List[str]
    is_ongoing: bool

