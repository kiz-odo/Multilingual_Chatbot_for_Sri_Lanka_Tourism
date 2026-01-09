"""
Import master_database.json into MongoDB
Maps simple JSON structure to appropriate model collections
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.app.core.config import settings
from backend.app.models.attraction import (
    Attraction, AttractionCategory, Location, MultilingualContent
)
from backend.app.models.hotel import (
    Hotel, HotelCategory, Location as HotelLocation, MultilingualContent as HotelMultilingualContent
)
from backend.app.models.restaurant import (
    Restaurant, Location as RestaurantLocation, MultilingualContent as RestaurantMultilingualContent
)


# Category mapping from master_database.json to model categories
CATEGORY_MAP = {
    "Beach": ("attraction", AttractionCategory.BEACH),
    "Wildlife": ("attraction", AttractionCategory.WILDLIFE),
    "Religious": ("attraction", AttractionCategory.TEMPLE),
    "Archaeological": ("attraction", AttractionCategory.HISTORICAL),
    "Nature": ("attraction", AttractionCategory.NATURE),
    "Mountain": ("attraction", AttractionCategory.MOUNTAIN),
    "Historical": ("attraction", AttractionCategory.HISTORICAL),
    "Hotel": ("hotel", HotelCategory.BUDGET),
    "Restaurant": ("restaurant", None),
    "Shop": ("attraction", AttractionCategory.CITY),
    "Hospital": ("attraction", AttractionCategory.CITY),
    "Police": ("attraction", AttractionCategory.CITY),
    "Post": ("attraction", AttractionCategory.CITY),
    "School": ("attraction", AttractionCategory.CITY),
    "Market": ("attraction", AttractionCategory.CITY),
}


def normalize_category(category: str) -> tuple:
    """Normalize category from master database to model type and category"""
    return CATEGORY_MAP.get(category, ("attraction", AttractionCategory.NATURE))


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name"""
    import re
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


async def import_data():
    """Import data from master_database.json"""
    
    # Load JSON data
    json_path = Path(__file__).parent.parent / "master_database.json"
    print(f"Loading data from {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items from master_database.json")
    
    # Initialize database connection
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[Attraction, Hotel, Restaurant]
    )
    print("Connected to MongoDB!")
    
    # Statistics
    stats = {
        "attractions": 0,
        "hotels": 0,
        "restaurants": 0,
        "skipped": 0,
        "errors": 0
    }
    
    for idx, item in enumerate(data, 1):
        try:
            name_en = item.get("name_en", "Unknown")
            name_si = item.get("name_si", "")
            name_ta = item.get("name_ta", "")
            category = item.get("category", "")
            city = item.get("city", "")
            description = item.get("description", "")
            coordinates = item.get("coordinates", [])
            
            # Skip if essential data missing
            if not name_en or not category:
                stats["skipped"] += 1
                continue
            
            # Determine collection type and category
            collection_type, model_category = normalize_category(category)
            
            # Create multilingual content
            multilingual_name = MultilingualContent(
                en=name_en,
                si=name_si if name_si else name_en,
                ta=name_ta if name_ta else name_en
            )
            
            multilingual_description = MultilingualContent(
                en=description,
                si=description,
                ta=description
            )
            
            # Default how_to_get_there content
            how_to_get_there = MultilingualContent(
                en=f"Located in {city}",
                si=f"{city} හි පිහිටා ඇත",
                ta=f"{city} இல் அமைந்துள்ளது"
            )
            
            # Create location
            location = Location(
                address=city,
                city=city,
                province="",
                coordinates=coordinates if len(coordinates) == 2 else [80.0, 7.0]  # Default Sri Lanka center
            )
            
            # Create slug
            slug = create_slug(name_en)
            
            # Insert based on collection type
            if collection_type == "attraction":
                # Check if exists
                exists = await Attraction.find_one(Attraction.slug == slug)
                if exists:
                    continue
                
                attraction = Attraction(
                    name=multilingual_name,
                    description=multilingual_description,
                    short_description=multilingual_description,
                    how_to_get_there=how_to_get_there,
                    category=model_category,
                    location=location,
                    slug=slug,
                    is_active=True,
                    is_featured=False
                )
                await attraction.insert()
                stats["attractions"] += 1
                
            elif collection_type == "hotel":
                # Check if exists
                exists = await Hotel.find_one(Hotel.slug == slug)
                if exists:
                    continue
                
                hotel = Hotel(
                    name=multilingual_name,
                    description=multilingual_description,
                    short_description=multilingual_description,
                    category=model_category,
                    location=location,
                    slug=slug,
                    is_active=True,
                    is_featured=False,
                    rooms=[]
                )
                await hotel.insert()
                stats["hotels"] += 1
                
            elif collection_type == "restaurant":
                # Check if exists
                exists = await Restaurant.find_one(Restaurant.slug == slug)
                if exists:
                    continue
                
                restaurant = Restaurant(
                    name=multilingual_name,
                    description=multilingual_description,
                    short_description=multilingual_description,
                    location=location,
                    slug=slug,
                    is_active=True,
                    is_featured=False,
                    cuisine_types=[],
                    menu_items=[]
                )
                await restaurant.insert()
                stats["restaurants"] += 1
            
            # Progress indicator
            if idx % 100 == 0:
                print(f"Processed {idx}/{len(data)} items...")
                
        except Exception as e:
            print(f"Error processing item {idx} ({name_en}): {str(e)}")
            stats["errors"] += 1
            continue
    
    # Print statistics
    print("\n" + "="*50)
    print("Import Complete!")
    print("="*50)
    print(f"Attractions imported: {stats['attractions']}")
    print(f"Hotels imported: {stats['hotels']}")
    print(f"Restaurants imported: {stats['restaurants']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total: {len(data)}")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(import_data())
