"""
Challenge Model for Location-Based Tourism Challenges
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ChallengeCategory(str, Enum):
    """Challenge categories"""
    HISTORICAL = "historical"
    CULINARY = "culinary"
    NATURE = "nature"
    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    PHOTOGRAPHY = "photography"
    SHOPPING = "shopping"
    RELAXATION = "relaxation"


class ChallengeDifficulty(str, Enum):
    """Challenge difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ChallengeLocation(BaseModel):
    """Challenge location"""
    name: str
    coordinates: List[float] = Field(..., min_items=2, max_items=2)  # [longitude, latitude]
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None


class ChallengeCheckIn(Document):
    """User check-in for a challenge"""
    
    challenge_id: Indexed(str)
    user_id: Indexed(str)
    coordinates: List[float] = Field(..., min_items=2, max_items=2)
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    verified: bool = False
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "challenge_checkins"
        indexes = [
            "challenge_id",
            "user_id",
            "created_at",
            [("challenge_id", 1), ("user_id", 1)],
            [("user_id", 1), ("created_at", -1)]
        ]


class Challenge(Document):
    """Location-based challenge document model"""
    
    # Basic Information
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    short_description: Optional[str] = Field(None, max_length=500)
    
    # Location
    location: ChallengeLocation
    
    # Classification
    category: ChallengeCategory
    difficulty: ChallengeDifficulty = ChallengeDifficulty.EASY
    tags: List[str] = Field(default_factory=list)
    
    # Requirements
    requirements: List[str] = Field(default_factory=list)  # What user needs to do
    check_ins_required: int = 1  # Number of check-ins needed to complete
    
    # Rewards
    points: int = 10
    reward: Optional[str] = None  # Badge name, certificate, etc.
    reward_description: Optional[str] = None
    
    # Status
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Statistics
    total_participants: int = 0
    total_completions: int = 0
    popularity_score: float = 0.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # Admin/Moderator user ID
    
    class Settings:
        name = "challenges"
        indexes = [
            "category",
            "difficulty",
            "is_active",
            "created_at",
            "popularity_score",
            [("category", 1), ("is_active", 1), ("popularity_score", -1)],
            [("location.coordinates", "2dsphere")]  # Geospatial index
        ]
    
    def to_dict(self):
        """Convert challenge to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "short_description": self.short_description,
            "location": self.location.dict(),
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "tags": self.tags,
            "requirements": self.requirements,
            "check_ins_required": self.check_ins_required,
            "points": self.points,
            "reward": self.reward,
            "reward_description": self.reward_description,
            "is_active": self.is_active,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_participants": self.total_participants,
            "total_completions": self.total_completions,
            "popularity_score": self.popularity_score,
            "created_at": self.created_at
        }


class UserChallengeProgress(Document):
    """User's progress on challenges"""
    
    user_id: Indexed(str)
    challenge_id: Indexed(str)
    check_ins: List[str] = Field(default_factory=list)  # Check-in IDs
    check_in_count: int = 0
    completed: bool = False
    completed_at: Optional[datetime] = None
    points_earned: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_challenge_progress"
        indexes = [
            "user_id",
            "challenge_id",
            "completed",
            [("user_id", 1), ("completed", 1)],
            [("challenge_id", 1), ("completed", 1)],
            [("user_id", 1), ("challenge_id", 1)]  # Unique constraint
        ]




