"""
Hotels API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from backend.app.models.hotel import Hotel, HotelResponse, HotelCategory, StarRating
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[HotelResponse])
async def get_hotels(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[HotelCategory] = None,
    star_rating: Optional[StarRating] = None,
    city: Optional[str] = None,
    language: str = "en"
):
    """Get list of hotels with filters"""
    query = Hotel.find(Hotel.is_active == True)
    
    if category:
        query = query.find(Hotel.category == category)
    
    if star_rating:
        query = query.find(Hotel.star_rating == star_rating)
    
    if city:
        query = query.find(Hotel.location.city == city)
    
    hotels = await query.sort(-Hotel.popularity_score).skip(skip).limit(limit).to_list()
    return [HotelResponse(**hotel.dict()) for hotel in hotels]


@router.get("/search", response_model=List[HotelResponse])
async def search_hotels(
    q: Optional[str] = Query(None),
    location: Optional[str] = None,
    category: Optional[HotelCategory] = None,
    star_rating: Optional[StarRating] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Search hotels"""
    query = Hotel.find(Hotel.is_active == True)
    
    if category:
        query = query.find(Hotel.category == category)
    
    if star_rating:
        query = query.find(Hotel.star_rating == star_rating)
    
    if location:
        query = query.find({"location.city": {"$regex": location, "$options": "i"}})
    
    if q:
        query = query.find({"name.en": {"$regex": q, "$options": "i"}})
    
    hotels = await query.sort(-Hotel.popularity_score).limit(limit).to_list()
    return [HotelResponse(**hotel.dict()) for hotel in hotels]


@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel_by_id(hotel_id: str):
    """Get hotel by ID"""
    try:
        hotel = await Hotel.get(hotel_id)
        return HotelResponse(**hotel.dict())
    except:
        raise HTTPException(status_code=404, detail="Hotel not found")
