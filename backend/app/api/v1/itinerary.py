"""
Itinerary & Trip Planning API Endpoints
AI-powered itinerary generation with monetization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
from datetime import date, datetime
import logging
import secrets

from backend.app.models.itinerary import (
    ItineraryGenerateRequest, ItineraryResponse,
    TripItinerary, BookingRequest, DayItinerary
)
from backend.app.models.user import User
from backend.app.services.itinerary_service import ItineraryService
from backend.app.core.auth import get_current_active_user
from backend.app.middleware.error_handler import NotFoundException, BadRequestException

router = APIRouter()
logger = logging.getLogger(__name__)

itinerary_service = ItineraryService()


@router.post("/generate", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
async def generate_itinerary(
    request: ItineraryGenerateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    🤖 Generate AI-powered travel itinerary using Mistral-7B LLM
    
    This is the CORE monetization feature!
    - Creates personalized day-by-day itineraries
    - Includes booking links (hotels, transport, activities)
    - Tracks potential commission revenue
    
    **Example:**
    ```json
    {
      "destination": "Kandy",
      "duration_days": 3,
      "budget_level": "mid_range",
      "interests": ["culture", "history"],
      "start_date": "2024-01-15",
      "travelers_count": 2,
      "custom_requirements": "I want to reduce costs but see major attractions"
    }
    ```
    """
    try:
        logger.info(f"Generating itinerary for user {current_user.username}: {request.destination}")
        
        itinerary = await itinerary_service.generate_itinerary(
            user_id=str(current_user.id),
            destination=request.destination,
            duration_days=request.duration_days,
            start_date=request.start_date,
            budget_level=request.budget_level,
            interests=request.interests,
            travelers_count=request.travelers_count,
            custom_requirements=request.custom_requirements
        )
        
        # Build share URL
        share_url = f"https://your-domain.com/itinerary/share/{itinerary.share_token}"
        
        return ItineraryResponse(
            id=str(itinerary.id),
            title=itinerary.title,
            destination=itinerary.destination,
            duration_days=itinerary.duration_days,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            days=itinerary.days,
            total_estimated_cost=itinerary.total_estimated_cost,
            currency=itinerary.currency,
            share_url=share_url
        )
        
    except Exception as e:
        logger.error(f"Failed to generate itinerary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate itinerary: {str(e)}"
        )


@router.get("/my-itineraries", response_model=List[ItineraryResponse])
async def get_my_itineraries(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all itineraries created by current user
    """
    try:
        itineraries = await itinerary_service.get_user_itineraries(str(current_user.id))
        
        return [
            ItineraryResponse(
                id=str(itin.id),
                title=itin.title,
                destination=itin.destination,
                duration_days=itin.duration_days,
                start_date=itin.start_date,
                end_date=itin.end_date,
                days=itin.days,
                total_estimated_cost=itin.total_estimated_cost,
                currency=itin.currency,
                share_url=f"https://your-domain.com/itinerary/share/{itin.share_token}"
            )
            for itin in itineraries
        ]
        
    except Exception as e:
        logger.error(f"Failed to fetch itineraries: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch itineraries")


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary(
    itinerary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific itinerary by ID
    """
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException(f"Itinerary {itinerary_id} not found")
        
        # Check ownership
        if str(itinerary.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )
        
        return ItineraryResponse(
            id=str(itinerary.id),
            title=itinerary.title,
            destination=itinerary.destination,
            duration_days=itinerary.duration_days,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            days=itinerary.days,
            total_estimated_cost=itinerary.total_estimated_cost,
            currency=itinerary.currency,
            share_url=f"https://your-domain.com/itinerary/share/{itinerary.share_token}"
        )
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch itinerary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch itinerary")


@router.put("/{itinerary_id}", response_model=ItineraryResponse)
async def update_itinerary(
    itinerary_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing itinerary
    """
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException(f"Itinerary {itinerary_id} not found")
        
        # Check ownership
        if str(itinerary.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this itinerary"
            )
        
        # Update allowed fields
        if "title" in update_data:
            itinerary.title = update_data["title"]
        if "destination" in update_data:
            itinerary.destination = update_data["destination"]
        if "start_date" in update_data:
            itinerary.start_date = update_data["start_date"]
        if "end_date" in update_data:
            itinerary.end_date = update_data["end_date"]
        if "days" in update_data:
            itinerary.days = update_data["days"]
        if "custom_requirements" in update_data:
            itinerary.custom_requirements = update_data["custom_requirements"]
        
        # Recalculate total cost if days changed
        if "days" in update_data:
            total_cost = sum(day.total_cost for day in itinerary.days)
            itinerary.total_estimated_cost = total_cost
        
        itinerary.updated_at = datetime.utcnow()
        await itinerary.save()
        
        return ItineraryResponse(
            id=str(itinerary.id),
            title=itinerary.title,
            destination=itinerary.destination,
            duration_days=itinerary.duration_days,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            days=itinerary.days,
            total_estimated_cost=itinerary.total_estimated_cost,
            currency=itinerary.currency,
            share_url=f"https://your-domain.com/itinerary/share/{itinerary.share_token}"
        )
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to update itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update itinerary: {str(e)}")


@router.get("/share/{share_token}", response_model=ItineraryResponse)
async def get_shared_itinerary(share_token: str):
    """
    📤 Get publicly shared itinerary (no auth required)
    
    Anyone with the link can view this itinerary.
    Great for sharing trip plans with friends and family!
    """
    try:
        itinerary = await itinerary_service.get_shared_itinerary(share_token)
        
        if not itinerary:
            raise NotFoundException("Itinerary not found or sharing link expired")
        
        return ItineraryResponse(
            id=str(itinerary.id),
            title=itinerary.title,
            destination=itinerary.destination,
            duration_days=itinerary.duration_days,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            days=itinerary.days,
            total_estimated_cost=itinerary.total_estimated_cost,
            currency=itinerary.currency,
            share_url=f"https://your-domain.com/itinerary/share/{share_token}"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch shared itinerary: {e}")
        raise HTTPException(status_code=404, detail="Itinerary not found")


@router.post("/{itinerary_id}/book", status_code=status.HTTP_201_CREATED)
async def track_booking(
    itinerary_id: str,
    booking: BookingRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    💰 Track a booking made through itinerary
    
    This endpoint is called when user clicks "Book Now" on any activity.
    It tracks the booking and calculates commission revenue.
    """
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException("Itinerary not found")
        
        # Get the activity
        activity = None
        for day in itinerary.days:
            if day.day_number == booking.day_number:
                if booking.activity_index < len(day.activities):
                    activity = day.activities[booking.activity_index]
                    break
        
        if not activity:
            raise BadRequestException("Activity not found")
        
        if not activity.booking_url:
            raise BadRequestException("This activity is not bookable")
        
        # Track the booking (in production, integrate with actual booking APIs)
        booking_tracking = await itinerary_service.track_booking(
            itinerary_id=itinerary_id,
            user_id=str(current_user.id),
            activity=activity,
            booking_reference=f"BOOK-{secrets.token_hex(4).upper()}",
            booking_amount=activity.estimated_cost
        )
        
        return {
            "success": True,
            "message": "Booking tracked successfully",
            "booking_id": str(booking_tracking.id),
            "booking_url": activity.booking_url,
            "commission_earned": booking_tracking.commission_amount
        }
        
    except (NotFoundException, BadRequestException):
        raise
    except Exception as e:
        logger.error(f"Failed to track booking: {e}")
        raise HTTPException(status_code=500, detail="Failed to track booking")


@router.delete("/{itinerary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_itinerary(
    itinerary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an itinerary
    """
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException("Itinerary not found")
        
        if str(itinerary.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        itinerary.is_active = False
        await itinerary.save()
        
        logger.info(f"Itinerary {itinerary_id} deleted by user {current_user.username}")
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete itinerary: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete itinerary")


@router.post("/{itinerary_id}/export/pdf")
async def export_to_pdf(
    itinerary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    📄 **Export Itinerary to PDF**
    
    Generates a beautiful PDF document of your itinerary.
    
    **Returns:** PDF file for download
    """
    from fastapi.responses import Response
    from backend.app.services.pdf_export_service import get_pdf_export_service
    
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException("Itinerary not found")
        
        if str(itinerary.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate PDF
        pdf_service = get_pdf_export_service()
        pdf_bytes = await pdf_service.export_itinerary_to_pdf(itinerary)
        
        # Update itinerary stats
        itinerary.exported_to_pdf = True
        await itinerary.save()
        
        # Return PDF file
        filename = f"{itinerary.title.replace(' ', '_')}_{itinerary.start_date}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except NotFoundException:
        raise
    except ImportError as e:
        logger.error(f"PDF export dependencies missing: {e}")
        return {
            "success": False,
            "message": "PDF export not available. Install reportlab: pip install reportlab"
        }
    except Exception as e:
        logger.error(f"Failed to export PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to export PDF")


@router.post("/{itinerary_id}/export/calendar/ics")
async def export_to_ics(
    itinerary_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    📅 **Export Itinerary to ICS (iCalendar)**
    
    Downloads an ICS file that works with:
    - Google Calendar
    - Apple Calendar
    - Outlook
    - Any calendar app
    
    **How to use:**
    1. Download the ICS file
    2. Open with your calendar app
    3. Events are automatically imported!
    """
    from fastapi.responses import Response
    from backend.app.services.calendar_export_service import get_calendar_export_service
    
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException("Itinerary not found")
        
        if str(itinerary.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate ICS file
        calendar_service = get_calendar_export_service()
        ics_content = await calendar_service.generate_ics_file(itinerary)
        
        # Update itinerary stats
        itinerary.exported_to_calendar = True
        await itinerary.save()
        
        # Return ICS file
        filename = f"{itinerary.title.replace(' ', '_')}_{itinerary.start_date}.ics"
        
        return Response(
            content=ics_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to export ICS: {e}")
        raise HTTPException(status_code=500, detail="Failed to export calendar")


@router.post("/{itinerary_id}/export/calendar/google")
async def export_to_google_calendar(
    itinerary_id: str,
    google_credentials: Dict[str, str],
    current_user: User = Depends(get_current_active_user)
):
    """
    📅 **Export Directly to Google Calendar**
    
    Creates a new Google Calendar with all your trip events.
    
    **Requires:** Google OAuth token with calendar scope
    
    **Request Body:**
    ```json
    {
      "token": "user's_google_access_token",
      "refresh_token": "user's_refresh_token"
    }
    ```
    """
    from backend.app.services.calendar_export_service import get_calendar_export_service
    
    try:
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            raise NotFoundException("Itinerary not found")
        
        if str(itinerary.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Export to Google Calendar
        calendar_service = get_calendar_export_service()
        result = await calendar_service.export_to_google_calendar(
            itinerary,
            google_credentials
        )
        
        # Update itinerary stats
        itinerary.exported_to_calendar = True
        await itinerary.save()
        
        return result
        
    except NotFoundException:
        raise
    except ImportError as e:
        logger.error(f"Google Calendar API dependencies missing: {e}")
        return {
            "success": False,
            "message": "Google Calendar export not available. Install google-api-python-client."
        }
    except Exception as e:
        logger.error(f"Failed to export to Google Calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

