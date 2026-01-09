"""
Analytics models for Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class AnalyticsEventType(str, Enum):
    """Analytics event types"""
    SEARCH = "search"
    VIEW = "view"
    CLICK = "click"
    BOOKING = "booking"
    RATING = "rating"
    SHARE = "share"
    FAVORITE = "favorite"
    VISIT = "visit"
    NAVIGATION = "navigation"
    VOICE_QUERY = "voice_query"
    IMAGE_SEARCH = "image_search"


class UserSegment(str, Enum):
    """User segments"""
    TOURIST = "tourist"
    LOCAL = "local"
    BUSINESS = "business"
    FREQUENT = "frequent"
    NEW = "new"
    INACTIVE = "inactive"


class DeviceType(str, Enum):
    """Device types"""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    VOICE_ASSISTANT = "voice_assistant"
    OTHER = "other"


class UserBehaviorEvent(Document):
    """User behavior event tracking"""
    
    # User Information
    user_id: Optional[Indexed(str)] = None  # Allow anonymous
    session_id: str
    
    # Event Information
    event_type: AnalyticsEventType
    event_name: str
    event_category: Optional[str] = None
    
    # Event Details
    resource_type: Optional[str] = None  # attraction, hotel, restaurant, etc.
    resource_id: Optional[str] = None
    
    # Search and Query
    search_query: Optional[str] = None
    search_filters: Dict[str, Any] = Field(default_factory=dict)
    search_results_count: Optional[int] = None
    
    # Interaction Details
    interaction_duration: Optional[float] = None  # in seconds
    scroll_depth: Optional[float] = None  # percentage
    click_position: Optional[int] = None
    
    # Location Information
    user_location: Optional[Dict[str, Any]] = None  # city, country, coordinates
    user_ip: Optional[str] = None
    
    # Device and Platform
    device_type: DeviceType = DeviceType.MOBILE
    browser: Optional[str] = None
    operating_system: Optional[str] = None
    screen_resolution: Optional[str] = None
    
    # Language and Localization
    language: str = "en"
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "user_behavior_events"
        indexes = [
            "user_id",
            "session_id",
            "event_type",
            "event_name",
            "resource_type",
            "resource_id",
            "created_at",
            "language",
            "device_type"
        ]


class ConversationAnalytics(Document):
    """Conversation analytics and insights"""
    
    # Conversation Reference
    conversation_id: Indexed(str, unique=True)
    user_id: Optional[str] = None
    session_id: str
    
    # Conversation Metrics
    total_messages: int = 0
    user_messages: int = 0
    bot_messages: int = 0
    average_response_time: float = 0.0  # in seconds
    
    # Intent Analysis
    intents_detected: List[str] = Field(default_factory=list)
    intent_counts: Dict[str, int] = Field(default_factory=dict)
    failed_intents: List[str] = Field(default_factory=list)
    fallback_count: int = 0
    
    # Entity Extraction
    entities_extracted: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Language Analysis
    languages_used: List[str] = Field(default_factory=list)
    language_switches: int = 0
    primary_language: str = "en"
    
    # Sentiment Analysis
    sentiment_scores: List[float] = Field(default_factory=list)
    average_sentiment: float = 0.0  # -1 (negative) to 1 (positive)
    sentiment_trend: Optional[str] = None  # improving, declining, stable
    
    # User Satisfaction
    user_satisfaction_score: Optional[float] = None  # 1-5
    resolved_queries: int = 0
    unresolved_queries: int = 0
    
    # Topics and Categories
    topics_discussed: List[str] = Field(default_factory=list)
    topic_durations: Dict[str, float] = Field(default_factory=dict)
    
    # Resources Recommended
    attractions_recommended: List[str] = Field(default_factory=list)
    hotels_recommended: List[str] = Field(default_factory=list)
    restaurants_recommended: List[str] = Field(default_factory=list)
    events_recommended: List[str] = Field(default_factory=list)
    
    # Engagement Metrics
    conversation_duration: float = 0.0  # in seconds
    user_engagement_score: float = 0.0  # 0-100
    
    # External API Usage
    apis_called: List[str] = Field(default_factory=list)
    api_call_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Timestamps
    conversation_started_at: datetime
    conversation_ended_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "conversation_analytics"
        indexes = [
            "conversation_id",
            "user_id",
            "session_id",
            "primary_language",
            "conversation_started_at",
            "user_satisfaction_score"
        ]


class DailyMetrics(Document):
    """Daily aggregated metrics"""
    
    # Date
    date: Indexed(date, unique=True)
    
    # User Metrics
    total_users: int = 0
    new_users: int = 0
    returning_users: int = 0
    active_users: int = 0
    
    # Conversation Metrics
    total_conversations: int = 0
    total_messages: int = 0
    average_conversation_duration: float = 0.0
    average_messages_per_conversation: float = 0.0
    
    # Engagement Metrics
    total_searches: int = 0
    total_views: int = 0
    total_bookings: int = 0
    total_ratings: int = 0
    average_satisfaction_score: float = 0.0
    
    # Content Metrics
    most_viewed_attractions: List[Dict[str, Any]] = Field(default_factory=list)
    most_searched_locations: List[Dict[str, Any]] = Field(default_factory=list)
    popular_categories: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Language Distribution
    language_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Device Distribution
    device_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Intent Statistics
    top_intents: List[Dict[str, Any]] = Field(default_factory=list)
    failed_intent_rate: float = 0.0
    
    # Response Time
    average_response_time: float = 0.0
    
    # Error Rates
    error_rate: float = 0.0
    fallback_rate: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "daily_metrics"
        indexes = [
            "date",
            "created_at"
        ]


class ResourcePopularity(Document):
    """Track popularity of tourism resources"""
    
    # Resource Information
    resource_type: str  # attraction, hotel, restaurant, event, transport
    resource_id: Indexed(str)
    
    # Popularity Metrics
    view_count: int = 0
    search_count: int = 0
    click_count: int = 0
    favorite_count: int = 0
    share_count: int = 0
    booking_count: int = 0
    
    # Rating Metrics
    total_ratings: int = 0
    average_rating: float = 0.0
    rating_distribution: Dict[str, int] = Field(default_factory=dict)  # {1: count, 2: count, ...}
    
    # Time-based Metrics
    views_last_7_days: int = 0
    views_last_30_days: int = 0
    views_last_90_days: int = 0
    
    # Calculated Scores
    popularity_score: float = 0.0  # Weighted calculation
    trending_score: float = 0.0  # Based on recent activity
    recommendation_score: float = 0.0  # ML-based recommendation score
    
    # User Segments
    popularity_by_segment: Dict[str, int] = Field(default_factory=dict)
    
    # Language-specific Views
    views_by_language: Dict[str, int] = Field(default_factory=dict)
    
    # Seasonal Trends
    monthly_views: Dict[str, int] = Field(default_factory=dict)
    
    # Timestamps
    last_viewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "resource_popularity"
        indexes = [
            "resource_type",
            "resource_id",
            [("resource_type", 1), ("resource_id", 1)],
            "popularity_score",
            "trending_score",
            "recommendation_score",
            "last_viewed_at"
        ]
    
    def update_popularity_score(self):
        """Calculate weighted popularity score"""
        # Weighted formula for popularity
        self.popularity_score = (
            (self.view_count * 1) +
            (self.search_count * 2) +
            (self.click_count * 3) +
            (self.favorite_count * 5) +
            (self.share_count * 4) +
            (self.booking_count * 10) +
            (self.average_rating * 10)
        )
    
    def update_trending_score(self):
        """Calculate trending score based on recent activity"""
        # Weight recent activity more heavily
        self.trending_score = (
            (self.views_last_7_days * 5) +
            (self.views_last_30_days * 2) +
            (self.views_last_90_days * 1)
        )


class UserSegmentProfile(Document):
    """User segment profiles for targeted recommendations"""
    
    # Segment Information
    segment_id: Indexed(str, unique=True)
    segment_name: str
    segment_type: UserSegment
    
    # Demographics
    age_range: Optional[str] = None
    countries: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    
    # Behavior Patterns
    preferred_categories: List[str] = Field(default_factory=list)
    preferred_price_range: Optional[str] = None
    average_trip_duration: Optional[int] = None  # in days
    travel_style: List[str] = Field(default_factory=list)
    
    # Engagement Metrics
    average_session_duration: float = 0.0
    average_messages_per_session: float = 0.0
    average_satisfaction_score: float = 0.0
    
    # Preferences
    top_attractions: List[str] = Field(default_factory=list)
    top_activities: List[str] = Field(default_factory=list)
    peak_booking_times: List[str] = Field(default_factory=list)
    
    # Conversion Metrics
    conversion_rate: float = 0.0
    average_booking_value: float = 0.0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "user_segment_profiles"
        indexes = [
            "segment_id",
            "segment_type",
            "created_at"
        ]


# Response models
class AnalyticsResponse(BaseModel):
    """General analytics response"""
    period: str
    metrics: Dict[str, Any]
    trends: Dict[str, Any]
    comparisons: Dict[str, Any]


class PopularResourcesResponse(BaseModel):
    """Popular resources response"""
    resource_type: str
    resources: List[Dict[str, Any]]
    time_period: str

