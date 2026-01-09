"""
Database Migration Script: Fix Image URL Format
Converts image URLs from dict format {'_url': 'https://...'} to string format 'https://...'
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.core.database import init_database, db
from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.event import Event
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_image_dict(img_dict):
    """Convert image dict to proper AttractionImage format"""
    if isinstance(img_dict, str):
        # If it's already a string URL, convert to dict format
        return {
            'url': img_dict,
            'alt_text': {'en': ''},
            'is_primary': False,
            'order': 0
        }
    elif isinstance(img_dict, dict):
        # Extract URL from various formats
        url = None
        if '_url' in img_dict:
            url = img_dict['_url']
        elif 'url' in img_dict:
            url_value = img_dict['url']
            if isinstance(url_value, dict) and '_url' in url_value:
                url = url_value['_url']
            elif isinstance(url_value, str):
                url = url_value
        
        if url:
            # Return proper AttractionImage format
            return {
                'url': url,
                'alt_text': img_dict.get('alt_text', {'en': ''}),
                'caption': img_dict.get('caption'),
                'is_primary': img_dict.get('is_primary', False),
                'order': img_dict.get('order', 0)
            }
    
    # Return as-is if we can't fix it
    return img_dict


async def migrate_image_urls():
    """Migrate image URLs from dict to string format"""
    await init_database()
    
    logger.info("Starting image URL migration...")
    
    # Collections that might have image URLs
    collections = [
        ("attractions", Attraction),
        ("hotels", Hotel),
        ("restaurants", Restaurant),
        ("events", Event),
    ]
    
    total_fixed = 0
    
    for collection_name, Model in collections:
        logger.info(f"Processing {collection_name}...")
        fixed_count = 0
        
        # Use raw MongoDB collection to avoid Pydantic validation
        collection_name = Model.get_collection_name()
        collection = db.database[collection_name]
        
        # Find all documents with raw cursor
        async for raw_doc in collection.find({}):
            doc_id = raw_doc.get("_id")
            updated = False
            update_fields = {}
            
            # Check images field
            if 'images' in raw_doc and raw_doc['images']:
                fixed_images = []
                for img in raw_doc['images']:
                    # Check if image needs fixing
                    needs_fix = False
                    if isinstance(img, dict):
                        # Check if it's a dict with _url or nested url dict
                        if '_url' in img:
                            needs_fix = True
                        elif 'url' in img and isinstance(img['url'], dict) and '_url' in img['url']:
                            needs_fix = True
                        elif isinstance(img, str) and img.startswith("{'") and "'_url'" in img:
                            # String representation of dict
                            needs_fix = True
                    
                    if needs_fix:
                        fixed_img = fix_image_dict(img)
                        if fixed_img != img:
                            updated = True
                        fixed_images.append(fixed_img)
                    else:
                        fixed_images.append(img)
                
                if updated:
                    update_fields['images'] = fixed_images
            
            # Check individual image fields (these are usually strings, not AttractionImage objects)
            for field_name in ['image_url', 'photo_url', 'thumbnail_url', 'cover_image']:
                if field_name in raw_doc:
                    field_value = raw_doc[field_name]
                    if isinstance(field_value, dict):
                        # Extract URL from dict
                        if '_url' in field_value:
                            update_fields[field_name] = field_value['_url']
                            updated = True
                        elif 'url' in field_value:
                            url_val = field_value['url']
                            if isinstance(url_val, str):
                                update_fields[field_name] = url_val
                                updated = True
                            elif isinstance(url_val, dict) and '_url' in url_val:
                                update_fields[field_name] = url_val['_url']
                                updated = True
            
            # Update document if needed
            if updated and update_fields:
                await collection.update_one(
                    {"_id": doc_id},
                    {"$set": update_fields}
                )
                fixed_count += 1
                total_fixed += 1
        
        logger.info(f"Fixed {fixed_count} {collection_name} documents")
    
    logger.info(f"Migration complete! Fixed {total_fixed} documents total.")
    return total_fixed


if __name__ == "__main__":
    try:
        fixed = asyncio.run(migrate_image_urls())
        print(f"Successfully migrated {fixed} documents")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)

