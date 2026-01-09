"""
Recommendation models for Sri Lanka Tourism Chatbot
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    """Recommendation types"""
    PERSONALIZED = "personalized"  # Based on user history
    COLLABORATIVE = "collaborative"  # Based on similar users
    CONTENT_BASED = "content_based"  # Based on item similarity
    CONTEXTUAL = "contextual"  # Based on context (weather, time, location)
    TRENDING = "trending"  # Popular items
    SEASONAL = "seasonal"  # Season-specific
    SIMILAR = "similar"  # Similar to a specific item


class UserPreferenceProfile(Document):
    """User preference profile for recommendations"""
    
    # User Reference
    user_id: Indexed(str, unique=True)
    
    # Category Preferences (0-1 scores)
    category_preferences: Dict[str, float] = Field(default_factory=dict)
    
    # Feature Preferences
    preferred_price_range: Optional[str] = None
    preferred_locations: List[str] = Field(default_factory=list)
    preferred_cuisines: List[str] = Field(default_factory=list)
    preferred_activities: List[str] = Field(default_factory=list)
    
    # Behavioral Patterns
    viewing_history: List[str] = Field(default_factory=list)  # Resource IDs
    search_history: List[Dict[str, Any]] = Field(default_factory=list)
    favorite_items: List[str] = Field(default_factory=list)
    
    # Time-based Patterns
    active_hours: List[int] = Field(default_factory=list)  # Hours of day (0-23)
    active_days: List[int] = Field(default_factory=list)  # Days of week (0-6)
    
    # Travel Style
    travel_style_scores: Dict[str, float] = Field(default_factory=dict)  # adventure, cultural, relaxation, etc.
    
    # Social Preferences
    group_size_preference: int = 1
    traveling_with: List[str] = Field(default_factory=list)  # family, friends, solo, etc.
    
    # Seasonal Preferences
    preferred_seasons: List[str] = Field(default_factory=list)
    
    # Implicit Preferences (learned from behavior)
    implicit_likes: Dict[str, float] = Field(default_factory=dict)
    implicit_dislikes: Dict[str, float] = Field(default_factory=dict)
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0  # How confident we are about preferences
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "user_preference_profiles"
        indexes = [
            "user_id",
            "last_updated"
        ]


class RecommendationEngine(Document):
    """Recommendation engine model configuration"""
    
    model_config = ConfigDict(protected_namespaces=())
    
    # Engine Configuration
    engine_id: Indexed(str, unique=True)
    engine_name: str
    recommendation_type: RecommendationType
    
    # Model Information
    model_version: str
    model_type: str  # collaborative_filtering, content_based, hybrid, neural_network
    model_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance Metrics
    accuracy_score: float = 0.0
    precision_score: float = 0.0
    recall_score: float = 0.0
    f1_score: float = 0.0
    ndcg_score: float = 0.0  # Normalized Discounted Cumulative Gain
    
    # Training Information
    training_data_size: int = 0
    last_trained_at: Optional[datetime] = None
    training_duration_seconds: Optional[float] = None
    
    # Feature Weights
    feature_weights: Dict[str, float] = Field(default_factory=dict)
    
    # Status
    is_active: bool = True
    is_default: bool = False
    
    # A/B Testing
    ab_test_group: Optional[str] = None
    conversion_rate: float = 0.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "recommendation_engines"
        indexes = [
            "engine_id",
            "recommendation_type",
            "is_active",
            "is_default"
        ]


class RecommendationResult(Document):
    """Individual recommendation result"""
    
    # User and Context
    user_id: Optional[str] = None  # Can be anonymous
    session_id: str
    
    # Recommendation Details
    recommendation_type: RecommendationType
    engine_id: str
    
    # Recommended Item
    resource_type: str  # attraction, hotel, restaurant, event, transport
    resource_id: str
    
    # Scoring
    relevance_score: float  # 0-1
    confidence_score: float  # 0-1
    ranking_position: int
    
    # Context
    context: Dict[str, Any] = Field(default_factory=dict)  # weather, location, time, etc.
    
    # User Interaction
    was_clicked: bool = False
    was_viewed: bool = False
    was_bookmarked: bool = False
    was_shared: bool = False
    interaction_time: Optional[datetime] = None
    
    # Feedback
    user_rating: Optional[float] = None  # Explicit feedback
    implicit_feedback_score: Optional[float] = None  # Derived from behavior
    
    # Explanation (for transparency)
    explanation_factors: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "recommendation_results"
        indexes = [
            "user_id",
            "session_id",
            "resource_type",
            "resource_id",
            "recommendation_type",
            "engine_id",
            "created_at",
            "relevance_score"
        ]


class ItemSimilarity(Document):
    """Pre-computed item similarity scores"""
    
    # Source Item
    source_resource_type: str
    source_resource_id: Indexed(str)
    
    # Similar Items (sorted by similarity)
    similar_items: List[Dict[str, Any]] = Field(default_factory=list)  # [{resource_id, resource_type, similarity_score}]
    
    # Similarity Method
    similarity_method: str  # cosine, jaccard, euclidean, neural_embedding
    
    # Feature Vectors (for debugging/analysis)
    feature_vector: Optional[List[float]] = None
    
    # Metadata
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    computation_duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "item_similarities"
        indexes = [
            "source_resource_id",
            [("source_resource_type", 1), ("source_resource_id", 1)],
            "computed_at"
        ]


class CollaborativeFilter(Document):
    """User-user and item-item collaborative filtering data"""
    
    # Filter Type
    filter_type: str  # user_based, item_based
    
    # User-Item Interaction Matrix (sparse representation)
    user_item_interactions: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Computed Similarities
    similarity_matrix_id: Optional[str] = None  # Reference to stored matrix
    
    # Model Parameters
    n_neighbors: int = 50
    min_support: int = 5  # Minimum interactions required
    
    # Performance Metrics
    coverage: float = 0.0  # Percentage of items that can be recommended
    diversity: float = 0.0  # How diverse are recommendations
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    total_users: int = 0
    total_items: int = 0
    total_interactions: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "collaborative_filters"
        indexes = [
            "filter_type",
            "last_updated"
        ]


class ContextualFactor(Document):
    """Contextual factors affecting recommendations"""
    
    # Context Type
    context_type: str  # weather, time, location, event, season
    context_value: str
    
    # Impact on Categories
    category_boosts: Dict[str, float] = Field(default_factory=dict)  # Positive or negative boosts
    
    # Impact on Specific Items
    item_boosts: Dict[str, float] = Field(default_factory=dict)
    
    # Rules
    recommendation_rules: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Effectiveness
    effectiveness_score: float = 0.0
    
    # Validity
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "contextual_factors"
        indexes = [
            "context_type",
            "context_value",
            "is_active"
        ]


# Response Models
class RecommendationRequest(BaseModel):
    """Recommendation request model"""
    user_id: Optional[str] = None
    session_id: str
    resource_type: Optional[str] = None  # Filter by type
    limit: int = 10
    context: Optional[Dict[str, Any]] = None
    exclude_ids: Optional[List[str]] = None  # Already seen items
    recommendation_type: Optional[RecommendationType] = None


class RecommendationResponse(BaseModel):
    """Recommendation response model"""
    recommendations: List[Dict[str, Any]]
    total_count: int
    recommendation_type: RecommendationType
    engine_id: str
    context_applied: bool
    personalization_level: float  # How personalized (0-1)


class SimilarItemsRequest(BaseModel):
    """Similar items request"""
    resource_type: str
    resource_id: str
    limit: int = 10


class SimilarItemsResponse(BaseModel):
    """Similar items response"""
    similar_items: List[Dict[str, Any]]
    similarity_method: str

