"""
Check database for existing hotels and restaurants
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.app.core.config import settings
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant


async def check_data():
    """Check existing hotels and restaurants in database"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize beanie
    await init_beanie(database=database, document_models=[Hotel, Restaurant])
    
    # Count hotels
    hotel_count = await Hotel.count()
    print(f"🏨 Hotels in database: {hotel_count}")
    
    if hotel_count > 0:
        print("\nSample Hotels:")
        hotels = await Hotel.find().limit(3).to_list()
        for hotel in hotels:
            print(f"  - {hotel.name.en}")
    
    # Count restaurants
    restaurant_count = await Restaurant.count()
    print(f"\n🍽️  Restaurants in database: {restaurant_count}")
    
    if restaurant_count > 0:
        print("\nSample Restaurants:")
        restaurants = await Restaurant.find().limit(3).to_list()
        for restaurant in restaurants:
            print(f"  - {restaurant.name.en}")


if __name__ == "__main__":
    asyncio.run(check_data())
