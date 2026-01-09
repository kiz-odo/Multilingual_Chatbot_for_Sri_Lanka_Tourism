"""
GraphQL Types for Sri Lanka Tourism Chatbot
Defines all GraphQL types, inputs, and enums
"""

from typing import List, Optional
from datetime import datetime, date
from enum import Enum
import strawberry


# ==========================================
# ENUMS
# ==========================================

@strawberry.enum
class BudgetLevelEnum(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"


@strawberry.enum
class TripInterestEnum(str, Enum):
    CULTURE = "culture"
    HISTORY = "history"
    ADVENTURE = "adventure"
    BEACH = "beach"
    WILDLIFE = "wildlife"
    FOOD = "food"
    PHOTOGRAPHY = "photography"
    RELAXATION = "relaxation"


# ==========================================
# BASIC TYPES
# ==========================================

@strawberry.type
class LocationType:
    """Location information"""
    city: str
    province: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@strawberry.type
class MultilingualText:
    """Multilingual content"""
    en: str
    si: Optional[str] = None
    ta: Optional[str] = None
    de: Optional[str] = None
    fr: Optional[str] = None


# ==========================================
# ATTRACTION
# ==========================================

@strawberry.type
class AttractionType:
    """Attraction type for GraphQL"""
    id: str
    name: MultilingualText
    description: MultilingualText
    short_description: MultilingualText
    category: str
    location: LocationType
    average_rating: float
    total_reviews: int
    photos: List[str]
    tags: List[str]
    is_free: bool
    popularity_score: float
    is_active: bool


# ==========================================
# HOTEL
# ==========================================

@strawberry.type
class HotelType:
    """Hotel type for GraphQL"""
    id: str
    name: MultilingualText
    description: MultilingualText
    short_description: MultilingualText
    category: str
    star_rating: str
    location: LocationType
    average_rating: float
    total_reviews: int
    photos: List[str]
    amenities: List[str]
    is_active: bool


# ==========================================
# RESTAURANT
# ==========================================

@strawberry.type
class RestaurantType:
    """Restaurant type for GraphQL"""
    id: str
    name: MultilingualText
    description: MultilingualText
    short_description: MultilingualText
    cuisine_types: List[str]
    restaurant_type: str
    price_range: str
    location: LocationType
    average_rating: float
    total_reviews: int
    photos: List[str]
    dietary_options: List[str]
    is_active: bool


# ==========================================
# EVENT
# ==========================================

@strawberry.type
class EventType:
    """Event type for GraphQL"""
    id: str
    title: MultilingualText
    description: MultilingualText
    category: str
    location: LocationType
    start_date: date
    end_date: Optional[date] = None
    status: str
    tags: List[str]


# ==========================================
# ITINERARY
# ==========================================

@strawberry.type
class ActivityItemType:
    """Single activity in itinerary"""
    time_slot: str
    activity_type: str
    title: str
    description: str
    location: str
    estimated_cost: float
    duration_minutes: int
    rating: Optional[float] = None
    booking_url: Optional[str] = None
    booking_partner: Optional[str] = None
    tips: List[str]


@strawberry.type
class DayItineraryType:
    """One day in the trip"""
    day_number: int
    date: date
    location: str
    title: str
    activities: List[ActivityItemType]
    total_cost: float
    highlights: List[str]


@strawberry.type
class ItineraryType:
    """Complete trip itinerary"""
    id: str
    title: str
    destination: str
    duration_days: int
    start_date: date
    end_date: date
    budget_level: str
    interests: List[str]
    travelers_count: int
    days: List[DayItineraryType]
    total_estimated_cost: float
    currency: str
    share_url: Optional[str] = None
    created_at: datetime
    bookings_made: int
    total_revenue: float


# ==========================================
# USER
# ==========================================

@strawberry.type
class UserType:
    """User type for GraphQL"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    role: str
    is_active: bool
    is_email_verified: bool
    oauth_provider: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None


# ==========================================
# CONVERSATION
# ==========================================

@strawberry.type
class MessageType:
    """Chat message type"""
    sender: str
    content: str
    language: str
    timestamp: datetime


@strawberry.type
class ConversationType:
    """Conversation type"""
    id: str
    user_id: str
    session_id: str
    language: str
    messages: List[MessageType]
    created_at: datetime
    updated_at: datetime


# ==========================================
# AUTHENTICATION
# ==========================================

@strawberry.type
class AuthPayload:
    """Authentication response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserType


# ==========================================
# INPUT TYPES
# ==========================================

@strawberry.input
class MessageInput:
    """Input for sending chat message"""
    message: str
    language: str = "en"
    session_id: Optional[str] = None


@strawberry.input
class ItineraryInput:
    """Input for generating itinerary"""
    destination: str
    duration_days: int
    budget_level: BudgetLevelEnum
    interests: List[TripInterestEnum]
    start_date: date
    travelers_count: int = 1
    custom_requirements: Optional[str] = None


@strawberry.input
class UserUpdateInput:
    """Input for updating user profile"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None


# ==========================================
# FILTER INPUTS
# ==========================================

@strawberry.input
class AttractionFilterInput:
    """Filter for attractions"""
    city: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = None
    is_free: Optional[bool] = None
    tags: Optional[List[str]] = None


@strawberry.input
class HotelFilterInput:
    """Filter for hotels"""
    city: Optional[str] = None
    star_rating: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[float] = None


@strawberry.input
class RestaurantFilterInput:
    """Filter for restaurants"""
    city: Optional[str] = None
    cuisine_types: Optional[List[str]] = None
    price_range: Optional[str] = None
    dietary_options: Optional[List[str]] = None

