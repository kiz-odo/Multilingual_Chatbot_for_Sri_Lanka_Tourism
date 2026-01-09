"""
Event model for Sri Lanka Tourism
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum

from backend.app.models.attraction import Location, MultilingualContent, AttractionImage


class EventCategory(str, Enum):
    """Event categories"""
    CULTURAL = "cultural"
    RELIGIOUS = "religious"
    FESTIVAL = "festival"
    MUSIC = "music"
    DANCE = "dance"
    ART = "art"
    SPORTS = "sports"
    FOOD = "food"
    EXHIBITION = "exhibition"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    TOUR = "tour"
    SEASONAL = "seasonal"
    NATIONAL = "national"


class EventStatus(str, Enum):
    """Event status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class TicketType(str, Enum):
    """Ticket types"""
    FREE = "free"
    PAID = "paid"
    DONATION = "donation"
    REGISTRATION = "registration"


class EventSchedule(BaseModel):
    """Event schedule model"""
    start_date: datetime
    end_date: Optional[datetime] = None
    start_time: Optional[str] = None  # Format: "HH:MM"
    end_time: Optional[str] = None  # Format: "HH:MM"
    is_all_day: bool = False
    recurring: bool = False
    recurring_pattern: Optional[str] = None  # daily, weekly, monthly, yearly
    recurring_end_date: Optional[datetime] = None


class Ticket(BaseModel):
    """Ticket model"""
    ticket_type: TicketType
    name: MultilingualContent
    description: Optional[MultilingualContent] = None
    price: float = 0.0
    currency: str = "LKR"
    quantity_available: Optional[int] = None
    quantity_sold: int = 0
    is_available: bool = True
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None


class Organizer(BaseModel):
    """Event organizer model"""
    name: str
    organization: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[HttpUrl] = None
    bio: Optional[MultilingualContent] = None


class Event(Document):
    """Event document model"""
    
    # Basic Information
    title: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    
    # Classification
    category: EventCategory
    subcategories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Schedule
    schedule: EventSchedule
    duration_minutes: Optional[int] = None
    
    # Location
    location: Location
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    is_online_event: bool = False
    online_platform: Optional[str] = None
    meeting_link: Optional[HttpUrl] = None
    
    # Media
    images: List[AttractionImage] = Field(default_factory=list)
    video_urls: List[HttpUrl] = Field(default_factory=list)
    
    # Organizer Information
    organizers: List[Organizer] = Field(default_factory=list)
    sponsors: List[str] = Field(default_factory=list)
    partners: List[str] = Field(default_factory=list)
    
    # Ticketing
    tickets: List[Ticket] = Field(default_factory=list)
    booking_required: bool = False
    booking_url: Optional[HttpUrl] = None
    booking_phone: Optional[str] = None
    booking_email: Optional[str] = None
    
    # Event Details
    target_audience: List[str] = Field(default_factory=list)  # families, adults, children, tourists
    languages: List[str] = Field(default_factory=list)  # languages used in event
    dress_code: Optional[MultilingualContent] = None
    what_to_bring: Optional[MultilingualContent] = None
    
    # Accessibility and Amenities
    accessibility_features: List[str] = Field(default_factory=list)
    amenities: List[str] = Field(default_factory=list)
    parking_available: bool = False
    food_available: bool = False
    
    # Cultural Information
    cultural_significance: Optional[MultilingualContent] = None
    historical_background: Optional[MultilingualContent] = None
    traditions_involved: List[str] = Field(default_factory=list)
    
    # Weather and Season
    best_weather_conditions: Optional[str] = None
    season: Optional[str] = None  # dry, wet, monsoon
    indoor_alternative: bool = False
    
    # Related Information
    related_attractions: List[str] = Field(default_factory=list)  # attraction IDs
    related_events: List[str] = Field(default_factory=list)  # event IDs
    recommended_accommodations: List[str] = Field(default_factory=list)  # hotel IDs
    
    # Status and Metadata
    status: EventStatus = EventStatus.DRAFT
    is_featured: bool = False
    popularity_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # SEO and Search
    slug: Indexed(str, unique=True)
    keywords: List[str] = Field(default_factory=list)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "events"
        indexes = [
            "title.en",
            "category",
            "schedule.start_date",
            "schedule.end_date",
            "location.city",
            "location.province",
            [("location.coordinates", "2dsphere")],
            "status",
            "is_featured",
            "popularity_score"
        ]
    
    def is_active(self) -> bool:
        """Check if event is currently active"""
        now = datetime.now().date()
        
        if self.schedule.end_date:
            return self.schedule.start_date <= now <= self.schedule.end_date
        else:
            return self.schedule.start_date == now
    
    def is_upcoming(self) -> bool:
        """Check if event is upcoming"""
        now = datetime.now().date()
        return self.schedule.start_date > now
    
    def is_past(self) -> bool:
        """Check if event is past"""
        now = datetime.now().date()
        
        if self.schedule.end_date:
            return self.schedule.end_date < now
        else:
            return self.schedule.start_date < now
    
    def get_available_tickets(self) -> List[Ticket]:
        """Get available tickets"""
        return [ticket for ticket in self.tickets if ticket.is_available]
    
    def get_free_tickets(self) -> List[Ticket]:
        """Get free tickets"""
        return [ticket for ticket in self.tickets if ticket.ticket_type == TicketType.FREE and ticket.is_available]


class EventCreate(BaseModel):
    """Event creation model"""
    title: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    category: EventCategory
    schedule: EventSchedule
    location: Location
    venue_name: Optional[str] = None
    is_online_event: bool = False


class EventUpdate(BaseModel):
    """Event update model"""
    title: Optional[MultilingualContent] = None
    description: Optional[MultilingualContent] = None
    short_description: Optional[MultilingualContent] = None
    category: Optional[EventCategory] = None
    schedule: Optional[EventSchedule] = None
    venue_name: Optional[str] = None
    status: Optional[EventStatus] = None
    is_featured: Optional[bool] = None


class EventResponse(BaseModel):
    """Event response model"""
    id: str
    title: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    category: EventCategory
    subcategories: List[str]
    tags: List[str]
    schedule: EventSchedule
    location: Location
    venue_name: Optional[str] = None
    venue_capacity: Optional[int] = None
    is_online_event: bool
    images: List[AttractionImage]
    organizers: List[Organizer]
    tickets: List[Ticket]
    target_audience: List[str]
    languages: List[str]
    accessibility_features: List[str]
    status: EventStatus
    is_featured: bool
    created_at: datetime
    updated_at: datetime


class EventSearchRequest(BaseModel):
    """Event search request model"""
    category: Optional[EventCategory] = None
    location: Optional[str] = None  # city or province
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_free: Optional[bool] = None
    language: Optional[str] = "en"
    tags: Optional[List[str]] = None
