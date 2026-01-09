"""
Safety & Emergency API Endpoints
Real-time safety tracking, SOS alerts, and emergency assistance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from backend.app.models.safety import (
    SOSRequest, LocationSharingRequest, SafetyScoreResponse,
    TravelAlertResponse, SOSAlert, LocationSharing, UserSafetyProfile,
    EmergencyType, AlertType, Location, EmergencyContact
)
from backend.app.models.user import User
from backend.app.services.safety_service import SafetyService
from backend.app.core.auth import get_current_active_user
from backend.app.middleware.error_handler import NotFoundException, BadRequestException

router = APIRouter(prefix="/safety", tags=["Safety & Emergency"])
logger = logging.getLogger(__name__)

safety_service = SafetyService()


@router.post("/sos", status_code=status.HTTP_201_CREATED)
async def create_sos_alert(
    request: SOSRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    🚨 **SOS EMERGENCY ALERT**
    
    This is a CRITICAL safety feature!
    - Immediately notifies emergency contacts
    - Alerts local authorities
    - Shares location
    - Triggers emergency response
    
    **Use this for:**
    - Medical emergencies
    - Accidents
    - Theft/robbery
    - Harassment
    - Natural disasters
    - Getting lost
    
    **Example:**
    ```json
    {
      "emergency_type": "medical",
      "description": "Severe allergic reaction, need ambulance",
      "severity": 5,
      "location": {
        "latitude": 6.9271,
        "longitude": 79.8612,
        "city": "Colombo"
      }
    }
    ```
    """
    try:
        logger.critical(f"🚨 SOS ALERT from user {current_user.username}")
        
        sos_alert = await safety_service.create_sos_alert(
            user_id=str(current_user.id),
            emergency_type=request.emergency_type,
            description=request.description,
            location=request.location,
            severity=request.severity,
            photo_urls=request.photo_urls
        )
        
        return {
            "success": True,
            "alert_id": str(sos_alert.id),
            "message": "SOS alert received! Help is on the way.",
            "emergency_numbers": safety_service.EMERGENCY_NUMBERS,
            "contacts_notified": sos_alert.emergency_contacts_notified,
            "authorities_notified": sos_alert.responders_notified
        }
        
    except Exception as e:
        logger.error(f"Failed to create SOS alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SOS alert"
        )


@router.get("/sos/{alert_id}")
async def get_sos_alert(
    alert_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get SOS alert details
    """
    try:
        alert = await SOSAlert.get(alert_id)
        
        if not alert:
            raise NotFoundException("SOS alert not found")
        
        # Check if user owns this alert
        if str(alert.user_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return alert
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch SOS alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch SOS alert")


@router.post("/location-sharing/start", status_code=status.HTTP_201_CREATED)
async def start_location_sharing(
    request: LocationSharingRequest,
    current_location: Location,
    current_user: User = Depends(get_current_active_user)
):
    """
    📍 **Start Real-Time Location Sharing**
    
    Share your live location with family/friends for safety.
    Perfect for solo travelers!
    
    **Features:**
    - Real-time location updates
    - Automatic safety check-ins
    - Alert contacts if you miss check-ins
    - Share trip details
    
    **Example:**
    ```json
    {
      "shared_with": ["family@example.com", "friend@example.com"],
      "duration_hours": 48,
      "trip_description": "Hiking in Ella, returning Sunday",
      "enable_auto_check_in": true
    }
    ```
    """
    try:
        location_sharing = await safety_service.start_location_sharing(
            user_id=str(current_user.id),
            shared_with=request.shared_with,
            duration_hours=request.duration_hours,
            current_location=current_location,
            trip_description=request.trip_description,
            enable_auto_check_in=request.enable_auto_check_in
        )
        
        tracking_url = f"https://your-domain.com/track/{location_sharing.share_token}"
        
        return {
            "success": True,
            "sharing_id": str(location_sharing.id),
            "tracking_url": tracking_url,
            "expires_at": location_sharing.expires_at.isoformat(),
            "shared_with": location_sharing.shared_with,
            "message": "Location sharing started. Your contacts have been notified."
        }
        
    except Exception as e:
        logger.error(f"Failed to start location sharing: {e}")
        raise HTTPException(status_code=500, detail="Failed to start location sharing")


@router.put("/location-sharing/{share_token}/update")
async def update_location(
    share_token: str,
    new_location: Location,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current location for active location sharing
    """
    try:
        updated = await safety_service.update_location(share_token, new_location)
        
        if not updated:
            raise NotFoundException("Location sharing session not found or expired")
        
        return {
            "success": True,
            "last_updated": updated.last_updated.isoformat(),
            "current_location": updated.current_location
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to update location: {e}")
        raise HTTPException(status_code=500, detail="Failed to update location")


@router.get("/location-sharing/track/{share_token}")
async def track_location(share_token: str):
    """
    🗺️ **Track Shared Location (Public)**
    
    Anyone with the tracking link can view the traveler's location.
    No authentication required.
    """
    try:
        location_sharing = await LocationSharing.find_one(
            LocationSharing.share_token == share_token,
            LocationSharing.is_active == True
        )
        
        if not location_sharing:
            raise NotFoundException("Tracking link not found or expired")
        
        return {
            "traveler_name": location_sharing.user_name,
            "current_location": location_sharing.current_location,
            "trip_description": location_sharing.trip_description,
            "last_updated": location_sharing.last_updated.isoformat(),
            "expires_at": location_sharing.expires_at.isoformat(),
            "location_history": location_sharing.location_history[-10:],  # Last 10 points
            "last_check_in": location_sharing.last_check_in.isoformat() if location_sharing.last_check_in else None
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to track location: {e}")
        raise HTTPException(status_code=404, detail="Tracking link not found")


@router.get("/score/{city}", response_model=SafetyScoreResponse)
async def get_safety_score(
    city: str,
    area: Optional[str] = Query(None, description="Specific area within city")
):
    """
    🛡️ **Get Safety Score for Area**
    
    Returns safety information and tips for a specific location.
    
    **Safety Score Breakdown:**
    - Crime score
    - Tourist safety score
    - Infrastructure score
    - Health safety score
    - Day vs Night scores
    
    **Example:** `GET /safety/score/Colombo?area=Fort`
    """
    try:
        safety_score = await safety_service.get_safety_score(city, area)
        
        return SafetyScoreResponse(
            area_name=safety_score.area_name,
            city=safety_score.city,
            safety_level=safety_score.safety_level,
            safety_score=safety_score.safety_score,
            safety_tips=safety_score.safety_tips,
            day_score=safety_score.day_score,
            night_score=safety_score.night_score
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch safety score: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch safety score")


@router.get("/alerts", response_model=List[TravelAlertResponse])
async def get_travel_alerts(
    city: Optional[str] = Query(None, description="Filter by city"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type")
):
    """
    ⚠️ **Get Active Travel Alerts**
    
    Real-time warnings about:
    - Weather (storms, floods)
    - Protests & strikes
    - Road closures
    - Health alerts
    - Security warnings
    
    **Example:** `GET /safety/alerts?city=Colombo&alert_type=weather`
    """
    try:
        alerts = await safety_service.get_active_alerts(city, alert_type)
        
        return [
            TravelAlertResponse(
                title=alert.title,
                description=alert.description,
                alert_type=alert.alert_type,
                severity=alert.severity,
                affected_cities=alert.affected_cities,
                recommended_actions=alert.recommended_actions,
                is_ongoing=alert.is_ongoing
            )
            for alert in alerts
        ]
        
    except Exception as e:
        logger.error(f"Failed to fetch travel alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch travel alerts")


@router.post("/check-in")
async def safety_check_in(
    location: Location,
    status: str = Query("safe", description="safe, needs_help, emergency"),
    message: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    ✅ **Safety Check-In**
    
    Let your emergency contacts know you're safe.
    """
    try:
        check_in = await safety_service.create_safety_check_in(
            user_id=str(current_user.id),
            location=location,
            status=status,
            message=message
        )
        
        return {
            "success": True,
            "check_in_id": str(check_in.id),
            "message": "Check-in recorded. Your contacts have been notified."
        }
        
    except Exception as e:
        logger.error(f"Failed to record check-in: {e}")
        raise HTTPException(status_code=500, detail="Failed to record check-in")


@router.get("/emergency-numbers")
async def get_emergency_numbers():
    """
    📞 **Emergency Hotline Numbers**
    
    Get all emergency contact numbers for Sri Lanka:
    - Police: 119
    - Ambulance: 110
    - Fire: 111
    - Tourist Police
    - Disaster Management
    """
    return safety_service.EMERGENCY_NUMBERS


@router.get("/embassy")
async def find_nearest_embassy(
    latitude: float = Query(...),
    longitude: float = Query(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    🏛️ **Find Nearest Embassy**
    
    Locate your country's embassy with contact details and directions.
    """
    try:
        location = Location(latitude=latitude, longitude=longitude)
        embassy = await safety_service.find_nearest_embassy(
            user_id=str(current_user.id),
            current_location=location
        )
        
        return embassy
        
    except Exception as e:
        logger.error(f"Failed to find embassy: {e}")
        raise HTTPException(status_code=500, detail="Failed to find embassy")


@router.get("/medical-phrases")
async def get_medical_phrases(
    language: str = Query("si", description="Language code: si, ta, en")
):
    """
    🏥 **Medical Emergency Phrases**
    
    Get essential medical phrases in local language:
    - "Help!"
    - "Doctor"
    - "Hospital"
    - "Ambulance"
    - "Pain"
    - "Medicine"
    - "Allergic"
    
    **Languages:** `si` (Sinhala), `ta` (Tamil), `en` (English)
    """
    return await safety_service.get_medical_phrases(language)


@router.get("/profile", response_model=UserSafetyProfile)
async def get_safety_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's safety profile
    """
    profile = await UserSafetyProfile.find_one(
        UserSafetyProfile.user_id == str(current_user.id)
    )
    
    if not profile:
        # Create default profile
        profile = UserSafetyProfile(
            user_id=str(current_user.id),
            home_country="Unknown"
        )
        await profile.insert()
    
    return profile


@router.put("/profile")
async def update_safety_profile(
    emergency_contacts: Optional[List[EmergencyContact]] = None,
    blood_type: Optional[str] = None,
    allergies: Optional[List[str]] = None,
    home_country: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update safety profile with emergency contacts and medical info
    """
    profile = await UserSafetyProfile.find_one(
        UserSafetyProfile.user_id == str(current_user.id)
    )
    
    if not profile:
        profile = UserSafetyProfile(user_id=str(current_user.id))
    
    if emergency_contacts is not None:
        profile.emergency_contacts = emergency_contacts
    if blood_type:
        profile.blood_type = blood_type
    if allergies is not None:
        profile.allergies = allergies
    if home_country:
        profile.home_country = home_country
    
    profile.updated_at = datetime.utcnow()
    await profile.save()
    
    return {"success": True, "message": "Safety profile updated"}

