"""
Emergency services model for Sri Lanka Tourism
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from backend.app.models.attraction import Location, MultilingualContent


class EmergencyType(str, Enum):
    """Emergency service types"""
    POLICE = "police"
    HOSPITAL = "hospital"
    FIRE = "fire"
    AMBULANCE = "ambulance"
    TOURIST_POLICE = "tourist_police"
    EMBASSY = "embassy"
    COAST_GUARD = "coast_guard"
    DISASTER_MANAGEMENT = "disaster_management"
    WILDLIFE_EMERGENCY = "wildlife_emergency"


class ServiceLevel(str, Enum):
    """Service levels"""
    EMERGENCY = "emergency"  # 24/7 emergency
    URGENT = "urgent"       # Quick response
    STANDARD = "standard"   # Normal hours
    INFORMATION = "information"  # Information only


class ContactMethod(BaseModel):
    """Contact method model"""
    type: str  # phone, email, fax, radio
    value: str
    is_primary: bool = False
    is_24_7: bool = False
    language_support: List[str] = Field(default_factory=list)
    notes: Optional[MultilingualContent] = None


class Emergency(Document):
    """Emergency service document model"""
    
    # Basic Information
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    
    # Classification
    service_type: EmergencyType
    service_level: ServiceLevel
    
    # Location
    location: Location
    coverage_area: Optional[str] = None  # area they serve
    jurisdiction: Optional[str] = None
    
    # Contact Information
    contact_methods: List[ContactMethod] = Field(default_factory=list)
    emergency_number: Optional[str] = None  # primary emergency number
    non_emergency_number: Optional[str] = None
    
    # Service Details
    services_offered: List[str] = Field(default_factory=list)
    languages_supported: List[str] = Field(default_factory=list)
    response_time: Optional[str] = None  # e.g., "5-10 minutes"
    availability: str = "24/7"  # operating hours
    
    # Specialized Information
    specializations: List[str] = Field(default_factory=list)
    equipment_available: List[str] = Field(default_factory=list)
    staff_qualifications: List[str] = Field(default_factory=list)
    
    # For Embassies/Consulates
    country: Optional[str] = None  # for embassies
    embassy_services: List[str] = Field(default_factory=list)
    visa_services: bool = False
    citizen_services: bool = False
    
    # For Medical Facilities
    medical_specialties: List[str] = Field(default_factory=list)
    bed_capacity: Optional[int] = None
    trauma_center: bool = False
    insurance_accepted: List[str] = Field(default_factory=list)
    
    # Instructions and Procedures
    when_to_contact: MultilingualContent
    what_to_expect: Optional[MultilingualContent] = None
    preparation_instructions: Optional[MultilingualContent] = None
    
    # Location and Access
    landmarks_nearby: List[str] = Field(default_factory=list)
    public_transport_access: Optional[MultilingualContent] = None
    parking_available: bool = False
    wheelchair_accessible: bool = False
    
    # Status and Metadata
    is_active: bool = True
    is_verified: bool = False
    last_verified: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # SEO and Search
    keywords: List[str] = Field(default_factory=list)
    
    # Additional Data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "emergency_services"
        indexes = [
            "name.en",
            "service_type",
            "service_level",
            "location.city",
            "location.province",
            [("location.coordinates", "2dsphere")],
            "country",  # for embassies
            "is_active",
            "is_verified"
        ]
    
    def get_primary_contact(self) -> Optional[ContactMethod]:
        """Get primary contact method"""
        for contact in self.contact_methods:
            if contact.is_primary:
                return contact
        return self.contact_methods[0] if self.contact_methods else None
    
    def get_emergency_contact(self) -> Optional[str]:
        """Get emergency contact number"""
        if self.emergency_number:
            return self.emergency_number
        
        # Look for primary phone contact
        for contact in self.contact_methods:
            if contact.type == "phone" and contact.is_primary:
                return contact.value
        
        # Look for any phone contact
        for contact in self.contact_methods:
            if contact.type == "phone":
                return contact.value
        
        return None


class EmergencyCreate(BaseModel):
    """Emergency service creation model"""
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    service_type: EmergencyType
    service_level: ServiceLevel
    location: Location
    emergency_number: Optional[str] = None
    availability: str = "24/7"


class EmergencyUpdate(BaseModel):
    """Emergency service update model"""
    name: Optional[MultilingualContent] = None
    description: Optional[MultilingualContent] = None
    short_description: Optional[MultilingualContent] = None
    service_type: Optional[EmergencyType] = None
    service_level: Optional[ServiceLevel] = None
    emergency_number: Optional[str] = None
    availability: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class EmergencyResponse(BaseModel):
    """Emergency service response model"""
    id: str
    name: MultilingualContent
    description: MultilingualContent
    short_description: MultilingualContent
    service_type: EmergencyType
    service_level: ServiceLevel
    location: Location
    contact_methods: List[ContactMethod]
    emergency_number: Optional[str] = None
    services_offered: List[str]
    languages_supported: List[str]
    response_time: Optional[str] = None
    availability: str
    when_to_contact: MultilingualContent
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class EmergencySearchRequest(BaseModel):
    """Emergency service search request model"""
    service_type: Optional[EmergencyType] = None
    location: Optional[str] = None  # city or province
    coordinates: Optional[List[float]] = None  # [longitude, latitude]
    radius_km: Optional[float] = 50  # search radius
    language: Optional[str] = "en"
    urgent_only: bool = False
