"""
Emergency services API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from backend.app.models.emergency import Emergency, EmergencyResponse, EmergencyType
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[EmergencyResponse])
async def get_emergency_services(
    service_type: Optional[EmergencyType] = None,
    city: Optional[str] = None,
    language: str = "en"
):
    """Get emergency services"""
    query = Emergency.find(Emergency.is_active == True)
    
    if service_type:
        query = query.find(Emergency.service_type == service_type)
    
    if city:
        query = query.find(Emergency.location.city == city)
    
    services = await query.to_list()
    return [EmergencyResponse(**service.dict()) for service in services]


@router.get("/search", response_model=List[EmergencyResponse])
async def search_emergency_services(
    service_type: Optional[str] = Query(None, description="Emergency service type"),
    location: Optional[str] = Query(None, description="Location to search"),
    urgent_only: bool = False
):
    """Search emergency services"""
    query = Emergency.find(Emergency.is_active == True)
    
    if service_type:
        try:
            # Convert string to enum
            service_type_enum = EmergencyType(service_type)
            query = query.find(Emergency.service_type == service_type_enum)
        except ValueError:
            # Invalid service type, return empty list
            return []
    
    if location:
        query = query.find(Emergency.location.city.contains(location, case_insensitive=True))
    
    services = await query.to_list()
    return [EmergencyResponse(**service.dict()) for service in services]


@router.get("/{service_id}", response_model=EmergencyResponse)
async def get_emergency_service_by_id(service_id: str):
    """Get emergency service by ID"""
    try:
        service = await Emergency.get(service_id)
        return EmergencyResponse(**service.dict())
    except:
        raise HTTPException(status_code=404, detail="Emergency service not found")
