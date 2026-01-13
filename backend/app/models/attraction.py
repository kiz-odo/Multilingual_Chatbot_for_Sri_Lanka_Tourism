"""
Attraction model for Sri Lanka Tourism
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from enum import Enum


class AttractionCategory(str, Enum):
    """Attraction categories"""
    HISTORICAL = "historical"
    WILDLIFE = "wildlife"
    BEACH = "beach"
    MOUNTAIN = "mountain"
    WATERFALL = "waterfall"
    TEMPLE = "temple"
    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    NATURE = "nature"
    MUSEUM = "museum"
    PARK = "park"
    CITY = "city"


class AccessibilityFeature(str, Enum):
    """Accessibility features"""
    WHEELCHAIR_ACCESSIBLE = "wheelchair_accessible"
    HEARING_LOOP = "hearing_loop"
    BRAILLE_SIGNS = "braille_signs"
    AUDIO_GUIDES = "audio_guides"
    SIGN_LANGUAGE = "sign_language"
    ACCESSIBLE_PARKING = "accessible_parking"
    ACCESSIBLE_RESTROOMS = "accessible_restrooms"


class Location(BaseModel):
    """Location model"""
    address: str
    city: str
    province: str
    postal_code: Optional[str] = None
    coordinates: List[float] = Field(..., min_items=2, max_items=2)  # [longitude, latitude]
    google_place_id: Optional[str] = None


class OpeningHours(BaseModel):
    """Opening hours model"""
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    open_time: Optional[str] = None  # Format: "HH:MM"
    close_time: Optional[str] = None  # Format: "HH:MM"
    is_closed: bool = False
    notes: Optional[str] = None


class PricingTier(BaseModel):
    """Pricing tier model"""
    category: str  # adult, child, senior, student, foreign, local
    price: float
    currency: str = "LKR"
    description: Optional[str] = None


class MultilingualContent(BaseModel):
    """Multilingual content model"""
    en: str  # English (required)
    si: Optional[str] = None  # Sinhala
    ta: Optional[str] = None  # Tamil
    de: Optional[str] = None  # German
    fr: Optional[str] = None  # French
    zh: Optional[str] = None  # Chinese
    ja: Optional[str] = None  # Japanese


class AttractionImage(BaseModel):
    """Attraction image model"""
    url: str  # Changed from HttpUrl to str for better frontend compatibility
    alt_text: MultilingualContent
    caption: Optional[MultilingualContent] = None
    is_primary: bool = False
    order: int = 0
    
    class Config:
        json_encoders = {
            str: lambda v: str(v) if v else ""
        }


class Review(BaseModel):
    """Review model"""
    user_id: str
    username: str
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    language: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    helpful_votes: int = 0


class Attraction(Document):
    """Attraction document model"""
    
    # Basic Information
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    
    # Classification
    category: AttractionCategory
    subcategories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Location
    location: Location
    
    # Contact Information
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    
    # Media
    images: List[AttractionImage] = Field(default_factory=list)
    virtual_tour_url: Optional[HttpUrl] = None
    video_urls: List[HttpUrl] = Field(default_factory=list)
    
    # Operational Information
    opening_hours: List[OpeningHours] = Field(default_factory=list)
    pricing: List[PricingTier] = Field(default_factory=list)
    is_free: bool = False
    requires_booking: bool = False
    booking_url: Optional[HttpUrl] = None
    
    # Visitor Information
    estimated_visit_duration: Optional[str] = None  # e.g., "2-3 hours"
    best_time_to_visit: Optional[str] = None
    difficulty_level: Optional[str] = None  # easy, moderate, difficult
    age_restrictions: Optional[str] = None
    
    # Features and Amenities
    amenities: List[str] = Field(default_factory=list)
    accessibility_features: List[AccessibilityFeature] = Field(default_factory=list)
    parking_available: bool = False
    guided_tours_available: bool = False
    languages_supported: List[str] = Field(default_factory=list)
    
    # Transportation
    how_to_get_there: MultilingualContent
    nearest_transport_hubs: List[str] = Field(default_factory=list)
    
    # Reviews and Ratings
    reviews: List[Review] = Field(default_factory=list)
    average_rating: float = 0.0
    total_reviews: int = 0
    
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
        name = "attractions"
        indexes = [
            "name.en",
            "category",
            "location.city",
            "location.province",
            [("location.coordinates", "2dsphere")],
            "is_active",
            "is_featured",
            "popularity_score",
            "average_rating"
        ]
    
    def add_review(self, user_id: str, username: str, rating: float, comment: Optional[str] = None, language: str = "en"):
        """Add a review to the attraction"""
        review = Review(
            user_id=user_id,
            username=username,
            rating=rating,
            comment=comment,
            language=language
        )
        self.reviews.append(review)
        self.update_rating_stats()
    
    def update_rating_stats(self):
        """Update average rating and total reviews"""
        if self.reviews:
            self.total_reviews = len(self.reviews)
            self.average_rating = sum(review.rating for review in self.reviews) / self.total_reviews
        else:
            self.total_reviews = 0
            self.average_rating = 0.0


class AttractionCreate(BaseModel):
    """Attraction creation model"""
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    category: AttractionCategory
    location: Location
    subcategories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    is_free: bool = False
    requires_booking: bool = False


class AttractionUpdate(BaseModel):
    """Attraction update model"""
    name: Optional[MultilingualContent] = None
    description: Optional[MultilingualContent] = None
    short_description: Optional[MultilingualContent] = None
    category: Optional[AttractionCategory] = None
    subcategories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class AttractionResponse(BaseModel):
    """Attraction response model"""
    id: str
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    category: AttractionCategory
    subcategories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    location: Location
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None  # Changed from HttpUrl to allow None
    images: List[AttractionImage] = Field(default_factory=list)
    opening_hours: List[OpeningHours] = Field(default_factory=list)
    pricing: List[PricingTier] = Field(default_factory=list)
    is_free: bool = False
    requires_booking: bool = False
    amenities: List[str] = Field(default_factory=list)
    accessibility_features: List[AccessibilityFeature] = Field(default_factory=list)
    average_rating: float = 0.0
    total_reviews: int = 0
    is_active: bool = True
    is_featured: bool = False
    slug: Optional[str] = None
    popularity_score: float = 0.0
    created_at: datetime
    updated_at: datetime
