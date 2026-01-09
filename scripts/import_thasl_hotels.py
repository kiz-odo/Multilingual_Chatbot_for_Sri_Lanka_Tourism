"""
Import THASL Hotels Data into MongoDB
======================================

Transforms and imports hotels from thasl_hotels.json into database
"""

import asyncio
import json
import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.core.database import init_database
from backend.app.models.hotel import Hotel


def clean_phone(phone_str):
    """Clean and format phone number"""
    if not phone_str:
        return None
    # Remove extra spaces, format consistently
    phone = phone_str.strip().replace(" ", "")
    # Add +94 if not present
    if not phone.startswith("+"):
        if phone.startswith("0"):
            phone = "+94" + phone[1:]
        else:
            phone = "+94" + phone
    return phone


def determine_category(classification):
    """Map classification to HotelCategory enum"""
    classification = classification.lower()
    
    if "boutique" in classification:
        return "boutique"
    elif "resort" in classification or "ayurvedic" in classification:
        return "resort"
    elif "villa" in classification:
        return "villa"
    elif "guest" in classification or "rest house" in classification:
        return "guesthouse"
    elif "eco" in classification:
        return "eco_lodge"
    elif "apartment" in classification:
        return "apartment"
    elif "luxury" in classification:
        return "luxury"
    elif "business" in classification:
        return "business"
    else:
        return "resort"  # default


def determine_star_rating(classification):
    """Extract star rating from classification"""
    classification = classification.lower()
    
    if "5 star" in classification or "five star" in classification:
        return "5"
    elif "4 star" in classification or "four star" in classification:
        return "4"
    elif "3 star" in classification or "three star" in classification:
        return "3"
    elif "2 star" in classification or "two star" in classification:
        return "2"
    elif "1 star" in classification or "one star" in classification:
        return "1"
    else:
        return "unrated"


def extract_city(address, province):
    """Extract city from address"""
    # Common cities in Sri Lanka
    cities = [
        "Colombo", "Kandy", "Galle", "Negombo", "Bentota", "Tangalle",
        "Dambulla", "Nuwara Eliya", "Ella", "Trincomalee", "Jaffna",
        "Hikkaduwa", "Unawatuna", "Mirissa", "Arugam Bay", "Anuradhapura",
        "Polonnaruwa", "Sigiriya", "Matara", "Badulla", "Ratnapura",
        "Kalutara", "Beruwala", "Ahungalla", "Koggala", "Weligama"
    ]
    
    address_upper = address.upper()
    for city in cities:
        if city.upper() in address_upper:
            return city
    
    # Extract from province if not found in address
    if "Western" in province:
        return "Colombo"
    elif "Southern" in province:
        return "Galle"
    elif "Central" in province:
        return "Kandy"
    elif "Northern" in province:
        return "Jaffna"
    elif "Eastern" in province:
        return "Trincomalee"
    elif "North Central" in province:
        return "Anuradhapura"
    elif "North Western" in province:
        return "Kurunegala"
    elif "Sabaragamuwa" in province:
        return "Ratnapura"
    elif "Uva" in province:
        return "Badulla"
    
    return "Sri Lanka"


def parse_coordinates(city):
    """Get approximate coordinates for city"""
    coords_map = {
        "Colombo": [6.9271, 79.8612],
        "Kandy": [7.2906, 80.6337],
        "Galle": [6.0535, 80.2210],
        "Negombo": [7.2094, 79.8358],
        "Bentota": [6.4256, 79.9956],
        "Tangalle": [6.0235, 80.7958],
        "Dambulla": [7.8600, 80.6515],
        "Nuwara Eliya": [6.9497, 80.7891],
        "Ella": [6.8667, 81.0467],
        "Trincomalee": [8.5874, 81.2152],
        "Hikkaduwa": [6.1408, 80.1000],
        "Unawatuna": [6.0100, 80.2480],
        "Mirissa": [5.9463, 80.4500],
        "Sigiriya": [7.9565, 80.7597],
        "Anuradhapura": [8.3114, 80.4037],
    }
    
    return coords_map.get(city, [7.8731, 80.7718])  # Default center of Sri Lanka


def transform_hotel(hotel_data):
    """Transform THASL hotel data to match our model"""
    
    name = hotel_data["name"].title()
    classification = hotel_data.get("classification", "Hotel")
    address = hotel_data.get("address", "")
    province = hotel_data.get("province", "")
    
    # Extract city
    city = extract_city(address, province)
    coords = parse_coordinates(city)
    
    # Clean phone
    phone = clean_phone(hotel_data.get("telephone"))
    
    # Email
    email = hotel_data.get("email", "").strip() or None
    
    # Website - fix format
    website = hotel_data.get("website", "").strip()
    if website:
        if not website.startswith("http"):
            website = "https://" + website
        # Remove trailing slashes and clean
        website = website.rstrip("/")
    else:
        website = None
    
    # Category and rating
    category = determine_category(classification)
    star_rating = determine_star_rating(classification)
    
    # Number of rooms
    try:
        total_rooms = int(hotel_data.get("number_of_rooms", "0"))
    except:
        total_rooms = 0
    
    # Create hotel document
    hotel_doc = {
        "name": {
            "en": name,
            "si": name,  # Can be translated later
            "ta": name
        },
        "description": {
            "en": f"{name} is a {classification.lower()} located in {city}, Sri Lanka. {classification} offering comfortable accommodation with excellent service.",
            "si": f"{name} {city} හි පිහිටි {classification.lower()} ය.",
            "ta": f"{name} {city} இல் அமைந்துள்ள {classification.lower()} ஆகும்."
        },
        "short_description": {
            "en": f"{classification} in {city}",
            "si": f"{city} හි {classification}",
            "ta": f"{city} இல் {classification}"
        },
        "category": category,
        "star_rating": star_rating,
        "location": {
            "city": city,
            "province": province,
            "address": address,
            "coordinates": coords
        },
        "phone": phone,
        "email": email,
        "website": website,
        "total_rooms": total_rooms,
        "slug": name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", ""),
        "is_active": True,
        "popularity_score": 50,  # Default
        "amenities": ["wifi", "parking", "restaurant"] if total_rooms > 20 else ["wifi"],
        "images": [],
        "rooms": []
    }
    
    return hotel_doc


async def import_hotels():
    """Import hotels into database"""
    
    print("\n🏨 Importing THASL Hotels Data")
    print("=" * 60)
    
    # Initialize database
    try:
        await init_database()
        print("✅ Database connection established\n")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # Load THASL data
    data_file = project_root / "scripts" / "thasl_hotels.json"
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            hotels_data = json.load(f)
        print(f"✅ Loaded {len(hotels_data)} hotels from file\n")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Import hotels
    imported = 0
    skipped = 0
    errors = 0
    
    print("🔄 Processing hotels...")
    print("-" * 60)
    
    for hotel_data in hotels_data:
        try:
            # Transform data
            hotel_doc = transform_hotel(hotel_data)
            
            # Check if already exists
            existing = await Hotel.find_one(
                Hotel.name.en == hotel_doc["name"]["en"]
            )
            
            if existing:
                skipped += 1
                continue
            
            # Create hotel
            hotel = Hotel(**hotel_doc)
            await hotel.save()
            imported += 1
            
            if imported % 10 == 0:
                print(f"  ✅ Imported {imported} hotels...")
            
        except Exception as e:
            errors += 1
            print(f"  ❌ Error importing {hotel_data.get('name', 'Unknown')}: {str(e)[:100]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Import Summary")
    print("=" * 60)
    print(f"✅ Imported: {imported}")
    print(f"⏭️  Skipped:  {skipped} (already exist)")
    print(f"❌ Errors:   {errors}")
    print("=" * 60)
    
    if imported > 0:
        print(f"\n✅ Successfully imported {imported} hotels!")
        print("🚀 Run tests to verify: python -m pytest backend/tests/")
    elif skipped > 0:
        print("\n⚠️  All hotels already in database")
    else:
        print("\n❌ Import failed")


if __name__ == "__main__":
    asyncio.run(import_hotels())
