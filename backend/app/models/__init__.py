"""
Models package initialization
"""

# Core Models
from backend.app.models.user import (
    User,
    UserRole,
    UserPreferences,
    UserLocation,
    UserStats,
    UserCreate,
    UserUpdate,
    UserResponse
)

from backend.app.models.attraction import (
    Attraction,
    AttractionCategory,
    AccessibilityFeature,
    Location,
    OpeningHours,
    PricingTier,
    MultilingualContent,
    AttractionImage,
    Review,
    AttractionCreate,
    AttractionUpdate,
    AttractionResponse
)

from backend.app.models.hotel import (
    Hotel,
    HotelCategory,
    RoomType,
    StarRating,
    Room,
    Amenity,
    HotelCreate,
    HotelUpdate,
    HotelResponse
)

from backend.app.models.restaurant import (
    Restaurant,
    CuisineType,
    RestaurantType,
    PriceRange,
    DietaryOption,
    MenuItem,
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse
)

from backend.app.models.transport import (
    Transport,
    TransportType,
    TransportCategory,
    ServiceLevel,
    Schedule,
    Route,
    PricingOption,
    TransportCreate,
    TransportUpdate,
    TransportResponse,
    TransportSearchRequest
)

from backend.app.models.event import (
    Event,
    EventCategory,
    EventStatus,
    TicketType,
    EventSchedule,
    Ticket,
    Organizer,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventSearchRequest
)

from backend.app.models.conversation import (
    Conversation,
    Message,
    MessageType,
    MessageSender,
    ConversationStatus,
    ConversationContext,
    ConversationSummary,
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    ConversationResponse
)

from backend.app.models.emergency import (
    Emergency,
    EmergencyType,
    ServiceLevel,
    ContactMethod,
    EmergencyCreate,
    EmergencyUpdate,
    EmergencyResponse,
    EmergencySearchRequest
)

from backend.app.models.feedback import (
    Feedback,
    FeedbackCategory,
    FeedbackStatus,
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse
)

# Analytics Models
from backend.app.models.analytics import (
    UserBehaviorEvent,
    ConversationAnalytics,
    DailyMetrics,
    ResourcePopularity,
    UserSegmentProfile,
    AnalyticsEventType,
    UserSegment,
    DeviceType,
    AnalyticsResponse,
    PopularResourcesResponse
)

# Recommendation Models
from backend.app.models.recommendation import (
    UserPreferenceProfile,
    RecommendationEngine,
    RecommendationResult,
    ItemSimilarity,
    CollaborativeFilter,
    ContextualFactor,
    RecommendationType,
    RecommendationRequest,
    RecommendationResponse,
    SimilarItemsRequest,
    SimilarItemsResponse
)

# Notification Models
from backend.app.models.notification import (
    NotificationTemplate,
    Notification,
    UserNotificationPreferences,
    NotificationCampaign,
    NotificationType,
    NotificationCategory,
    NotificationPriority,
    NotificationStatus,
    NotificationRequest,
    NotificationResponse,
    NotificationPreferencesUpdate
)

# Security Models
from backend.app.models.security import (
    UserMFA,
    AuditLog,
    APIKey,
    SessionToken,
    SecurityAlert,
    RateLimitEntry,
    DataAccessLog,
    MFAMethod,
    AuditAction,
    ThreatLevel,
    MFASetupResponse,
    AuditLogResponse,
    APIKeyResponse,
    SecurityAlertResponse
)

__all__ = [
    # User
    "User", "UserRole", "UserPreferences", "UserLocation", "UserStats",
    "UserCreate", "UserUpdate", "UserResponse",
    
    # Attraction
    "Attraction", "AttractionCategory", "AccessibilityFeature", "Location",
    "OpeningHours", "PricingTier", "MultilingualContent", "AttractionImage",
    "Review", "AttractionCreate", "AttractionUpdate", "AttractionResponse",
    
    # Hotel
    "Hotel", "HotelCategory", "RoomType", "StarRating", "Room", "Amenity",
    "HotelCreate", "HotelUpdate", "HotelResponse",
    
    # Restaurant
    "Restaurant", "CuisineType", "RestaurantType", "PriceRange", "DietaryOption",
    "MenuItem", "RestaurantCreate", "RestaurantUpdate", "RestaurantResponse",
    
    # Transport
    "Transport", "TransportType", "TransportCategory", "ServiceLevel",
    "Schedule", "Route", "PricingOption", "TransportCreate", "TransportUpdate",
    "TransportResponse", "TransportSearchRequest",
    
    # Event
    "Event", "EventCategory", "EventStatus", "TicketType", "EventSchedule",
    "Ticket", "Organizer", "EventCreate", "EventUpdate", "EventResponse",
    "EventSearchRequest",
    
    # Conversation
    "Conversation", "Message", "MessageType", "MessageSender", "ConversationStatus",
    "ConversationContext", "ConversationSummary", "ConversationCreate",
    "ConversationUpdate", "MessageCreate", "ConversationResponse",
    
    # Emergency
    "Emergency", "EmergencyType", "ServiceLevel", "ContactMethod",
    "EmergencyCreate", "EmergencyUpdate", "EmergencyResponse", "EmergencySearchRequest",
    
    # Feedback
    "Feedback", "FeedbackCategory", "FeedbackStatus", "FeedbackCreate",
    "FeedbackUpdate", "FeedbackResponse",
    
    # Analytics
    "UserBehaviorEvent", "ConversationAnalytics", "DailyMetrics",
    "ResourcePopularity", "UserSegmentProfile", "AnalyticsEventType",
    "UserSegment", "DeviceType", "AnalyticsResponse", "PopularResourcesResponse",
    
    # Recommendation
    "UserPreferenceProfile", "RecommendationEngine", "RecommendationResult",
    "ItemSimilarity", "CollaborativeFilter", "ContextualFactor",
    "RecommendationType", "RecommendationRequest", "RecommendationResponse",
    "SimilarItemsRequest", "SimilarItemsResponse",
    
    # Notification
    "NotificationTemplate", "Notification", "UserNotificationPreferences",
    "NotificationCampaign", "NotificationType", "NotificationCategory",
    "NotificationPriority", "NotificationStatus", "NotificationRequest",
    "NotificationResponse", "NotificationPreferencesUpdate",
    
    # Security
    "UserMFA", "AuditLog", "APIKey", "SessionToken", "SecurityAlert",
    "RateLimitEntry", "DataAccessLog", "MFAMethod", "AuditAction",
    "ThreatLevel", "MFASetupResponse", "AuditLogResponse", "APIKeyResponse",
    "SecurityAlertResponse"
]

