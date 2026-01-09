"""
Script to fix image URL format in database

Changes image URLs from {'_url': 'https://...'} format to plain strings
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_image_urls():
    """Fix image URL format in attractions collection"""
    # Import models after env vars are set
    os.environ["DEBUG"] = "true"
    os.environ["ENVIRONMENT"] = "development"
    
    from backend.app.core.config import settings
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    logger.info("Connected to MongoDB")
    
    # Fix Attractions - direct MongoDB update without Beanie validation
    logger.info("Fixing attraction image URLs...")
    attractions_collection = db['attractions']
    
    # Find documents with dict-formatted URLs
    cursor = attractions_collection.find({
        "images.url": {"$regex": "^{'_url':", "$options": "i"}
    })
    
    fixed_attractions = 0
    async for doc in cursor:
        images = doc.get('images', [])
        updated_images = []
        needs_update = False
        
        for img in images:
            url = img.get('url', '')
            # Check if URL is in dict string format
            if isinstance(url, str) and url.startswith("{'_url':"):
                try:
                    # Extract actual URL from dict string
                    import ast
                    url_dict = ast.literal_eval(url)
                    if isinstance(url_dict, dict) and '_url' in url_dict:
                        img['url'] = url_dict['_url']
                        needs_update = True
                        logger.info(f"Fixed image URL for: {doc.get('name', 'Unknown')}")
                except:
                    logger.warning(f"Could not parse URL for: {doc.get('name', 'Unknown')}")
            updated_images.append(img)
        
        if needs_update:
            await attractions_collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'images': updated_images}}
            )
            fixed_attractions += 1
    
    logger.info(f"✅ Fixed {fixed_attractions} attractions")
    
    # Fix Hotels
    logger.info("Fixing hotel image URLs...")
    hotels_collection = db['hotels']
    
    cursor = hotels_collection.find({
        "images.url": {"$regex": "^{'_url':", "$options": "i"}
    })
    
    fixed_hotels = 0
    async for doc in cursor:
        images = doc.get('images', [])
        updated_images = []
        needs_update = False
        
        for img in images:
            url = img.get('url', '')
            if isinstance(url, str) and url.startswith("{'_url':"):
                try:
                    import ast
                    url_dict = ast.literal_eval(url)
                    if isinstance(url_dict, dict) and '_url' in url_dict:
                        img['url'] = url_dict['_url']
                        needs_update = True
                        logger.info(f"Fixed image URL for: {doc.get('name', 'Unknown')}")
                except:
                    logger.warning(f"Could not parse URL for: {doc.get('name', 'Unknown')}")
            updated_images.append(img)
        
        if needs_update:
            await hotels_collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'images': updated_images}}
            )
            fixed_hotels += 1
    
    logger.info(f"✅ Fixed {fixed_hotels} hotels")
    
    # Fix Restaurants
    logger.info("Fixing restaurant image URLs...")
    restaurants_collection = db['restaurants']
    
    cursor = restaurants_collection.find({
        "images.url": {"$regex": "^{'_url':", "$options": "i"}
    })
    
    fixed_restaurants = 0
    async for doc in cursor:
        images = doc.get('images', [])
        updated_images = []
        needs_update = False
        
        for img in images:
            url = img.get('url', '')
            if isinstance(url, str) and url.startswith("{'_url':"):
                try:
                    import ast
                    url_dict = ast.literal_eval(url)
                    if isinstance(url_dict, dict) and '_url' in url_dict:
                        img['url'] = url_dict['_url']
                        needs_update = True
                        logger.info(f"Fixed image URL for: {doc.get('name', 'Unknown')}")
                except:
                    logger.warning(f"Could not parse URL for: {doc.get('name', 'Unknown')}")
            updated_images.append(img)
        
        if needs_update:
            await restaurants_collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'images': updated_images}}
            )
            fixed_restaurants += 1
    
    logger.info(f"✅ Fixed {fixed_restaurants} restaurants")
    
    logger.info(f"\n🎉 Total fixed: {fixed_attractions + fixed_hotels + fixed_restaurants} documents")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(fix_image_urls())
