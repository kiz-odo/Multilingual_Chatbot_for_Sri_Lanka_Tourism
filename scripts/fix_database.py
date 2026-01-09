#!/usr/bin/env python3
"""
Database Fix Script
Fixes image URL validation errors in attractions and other collections
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_image_urls():
    """Fix image URL validation errors"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    logger.info("=" * 60)
    logger.info("Starting Database Fix")
    logger.info("=" * 60)
    
    # Fix attractions images
    logger.info("\n1. Fixing Attractions image URLs...")
    attractions_collection = db.attractions
    
    # Find all attractions with invalid image URLs
    attractions = await attractions_collection.find({}).to_list(length=None)
    fixed_count = 0
    
    for attraction in attractions:
        needs_update = False
        images = attraction.get('images', [])
        fixed_images = []
        
        for img in images:
            if isinstance(img, dict):
                # Fix URL field if it's not a string
                if 'url' in img:
                    if not isinstance(img['url'], str):
                        img['url'] = str(img['url']) if img['url'] else ""
                        needs_update = True
                else:
                    # Add missing URL field
                    img['url'] = ""
                    needs_update = True
                
                # Ensure other required fields
                if 'caption' not in img:
                    img['caption'] = {"en": "", "si": "", "ta": ""}
                if 'is_primary' not in img:
                    img['is_primary'] = False
                    
                fixed_images.append(img)
        
        if needs_update:
            await attractions_collection.update_one(
                {"_id": attraction["_id"]},
                {"$set": {"images": fixed_images}}
            )
            fixed_count += 1
    
    logger.info(f"   ✅ Fixed {fixed_count} attractions")
    
    # Fix hotels images
    logger.info("\n2. Fixing Hotels image URLs...")
    hotels_collection = db.hotels
    hotels = await hotels_collection.find({}).to_list(length=None)
    fixed_hotels = 0
    
    for hotel in hotels:
        needs_update = False
        images = hotel.get('images', [])
        fixed_images = []
        
        for img in images:
            if isinstance(img, dict):
                if 'url' in img:
                    if not isinstance(img['url'], str):
                        img['url'] = str(img['url']) if img['url'] else ""
                        needs_update = True
                else:
                    img['url'] = ""
                    needs_update = True
                    
                if 'caption' not in img:
                    img['caption'] = {"en": "", "si": "", "ta": ""}
                if 'is_primary' not in img:
                    img['is_primary'] = False
                    
                fixed_images.append(img)
        
        # Fix room images
        rooms = hotel.get('rooms', [])
        for room in rooms:
            room_images = room.get('images', [])
            fixed_room_images = []
            for img in room_images:
                if isinstance(img, dict):
                    if 'url' in img:
                        if not isinstance(img['url'], str):
                            img['url'] = str(img['url']) if img['url'] else ""
                            needs_update = True
                    else:
                        img['url'] = ""
                        needs_update = True
                    fixed_room_images.append(img)
            room['images'] = fixed_room_images
        
        if needs_update:
            await hotels_collection.update_one(
                {"_id": hotel["_id"]},
                {"$set": {"images": fixed_images, "rooms": rooms}}
            )
            fixed_hotels += 1
    
    logger.info(f"   ✅ Fixed {fixed_hotels} hotels")
    
    # Fix restaurants images
    logger.info("\n3. Fixing Restaurants image URLs...")
    restaurants_collection = db.restaurants
    restaurants = await restaurants_collection.find({}).to_list(length=None)
    fixed_restaurants = 0
    
    for restaurant in restaurants:
        needs_update = False
        images = restaurant.get('images', [])
        fixed_images = []
        
        for img in images:
            if isinstance(img, dict):
                if 'url' in img:
                    if not isinstance(img['url'], str):
                        img['url'] = str(img['url']) if img['url'] else ""
                        needs_update = True
                else:
                    img['url'] = ""
                    needs_update = True
                    
                if 'caption' not in img:
                    img['caption'] = {"en": "", "si": "", "ta": ""}
                if 'is_primary' not in img:
                    img['is_primary'] = False
                    
                fixed_images.append(img)
        
        if needs_update:
            await restaurants_collection.update_one(
                {"_id": restaurant["_id"]},
                {"$set": {"images": fixed_images}}
            )
            fixed_restaurants += 1
    
    logger.info(f"   ✅ Fixed {fixed_restaurants} restaurants")
    
    # Fix events images
    logger.info("\n4. Fixing Events image URLs...")
    events_collection = db.events
    events = await events_collection.find({}).to_list(length=None)
    fixed_events = 0
    
    for event in events:
        needs_update = False
        images = event.get('images', [])
        fixed_images = []
        
        for img in images:
            if isinstance(img, dict):
                if 'url' in img:
                    if not isinstance(img['url'], str):
                        img['url'] = str(img['url']) if img['url'] else ""
                        needs_update = True
                else:
                    img['url'] = ""
                    needs_update = True
                    
                if 'caption' not in img:
                    img['caption'] = {"en": "", "si": "", "ta": ""}
                if 'is_primary' not in img:
                    img['is_primary'] = False
                    
                fixed_images.append(img)
        
        if needs_update:
            await events_collection.update_one(
                {"_id": event["_id"]},
                {"$set": {"images": fixed_images}}
            )
            fixed_events += 1
    
    logger.info(f"   ✅ Fixed {fixed_events} events")
    
    logger.info("\n" + "=" * 60)
    logger.info("Database Fix Complete!")
    logger.info(f"Total Fixed: {fixed_count + fixed_hotels + fixed_restaurants + fixed_events} documents")
    logger.info("=" * 60)
    
    client.close()


async def validate_data():
    """Validate fixed data"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    logger.info("\n" + "=" * 60)
    logger.info("Validating Fixed Data")
    logger.info("=" * 60)
    
    collections = ['attractions', 'hotels', 'restaurants', 'events']
    
    for coll_name in collections:
        collection = db[coll_name]
        count = await collection.count_documents({})
        logger.info(f"\n{coll_name.capitalize()}: {count} documents")
        
        # Check for invalid image URLs - find documents with missing url field
        docs_with_images = await collection.find(
            {"images": {"$exists": True, "$ne": []}}
        ).to_list(length=None)
        
        invalid_docs = []
        for doc in docs_with_images:
            for img in doc.get('images', []):
                if not isinstance(img.get('url'), str):
                    invalid_docs.append(doc)
                    break
        
        invalid_docs = invalid_docs[:10]  # Limit to 10 for display
        
        if invalid_docs:
            logger.warning(f"   ⚠️ Found {len(invalid_docs)} documents with potential issues")
        else:
            logger.info(f"   ✅ All image URLs valid")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_image_urls())
    asyncio.run(validate_data())
