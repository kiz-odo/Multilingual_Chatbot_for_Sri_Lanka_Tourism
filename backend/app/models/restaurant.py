"""
Restaurant model for Sri Lanka Tourism
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from enum import Enum

from backend.app.models.attraction import Location, OpeningHours, MultilingualContent, Review, AttractionImage


class CuisineType(str, Enum):
    """Cuisine types"""
    SRI_LANKAN = "sri_lankan"
    INDIAN = "indian"
    CHINESE = "chinese"
    ITALIAN = "italian"
    JAPANESE = "japanese"
    THAI = "thai"
    CONTINENTAL = "continental"
    SEAFOOD = "seafood"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    HALAL = "halal"
    FAST_FOOD = "fast_food"
    CAFE = "cafe"
    BAKERY = "bakery"
    BAR = "bar"


class RestaurantType(str, Enum):
    """Restaurant types"""
    FINE_DINING = "fine_dining"
    CASUAL_DINING = "casual_dining"
    FAST_FOOD = "fast_food"
    CAFE = "cafe"
    BAR = "bar"
    FOOD_COURT = "food_court"
    STREET_FOOD = "street_food"
    BUFFET = "buffet"
    TAKEAWAY = "takeaway"


class PriceRange(str, Enum):
    """Price ranges"""
    BUDGET = "budget"  # Under 1000 LKR
    MODERATE = "moderate"  # 1000-3000 LKR
    EXPENSIVE = "expensive"  # 3000-5000 LKR
    LUXURY = "luxury"  # Above 5000 LKR


class DietaryOption(str, Enum):
    """Dietary options"""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    HALAL = "halal"
    KOSHER = "kosher"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"


class MenuItem(BaseModel):
    """Menu item model"""
    name: MultilingualContent
    description: Optional[MultilingualContent] = None
    price: float
    currency: str = "LKR"
    category: str  # appetizer, main_course, dessert, beverage
    dietary_options: List[DietaryOption] = Field(default_factory=list)
    spice_level: Optional[str] = None  # mild, medium, hot, very_hot
    image_url: Optional[HttpUrl] = None
    is_available: bool = True
    is_recommended: bool = False


class Restaurant(Document):
    """Restaurant document model"""
    
    # Basic Information
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    
    # Classification
    cuisine_types: List[CuisineType]
    restaurant_type: RestaurantType
    price_range: PriceRange
    
    # Location
    location: Location
    
    # Contact Information
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    
    # Media
    images: List[AttractionImage] = Field(default_factory=list)
    menu_images: List[AttractionImage] = Field(default_factory=list)
    
    # Operational Information
    opening_hours: List[OpeningHours] = Field(default_factory=list)
    accepts_reservations: bool = False
    reservation_phone: Optional[str] = None
    online_booking_url: Optional[HttpUrl] = None
    
    # Menu and Dining
    menu_items: List[MenuItem] = Field(default_factory=list)
    dietary_options: List[DietaryOption] = Field(default_factory=list)
    alcohol_served: bool = False
    smoking_allowed: bool = False
    
    # Capacity and Features
    seating_capacity: Optional[int] = None
    private_dining_available: bool = False
    outdoor_seating: bool = False
    air_conditioning: bool = False
    wifi_available: bool = False
    parking_available: bool = False
    
    # Payment and Services
    payment_methods: List[str] = Field(default_factory=list)  # cash, card, mobile_payment
    delivery_available: bool = False
    takeaway_available: bool = True
    catering_services: bool = False
    
    # Reviews and Ratings
    reviews: List[Review] = Field(default_factory=list)
    average_rating: float = 0.0
    total_reviews: int = 0
    food_rating: float = 0.0
    service_rating: float = 0.0
    ambiance_rating: float = 0.0
    value_rating: float = 0.0
    
    # Certifications and Awards
    certifications: List[str] = Field(default_factory=list)  # halal, organic, etc.
    awards: List[str] = Field(default_factory=list)
    
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
        name = "restaurants"
        indexes = [
            "name.en",
            "cuisine_types",
            "restaurant_type",
            "price_range",
            "location.city",
            "location.province",
            [("location.coordinates", "2dsphere")],
            "is_active",
            "is_featured",
            "popularity_score",
            "average_rating"
        ]
    
    def add_review(self, user_id: str, username: str, rating: float, comment: Optional[str] = None, 
                   food_rating: Optional[float] = None, service_rating: Optional[float] = None,
                   ambiance_rating: Optional[float] = None, value_rating: Optional[float] = None,
                   language: str = "en"):
        """Add a review to the restaurant"""
        review = Review(
            user_id=user_id,
            username=username,
            rating=rating,
            comment=comment,
            language=language
        )
        
        # Add additional rating metadata
        if any([food_rating, service_rating, ambiance_rating, value_rating]):
            review.metadata = {
                "food_rating": food_rating,
                "service_rating": service_rating,
                "ambiance_rating": ambiance_rating,
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
            food_ratings = [r.metadata.get("food_rating") for r in self.reviews if r.metadata and r.metadata.get("food_rating")]
            service_ratings = [r.metadata.get("service_rating") for r in self.reviews if r.metadata and r.metadata.get("service_rating")]
            ambiance_ratings = [r.metadata.get("ambiance_rating") for r in self.reviews if r.metadata and r.metadata.get("ambiance_rating")]
            value_ratings = [r.metadata.get("value_rating") for r in self.reviews if r.metadata and r.metadata.get("value_rating")]
            
            if food_ratings:
                self.food_rating = sum(food_ratings) / len(food_ratings)
            if service_ratings:
                self.service_rating = sum(service_ratings) / len(service_ratings)
            if ambiance_ratings:
                self.ambiance_rating = sum(ambiance_ratings) / len(ambiance_ratings)
            if value_ratings:
                self.value_rating = sum(value_ratings) / len(value_ratings)
        else:
            self.total_reviews = 0
            self.average_rating = 0.0
            self.food_rating = 0.0
            self.service_rating = 0.0
            self.ambiance_rating = 0.0
            self.value_rating = 0.0


class RestaurantCreate(BaseModel):
    """Restaurant creation model"""
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    cuisine_types: List[CuisineType]
    restaurant_type: RestaurantType
    price_range: PriceRange
    location: Location
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None


class RestaurantUpdate(BaseModel):
    """Restaurant update model"""
    name: Optional[MultilingualContent] = None
    description: Optional[MultilingualContent] = None
    short_description: Optional[MultilingualContent] = None
    cuisine_types: Optional[List[CuisineType]] = None
    restaurant_type: Optional[RestaurantType] = None
    price_range: Optional[PriceRange] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class RestaurantResponse(BaseModel):
    """Restaurant response model"""
    id: str
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    cuisine_types: List[CuisineType]
    restaurant_type: RestaurantType
    price_range: PriceRange
    location: Location
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    images: List[AttractionImage]
    opening_hours: List[OpeningHours]
    dietary_options: List[DietaryOption]
    average_rating: float
    total_reviews: int
    food_rating: float
    service_rating: float
    ambiance_rating: float
    value_rating: float
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
