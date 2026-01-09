"""
Hotel model for Sri Lanka Tourism
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

from backend.app.models.attraction import Location, MultilingualContent, Review, AttractionImage


class HotelCategory(str, Enum):
    """Hotel categories"""
    LUXURY = "luxury"
    BOUTIQUE = "boutique"
    BUSINESS = "business"
    RESORT = "resort"
    BUDGET = "budget"
    HOSTEL = "hostel"
    GUESTHOUSE = "guesthouse"
    VILLA = "villa"
    APARTMENT = "apartment"
    ECO_LODGE = "eco_lodge"


class RoomType(str, Enum):
    """Room types"""
    SINGLE = "single"
    DOUBLE = "double"
    TWIN = "twin"
    TRIPLE = "triple"
    FAMILY = "family"
    SUITE = "suite"
    DELUXE = "deluxe"
    PRESIDENTIAL = "presidential"
    DORMITORY = "dormitory"


class StarRating(str, Enum):
    """Star ratings"""
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    UNRATED = "unrated"


class Room(BaseModel):
    """Room model"""
    room_type: RoomType
    name: MultilingualContent
    description: Optional[MultilingualContent] = None
    max_occupancy: int
    bed_type: Optional[str] = None  # king, queen, twin, bunk
    room_size: Optional[float] = None  # in square meters
    price_per_night: float
    currency: str = "LKR"
    amenities: List[str] = Field(default_factory=list)
    images: List[AttractionImage] = Field(default_factory=list)
    is_available: bool = True
    total_rooms: int = 1


class Amenity(str, Enum):
    """Hotel amenities"""
    WIFI = "wifi"
    PARKING = "parking"
    POOL = "pool"
    SPA = "spa"
    GYM = "gym"
    RESTAURANT = "restaurant"
    BAR = "bar"
    ROOM_SERVICE = "room_service"
    CONCIERGE = "concierge"
    LAUNDRY = "laundry"
    BUSINESS_CENTER = "business_center"
    CONFERENCE_ROOMS = "conference_rooms"
    AIRPORT_SHUTTLE = "airport_shuttle"
    PET_FRIENDLY = "pet_friendly"
    BEACH_ACCESS = "beach_access"
    KIDS_CLUB = "kids_club"
    TENNIS_COURT = "tennis_court"
    GOLF_COURSE = "golf_course"


class Hotel(Document):
    """Hotel document model"""
    
    # Basic Information
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    
    # Classification
    category: HotelCategory
    star_rating: StarRating = StarRating.UNRATED
    
    # Location
    location: Location
    
    # Contact Information
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    
    # Media
    images: List[AttractionImage] = Field(default_factory=list)
    virtual_tour_url: Optional[HttpUrl] = None
    
    # Rooms and Pricing
    rooms: List[Room] = Field(default_factory=list)
    total_rooms: int = 0
    check_in_time: Optional[str] = "14:00"
    check_out_time: Optional[str] = "12:00"
    
    # Amenities and Services
    amenities: List[Amenity] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    languages_spoken: List[str] = Field(default_factory=list)
    
    # Policies
    cancellation_policy: Optional[MultilingualContent] = None
    pet_policy: Optional[MultilingualContent] = None
    child_policy: Optional[MultilingualContent] = None
    smoking_policy: Optional[MultilingualContent] = None
    
    # Booking Information
    accepts_online_booking: bool = False
    booking_url: Optional[HttpUrl] = None
    booking_phone: Optional[str] = None
    booking_email: Optional[str] = None
    
    # Reviews and Ratings
    reviews: List[Review] = Field(default_factory=list)
    average_rating: float = 0.0
    total_reviews: int = 0
    cleanliness_rating: float = 0.0
    service_rating: float = 0.0
    location_rating: float = 0.0
    value_rating: float = 0.0
    
    # Certifications and Awards
    certifications: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    
    # Nearby Attractions
    nearby_attractions: List[str] = Field(default_factory=list)  # attraction IDs
    distance_to_airport: Optional[float] = None  # in kilometers
    distance_to_city_center: Optional[float] = None  # in kilometers
    
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
    
    @field_validator('website', mode='before')
    @classmethod
    def validate_website(cls, v):
        """Handle website URL that might be in dict format from database"""
        if v is None:
            return None
        if isinstance(v, dict):
            # Handle dict format like {'_url': 'http://...'}
            return v.get('_url') or v.get('url')
        return v
    
    @field_validator('booking_url', 'virtual_tour_url', mode='before')
    @classmethod
    def validate_urls(cls, v):
        """Handle URLs that might be in dict format from database"""
        if v is None:
            return None
        if isinstance(v, dict):
            return v.get('_url') or v.get('url')
        return v
    
    class Settings:
        name = "hotels"
        indexes = [
            "name.en",
            "category",
            "star_rating",
            "location.city",
            "location.province",
            [("location.coordinates", "2dsphere")],
            "is_active",
            "is_featured",
            "popularity_score",
            "average_rating"
        ]
    
    def add_review(self, user_id: str, username: str, rating: float, comment: Optional[str] = None,
                   cleanliness_rating: Optional[float] = None, service_rating: Optional[float] = None,
                   location_rating: Optional[float] = None, value_rating: Optional[float] = None,
                   language: str = "en"):
        """Add a review to the hotel"""
        review = Review(
            user_id=user_id,
            username=username,
            rating=rating,
            comment=comment,
            language=language
        )
        
        # Add additional rating metadata
        if any([cleanliness_rating, service_rating, location_rating, value_rating]):
            review.metadata = {
                "cleanliness_rating": cleanliness_rating,
                "service_rating": service_rating,
                "location_rating": location_rating,
                "value_rating": value_rating
            }
        
        self.reviews.append(review)
        self.update_rating_stats()
    
    def update_rating_stats(self):
        """Update average rating and total reviews"""
        if self.reviews:
            self.total_reviews = len(self.reviews)
            self.average_rating = sum(review.rating for review in self.reviews) / self.total_reviews
            
            # Calculate specific ratings
            cleanliness_ratings = [r.metadata.get("cleanliness_rating") for r in self.reviews if r.metadata and r.metadata.get("cleanliness_rating")]
            service_ratings = [r.metadata.get("service_rating") for r in self.reviews if r.metadata and r.metadata.get("service_rating")]
            location_ratings = [r.metadata.get("location_rating") for r in self.reviews if r.metadata and r.metadata.get("location_rating")]
            value_ratings = [r.metadata.get("value_rating") for r in self.reviews if r.metadata and r.metadata.get("value_rating")]
            
            if cleanliness_ratings:
                self.cleanliness_rating = sum(cleanliness_ratings) / len(cleanliness_ratings)
            if service_ratings:
                self.service_rating = sum(service_ratings) / len(service_ratings)
            if location_ratings:
                self.location_rating = sum(location_ratings) / len(location_ratings)
            if value_ratings:
                self.value_rating = sum(value_ratings) / len(value_ratings)
        else:
            self.total_reviews = 0
            self.average_rating = 0.0
            self.cleanliness_rating = 0.0
            self.service_rating = 0.0
            self.location_rating = 0.0
            self.value_rating = 0.0
    
    def get_price_range(self) -> Dict[str, float]:
        """Get price range for the hotel"""
        if not self.rooms:
            return {"min": 0.0, "max": 0.0}
        
        prices = [room.price_per_night for room in self.rooms if room.is_available]
        if not prices:
            return {"min": 0.0, "max": 0.0}
        
        return {"min": min(prices), "max": max(prices)}


class HotelCreate(BaseModel):
    """Hotel creation model"""
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    category: HotelCategory
    location: Location
    star_rating: StarRating = StarRating.UNRATED
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None


class HotelUpdate(BaseModel):
    """Hotel update model"""
    name: Optional[MultilingualContent] = None
    description: Optional[MultilingualContent] = None
    short_description: Optional[MultilingualContent] = None
    category: Optional[HotelCategory] = None
    star_rating: Optional[StarRating] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class HotelResponse(BaseModel):
    """Hotel response model"""
    id: str
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    category: HotelCategory
    star_rating: StarRating
    location: Location
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    images: List[AttractionImage]
    rooms: List[Room]
    total_rooms: int
    amenities: List[Amenity]
    average_rating: float
    total_reviews: int
    cleanliness_rating: float
    service_rating: float
    location_rating: float
    value_rating: float
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
