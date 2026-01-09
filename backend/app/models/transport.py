"""
Transport model for Sri Lanka Tourism
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from enum import Enum

from backend.app.models.attraction import Location, MultilingualContent


class TransportType(str, Enum):
    """Transport types"""
    TRAIN = "train"
    BUS = "bus"
    TAXI = "taxi"
    TUK_TUK = "tuk_tuk"
    RENTAL_CAR = "rental_car"
    BOAT = "boat"
    PLANE = "plane"
    BICYCLE = "bicycle"
    WALKING = "walking"


class TransportCategory(str, Enum):
    """Transport categories"""
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"
    RENTAL = "rental"


class ServiceLevel(str, Enum):
    """Service levels"""
    ECONOMY = "economy"
    STANDARD = "standard"
    PREMIUM = "premium"
    LUXURY = "luxury"


class Schedule(BaseModel):
    """Schedule model"""
    departure_time: str  # Format: "HH:MM"
    arrival_time: str  # Format: "HH:MM"
    duration_minutes: int
    frequency: Optional[str] = None  # daily, hourly, etc.
    days_of_week: List[int] = Field(default_factory=list)  # 0=Monday, 6=Sunday
    seasonal_availability: Optional[str] = None
    notes: Optional[MultilingualContent] = None


class Route(BaseModel):
    """Route model"""
    origin: str
    destination: str
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    stops: List[str] = Field(default_factory=list)
    route_description: Optional[MultilingualContent] = None


class PricingOption(BaseModel):
    """Pricing option model"""
    service_level: ServiceLevel
    price: float
    currency: str = "LKR"
    price_type: str = "per_person"  # per_person, per_vehicle, per_km
    description: Optional[MultilingualContent] = None
    includes: List[str] = Field(default_factory=list)
    excludes: List[str] = Field(default_factory=list)


class Transport(Document):
    """Transport document model"""
    
    # Basic Information
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    
    # Classification
    transport_type: TransportType
    category: TransportCategory
    service_levels: List[ServiceLevel] = Field(default_factory=list)
    
    # Operator Information
    operator_name: Optional[str] = None
    operator_contact: Optional[str] = None
    operator_website: Optional[HttpUrl] = None
    license_number: Optional[str] = None
    
    # Route and Schedule
    routes: List[Route] = Field(default_factory=list)
    schedules: List[Schedule] = Field(default_factory=list)
    operates_24_7: bool = False
    
    # Pricing
    pricing_options: List[PricingOption] = Field(default_factory=list)
    accepts_online_booking: bool = False
    booking_url: Optional[HttpUrl] = None
    booking_phone: Optional[str] = None
    
    # Vehicle Information
    vehicle_capacity: Optional[int] = None
    vehicle_type: Optional[str] = None
    fleet_size: Optional[int] = None
    average_vehicle_age: Optional[int] = None
    
    # Features and Amenities
    amenities: List[str] = Field(default_factory=list)  # AC, WiFi, restroom, etc.
    accessibility_features: List[str] = Field(default_factory=list)
    luggage_policy: Optional[MultilingualContent] = None
    
    # Safety and Regulations
    safety_certifications: List[str] = Field(default_factory=list)
    insurance_coverage: Optional[str] = None
    driver_requirements: Optional[str] = None
    
    # Location Coverage
    service_areas: List[str] = Field(default_factory=list)  # cities, provinces
    pickup_locations: List[Location] = Field(default_factory=list)
    drop_off_locations: List[Location] = Field(default_factory=list)
    
    # Booking and Policies
    advance_booking_required: bool = False
    cancellation_policy: Optional[MultilingualContent] = None
    refund_policy: Optional[MultilingualContent] = None
    terms_and_conditions: Optional[MultilingualContent] = None
    
    # Reviews and Ratings
    average_rating: float = 0.0
    total_reviews: int = 0
    safety_rating: float = 0.0
    punctuality_rating: float = 0.0
    comfort_rating: float = 0.0
    value_rating: float = 0.0
    
    # Environmental Impact
    eco_friendly: bool = False
    carbon_footprint: Optional[str] = None
    sustainability_practices: List[str] = Field(default_factory=list)
    
    # Status and Metadata
    is_active: bool = True
    is_featured: bool = False
    popularity_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # SEO and Search
    slug: Indexed(str, unique=True)
    keywords: List[str] = Field(default_factory=list)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "transport"
        indexes = [
            "name.en",
            "transport_type",
            "category",
            "service_areas",
            "is_active",
            "is_featured",
            "popularity_score",
            "average_rating"
        ]
    
    def get_route_by_destinations(self, origin: str, destination: str) -> Optional[Route]:
        """Get route by origin and destination"""
        for route in self.routes:
            if route.origin.lower() == origin.lower() and route.destination.lower() == destination.lower():
                return route
        return None
    
    def get_pricing_by_service_level(self, service_level: ServiceLevel) -> Optional[PricingOption]:
        """Get pricing by service level"""
        for pricing in self.pricing_options:
            if pricing.service_level == service_level:
                return pricing
        return None


class TransportCreate(BaseModel):
    """Transport creation model"""
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    transport_type: TransportType
    category: TransportCategory
    operator_name: Optional[str] = None
    operator_contact: Optional[str] = None
    operator_website: Optional[HttpUrl] = None


class TransportUpdate(BaseModel):
    """Transport update model"""
    name: Optional[MultilingualContent] = None
    description: Optional[MultilingualContent] = None
    short_description: Optional[MultilingualContent] = None
    transport_type: Optional[TransportType] = None
    category: Optional[TransportCategory] = None
    operator_name: Optional[str] = None
    operator_contact: Optional[str] = None
    operator_website: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class TransportResponse(BaseModel):
    """Transport response model"""
    id: str
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    transport_type: TransportType
    category: TransportCategory
    service_levels: List[ServiceLevel]
    operator_name: Optional[str] = None
    operator_contact: Optional[str] = None
    operator_website: Optional[HttpUrl] = None
    routes: List[Route]
    schedules: List[Schedule]
    pricing_options: List[PricingOption]
    amenities: List[str]
    accessibility_features: List[str]
    average_rating: float
    total_reviews: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime


class TransportSearchRequest(BaseModel):
    """Transport search request model"""
    origin: Optional[str] = None
    destination: Optional[str] = None
    transport_type: Optional[TransportType] = None
    category: Optional[TransportCategory] = None
    service_level: Optional[ServiceLevel] = None
    departure_date: Optional[datetime] = None
    max_price: Optional[float] = None
    amenities: Optional[List[str]] = None
