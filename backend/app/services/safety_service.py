"""
Safety & Emergency Service
Real-time safety tracking, SOS alerts, and emergency assistance
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from backend.app.models.safety import (
    SOSAlert, LocationSharing, SafetyScore, TravelAlert,
    UserSafetyProfile, SafetyCheckIn, EmergencyType,
    EmergencyStatus, SafetyLevel, AlertType, Location
)
from backend.app.models.user import User
from backend.app.tasks.email_tasks import send_notification_email
from backend.app.tasks.notification_tasks import send_push_notification

logger = logging.getLogger(__name__)


class SafetyService:
    """Service for safety and emergency features"""
    
    # Emergency hotlines in Sri Lanka
    EMERGENCY_NUMBERS = {
        "police": "119",
        "ambulance": "110",
        "fire": "111",
        "tourist_police": "+94-11-2421-052",
        "accident_service": "110",
        "disaster_management": "117"
    }
    
    # Embassy contacts (example - expand with all countries)
    EMBASSY_CONTACTS = {
        "USA": {
            "name": "US Embassy Colombo",
            "phone": "+94-11-249-8500",
            "email": "colomboacs@state.gov",
            "address": "210 Galle Road, Colombo 03",
            "coordinates": {"latitude": 6.9147, "longitude": 79.8553}
        },
        "UK": {
            "name": "British High Commission",
            "phone": "+94-11-539-0639",
            "email": "colombo.consular@fcdo.gov.uk",
            "address": "389 Bauddhaloka Mawatha, Colombo 07",
            "coordinates": {"latitude": 6.9147, "longitude": 79.8607}
        },
        "India": {
            "name": "Indian High Commission",
            "phone": "+94-11-242-1604",
            "email": "hc.colombo@mea.gov.in",
            "address": "36-38 Galle Road, Colombo 03",
            "coordinates": {"latitude": 6.9147, "longitude": 79.8500}
        }
        # Add more embassies...
    }
    
    async def create_sos_alert(
        self,
        user_id: str,
        emergency_type: EmergencyType,
        description: str,
        location: Location,
        severity: int = 3,
        photo_urls: Optional[List[str]] = None
    ) -> SOSAlert:
        """
        Create SOS emergency alert and notify responders
        
        This is a CRITICAL feature for user safety!
        """
        try:
            # Get user info
            user = await User.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Create SOS alert
            sos_alert = SOSAlert(
                user_id=user_id,
                user_name=user.full_name or user.username,
                user_phone=getattr(user, 'phone', None),
                emergency_type=emergency_type,
                description=description,
                severity=severity,
                location=location,
                photos=photo_urls or []
            )
            
            await sos_alert.insert()
            
            logger.critical(f"🚨 SOS ALERT: {emergency_type.value} - User: {user.username} - Location: {location.city}")
            
            # Get user's safety profile
            safety_profile = await UserSafetyProfile.find_one(
                UserSafetyProfile.user_id == user_id
            )
            
            # Notify emergency contacts
            if safety_profile and safety_profile.notify_contacts_on_sos:
                await self._notify_emergency_contacts(user, sos_alert, safety_profile)
            
            # Notify local authorities (in production, integrate with emergency services API)
            await self._notify_local_authorities(sos_alert)
            
            # Send push notification to user
            send_push_notification.delay(
                user_id=user_id,
                title="SOS Alert Received",
                body="We've received your emergency alert. Help is on the way.",
                data={
                    "type": "sos_response",
                    "alert_id": str(sos_alert.id)
                }
            )
            
            return sos_alert
            
        except Exception as e:
            logger.error(f"Failed to create SOS alert: {e}", exc_info=True)
            raise
    
    async def _notify_emergency_contacts(
        self,
        user: User,
        sos_alert: SOSAlert,
        safety_profile: UserSafetyProfile
    ):
        """Notify user's emergency contacts"""
        
        for contact in safety_profile.emergency_contacts:
            try:
                # Send email to emergency contact
                send_notification_email.delay(
                    user_email=contact.email if contact.email else None,
                    subject=f"🚨 EMERGENCY ALERT: {user.full_name}",
                    message=f"""
                    <h2>Emergency Alert</h2>
                    <p><strong>{user.full_name}</strong> has triggered an emergency alert.</p>
                    <p><strong>Type:</strong> {sos_alert.emergency_type.value}</p>
                    <p><strong>Description:</strong> {sos_alert.description}</p>
                    <p><strong>Location:</strong> {sos_alert.location.city} ({sos_alert.location.latitude}, {sos_alert.location.longitude})</p>
                    <p><strong>Time:</strong> {sos_alert.created_at.isoformat()}</p>
                    <p><a href="https://maps.google.com/?q={sos_alert.location.latitude},{sos_alert.location.longitude}">View on Map</a></p>
                    """
                )
                
                sos_alert.emergency_contacts_notified.append(contact.name)
                
            except Exception as e:
                logger.error(f"Failed to notify emergency contact {contact.name}: {e}")
        
        await sos_alert.save()
    
    async def _notify_local_authorities(self, sos_alert: SOSAlert):
        """Notify local authorities (mock for now)"""
        # In production: integrate with emergency services API
        logger.critical(
            f"LOCAL AUTHORITIES NOTIFICATION: "
            f"{sos_alert.emergency_type.value} at "
            f"{sos_alert.location.city} "
            f"({sos_alert.location.latitude}, {sos_alert.location.longitude})"
        )
        
        sos_alert.responders_notified.append("local_police")
        sos_alert.responders_notified.append("tourist_police")
        await sos_alert.save()
    
    async def start_location_sharing(
        self,
        user_id: str,
        shared_with: List[str],
        duration_hours: int,
        current_location: Location,
        trip_description: Optional[str] = None,
        enable_auto_check_in: bool = False
    ) -> LocationSharing:
        """
        Start sharing location with family/friends
        
        Safety feature for solo travelers!
        """
        user = await User.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        share_token = secrets.token_urlsafe(16)
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        location_sharing = LocationSharing(
            user_id=user_id,
            user_name=user.full_name or user.username,
            current_location=current_location,
            shared_with=shared_with,
            share_token=share_token,
            expires_at=expires_at,
            is_active=True,
            trip_description=trip_description,
            auto_check_in_enabled=enable_auto_check_in
        )
        
        await location_sharing.insert()
        
        # Notify shared contacts
        share_url = f"https://your-domain.com/track/{share_token}"
        
        for contact in shared_with:
            # Send notification (email or SMS)
            send_notification_email.delay(
                user_email=contact,
                subject=f"{user.full_name} is sharing their location with you",
                message=f"""
                <h2>Location Sharing Active</h2>
                <p><strong>{user.full_name}</strong> is sharing their live location with you.</p>
                <p><strong>Trip:</strong> {trip_description or 'Traveling in Sri Lanka'}</p>
                <p><strong>Duration:</strong> {duration_hours} hours</p>
                <p><a href="{share_url}">Track Location</a></p>
                <p>You will receive automatic updates every {location_sharing.update_interval_minutes} minutes.</p>
                """
            )
        
        logger.info(f"Location sharing started for user {user_id} - Token: {share_token}")
        
        return location_sharing
    
    async def update_location(
        self,
        share_token: str,
        new_location: Location
    ) -> Optional[LocationSharing]:
        """Update user's shared location"""
        
        location_sharing = await LocationSharing.find_one(
            LocationSharing.share_token == share_token,
            LocationSharing.is_active == True
        )
        
        if not location_sharing:
            return None
        
        # Check if expired
        if location_sharing.expires_at < datetime.utcnow():
            location_sharing.is_active = False
            await location_sharing.save()
            return None
        
        # Update location
        location_sharing.current_location = new_location
        location_sharing.location_history.append({
            "location": new_location.dict(),
            "timestamp": datetime.utcnow().isoformat()
        })
        location_sharing.last_updated = datetime.utcnow()
        
        await location_sharing.save()
        
        return location_sharing
    
    async def get_safety_score(self, city: str, area: Optional[str] = None) -> SafetyScore:
        """Get safety score for area"""
        
        # Try to find existing score
        query = SafetyScore.find(SafetyScore.city == city)
        if area:
            query = query.find(SafetyScore.area_name == area)
        
        score = await query.first_or_none()
        
        if score:
            return score
        
        # Generate default score (in production, calculate from data)
        default_score = SafetyScore(
            area_name=area or "City Center",
            city=city,
            coordinates=Location(latitude=6.9271, longitude=79.8612),  # Default Colombo
            safety_level=SafetyLevel.SAFE,
            safety_score=75.0,
            crime_score=80.0,
            tourist_safety_score=85.0,
            infrastructure_score=70.0,
            health_safety_score=75.0,
            day_score=85.0,
            night_score=65.0,
            safety_tips=[
                "Use registered taxis or ride-sharing apps",
                "Keep valuables secure",
                "Stay in well-lit areas at night",
                "Keep emergency numbers handy"
            ]
        )
        
        await default_score.insert()
        return default_score
    
    async def get_active_alerts(
        self,
        city: Optional[str] = None,
        alert_type: Optional[AlertType] = None
    ) -> List[TravelAlert]:
        """Get active travel alerts"""
        
        query = TravelAlert.find(TravelAlert.is_ongoing == True)
        
        if city:
            query = query.find({"affected_cities": city})
        
        if alert_type:
            query = query.find(TravelAlert.alert_type == alert_type)
        
        alerts = await query.sort(-TravelAlert.severity).to_list()
        
        return alerts
    
    async def create_safety_check_in(
        self,
        user_id: str,
        location: Location,
        status: str = "safe",
        message: Optional[str] = None
    ) -> SafetyCheckIn:
        """Record safety check-in"""
        
        check_in = SafetyCheckIn(
            user_id=user_id,
            location=location,
            status=status,
            message=message
        )
        
        await check_in.insert()
        
        # If user has active location sharing, update it
        active_sharing = await LocationSharing.find_one(
            LocationSharing.user_id == user_id,
            LocationSharing.is_active == True
        )
        
        if active_sharing:
            active_sharing.last_check_in = datetime.utcnow()
            active_sharing.missed_check_ins = 0
            await active_sharing.save()
            
            # Notify shared contacts
            user = await User.get(user_id)
            for contact in active_sharing.shared_with:
                send_notification_email.delay(
                    user_email=contact,
                    subject=f"✅ {user.full_name} checked in safely",
                    message=f"{user.full_name} checked in at {location.city}. Status: {status}. {message or ''}"
                )
        
        logger.info(f"Safety check-in recorded for user {user_id}: {status}")
        
        return check_in
    
    async def get_emergency_numbers(self) -> Dict[str, str]:
        """Get emergency hotline numbers"""
        return self.EMERGENCY_NUMBERS
    
    async def find_nearest_embassy(
        self,
        user_id: str,
        current_location: Location
    ) -> Dict[str, Any]:
        """Find nearest embassy for user's country"""
        
        user = await User.get(user_id)
        if not user:
            return {}
        
        # Get user's country (from profile or safety profile)
        safety_profile = await UserSafetyProfile.find_one(
            UserSafetyProfile.user_id == user_id
        )
        
        home_country = safety_profile.home_country if safety_profile else "USA"
        
        # Get embassy info
        embassy = self.EMBASSY_CONTACTS.get(home_country, self.EMBASSY_CONTACTS["USA"])
        
        # Calculate distance (simple calculation)
        embassy_location = embassy["coordinates"]
        distance_km = self._calculate_distance(
            current_location.latitude,
            current_location.longitude,
            embassy_location["latitude"],
            embassy_location["longitude"]
        )
        
        return {
            **embassy,
            "distance_km": distance_km,
            "google_maps_url": f"https://maps.google.com/?q={embassy_location['latitude']},{embassy_location['longitude']}"
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points (Haversine formula)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def get_medical_phrases(self, language: str = "si") -> Dict[str, str]:
        """Get medical emergency phrases in local language"""
        
        phrases = {
            "si": {  # Sinhala
                "help": "උදව්! (Udaw!)",
                "doctor": "වෛද්‍යවරයෙක් (Vaidyawaryek)",
                "hospital": "රෝහල (Rohala)",
                "ambulance": "ගිලන් රථය (Gilan rathaya)",
                "pain": "වේදනාව (Wedanawa)",
                "medicine": "බෙහෙත් (Behet)",
                "allergic": "අසාත්මිකතාව (Asatmikatawa)",
                "emergency": "හදිසි (Hadisi)"
            },
            "ta": {  # Tamil
                "help": "உதவி! (Uthavi!)",
                "doctor": "மருத்துவர் (Maruthuvar)",
                "hospital": "மருத்துவமனை (Maruthuvamanai)",
                "ambulance": "ஆம்புலன்ஸ் (Ambulance)",
                "pain": "வலி (Vali)",
                "medicine": "மருந்து (Marunthu)",
                "allergic": "ஒவ்வாமை (Ovvamai)",
                "emergency": "அவசரம் (Avasaram)"
            },
            "en": {
                "help": "Help!",
                "doctor": "Doctor",
                "hospital": "Hospital",
                "ambulance": "Ambulance",
                "pain": "Pain",
                "medicine": "Medicine",
                "allergic": "Allergic",
                "emergency": "Emergency"
            }
        }
        
        return phrases.get(language, phrases["en"])
    
    async def check_missed_checkins(self):
        """Check for missed safety check-ins (background task)"""
        
        # Find active location shares with auto check-in enabled
        active_shares = await LocationSharing.find(
            LocationSharing.is_active == True,
            LocationSharing.auto_check_in_enabled == True
        ).to_list()
        
        for share in active_shares:
            # Check if check-in is overdue
            if share.last_check_in:
                hours_since = (datetime.utcnow() - share.last_check_in).total_seconds() / 3600
                
                if hours_since > share.check_in_interval_hours:
                    # Missed check-in!
                    share.missed_check_ins += 1
                    await share.save()
                    
                    # Alert contacts
                    user = await User.get(share.user_id)
                    for contact in share.shared_with:
                        send_notification_email.delay(
                            user_email=contact,
                            subject=f"⚠️ {user.full_name} missed safety check-in",
                            message=f"""
                            <h2>Missed Check-in Alert</h2>
                            <p>{user.full_name} has not checked in for {int(hours_since)} hours.</p>
                            <p>Last known location: {share.current_location.city}</p>
                            <p>This may be normal, but you may want to contact them.</p>
                            <p><a href="https://your-domain.com/track/{share.share_token}">View Location</a></p>
                            """
                        )
                    
                    logger.warning(f"User {user.username} missed check-in ({share.missed_check_ins} missed)")

