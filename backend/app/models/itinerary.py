"""
Smart Itinerary & Trip Planning Models
AI-powered travel planning with monetization features
"""

from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field, BaseModel
from beanie import Document


class BudgetLevel(str, Enum):
    """Budget level for trip"""
    BUDGET = "budget"  # < $30/day
    MID_RANGE = "mid_range"  # $30-100/day
    LUXURY = "luxury"  # > $100/day


class TripInterest(str, Enum):
    """Travel interests"""
    CULTURE = "culture"
    HISTORY = "history"
    ADVENTURE = "adventure"
    BEACH = "beach"
    WILDLIFE = "wildlife"
    FOOD = "food"
    PHOTOGRAPHY = "photography"
    RELAXATION = "relaxation"


class BookingStatus(str, Enum):
    """Booking status"""
    NOT_BOOKED = "not_booked"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ActivityItem(BaseModel):
    """Single activity in itinerary"""
    time_slot: str = Field(..., description="e.g., '09:00 AM - 11:00 AM'")
    activity_type: str = Field(..., description="attraction, meal, transport, hotel")
    title: str
    description: str
    location: str
    estimated_cost: float = 0
    duration_minutes: int = 0
    
    # Booking integration
    resource_id: Optional[str] = None
    booking_url: Optional[str] = None
    booking_partner: Optional[str] = None  # booking.com, agoda, uber, etc.
    commission_rate: Optional[float] = None
    
    # Additional info
    tips: List[str] = Field(default_factory=list)
    photos: List[str] = Field(default_factory=list)
    rating: Optional[float] = None


class DayItinerary(BaseModel):
    """One day in the trip"""
    day_number: int
    date: date
    location: str  # Main location for the day
    title: str  # e.g., "Exploring Cultural Kandy"
    activities: List[ActivityItem] = Field(default_factory=list)
    total_cost: float = 0
    highlights: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }


class TripItinerary(Document):
    """Complete trip itinerary"""
    
    # User info
    user_id: str
    session_id: Optional[str] = None
    
    # Trip details
    title: str
    destination: str
    duration_days: int
    start_date: date
    end_date: date
    
    class Settings:
        name = "trip_itineraries"
        
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    
    # Preferences
    budget_level: BudgetLevel
    interests: List[TripInterest] = Field(default_factory=list)
    travelers_count: int = 1
    
    # Itinerary content
    days: List[DayItinerary] = Field(default_factory=list)
    
    # Costs
    total_estimated_cost: float = 0
    currency: str = "USD"
    cost_breakdown: Dict[str, float] = Field(
        default_factory=lambda: {
            "accommodation": 0,
            "food": 0,
            "transport": 0,
            "activities": 0,
            "other": 0
        }
    )
    
    # AI Generation
    generated_by_ai: bool = True
    generation_prompt: Optional[str] = None
    llm_model: str = "mistral-7b"
    
    # Monetization
    contains_bookable_items: bool = False
    total_potential_commission: float = 0
    
    # Status
    is_active: bool = True
    is_shared: bool = False
    share_token: Optional[str] = None
    
    # Engagement
    views: int = 0
    bookings_made: int = 0
    total_revenue: float = 0
    
    # Export
    exported_to_pdf: bool = False
    exported_to_calendar: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_viewed_at: Optional[datetime] = None
    
    class Settings:
        name = "trip_itineraries"
        indexes = [
            "user_id",
            "session_id",
            "start_date",
            "created_at",
            "share_token",
            [("user_id", 1), ("created_at", -1)],
            [("is_shared", 1), ("views", -1)],
        ]
    
    def calculate_totals(self):
        """Calculate total costs and commissions"""
        total = 0
        commission = 0
        
        for day in self.days:
            day_total = 0
            for activity in day.activities:
                day_total += activity.estimated_cost
                if activity.booking_url and activity.commission_rate:
                    commission += activity.estimated_cost * activity.commission_rate
            day.total_cost = day_total
            total += day_total
        
        self.total_estimated_cost = total
        self.total_potential_commission = commission
        self.contains_bookable_items = commission > 0


class BookingTracking(Document):
    """Track bookings made through itinerary"""
    
    itinerary_id: str
    user_id: str
    activity_item: ActivityItem
    
    # Booking details
    booking_partner: str  # booking.com, agoda, uber, etc.
    booking_reference: Optional[str] = None
    booking_status: BookingStatus = BookingStatus.PENDING
    
    # Financial
    booking_amount: float
    commission_amount: float
    commission_rate: float
    currency: str = "USD"
    
    # Payment
    payment_status: str = "pending"
    payment_reference: Optional[str] = None
    
    # Tracking
    booked_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "booking_tracking"
        indexes = [
            "itinerary_id",
            "user_id",
            "booking_partner",
            "booking_status",
            [("user_id", 1), ("booked_at", -1)],
        ]


# API Request/Response Models

class ItineraryGenerateRequest(BaseModel):
    """Request to generate AI itinerary"""
    destination: str = Field(..., description="e.g., 'Kandy', 'Galle'")
    duration_days: int = Field(..., ge=1, le=14, description="1-14 days")
    budget_level: BudgetLevel
    interests: List[TripInterest]
    start_date: date
    travelers_count: int = Field(1, ge=1, le=10)
    custom_requirements: Optional[str] = None


class ItineraryResponse(BaseModel):
    """Itinerary response"""
    id: str
    title: str
    destination: str
    duration_days: int
    start_date: date
    end_date: date
    days: List[DayItinerary]
    total_estimated_cost: float
    currency: str
    share_url: Optional[str] = None


class BookingRequest(BaseModel):
    """Request to book an activity"""
    itinerary_id: str
    day_number: int
    activity_index: int
    user_details: Dict[str, Any]

