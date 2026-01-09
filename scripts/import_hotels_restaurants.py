"""
Import Hotels and Restaurants Data to MongoDB
This script imports hotels and restaurants from the JSON file into the database.
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
from backend.app.models.hotel import Hotel, HotelCategory
from backend.app.models.restaurant import Restaurant, CuisineType, PriceRange
from backend.app.models.attraction import Location, MultilingualContent


# Mapping from JSON star_rating to HotelCategory enum
HOTEL_CATEGORY_MAPPING = {
    "five_star": HotelCategory.LUXURY,
    "four_star": HotelCategory.BUSINESS,
    "three_star": HotelCategory.BUDGET,
    "boutique": HotelCategory.BOUTIQUE,
    "budget": HotelCategory.BUDGET,
    "luxury": HotelCategory.LUXURY,
}


async def import_data():
    """Import hotels and restaurants from JSON file"""
    
    print("Running in DEBUG mode - not suitable for production!")
    
    # Connect to MongoDB
    mongo_url = settings.MONGODB_URL
    print(f"🔗 Connecting to MongoDB: {mongo_url}")
    
    client = AsyncIOMotorClient(mongo_url)
    database = client[settings.DATABASE_NAME]
    
    # Initialize beanie
    await init_beanie(database=database, document_models=[Hotel, Restaurant])
    print("✅ Connected to database")
    
    # Load JSON data
    json_file = project_root / "sample_tourism_data.json"
    print(f"📂 Loading data from: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hotels_data = data.get('hotels', [])
    restaurants_data = data.get('restaurants', [])
    
    print(f"📊 Found {len(hotels_data)} hotels and {len(restaurants_data)} restaurants to import")
    
    # Statistics
    stats = {
        "hotels_created": 0,
        "hotels_updated": 0,
        "hotels_skipped": 0,
        "restaurants_created": 0,
        "restaurants_updated": 0,
        "restaurants_skipped": 0,
    }
    
    # Import hotels
    print("\n🏨 Importing Hotels...")
    for hotel_data in hotels_data:
        try:
            name_en = hotel_data.get('name', {}).get('en', '')
            name_si = hotel_data.get('name', {}).get('si', '')
            name_ta = hotel_data.get('name', {}).get('ta', '')
            
            # Create multilingual content
            name = MultilingualContent(
                en=name_en,
                si=name_si,
                ta=name_ta
            )
            
            desc_data = hotel_data.get('description', {})
            description = MultilingualContent(
                en=desc_data.get('en', ''),
                si=desc_data.get('si', ''),
                ta=desc_data.get('ta', '')
            )
            
            # Create location
            loc_data = hotel_data.get('location', {})
            coords_data = loc_data.get('coordinates', {})
            
            location = Location(
                address=loc_data.get('address', ''),
                city=loc_data.get('city', 'Colombo'),
                province='Western',  # Default province
                coordinates=[
                    coords_data.get('longitude', 0.0),
                    coords_data.get('latitude', 0.0)
                ]
            )
            
            # Get category
            star_rating = hotel_data.get('star_rating', 'budget')
            category = HOTEL_CATEGORY_MAPPING.get(star_rating, HotelCategory.BUDGET)
            
            # Get contact info
            contact_data = hotel_data.get('contact', {})
            
            # Check if already exists
            existing = await Hotel.find_one(Hotel.name.en == name_en)
            
            if existing:
                # Update existing record
                existing.name = name
                existing.description = description
                existing.location = location
                existing.category = category
                existing.rating = hotel_data.get('rating', 0.0)
                existing.price_range = hotel_data.get('price_range', {})
                existing.amenities = hotel_data.get('amenities', [])
                existing.contact_phone = contact_data.get('phone')
                existing.contact_email = contact_data.get('email')
                existing.website = contact_data.get('website')
                existing.room_count = hotel_data.get('room_count')
                existing.check_in_time = hotel_data.get('check_in')
                existing.check_out_time = hotel_data.get('check_out')
                existing.is_active = hotel_data.get('is_active', True)
                existing.updated_at = datetime.utcnow()
                await existing.save()
                stats["hotels_updated"] += 1
                print(f"  🔄 Updated: {name_en}")
            else:
                # Create new record
                hotel = Hotel(
                    name=name,
                    description=description,
                    location=location,
                    category=category,
                    rating=hotel_data.get('rating', 0.0),
                    price_range=hotel_data.get('price_range', {}),
                    amenities=hotel_data.get('amenities', []),
                    contact_phone=contact_data.get('phone'),
                    contact_email=contact_data.get('email'),
                    website=contact_data.get('website'),
                    room_count=hotel_data.get('room_count'),
                    check_in_time=hotel_data.get('check_in'),
                    check_out_time=hotel_data.get('check_out'),
                    is_active=hotel_data.get('is_active', True),
                )
                await hotel.insert()
                stats["hotels_created"] += 1
                print(f"  ✅ Created: {name_en}")
                
        except Exception as e:
            print(f"  ❌ Error processing {hotel_data.get('name', {}).get('en', 'Unknown')}: {e}")
            stats["hotels_skipped"] += 1
    
    # Import restaurants
    print("\n🍽️  Importing Restaurants...")
    for rest_data in restaurants_data:
        try:
            name_en = rest_data.get('name', {}).get('en', '')
            name_si = rest_data.get('name', {}).get('si', '')
            name_ta = rest_data.get('name', {}).get('ta', '')
            
            # Create multilingual content
            name = MultilingualContent(
                en=name_en,
                si=name_si,
                ta=name_ta
            )
            
            desc_data = rest_data.get('description', {})
            description = MultilingualContent(
                en=desc_data.get('en', ''),
                si=desc_data.get('si', ''),
                ta=desc_data.get('ta', '')
            )
            
            # Create location
            loc_data = rest_data.get('location', {})
            coords_data = loc_data.get('coordinates', {})
            
            location = Location(
                address=loc_data.get('address', ''),
                city=loc_data.get('city', 'Colombo'),
                province='Western',  # Default province
                coordinates=[
                    coords_data.get('longitude', 0.0),
                    coords_data.get('latitude', 0.0)
                ]
            )
            
            # Get cuisine types
            cuisine_types_str = rest_data.get('cuisine', [])
            cuisine_types = []
            for cuisine in cuisine_types_str:
                # Try to map to CuisineType enum
                try:
                    cuisine_types.append(CuisineType[cuisine.upper().replace(' ', '_')])
                except:
                    # If not found, use OTHER
                    cuisine_types.append(CuisineType.OTHER)
            
            if not cuisine_types:
                cuisine_types = [CuisineType.OTHER]
            
            # Get price range
            price_range_str = rest_data.get('price_range', 'moderate')
            try:
                price_range = PriceRange[price_range_str.upper()]
            except:
                price_range = PriceRange.MODERATE
            
            # Get contact info
            contact_data = rest_data.get('contact', {})
            
            # Check if already exists
            existing = await Restaurant.find_one(Restaurant.name.en == name_en)
            
            if existing:
                # Update existing record
                existing.name = name
                existing.description = description
                existing.location = location
                existing.cuisine_types = cuisine_types
                existing.price_range = price_range
                existing.rating = rest_data.get('rating', 0.0)
                existing.contact_phone = contact_data.get('phone')
                existing.contact_email = contact_data.get('email')
                existing.website = contact_data.get('website')
                existing.seating_capacity = rest_data.get('seating_capacity')
                existing.has_outdoor_seating = rest_data.get('outdoor_seating', False)
                existing.has_delivery = rest_data.get('delivery', False)
                existing.has_takeaway = rest_data.get('takeaway', False)
                existing.is_active = rest_data.get('is_active', True)
                existing.updated_at = datetime.utcnow()
                await existing.save()
                stats["restaurants_updated"] += 1
                print(f"  🔄 Updated: {name_en}")
            else:
                # Create new record
                restaurant = Restaurant(
                    name=name,
                    description=description,
                    location=location,
                    cuisine_types=cuisine_types,
                    price_range=price_range,
                    rating=rest_data.get('rating', 0.0),
                    contact_phone=contact_data.get('phone'),
                    contact_email=contact_data.get('email'),
                    website=contact_data.get('website'),
                    seating_capacity=rest_data.get('seating_capacity'),
                    has_outdoor_seating=rest_data.get('outdoor_seating', False),
                    has_delivery=rest_data.get('delivery', False),
                    has_takeaway=rest_data.get('takeaway', False),
                    is_active=rest_data.get('is_active', True),
                )
                await restaurant.insert()
                stats["restaurants_created"] += 1
                print(f"  ✅ Created: {name_en}")
                
        except Exception as e:
            print(f"  ❌ Error processing {rest_data.get('name', {}).get('en', 'Unknown')}: {e}")
            stats["restaurants_skipped"] += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print("=" * 50)
    print(f"  Hotels:")
    print(f"    Created: {stats['hotels_created']}")
    print(f"    Updated: {stats['hotels_updated']}")
    print(f"    Skipped: {stats['hotels_skipped']}")
    print(f"  Restaurants:")
    print(f"    Created: {stats['restaurants_created']}")
    print(f"    Updated: {stats['restaurants_updated']}")
    print(f"    Skipped: {stats['restaurants_skipped']}")
    print("=" * 50)
    print("\n✅ Import complete!")


if __name__ == "__main__":
    asyncio.run(import_data())
