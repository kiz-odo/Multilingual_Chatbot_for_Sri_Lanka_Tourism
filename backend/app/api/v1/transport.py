"""
Transport API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from backend.app.models.transport import Transport, TransportResponse, TransportType
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[TransportResponse])
async def get_transport_options(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    transport_type: Optional[TransportType] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    language: str = "en"
):
    """Get transport options with filters"""
    query = Transport.find(Transport.is_active == True)
    
    if transport_type:
        query = query.find(Transport.transport_type == transport_type)
    
    # Fetch transports (we'll filter by origin/destination in Python since routes is an array)
    transports = await query.sort(-Transport.popularity_score).skip(skip).limit(limit * 3).to_list()
    
    # Filter by origin/destination if specified (check routes array)
    if origin or destination:
        filtered_transports = []
        for transport in transports:
            match = True
            if origin:
                # Check if any route has matching origin
                if not any(route.origin.lower() == origin.lower() for route in transport.routes):
                    match = False
            if destination:
                # Check if any route has matching destination
                if not any(route.destination.lower() == destination.lower() for route in transport.routes):
                    match = False
            if match:
                filtered_transports.append(transport)
        transports = filtered_transports[:limit]
    
    return [TransportResponse(**transport.dict()) for transport in transports]


@router.get("/search", response_model=List[TransportResponse])
async def search_transport(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    transport_type: Optional[TransportType] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Search transport options"""
    query = Transport.find(Transport.is_active == True)
    
    if transport_type:
        query = query.find(Transport.transport_type == transport_type)
    
    transports = await query.sort(-Transport.popularity_score).limit(limit).to_list()
    return [TransportResponse(**transport.dict()) for transport in transports]


@router.get("/{transport_id}", response_model=TransportResponse)
async def get_transport_by_id(transport_id: str):
    """Get transport by ID"""
    try:
        transport = await Transport.get(transport_id)
        return TransportResponse(**transport.dict())
    except:
        raise HTTPException(status_code=404, detail="Transport not found")
