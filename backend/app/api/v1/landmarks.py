"""
Landmark Recognition API endpoints
Computer vision for identifying Sri Lankan landmarks
"""

from fastapi import APIRouter, File, UploadFile, Query, HTTPException, status
from typing import Optional
from pydantic import BaseModel

from backend.app.services.landmark_recognition_service import LandmarkRecognitionService
from backend.app.middleware.error_handler import BadRequestException

router = APIRouter(prefix="/landmarks", tags=["landmarks"])


class LandmarkRecognitionResponse(BaseModel):
    """Response model for landmark recognition"""
    success: bool
    landmark: Optional[dict] = None
    confidence: Optional[float] = None
    alternative_matches: list = []
    suggestions: list = []
    message: Optional[str] = None


@router.post("/recognize", response_model=LandmarkRecognitionResponse)
async def recognize_landmark(
    file: UploadFile = File(..., description="Image file (JPEG, PNG, GIF)"),
    language: str = Query("en", description="Response language")
):
    """
    Recognize Sri Lankan landmark from image
    
    Upload an image and get:
    - Landmark identification
    - Confidence score
    - Alternative matches
    - Multilingual description
    
    Supported landmarks:
    - Sigiriya Rock Fortress
    - Temple of the Tooth
    - Galle Fort
    - Nine Arch Bridge
    - Adam's Peak
    - Lotus Tower
    - Anuradhapura
    """
    
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/jpg", "image/png", "image/gif"]:
        raise BadRequestException(
            "Invalid file type. Please upload JPEG, PNG, or GIF image."
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    
    if len(content) > max_size:
        raise BadRequestException(
            "File too large. Maximum size is 10MB."
        )
    
    # Initialize service
    service = LandmarkRecognitionService()
    
    try:
        # Recognize landmark
        result = await service.recognize_landmark(content, language)
        
        return LandmarkRecognitionResponse(**result)
    
    except Exception as e:
        raise BadRequestException(f"Failed to recognize landmark: {str(e)}")


@router.get("/nearby")
async def get_nearby_landmarks(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius_km: float = Query(10, ge=1, le=100, description="Search radius in kilometers"),
    language: str = Query("en")
):
    """
    Get landmarks near a geographic location
    
    Returns landmarks within specified radius
    """
    service = LandmarkRecognitionService()
    
    try:
        landmarks = await service.get_landmark_by_location(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        
        return {
            "success": True,
            "landmarks": landmarks,
            "total_count": len(landmarks),
            "search_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "radius_km": radius_km
        }
    
    except Exception as e:
        raise BadRequestException(f"Failed to find nearby landmarks: {str(e)}")


@router.get("/similar/{landmark_id}")
async def get_similar_landmarks(
    landmark_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """
    Get similar landmarks based on category and location
    """
    service = LandmarkRecognitionService()
    
    try:
        similar = await service.search_similar_landmarks(landmark_id, limit)
        
        return {
            "success": True,
            "similar_landmarks": similar,
            "total_count": len(similar),
            "source_landmark_id": landmark_id
        }
    
    except Exception as e:
        raise BadRequestException(f"Failed to find similar landmarks: {str(e)}")

