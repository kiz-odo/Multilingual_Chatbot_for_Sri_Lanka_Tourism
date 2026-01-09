"""
Recommendation API endpoints
ML-powered personalized recommendations
"""

from fastapi import APIRouter, Query, Path, Depends, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel, Field

from backend.app.services.recommendation_service import RecommendationService
from backend.app.middleware.error_handler import NotFoundException, BadRequestException

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    """Request model for recommendations"""
    user_id: Optional[str] = None
    session_id: str
    resource_type: Optional[str] = Field(None, description="Filter by type: attraction, hotel, restaurant")
    context: Optional[dict] = Field(None, description="Context data: weather, location, time")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of recommendations")
    exclude_ids: Optional[List[str]] = Field(None, description="Resource IDs to exclude")


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    success: bool = True
    recommendations: List[dict]
    total_count: int
    personalization_level: float
    context_applied: bool
    recommendation_types: dict


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations
    
    Returns recommendations based on:
    - User preferences and history
    - Similar user patterns (collaborative filtering)
    - Content similarity (content-based filtering)
    - Context (weather, location, time)
    - Trending items
    """
    service = RecommendationService()
    
    try:
        result = await service.get_personalized_recommendations(
            user_id=request.user_id,
            session_id=request.session_id,
            resource_type=request.resource_type,
            context=request.context,
            limit=request.limit
        )
        
        return RecommendationResponse(**result)
    
    except Exception as e:
        raise BadRequestException(f"Failed to generate recommendations: {str(e)}")


@router.get("/similar/{resource_type}/{resource_id}")
async def get_similar_items(
    resource_type: str,
    resource_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get similar items based on a specific resource
    
    - **resource_type**: attraction, hotel, restaurant, event
    - **resource_id**: ID of the resource
    - **limit**: Maximum number of similar items
    """
    service = RecommendationService()
    
    # Validate resource type
    valid_types = ["attraction", "hotel", "restaurant", "event"]
    if resource_type not in valid_types:
        raise BadRequestException(
            f"Invalid resource_type. Must be one of: {', '.join(valid_types)}"
        )
    
    try:
        # For now, return trending items of same type
        # In production, would use similarity algorithms
        result = await service._get_trending_items(resource_type, limit)
        
        return {
            "success": True,
            "similar_items": result,
            "total_count": len(result),
            "source_resource": {
                "type": resource_type,
                "id": resource_id
            }
        }
    
    except Exception as e:
        raise BadRequestException(f"Failed to find similar items: {str(e)}")


@router.get("/attractions")
async def get_attraction_recommendations(
    limit: int = Query(10, ge=1, le=50),
    user_id: Optional[str] = None
):
    """
    Get attraction recommendations
    
    Returns personalized attraction recommendations based on:
    - User preferences
    - Similar users' preferences
    - Content similarity
    """
    service = RecommendationService()
    
    try:
        result = await service.get_personalized_recommendations(
            user_id=user_id,
            session_id="attractions",
            resource_type="attraction",
            context=None,
            limit=limit
        )
        
        return {
            "success": True,
            "recommendations": result.get("recommendations", []),
            "total_count": result.get("total_count", 0),
            "resource_type": "attraction"
        }
    
    except Exception as e:
        raise BadRequestException(f"Failed to get attraction recommendations: {str(e)}")


@router.get("/itineraries")
async def get_itinerary_recommendations(
    limit: int = Query(10, ge=1, le=50),
    user_id: Optional[str] = None
):
    """
    Get itinerary recommendations
    
    Returns recommended travel itineraries based on:
    - User preferences
    - Popular itineraries
    - Seasonal recommendations
    """
    service = RecommendationService()
    
    try:
        # In production, this would use itinerary service
        # For now, return mock data
        return {
            "success": True,
            "recommendations": [],
            "total_count": 0,
            "resource_type": "itinerary",
            "message": "Itinerary recommendations coming soon"
        }
    
    except Exception as e:
        raise BadRequestException(f"Failed to get itinerary recommendations: {str(e)}")


@router.get("/based-on-location")
async def get_location_based_recommendations(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius: float = Query(10.0, ge=0.1, le=100, description="Radius in km"),
    resource_type: Optional[str] = Query(None, description="Filter by type: attraction, hotel, restaurant"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get location-based recommendations
    
    Returns recommendations based on:
    - User's current location
    - Nearby attractions/hotels/restaurants
    - Distance and popularity
    """
    service = RecommendationService()
    
    try:
        context = {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius
            }
        }
        
        result = await service.get_personalized_recommendations(
            user_id=None,
            session_id="location-based",
            resource_type=resource_type,
            context=context,
            limit=limit
        )
        
        return {
            "success": True,
            "recommendations": result.get("recommendations", []),
            "total_count": result.get("total_count", 0),
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius
            }
        }
    
    except Exception as e:
        raise BadRequestException(f"Failed to get location-based recommendations: {str(e)}")

