"""
Google Maps API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.app.models.user import User
from backend.app.models.attraction import Location
from backend.app.core.auth import get_current_active_user
from backend.app.services.maps_service import MapsService

router = APIRouter()


class LocationRequest(BaseModel):
    address: str


class CoordinatesRequest(BaseModel):
    latitude: float
    longitude: float


class PlaceSearchRequest(BaseModel):
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: int = 5000
    place_type: Optional[str] = None


class DirectionsRequest(BaseModel):
    origin: str
    destination: str
    mode: str = "driving"


class LocationResponse(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None
    place_id: Optional[str] = None
    name: Optional[str] = None


class PlaceResponse(BaseModel):
    place_id: str
    name: str
    address: str
    location: LocationResponse
    rating: Optional[float] = None
    price_level: Optional[int] = None
    types: Optional[List[str]] = None
    photos: Optional[List[str]] = None


class RouteResponse(BaseModel):
    distance: str
    duration: str
    steps: List[Dict[str, Any]]
    polyline: Optional[str] = None


@router.post("/geocode", response_model=LocationResponse)
async def geocode_address(
    location_request: LocationRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Convert address to coordinates"""
    try:
        maps_service = MapsService()
        location = await maps_service.geocode_address(location_request.address)
        
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found"
            )
        
        return LocationResponse(
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            place_id=location.place_id,
            name=location.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error geocoding address: {str(e)}"
        )


@router.post("/reverse-geocode", response_model=LocationResponse)
async def reverse_geocode(
    coordinates_request: CoordinatesRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Convert coordinates to address"""
    try:
        maps_service = MapsService()
        location = await maps_service.reverse_geocode(
            coordinates_request.latitude,
            coordinates_request.longitude
        )
        
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        
        return LocationResponse(
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            place_id=location.place_id,
            name=location.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reverse geocoding: {str(e)}"
        )


@router.post("/search-places", response_model=List[PlaceResponse])
async def search_places(
    search_request: PlaceSearchRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Search for places"""
    try:
        maps_service = MapsService()
        
        location = None
        if search_request.latitude and search_request.longitude:
            location = Location(
                latitude=search_request.latitude,
                longitude=search_request.longitude
            )
        
        places = await maps_service.search_places(
            query=search_request.query,
            location=location,
            radius=search_request.radius,
            place_type=search_request.place_type
        )
        
        return [
            PlaceResponse(
                place_id=place.place_id,
                name=place.name,
                address=place.address,
                location=LocationResponse(
                    latitude=place.location.latitude,
                    longitude=place.location.longitude,
                    address=place.location.address,
                    place_id=place.location.place_id,
                    name=place.location.name
                ),
                rating=place.rating,
                price_level=place.price_level,
                types=place.types,
                photos=place.photos
            )
            for place in places
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching places: {str(e)}"
        )


@router.get("/place/{place_id}", response_model=PlaceResponse)
async def get_place_details(
    place_id: str,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get detailed information about a place"""
    try:
        maps_service = MapsService()
        place = await maps_service.get_place_details(place_id)
        
        if not place:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Place not found"
            )
        
        return PlaceResponse(
            place_id=place.place_id,
            name=place.name,
            address=place.address,
            location=LocationResponse(
                latitude=place.location.latitude,
                longitude=place.location.longitude,
                address=place.location.address,
                place_id=place.location.place_id,
                name=place.location.name
            ),
            rating=place.rating,
            price_level=place.price_level,
            types=place.types,
            photos=place.photos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting place details: {str(e)}"
        )


@router.post("/directions", response_model=RouteResponse)
async def get_directions(
    directions_request: DirectionsRequest,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get directions between two points"""
    try:
        maps_service = MapsService()
        route = await maps_service.get_directions(
            origin=directions_request.origin,
            destination=directions_request.destination,
            mode=directions_request.mode
        )
        
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found"
            )
        
        return RouteResponse(
            distance=route.distance,
            duration=route.duration,
            steps=route.steps,
            polyline=route.polyline
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting directions: {str(e)}"
        )


@router.get("/nearby-attractions")
async def find_nearby_attractions(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius: int = Query(5000, description="Search radius in meters"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Find nearby tourist attractions"""
    try:
        maps_service = MapsService()
        location = Location(latitude=latitude, longitude=longitude)
        attractions = await maps_service.find_nearby_attractions(location, radius)
        
        return [
            PlaceResponse(
                place_id=place.place_id,
                name=place.name,
                address=place.address,
                location=LocationResponse(
                    latitude=place.location.latitude,
                    longitude=place.location.longitude,
                    address=place.location.address,
                    place_id=place.location.place_id,
                    name=place.location.name
                ),
                rating=place.rating,
                price_level=place.price_level,
                types=place.types,
                photos=place.photos
            )
            for place in attractions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding nearby attractions: {str(e)}"
        )


@router.get("/nearby-restaurants")
async def find_nearby_restaurants(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius: int = Query(2000, description="Search radius in meters"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Find nearby restaurants"""
    try:
        maps_service = MapsService()
        location = Location(latitude=latitude, longitude=longitude)
        restaurants = await maps_service.find_nearby_restaurants(location, radius)
        
        return [
            PlaceResponse(
                place_id=place.place_id,
                name=place.name,
                address=place.address,
                location=LocationResponse(
                    latitude=place.location.latitude,
                    longitude=place.location.longitude,
                    address=place.location.address,
                    place_id=place.location.place_id,
                    name=place.location.name
                ),
                rating=place.rating,
                price_level=place.price_level,
                types=place.types,
                photos=place.photos
            )
            for place in restaurants
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding nearby restaurants: {str(e)}"
        )


@router.get("/nearby-hotels")
async def find_nearby_hotels(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    radius: int = Query(5000, description="Search radius in meters"),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Find nearby hotels"""
    try:
        maps_service = MapsService()
        location = Location(latitude=latitude, longitude=longitude)
        hotels = await maps_service.find_nearby_hotels(location, radius)
        
        return [
            PlaceResponse(
                place_id=place.place_id,
                name=place.name,
                address=place.address,
                location=LocationResponse(
                    latitude=place.location.latitude,
                    longitude=place.location.longitude,
                    address=place.location.address,
                    place_id=place.location.place_id,
                    name=place.location.name
                ),
                rating=place.rating,
                price_level=place.price_level,
                types=place.types,
                photos=place.photos
            )
            for place in hotels
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding nearby hotels: {str(e)}"
        )


@router.post("/distance-matrix")
async def get_distance_matrix(
    origins: List[str],
    destinations: List[str],
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get distance matrix between multiple origins and destinations"""
    try:
        maps_service = MapsService()
        matrix = await maps_service.get_distance_matrix(origins, destinations)
        
        if not matrix:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distance matrix not available"
            )
        
        return matrix
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting distance matrix: {str(e)}"
        )
