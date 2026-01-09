"""
Check database contents and verify duplicate prevention
"""

import sys
import asyncio
from pathlib import Path
from collections import Counter

sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.app.core.config import settings
from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant


async def check_database():
    """Check database contents"""
    
    # Initialize database connection
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[Attraction, Hotel, Restaurant]
    )
    print("Connected!\n")
    
    # Count documents
    attraction_count = await Attraction.count()
    hotel_count = await Hotel.count()
    restaurant_count = await Restaurant.count()
    
    print("="*60)
    print("DATABASE CONTENTS")
    print("="*60)
    print(f"Attractions: {attraction_count:,}")
    print(f"Hotels: {hotel_count:,}")
    print(f"Restaurants: {restaurant_count:,}")
    print(f"Total: {attraction_count + hotel_count + restaurant_count:,}")
    print("="*60)
    
    # Check for duplicates by slug
    print("\nCHECKING FOR DUPLICATES...")
    
    # Get raw data to avoid validation errors
    db = client[settings.DATABASE_NAME]
    attractions_raw = await db.attractions.find({}).to_list(None)
    
    # Count those with slugs (new format)
    slugs = [a.get('slug') for a in attractions_raw if a.get('slug')]
    slug_counts = Counter(slugs)
    duplicates = {slug: count for slug, count in slug_counts.items() if count > 1}
    
    # Count old vs new format
    old_format = sum(1 for a in attractions_raw if not a.get('slug'))
    new_format = sum(1 for a in attractions_raw if a.get('slug'))
    print(f"\nData format breakdown:")
    print(f"  Old format (no slug): {old_format:,}")
    print(f"  New format (with slug): {new_format:,}")
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate slugs in Attractions:")
        for slug, count in list(duplicates.items())[:5]:
            print(f"   - {slug}: {count} entries")
    else:
        print("\n✅ No duplicate slugs found in Attractions")
    
    # Check hotels
    hotels_raw = await db.hotels.find({}).to_list(None)
    hotel_slugs = [h.get('slug') for h in hotels_raw if h.get('slug')]
    hotel_slug_counts = Counter(hotel_slugs)
    hotel_duplicates = {slug: count for slug, count in hotel_slug_counts.items() if count > 1}
    
    if hotel_duplicates:
        print(f"⚠️  Found {len(hotel_duplicates)} duplicate slugs in Hotels:")
        for slug, count in list(hotel_duplicates.items())[:5]:
            print(f"   - {slug}: {count} entries")
    else:
        print("✅ No duplicate slugs found in Hotels")
    
    # Show sample data from new format
    print("\n" + "="*60)
    print("SAMPLE NEW FORMAT ATTRACTIONS (first 5)")
    print("="*60)
    new_format_attractions = [a for a in attractions_raw if a.get('slug')][:5]
    for attraction in new_format_attractions:
        name = attraction.get('name', {})
        if isinstance(name, dict):
            name_en = name.get('en', 'Unknown')
        else:
            name_en = str(name)
        print(f"\n{name_en}")
        print(f"  Category: {attraction.get('category')}")
        location = attraction.get('location', {})
        print(f"  City: {location.get('city') if isinstance(location, dict) else 'N/A'}")
        print(f"  Slug: {attraction.get('slug')}")
        print(f"  Featured: {attraction.get('is_featured')}")
    
    # Category breakdown
    print("\n" + "="*60)
    print("ATTRACTIONS BY CATEGORY")
    print("="*60)
    categories = [a.get('category') for a in attractions_raw if a.get('category')]
    category_counts = Counter(categories)
    for category, count in category_counts.most_common():
        print(f"{category}: {count:,}")
    
    # Featured attractions
    featured_count = sum(1 for a in attractions_raw if a.get('is_featured'))
    print(f"\n✨ Featured attractions: {featured_count}")


if __name__ == "__main__":
    asyncio.run(check_database())
