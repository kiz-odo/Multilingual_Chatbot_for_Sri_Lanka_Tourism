"""
Database Migration Script: Fix Website URL Format
Converts website URLs from dict format {'_url': 'https://...'} to string format 'https://...'
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.core.database import init_database, db
from backend.app.models.attraction import Attraction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_website_urls():
    """Migrate website URLs from dict to string format"""
    await init_database()
    
    logger.info("Starting website URL migration...")
    
    # Use raw MongoDB collection to avoid Pydantic validation
    collection_name = Attraction.get_collection_name()
    collection = db.database[collection_name]
    
    fixed_count = 0
    total_checked = 0
    
    # Find all documents with raw cursor
    async for raw_doc in collection.find({}):
        total_checked += 1
        doc_id = raw_doc.get("_id")
        updated = False
        update_fields = {}
        
        # Check website field
        if 'website' in raw_doc:
            website_value = raw_doc['website']
            
            # Skip if already None or empty
            if website_value is None:
                continue
            
            # Check if it's a dict that needs fixing
            if isinstance(website_value, dict):
                # Extract URL from dict format
                url = None
                if '_url' in website_value:
                    url = website_value['_url']
                elif 'url' in website_value:
                    url_value = website_value['url']
                    if isinstance(url_value, str):
                        url = url_value
                    elif isinstance(url_value, dict) and '_url' in url_value:
                        url = url_value['_url']
                
                if url:
                    # Convert to string if not already
                    if isinstance(url, str):
                        update_fields['website'] = url
                        updated = True
                    else:
                        update_fields['website'] = str(url)
                        updated = True
                    logger.debug(f"Fixed website for document {doc_id}: {url}")
            
            # Handle edge case: string representation of dict
            elif isinstance(website_value, str):
                # Check if it's a string representation of a dict
                if website_value.startswith("{'") or website_value.startswith('{"'):
                    # Try to extract URL from string representation
                    import re
                    url_match = re.search(r"['\"]_url['\"]:\s*['\"](https?://[^'\"]+)['\"]", website_value)
                    if url_match:
                        url = url_match.group(1)
                        update_fields['website'] = url
                        updated = True
                        logger.debug(f"Fixed website from string dict for document {doc_id}: {url}")
        
        # Update document if needed
        if updated and update_fields:
            try:
                await collection.update_one(
                    {"_id": doc_id},
                    {"$set": update_fields}
                )
                fixed_count += 1
                if fixed_count % 10 == 0:
                    logger.info(f"Fixed {fixed_count} documents so far...")
            except Exception as e:
                logger.error(f"Error updating document {doc_id}: {e}")
    
    logger.info(f"Migration complete! Fixed {fixed_count} out of {total_checked} documents.")
    return fixed_count


if __name__ == "__main__":
    try:
        fixed = asyncio.run(fix_website_urls())
        print(f"Successfully migrated {fixed} documents")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)



