"""
Attractions API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from backend.app.models.attraction import (
    Attraction, AttractionResponse, AttractionCategory,
    AttractionCreate, AttractionUpdate
)
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user
from backend.app.services.attraction_service import AttractionService

router = APIRouter()


@router.get("/", response_model=List[AttractionResponse])
async def get_attractions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[AttractionCategory] = None,
    city: Optional[str] = None,
    province: Optional[str] = None,
    featured_only: bool = False,
    language: str = "en"
):
    """Get list of attractions with filters"""
    attraction_service = AttractionService()
    
    attractions = await attraction_service.get_attractions(
        skip=skip,
        limit=limit,
        category=category,
        city=city,
        province=province,
        featured_only=featured_only
    )
    
    result = []
    for attraction in attractions:
        data = attraction.dict()
        data['id'] = str(attraction.id)
        result.append(AttractionResponse(**data))
    return result


@router.get("/search", response_model=List[AttractionResponse])
async def search_attractions(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[AttractionCategory] = None,
    location: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    language: str = "en"
):
    """Search attractions by various criteria"""
    attraction_service = AttractionService()
    
    attractions = await attraction_service.search_attractions(
        query=q,
        category=category,
        location=location,
        tags=tags,
        limit=limit
    )
    
    return [AttractionResponse(**attraction.dict()) for attraction in attractions]


@router.get("/categories")
async def get_attraction_categories():
    """Get all attraction categories"""
    categories = [
        {
            "value": category.value,
            "label": category.value.replace("_", " ").title(),
            "description": get_category_description(category)
        }
        for category in AttractionCategory
    ]
    
    return {"categories": categories}


@router.get("/featured", response_model=List[AttractionResponse])
async def get_featured_attractions(
    limit: int = Query(6, ge=1, le=20),
    language: str = "en"
):
    """Get featured attractions"""
    attraction_service = AttractionService()
    
    attractions = await attraction_service.get_featured_attractions(limit=limit)
    
    return [AttractionResponse(**attraction.dict()) for attraction in attractions]


@router.get("/popular", response_model=List[AttractionResponse])
async def get_popular_attractions(
    limit: int = Query(10, ge=1, le=20),
    language: str = "en"
):
    """Get popular attractions by popularity score"""
    attraction_service = AttractionService()
    
    attractions = await attraction_service.get_popular_attractions(limit=limit)
    
    return [AttractionResponse(**attraction.dict()) for attraction in attractions]


@router.get("/nearby", response_model=List[AttractionResponse])
async def get_nearby_attractions(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(50, ge=1, le=500),
    limit: int = Query(10, ge=1, le=50),
    language: str = "en"
):
    """Get attractions near a location"""
    attraction_service = AttractionService()
    
    attractions = await attraction_service.get_nearby_attractions(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        limit=limit
    )
    
    return [AttractionResponse(**attraction.dict()) for attraction in attractions]


@router.get("/{attraction_id}", response_model=AttractionResponse)
async def get_attraction_by_id(
    attraction_id: str,
    language: str = "en"
):
    """Get attraction by ID"""
    attraction_service = AttractionService()
    
    attraction = await attraction_service.get_attraction_by_id(attraction_id)
    if not attraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attraction not found"
        )
    
    return AttractionResponse(**attraction.dict())


@router.get("/{attraction_id}/reviews")
async def get_attraction_reviews(
    attraction_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """Get reviews for an attraction"""
    attraction_service = AttractionService()
    
    attraction = await attraction_service.get_attraction_by_id(attraction_id)
    if not attraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attraction not found"
        )
    
    # Get paginated reviews
    reviews = attraction.reviews[skip:skip + limit]
    
    return {
        "reviews": reviews,
        "total_reviews": len(attraction.reviews),
        "average_rating": attraction.average_rating
    }


@router.post("/{attraction_id}/reviews")
async def add_attraction_review(
    attraction_id: str,
    rating: float = Query(..., ge=1, le=5),
    comment: Optional[str] = None,
    language: str = "en",
    current_user: User = Depends(get_current_active_user)
):
    """Add a review for an attraction"""
    attraction_service = AttractionService()
    
    success = await attraction_service.add_review(
        attraction_id=attraction_id,
        user_id=str(current_user.id),
        username=current_user.username,
        rating=rating,
        comment=comment,
        language=language
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attraction not found"
        )
    
    return {"message": "Review added successfully"}


@router.post("/{attraction_id}/favorite", status_code=status.HTTP_200_OK)
async def add_to_favorites(
    attraction_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Add attraction to favorites (authenticated)
    
    - Adds attraction to user's favorite list
    """
    attraction_service = AttractionService()
    
    attraction = await attraction_service.get_attraction_by_id(attraction_id)
    if not attraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attraction not found"
        )
    
    # Add to user's favorites
    if attraction_id not in current_user.stats.favorite_attractions:
        current_user.stats.favorite_attractions.append(attraction_id)
        await current_user.save()
    
    return {"message": "Attraction added to favorites", "attraction_id": attraction_id}


@router.delete("/{attraction_id}/favorite", status_code=status.HTTP_200_OK)
async def remove_from_favorites(
    attraction_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove attraction from favorites
    
    - Removes attraction from user's favorite list
    """
    # Remove from user's favorites
    if attraction_id in current_user.stats.favorite_attractions:
        current_user.stats.favorite_attractions.remove(attraction_id)
        await current_user.save()
    
    return {"message": "Attraction removed from favorites", "attraction_id": attraction_id}


def get_category_description(category: AttractionCategory) -> str:
    """Get description for attraction category"""
    descriptions = {
        AttractionCategory.HISTORICAL: "Ancient sites, archaeological ruins, and historical monuments",
        AttractionCategory.WILDLIFE: "National parks, wildlife sanctuaries, and nature reserves",
        AttractionCategory.BEACH: "Beautiful beaches, coastal areas, and water activities",
        AttractionCategory.MOUNTAIN: "Hill stations, mountain peaks, and highland attractions",
        AttractionCategory.WATERFALL: "Scenic waterfalls and natural water features",
        AttractionCategory.TEMPLE: "Buddhist temples, Hindu kovils, and religious sites",
        AttractionCategory.CULTURAL: "Cultural centers, traditional villages, and heritage sites",
        AttractionCategory.ADVENTURE: "Adventure sports, trekking, and outdoor activities",
        AttractionCategory.NATURE: "Natural landscapes, gardens, and eco-tourism sites",
        AttractionCategory.MUSEUM: "Museums, galleries, and educational centers",
        AttractionCategory.PARK: "Public parks, recreational areas, and green spaces",
        AttractionCategory.CITY: "Urban attractions, city centers, and metropolitan areas"
    }
    return descriptions.get(category, "Tourist attraction")
