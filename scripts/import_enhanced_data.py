"""
Import tourism_data_google_enhanced.json into MongoDB
Handles Google Places enhanced data with photos, ratings, reviews
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pydantic import HttpUrl

from backend.app.core.config import settings
from backend.app.models.attraction import (
    Attraction, AttractionCategory, Location, MultilingualContent, AttractionImage
)
from backend.app.models.hotel import (
    Hotel, HotelCategory, Location as HotelLocation, 
    MultilingualContent as HotelMultilingualContent
)
from backend.app.models.restaurant import (
    Restaurant, Location as RestaurantLocation, 
    MultilingualContent as RestaurantMultilingualContent
)


# Category mapping
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
}


def normalize_category(category: str) -> tuple:
    """Normalize category from database to model type and category"""
    return CATEGORY_MAP.get(category, ("attraction", AttractionCategory.NATURE))


def create_slug(name: str) -> str:
    """Create URL-friendly slug from name"""
    import re
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def extract_url(url_data: Any) -> str:
    """Extract URL string from various formats"""
    if isinstance(url_data, str):
        return url_data
    elif isinstance(url_data, dict) and '_url' in url_data:
        return url_data['_url']
    return ""


def process_images(photos: List[Any]) -> List[AttractionImage]:
    """Process photos data into AttractionImage objects"""
    images = []
    for photo in photos[:10]:  # Limit to 10 images
        if isinstance(photo, dict):
            url = extract_url(photo.get('url', ''))
            caption = photo.get('caption', '')
            if url:
                try:
                    images.append(AttractionImage(
                        url=url,
                        alt_text=MultilingualContent(en=caption, si=caption, ta=caption),
                        caption=MultilingualContent(en=caption, si=caption, ta=caption) if caption else None,
                        is_primary=len(images) == 0,  # First image is primary
                        order=len(images)
                    ))
                except Exception:
                    continue
    return images


async def import_data():
    """Import data from tourism_data_google_enhanced.json"""
    
    # Load JSON data
    json_path = Path(__file__).parent.parent / "tourism_data_google_enhanced.json"
    print(f"Loading data from {json_path}...")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        file_data = json.load(f)
    
    data = file_data.get('data', [])
    print(f"Loaded {len(data)} items from enhanced data file")
    
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
        "errors": 0,
        "updated": 0
    }
    
    for idx, item in enumerate(data, 1):
        try:
            name_en = item.get("verified_name") or item.get("name_en", "Unknown")
            name_si = item.get("name_si", "")
            name_ta = item.get("name_ta", "")
            category = item.get("category", "")
            city = item.get("city", "")
            description = item.get("description", "")
            
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
            
            # Enhanced description with Google data
            google_desc = item.get("google_description", "")
            full_desc = f"{description}\n\n{google_desc}" if google_desc else description
            
            multilingual_description = MultilingualContent(
                en=full_desc,
                si=full_desc,
                ta=full_desc
            )
            
            # Get coordinates from location object
            loc_data = item.get("location", {})
            coordinates = loc_data.get("coordinates", [80.0, 7.0])
            
            # Create location
            location = Location(
                address=item.get("formatted_address", city),
                city=city,
                province="",
                coordinates=coordinates
            )
            
            # Create slug
            slug = create_slug(name_en)
            
            # Process images
            photos = item.get("photos", [])
            images = process_images(photos)
            
            # Extract website URL
            website_url = extract_url(item.get("website", ""))
            
            # Insert based on collection type
            if collection_type == "attraction":
                # Check if exists
                exists = await Attraction.find_one(Attraction.slug == slug)
                if exists:
                    stats["skipped"] += 1
                    continue
                
                attraction = Attraction(
                    name=multilingual_name,
                    description=multilingual_description,
                    short_description=MultilingualContent(
                        en=description[:200] if description else "",
                        si=description[:200] if description else "",
                        ta=description[:200] if description else ""
                    ),
                    how_to_get_there=MultilingualContent(
                        en=f"Located in {city}",
                        si=f"{city} හි පිහිටා ඇත",
                        ta=f"{city} இல் அமைந்துள்ளது"
                    ),
                    category=model_category,
                    location=location,
                    slug=slug,
                    is_active=True,
                    is_featured=item.get("google_rating", 0) >= 4.5,
                    images=images,
                    website=website_url if website_url else None,
                    google_place_id=item.get("google_place_id"),
                    google_rating=item.get("google_rating"),
                    total_ratings=item.get("google_total_ratings", 0)
                )
                await attraction.insert()
                stats["attractions"] += 1
                
            elif collection_type == "hotel":
                # Check if exists
                exists = await Hotel.find_one(Hotel.slug == slug)
                if exists:
                    stats["skipped"] += 1
                    continue
                
                hotel = Hotel(
                    name=HotelMultilingualContent(
                        en=name_en,
                        si=name_si if name_si else name_en,
                        ta=name_ta if name_ta else name_en
                    ),
                    description=HotelMultilingualContent(
                        en=full_desc,
                        si=full_desc,
                        ta=full_desc
                    ),
                    short_description=HotelMultilingualContent(
                        en=description[:200] if description else "",
                        si=description[:200] if description else "",
                        ta=description[:200] if description else ""
                    ),
                    category=model_category,
                    location=HotelLocation(
                        address=item.get("formatted_address", city),
                        city=city,
                        province="",
                        coordinates=coordinates
                    ),
                    slug=slug,
                    is_active=True,
                    is_featured=item.get("google_rating", 0) >= 4.5,
                    rooms=[],
                    images=images,
                    website=website_url if website_url else None,
                    google_place_id=item.get("google_place_id"),
                    google_rating=item.get("google_rating"),
                    total_ratings=item.get("google_total_ratings", 0)
                )
                await hotel.insert()
                stats["hotels"] += 1
                
            elif collection_type == "restaurant":
                # Check if exists
                exists = await Restaurant.find_one(Restaurant.slug == slug)
                if exists:
                    stats["skipped"] += 1
                    continue
                
                restaurant = Restaurant(
                    name=RestaurantMultilingualContent(
                        en=name_en,
                        si=name_si if name_si else name_en,
                        ta=name_ta if name_ta else name_en
                    ),
                    description=RestaurantMultilingualContent(
                        en=full_desc,
                        si=full_desc,
                        ta=full_desc
                    ),
                    short_description=RestaurantMultilingualContent(
                        en=description[:200] if description else "",
                        si=description[:200] if description else "",
                        ta=description[:200] if description else ""
                    ),
                    location=RestaurantLocation(
                        address=item.get("formatted_address", city),
                        city=city,
                        province="",
                        coordinates=coordinates
                    ),
                    slug=slug,
                    is_active=True,
                    is_featured=item.get("google_rating", 0) >= 4.5,
                    cuisine_types=[],
                    menu_items=[],
                    images=images,
                    website=website_url if website_url else None,
                    google_place_id=item.get("google_place_id"),
                    google_rating=item.get("google_rating"),
                    total_ratings=item.get("google_total_ratings", 0)
                )
                await restaurant.insert()
                stats["restaurants"] += 1
            
            # Progress indicator
            if idx % 100 == 0:
                print(f"Processed {idx}/{len(data)} items...")
                
        except Exception as e:
            print(f"Error processing item {idx} ({item.get('name_en', 'unknown')}): {str(e)}")
            stats["errors"] += 1
            continue
    
    # Print statistics
    print("\n" + "="*50)
    print("Import Complete!")
    print("="*50)
    print(f"Attractions imported: {stats['attractions']}")
    print(f"Hotels imported: {stats['hotels']}")
    print(f"Restaurants imported: {stats['restaurants']}")
    print(f"Skipped (already exist): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total items processed: {len(data)}")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(import_data())
