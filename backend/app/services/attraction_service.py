"""
Attraction service for managing attraction operations
"""

from typing import Optional, List
from datetime import datetime

from backend.app.models.attraction import Attraction, AttractionCategory


class AttractionService:
    """Attraction service class"""
    
    async def get_attractions(
        self,
        skip: int = 0,
        limit: int = 10,
        category: Optional[AttractionCategory] = None,
        city: Optional[str] = None,
        province: Optional[str] = None,
        featured_only: bool = False
    ) -> List[Attraction]:
        """Get attractions with filters"""
        
        query = Attraction.find(Attraction.is_active == True)
        
        if category:
            query = query.find(Attraction.category == category)
        
        if city:
            query = query.find(Attraction.location.city == city)
        
        if province:
            query = query.find(Attraction.location.province == province)
        
        if featured_only:
            query = query.find(Attraction.is_featured == True)
        
        return await query.sort(-Attraction.popularity_score).skip(skip).limit(limit).to_list()
    
    async def search_attractions(
        self,
        query: Optional[str] = None,
        category: Optional[AttractionCategory] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Attraction]:
        """Search attractions by various criteria"""
        
        find_query = Attraction.find(Attraction.is_active == True)
        
        if category:
            find_query = find_query.find(Attraction.category == category)
        
        if location:
            # Search in city or province using MongoDB regex
            find_query = find_query.find(
                {"$or": [
                    {"location.city": {"$regex": location, "$options": "i"}},
                    {"location.province": {"$regex": location, "$options": "i"}}
                ]}
            )
        
        if tags:
            find_query = find_query.find(Attraction.tags.in_(tags))
        
        if query:
            # Search in name (English) and tags using MongoDB regex
            find_query = find_query.find(
                {"$or": [
                    {"name.en": {"$regex": query, "$options": "i"}},
                    {"tags": query.lower()}
                ]}
            )
        
        return await find_query.sort(-Attraction.popularity_score).limit(limit).to_list()
    
    async def get_attraction_by_id(self, attraction_id: str) -> Optional[Attraction]:
        """Get attraction by ID"""
        try:
            return await Attraction.get(attraction_id)
        except:
            return None
    
    async def get_attraction_by_slug(self, slug: str) -> Optional[Attraction]:
        """Get attraction by slug"""
        return await Attraction.find_one({"slug": slug})
    
    async def get_featured_attractions(self, limit: int = 6) -> List[Attraction]:
        """Get featured attractions"""
        return await Attraction.find(
            {"is_active": True, "is_featured": True}
        ).sort([("-popularity_score", -1)]).limit(limit).to_list()
    
    async def get_popular_attractions(self, limit: int = 10) -> List[Attraction]:
        """Get popular attractions by popularity score"""
        return await Attraction.find(
            {"is_active": True}
        ).sort([("-popularity_score", -1)]).limit(limit).to_list()
    
    async def get_nearby_attractions(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50,
        limit: int = 10
    ) -> List[Attraction]:
        """Get attractions near a location using geospatial query"""
        
        # MongoDB geospatial query
        # Note: This requires a 2dsphere index on location.coordinates
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "distanceField": "distance",
                    "maxDistance": radius_km * 1000,  # Convert km to meters
                    "spherical": True,
                    "query": {"is_active": True}
                }
            },
            {"$limit": limit}
        ]
        
        try:
            results = await Attraction.aggregate(pipeline).to_list()
            return [Attraction(**doc) for doc in results]
        except Exception:
            # Fallback to regular query if geospatial query fails
            return await self.get_popular_attractions(limit=limit)
    
    async def get_attractions_by_category(
        self,
        category: AttractionCategory,
        limit: int = 10
    ) -> List[Attraction]:
        """Get attractions by category"""
        return await Attraction.find(
            {"is_active": True, "category": category.value}
        ).sort([("-popularity_score", -1)]).limit(limit).to_list()
    
    async def add_review(
        self,
        attraction_id: str,
        user_id: str,
        username: str,
        rating: float,
        comment: Optional[str] = None,
        language: str = "en"
    ) -> bool:
        """Add a review to an attraction"""
        attraction = await self.get_attraction_by_id(attraction_id)
        if not attraction:
            return False
        
        attraction.add_review(user_id, username, rating, comment, language)
        await attraction.save()
        return True
    
    async def get_attraction_stats(self) -> dict:
        """Get attraction statistics"""
        total_attractions = await Attraction.find({"is_active": True}).count()
        
        # Count by category
        category_counts = {}
        for category in AttractionCategory:
            count = await Attraction.find(
                {"is_active": True, "category": category.value}
            ).count()
            category_counts[category.value] = count
        
        # Count featured
        featured_count = await Attraction.find(
            {"is_active": True, "is_featured": True}
        ).count()
        
        return {
            "total_attractions": total_attractions,
            "featured_attractions": featured_count,
            "by_category": category_counts
        }
