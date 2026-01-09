"""
Import Emergency Services Data to MongoDB
This script imports emergency services from the JSON file into the database.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.app.core.config import settings
from backend.app.models.emergency import (
    Emergency, 
    EmergencyType, 
    ServiceLevel, 
    ContactMethod
)
from backend.app.models.attraction import Location, MultilingualContent


# Mapping from JSON type to EmergencyType enum
TYPE_MAPPING = {
    "Embassy": EmergencyType.EMBASSY,
    "Hospital": EmergencyType.HOSPITAL,
    "Police": EmergencyType.POLICE,
    "Fire": EmergencyType.FIRE,
    "Ambulance": EmergencyType.AMBULANCE,
}

# Service level mapping based on type
SERVICE_LEVEL_MAPPING = {
    "Embassy": ServiceLevel.INFORMATION,
    "Hospital": ServiceLevel.EMERGENCY,
    "Police": ServiceLevel.EMERGENCY,
    "Fire": ServiceLevel.EMERGENCY,
    "Ambulance": ServiceLevel.EMERGENCY,
}


def get_city_from_location(location: str) -> str:
    """Extract city name from location string"""
    # Common Sri Lankan cities
    cities = [
        "Colombo", "Kandy", "Galle", "Jaffna", "Negombo", "Nuwara Eliya",
        "Anuradhapura", "Matara", "Ratnapura", "Trincomalee", "Batticaloa",
        "Badulla", "Kurunegala", "Kalutara", "Moratuwa", "Dehiwala",
        "Chilaw", "Vavuniya", "Gampaha", "Peradeniya", "Puttalam",
        "Maharagama", "Homagama", "Wattala", "Matale", "Nawalapitiya",
        "Gampola", "Balapitiya", "Elpitiya", "Udugama", "Kalawanchikudi"
    ]
    
    for city in cities:
        if city.lower() in location.lower():
            return city
    
    # Check for Colombo districts
    if "Colombo" in location or any(f"Colombo {i:02d}" in location for i in range(1, 16)):
        return "Colombo"
    
    # Default to location if no city found
    return location.split(",")[0].strip() if "," in location else location


def get_province_from_city(city: str) -> str:
    """Get province from city name"""
    province_mapping = {
        "Colombo": "Western",
        "Moratuwa": "Western",
        "Dehiwala": "Western",
        "Wattala": "Western",
        "Homagama": "Western",
        "Gampaha": "Western",
        "Negombo": "Western",
        "Kalutara": "Western",
        "Kandy": "Central",
        "Peradeniya": "Central",
        "Gampola": "Central",
        "Nawalapitiya": "Central",
        "Matale": "Central",
        "Nuwara Eliya": "Central",
        "Galle": "Southern",
        "Matara": "Southern",
        "Balapitiya": "Southern",
        "Elpitiya": "Southern",
        "Udugama": "Southern",
        "Ahangama": "Southern",
        "Ahungalla": "Southern",
        "Akmeemana": "Southern",
        "Akuressa": "Southern",
        "Jaffna": "Northern",
        "Vavuniya": "Northern",
        "Anuradhapura": "North Central",
        "Trincomalee": "Eastern",
        "Batticaloa": "Eastern",
        "Akkaraipattu": "Eastern",
        "Kalawanchikudi": "Eastern",
        "Badulla": "Uva",
        "Ratnapura": "Sabaragamuwa",
        "Kurunegala": "North Western",
        "Chilaw": "North Western",
        "Puttalam": "North Western",
        "Alawwa": "North Western",
        "Maharagama": "Western",
    }
    return province_mapping.get(city, "Western")  # Default to Western


async def import_emergency_services():
    """Import emergency services from JSON to database"""
    
    # Connect to MongoDB
    print(f"🔗 Connecting to MongoDB: {settings.MONGODB_URL}")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize Beanie
    await init_beanie(database=database, document_models=[Emergency])
    print("✅ Connected to database")
    
    # Load JSON data
    json_file = project_root / "emergency_services_sri_lanka.json"
    print(f"📂 Loading data from: {json_file}")
    
    with open(json_file, "r", encoding="utf-8") as f:
        services_data = json.load(f)
    
    print(f"📊 Found {len(services_data)} emergency services to import")
    
    # Statistics
    stats = {
        "Embassy": 0,
        "Hospital": 0,
        "Police": 0,
        "Fire": 0,
        "total": 0,
        "skipped": 0,
        "updated": 0,
        "created": 0
    }
    
    for service in services_data:
        try:
            service_type = service.get("type", "Police")
            name_en = service.get("name_en", "")
            name_si = service.get("name_si", "")
            location_str = service.get("location", "")
            phone = service.get("phone", "")
            description = service.get("description", "")
            
            # Get city and province
            city = get_city_from_location(location_str)
            province = get_province_from_city(city)
            
            # Create multilingual content
            name = MultilingualContent(
                en=name_en,
                si=name_si,
                ta=name_en  # Use English as fallback for Tamil
            )
            
            desc = MultilingualContent(
                en=description,
                si=description,  # Could be translated later
                ta=description
            )
            
            short_desc = MultilingualContent(
                en=description[:100] if len(description) > 100 else description,
                si=description[:100] if len(description) > 100 else description,
                ta=description[:100] if len(description) > 100 else description
            )
            
            when_to_contact = MultilingualContent(
                en=f"Contact {name_en} for {service_type.lower()} services.",
                si=f"{name_si} සම්බන්ධ කර ගන්න.",
                ta=f"Contact {name_en} for {service_type.lower()} services."
            )
            
            # Create location
            location = Location(
                address=location_str,
                city=city,
                province=province,
                coordinates=[0.0, 0.0]  # [longitude, latitude] - TODO: Add geocoding
            )
            
            # Create contact method
            contact_methods = []
            if phone:
                # Handle multiple phone numbers
                phones = phone.replace(" / ", ",").replace("/", ",").split(",")
                for i, p in enumerate(phones):
                    p = p.strip()
                    if p:
                        contact_methods.append(ContactMethod(
                            type="phone",
                            value=p,
                            is_primary=(i == 0),
                            is_24_7=(service_type in ["Police", "Fire", "Ambulance", "Hospital"]),
                            language_support=["en", "si", "ta"]
                        ))
            
            # Determine emergency type and service level
            emergency_type = TYPE_MAPPING.get(service_type, EmergencyType.POLICE)
            service_level = SERVICE_LEVEL_MAPPING.get(service_type, ServiceLevel.STANDARD)
            
            # Check if already exists
            existing = await Emergency.find_one(
                Emergency.name.en == name_en
            )
            
            if existing:
                # Update existing record
                existing.name = name
                existing.description = desc
                existing.short_description = short_desc
                existing.location = location
                existing.contact_methods = contact_methods
                existing.emergency_number = phone.split("/")[0].strip() if phone else None
                existing.updated_at = datetime.utcnow()
                await existing.save()
                stats["updated"] += 1
                print(f"  🔄 Updated: {name_en}")
            else:
                # Create new record
                emergency = Emergency(
                    name=name,
                    description=desc,
                    short_description=short_desc,
                    service_type=emergency_type,
                    service_level=service_level,
                    location=location,
                    contact_methods=contact_methods,
                    emergency_number=phone.split("/")[0].strip() if phone else None,
                    non_emergency_number=phone.split("/")[1].strip() if "/" in phone and len(phone.split("/")) > 1 else None,
                    services_offered=[f"{service_type} services"],
                    languages_supported=["en", "si", "ta"],
                    availability="24/7" if service_type in ["Police", "Fire", "Hospital"] else "Business hours",
                    when_to_contact=when_to_contact,
                    is_active=True,
                    is_verified=True,
                    last_verified=datetime.utcnow(),
                    keywords=[service_type.lower(), city.lower(), name_en.lower()],
                    country=name_en.replace(" Embassy", "").replace(" High Commission", "") if service_type == "Embassy" else None,
                    citizen_services=(service_type == "Embassy"),
                    visa_services=(service_type == "Embassy"),
                    trauma_center=(service_type == "Hospital"),
                    metadata={
                        "source": "emergency_services_sri_lanka.json",
                        "imported_at": datetime.utcnow().isoformat()
                    }
                )
                
                await emergency.insert()
                stats["created"] += 1
                print(f"  ✅ Created: {name_en}")
            
            stats[service_type] = stats.get(service_type, 0) + 1
            stats["total"] += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {service.get('name_en', 'Unknown')}: {e}")
            stats["skipped"] += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print("=" * 50)
    print(f"  Total processed: {stats['total']}")
    print(f"  Created: {stats['created']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped: {stats['skipped']}")
    print("-" * 50)
    print(f"  Embassies: {stats.get('Embassy', 0)}")
    print(f"  Hospitals: {stats.get('Hospital', 0)}")
    print(f"  Police: {stats.get('Police', 0)}")
    print(f"  Fire: {stats.get('Fire', 0)}")
    print("=" * 50)
    
    # Close connection
    client.close()
    print("\n✅ Import complete!")


if __name__ == "__main__":
    asyncio.run(import_emergency_services())
