"""
Events API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date

from backend.app.models.event import Event, EventResponse, EventCategory
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[EventCategory] = None,
    city: Optional[str] = None,
    upcoming_only: bool = True,
    language: str = "en"
):
    """Get events with filters"""
    query = Event.find(Event.status == "published")
    
    if category:
        query = query.find(Event.category == category)
    
    if city:
        query = query.find(Event.location.city == city)
    
    if upcoming_only:
        today = date.today()
        query = query.find(Event.schedule.start_date >= today)
    
    events = await query.sort(Event.schedule.start_date).skip(skip).limit(limit).to_list()
    return [EventResponse(**event.dict()) for event in events]


@router.get("/search", response_model=List[EventResponse])
async def search_events(
    q: Optional[str] = Query(None),
    category: Optional[EventCategory] = None,
    location: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Search events"""
    query = Event.find(Event.status == "published")
    
    if category:
        query = query.find(Event.category == category)
    
    if location:
        query = query.find({"location.city": {"$regex": location, "$options": "i"}})
    
    if date_from:
        query = query.find(Event.schedule.start_date >= date_from)
    
    if date_to:
        query = query.find(Event.schedule.start_date <= date_to)
    
    if q:
        query = query.find({"title.en": {"$regex": q, "$options": "i"}})
    
    events = await query.sort(Event.schedule.start_date).limit(limit).to_list()
    return [EventResponse(**event.dict()) for event in events]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event_by_id(event_id: str):
    """Get event by ID"""
    try:
        event = await Event.get(event_id)
        return EventResponse(**event.dict())
    except:
        raise HTTPException(status_code=404, detail="Event not found")
