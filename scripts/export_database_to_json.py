"""
Export all database data to a single JSON file
This creates a complete backup of the database in JSON format
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from pydantic import HttpUrl
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.app.core.config import settings
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.attraction import Attraction
from backend.app.models.emergency import Emergency


def convert_to_serializable(obj: Any) -> Any:
    """Convert non-serializable objects to JSON-serializable format"""
    if obj is None:
        return None
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, Enum):
        # Enum objects
        return obj.value
    elif hasattr(obj, '__class__') and 'Url' in obj.__class__.__name__:
        # Pydantic Url objects
        return str(obj)
    elif hasattr(obj, 'dict'):
        # Pydantic models
        data = obj.dict()
        return convert_to_serializable(data)
    elif hasattr(obj, 'isoformat'):
        # datetime objects
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (int, float, bool)):
        return obj
    else:
        # Try to convert to string as fallback
        try:
            return str(obj)
        except:
            return None


async def export_database():
    """Export all database collections to a single JSON file"""
    
    print("🔄 Starting Database Export...")
    print("=" * 60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Initialize beanie with all models
    await init_beanie(
        database=database, 
        document_models=[Hotel, Restaurant, Attraction, Emergency]
    )
    
    # Prepare export data structure
    export_data = {
        "metadata": {
            "export_date": datetime.utcnow().isoformat(),
            "database_name": settings.DATABASE_NAME,
            "version": "1.0"
        },
        "collections": {}
    }
    
    # Export Attractions
    print("📍 Exporting Attractions...")
    attractions = await Attraction.find_all().to_list()
    export_data["collections"]["attractions"] = [
        convert_to_serializable(attr.dict()) for attr in attractions
    ]
    print(f"   ✅ Exported {len(attractions)} attractions")
    
    # Export Hotels
    print("🏨 Exporting Hotels...")
    hotels = await Hotel.find_all().to_list()
    export_data["collections"]["hotels"] = [
        convert_to_serializable(hotel.dict()) for hotel in hotels
    ]
    print(f"   ✅ Exported {len(hotels)} hotels")
    
    # Export Restaurants
    print("🍽️  Exporting Restaurants...")
    restaurants = await Restaurant.find_all().to_list()
    export_data["collections"]["restaurants"] = [
        convert_to_serializable(rest.dict()) for rest in restaurants
    ]
    print(f"   ✅ Exported {len(restaurants)} restaurants")
    
    # Export Emergency Services
    print("🚨 Exporting Emergency Services...")
    emergencies = await Emergency.find_all().to_list()
    export_data["collections"]["emergency_services"] = [
        convert_to_serializable(emerg.dict()) for emerg in emergencies
    ]
    print(f"   ✅ Exported {len(emergencies)} emergency services")
    
    # Calculate statistics
    total_records = (
        len(attractions) + 
        len(hotels) + 
        len(restaurants) + 
        len(emergencies)
    )
    
    export_data["metadata"]["total_records"] = total_records
    export_data["metadata"]["statistics"] = {
        "attractions": len(attractions),
        "hotels": len(hotels),
        "restaurants": len(restaurants),
        "emergency_services": len(emergencies)
    }
    
    # Save to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = project_root / f"database_export_{timestamp}.json"
    
    print(f"\n💾 Saving to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    # Get file size
    file_size = output_file.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EXPORT SUMMARY")
    print("=" * 60)
    print(f"Total Records Exported: {total_records:,}")
    print(f"  - Attractions:        {len(attractions):,}")
    print(f"  - Hotels:             {len(hotels):,}")
    print(f"  - Restaurants:        {len(restaurants):,}")
    print(f"  - Emergency Services: {len(emergencies):,}")
    print(f"\nFile: {output_file.name}")
    print(f"Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    print("=" * 60)
    print("\n✅ Export completed successfully!")


if __name__ == "__main__":
    asyncio.run(export_database())
