"""
Challenges API endpoints
Location-based challenges for tourism engagement
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId

from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user, get_optional_user
from fastapi import Request
from backend.app.middleware.error_handler import NotFoundException, BadRequestException

router = APIRouter(prefix="/challenges", tags=["Challenges"])


# Request/Response Models
class ChallengeLocation(BaseModel):
    """Challenge location"""
    name: str
    coordinates: List[float] = Field(..., min_items=2, max_items=2)  # [longitude, latitude]
    address: Optional[str] = None


class Challenge(BaseModel):
    """Challenge model"""
    id: Optional[str] = None
    title: str
    description: str
    location: ChallengeLocation
    category: str
    difficulty: str = "easy"  # easy, medium, hard
    points: int = 10
    requirements: List[str] = Field(default_factory=list)
    reward: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class ChallengeCheckIn(BaseModel):
    """Challenge check-in request"""
    challenge_id: str
    coordinates: List[float] = Field(..., min_items=2, max_items=2)
    photo_url: Optional[str] = None
    notes: Optional[str] = None


class ChallengeProgress(BaseModel):
    """User challenge progress"""
    challenge_id: str
    challenge_title: str
    completed: bool
    check_ins: int
    total_required: int
    completed_at: Optional[datetime] = None
    points_earned: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    user_id: str
    username: str
    total_points: int
    challenges_completed: int
    rank: int


# Mock data - In production, this would be in a database model
CHALLENGES_DB = [
    {
        "id": "1",
        "title": "Visit Sigiriya Rock Fortress",
        "description": "Climb the ancient rock fortress and take a photo at the top",
        "location": {
            "name": "Sigiriya Rock Fortress",
            "coordinates": [80.7596, 7.9569],
            "address": "Sigiriya, Central Province"
        },
        "category": "historical",
        "difficulty": "medium",
        "points": 50,
        "requirements": ["Check in at location", "Take photo"],
        "reward": "Historical Explorer Badge"
    },
    {
        "id": "2",
        "title": "Taste Traditional Rice and Curry",
        "description": "Try authentic Sri Lankan rice and curry at a local restaurant",
        "location": {
            "name": "Any Local Restaurant",
            "coordinates": [79.8612, 6.9271],
            "address": "Colombo"
        },
        "category": "culinary",
        "difficulty": "easy",
        "points": 25,
        "requirements": ["Check in at restaurant", "Order rice and curry"],
        "reward": "Foodie Badge"
    }
]


@router.get("/", response_model=List[Challenge])
async def list_challenges(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    List location-based challenges
    
    - Returns all active challenges
    - Can filter by category and difficulty
    """
    challenges = CHALLENGES_DB.copy()
    
    if category:
        challenges = [c for c in challenges if c["category"] == category]
    
    if difficulty:
        challenges = [c for c in challenges if c["difficulty"] == difficulty]
    
    # Paginate
    challenges = challenges[skip:skip + limit]
    
    return [Challenge(**c) for c in challenges]


@router.get("/my-progress", response_model=List[ChallengeProgress])
async def get_my_progress(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's challenge progress
    
    - Returns all challenges with user's progress
    """
    # In production, fetch from database
    # For now, return mock data
    
    progress = [
        ChallengeProgress(
            challenge_id="1",
            challenge_title="Visit Sigiriya Rock Fortress",
            completed=True,
            check_ins=1,
            total_required=1,
            completed_at=datetime.utcnow(),
            points_earned=50
        ),
        ChallengeProgress(
            challenge_id="2",
            challenge_title="Taste Traditional Rice and Curry",
            completed=False,
            check_ins=0,
            total_required=1,
            completed_at=None,
            points_earned=0
        )
    ]
    
    return progress


@router.get("/{challenge_id}", response_model=Challenge)
async def get_challenge(challenge_id: str):
    """
    Get challenge details
    
    - Returns full challenge information
    """
    challenge = next((c for c in CHALLENGES_DB if c["id"] == challenge_id), None)
    
    if not challenge:
        raise NotFoundException(f"Challenge {challenge_id} not found")
    
    return Challenge(**challenge)


@router.post("/{challenge_id}/check-in", status_code=status.HTTP_200_OK)
async def check_in_challenge(
    challenge_id: str,
    check_in: ChallengeCheckIn,
    current_user: User = Depends(get_current_active_user)
):
    """
    Check in at challenge location
    
    - Verifies user is at challenge location
    - Records check-in
    - Awards points if challenge completed
    """
    challenge = next((c for c in CHALLENGES_DB if c["id"] == challenge_id), None)
    
    if not challenge:
        raise NotFoundException(f"Challenge {challenge_id} not found")
    
    # Verify location (simplified - in production, use geospatial queries)
    challenge_coords = challenge["location"]["coordinates"]
    user_coords = check_in.coordinates
    
    # Calculate distance (simplified - use haversine formula in production)
    distance = ((challenge_coords[0] - user_coords[0])**2 + 
                (challenge_coords[1] - user_coords[1])**2)**0.5
    
    # Allow check-in within ~1km radius (simplified)
    if distance > 0.01:  # Roughly 1km
        raise BadRequestException("You are not at the challenge location")
    
    # Record check-in (in production, save to database)
    # For now, return success
    
    return {
        "message": "Check-in successful",
        "challenge_id": challenge_id,
        "points_earned": challenge["points"],
        "completed": True  # Simplified - check completion logic in production
    }


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get challenge leaderboard
    
    - Returns top users by points
    """
    # In production, fetch from database with aggregation
    # For now, return mock data
    
    leaderboard = [
        LeaderboardEntry(
            user_id="1",
            username="traveler123",
            total_points=500,
            challenges_completed=10,
            rank=1
        ),
        LeaderboardEntry(
            user_id="2",
            username="explorer456",
            total_points=350,
            challenges_completed=7,
            rank=2
        )
    ]
    
    return leaderboard[:limit]

