"""
View Images in Database
Display all images stored in the database for attractions, hotels, restaurants, and events
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def format_image_info(image: Any, index: int) -> str:
    """Format image information for display"""
    if isinstance(image, str):
        return f"  [{index}] URL: {image}"
    elif isinstance(image, dict):
        url = image.get('url') or image.get('_url') or 'NO URL'
        is_primary = image.get('is_primary', False)
        alt_text = image.get('alt_text', {})
        alt_en = alt_text.get('en', '') if isinstance(alt_text, dict) else ''
        
        primary_marker = " ⭐ PRIMARY" if is_primary else ""
        return f"  [{index}] URL: {url}{primary_marker}\n      Alt: {alt_en}"
    else:
        return f"  [{index}] Invalid format: {type(image)}"


def validate_url(url: str) -> bool:
    """Check if URL is valid"""
    if not url or not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False


async def view_images_in_collection(collection_name: str, db: Any, limit: int = 10):
    """View images in a specific collection"""
    collection = db[collection_name]
    
    # Count total documents
    total_count = await collection.count_documents({})
    logger.info(f"\n{'='*80}")
    logger.info(f"📁 Collection: {collection_name.upper()}")
    logger.info(f"📊 Total Documents: {total_count}")
    logger.info(f"{'='*80}")
    
    if total_count == 0:
        logger.info("   ⚠️  No documents found in this collection")
        return
    
    # Find documents with images
    cursor = collection.find({"images": {"$exists": True, "$ne": []}})
    docs_with_images = await cursor.to_list(length=limit)
    
    if not docs_with_images:
        logger.info("   ⚠️  No documents with images found")
        return
    
    logger.info(f"\n📸 Showing {len(docs_with_images)} documents with images:\n")
    
    valid_images_count = 0
    invalid_images_count = 0
    
    for idx, doc in enumerate(docs_with_images, 1):
        # Get name
        name_obj = doc.get('name', {})
        if isinstance(name_obj, dict):
            name = name_obj.get('en') or name_obj.get('si') or name_obj.get('ta') or 'Unknown'
        else:
            name = str(name_obj) if name_obj else 'Unknown'
        
        # Get ID
        doc_id = str(doc.get('_id', 'Unknown'))
        
        logger.info(f"\n{idx}. {name}")
        logger.info(f"   ID: {doc_id}")
        
        images = doc.get('images', [])
        if not images:
            logger.info("   ⚠️  No images in this document")
            continue
        
        logger.info(f"   📷 Total Images: {len(images)}")
        
        for img_idx, image in enumerate(images, 1):
            img_info = format_image_info(image, img_idx)
            logger.info(img_info)
            
            # Validate URL
            url = None
            if isinstance(image, str):
                url = image
            elif isinstance(image, dict):
                url = image.get('url') or image.get('_url')
            
            if url and validate_url(url):
                valid_images_count += 1
                logger.info(f"      ✅ Valid URL")
            else:
                invalid_images_count += 1
                logger.info(f"      ❌ Invalid or missing URL")
    
    logger.info(f"\n{'─'*80}")
    logger.info(f"📊 Summary for {collection_name}:")
    logger.info(f"   ✅ Valid Images: {valid_images_count}")
    logger.info(f"   ❌ Invalid Images: {invalid_images_count}")
    logger.info(f"{'─'*80}")


async def generate_html_report(db: Any, output_file: str = "database_images_report.html"):
    """Generate HTML report with clickable image links"""
    collections = ['attractions', 'hotels', 'restaurants', 'events']
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Images Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #333; }
            .collection { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .item { margin: 15px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; }
            .item-name { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
            .image-list { margin-left: 20px; }
            .image-item { margin: 8px 0; padding: 8px; background: white; border-radius: 4px; }
            .image-url { color: #0066cc; text-decoration: none; word-break: break-all; }
            .image-url:hover { text-decoration: underline; }
            .valid { color: #4CAF50; font-weight: bold; }
            .invalid { color: #f44336; font-weight: bold; }
            .primary { background: #fff9c4; }
            .stats { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📸 Database Images Report</h1>
    """
    
    for collection_name in collections:
        collection = db[collection_name]
        total_count = await collection.count_documents({})
        cursor = collection.find({"images": {"$exists": True, "$ne": []}})
        docs_with_images = await cursor.to_list(length=50)
        
        if not docs_with_images:
            continue
        
        html_content += f"""
            <div class="collection">
                <h2>{collection_name.upper()} ({len(docs_with_images)} items with images)</h2>
        """
        
        for doc in docs_with_images:
            name_obj = doc.get('name', {})
            if isinstance(name_obj, dict):
                name = name_obj.get('en') or name_obj.get('si') or name_obj.get('ta') or 'Unknown'
            else:
                name = str(name_obj) if name_obj else 'Unknown'
            
            doc_id = str(doc.get('_id', 'Unknown'))
            images = doc.get('images', [])
            
            html_content += f"""
                <div class="item">
                    <div class="item-name">{name}</div>
                    <div style="color: #666; font-size: 12px;">ID: {doc_id}</div>
                    <div class="image-list">
            """
            
            for img_idx, image in enumerate(images, 1):
                url = None
                is_primary = False
                alt_text = ''
                
                if isinstance(image, str):
                    url = image
                elif isinstance(image, dict):
                    url = image.get('url') or image.get('_url')
                    is_primary = image.get('is_primary', False)
                    alt_obj = image.get('alt_text', {})
                    if isinstance(alt_obj, dict):
                        alt_text = alt_obj.get('en', '')
                
                is_valid = url and (url.startswith('http://') or url.startswith('https://'))
                primary_class = 'primary' if is_primary else ''
                status_class = 'valid' if is_valid else 'invalid'
                status_text = '✅ Valid' if is_valid else '❌ Invalid'
                
                html_content += f"""
                    <div class="image-item {primary_class}">
                        <strong>Image {img_idx}</strong> {status_text}
                        {f' ⭐ PRIMARY' if is_primary else ''}<br>
                        {f'Alt: {alt_text}' if alt_text else ''}<br>
                        <a href="{url if url else '#'}" target="_blank" class="image-url">
                            {url if url else 'NO URL'}
                        </a>
                    </div>
                """
            
            html_content += """
                    </div>
                </div>
            """
        
        html_content += "</div>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    output_path = Path(__file__).parent.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"\n✅ HTML report generated: {output_path}")
    logger.info(f"   Open this file in your browser to view images")


async def main():
    """Main function"""
    logger.info("="*80)
    logger.info("📸 DATABASE IMAGES VIEWER")
    logger.info("="*80)
    
    # Connect to MongoDB
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        logger.info(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return
    
    # Collections to check
    collections = ['attractions', 'hotels', 'restaurants', 'events']
    
    # View images in each collection
    for collection_name in collections:
        await view_images_in_collection(collection_name, db, limit=20)
    
    # Generate HTML report
    logger.info(f"\n{'='*80}")
    logger.info("Generating HTML Report...")
    logger.info(f"{'='*80}")
    await generate_html_report(db)
    
    # Close connection
    client.close()
    logger.info("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())

