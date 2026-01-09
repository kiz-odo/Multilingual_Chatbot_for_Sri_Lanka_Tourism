"""
Restaurants API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from backend.app.models.restaurant import Restaurant, RestaurantResponse, CuisineType, PriceRange
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[RestaurantResponse])
async def get_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    cuisine_type: Optional[CuisineType] = None,
    price_range: Optional[PriceRange] = None,
    city: Optional[str] = None,
    language: str = "en"
):
    """Get list of restaurants with filters"""
    query = Restaurant.find(Restaurant.is_active == True)
    
    if cuisine_type:
        query = query.find(Restaurant.cuisine_types.contains(cuisine_type))
    
    if price_range:
        query = query.find(Restaurant.price_range == price_range)
    
    if city:
        query = query.find(Restaurant.location.city == city)
    
    restaurants = await query.sort(-Restaurant.popularity_score).skip(skip).limit(limit).to_list()
    return [RestaurantResponse(**restaurant.dict()) for restaurant in restaurants]


@router.get("/search", response_model=List[RestaurantResponse])
async def search_restaurants(
    q: Optional[str] = Query(None),
    cuisine_type: Optional[CuisineType] = None,
    location: Optional[str] = None,
    price_range: Optional[PriceRange] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Search restaurants"""
    query = Restaurant.find(Restaurant.is_active == True)
    
    if cuisine_type:
        query = query.find(Restaurant.cuisine_types.contains(cuisine_type))
    
    if price_range:
        query = query.find(Restaurant.price_range == price_range)
    
    if location:
        query = query.find({"location.city": {"$regex": location, "$options": "i"}})
    
    if q:
        query = query.find({"name.en": {"$regex": q, "$options": "i"}})
    
    restaurants = await query.sort(-Restaurant.popularity_score).limit(limit).to_list()
    return [RestaurantResponse(**restaurant.dict()) for restaurant in restaurants]


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant_by_id(restaurant_id: str):
    """Get restaurant by ID"""
    try:
        restaurant = await Restaurant.get(restaurant_id)
        return RestaurantResponse(**restaurant.dict())
    except:
        raise HTTPException(status_code=404, detail="Restaurant not found")
