"""
Recommendation Service for personalized tourism suggestions
Uses machine learning and collaborative filtering
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from backend.app.models.recommendation import (
    UserPreferenceProfile,
    RecommendationResult,
    RecommendationType
)
from backend.app.models.user import User
from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.analytics import UserBehaviorEvent

logger = logging.getLogger(__name__)


class RecommendationService:
    """ML-based recommendation service"""
    
    def __init__(self):
        self.initialized = False
        
    async def get_personalized_recommendations(
        self,
        user_id: Optional[str],
        session_id: str,
        resource_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User ID (optional for anonymous users)
            session_id: Session ID
            resource_type: Filter by type (attraction, hotel, restaurant)
            context: Context information (location, weather, time, etc.)
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended items with scores
        """
        try:
            # Get user preferences
            preferences = await self._get_user_preferences(user_id)
            
            # Get user behavior history
            behavior = await self._get_user_behavior(user_id, session_id)
            
            # Generate recommendations based on multiple algorithms
            recommendations = []
            
            # Collaborative filtering recommendations
            collab_recs = await self._collaborative_filtering(
                user_id, resource_type, limit
            )
            recommendations.extend(collab_recs)
            
            # Content-based recommendations
            content_recs = await self._content_based_filtering(
                preferences, resource_type, limit
            )
            recommendations.extend(content_recs)
            
            # Context-aware recommendations
            if context:
                context_recs = await self._contextual_recommendations(
                    context, resource_type, limit
                )
                recommendations.extend(context_recs)
            
            # Trending items
            trending_recs = await self._get_trending_items(resource_type, limit // 2)
            recommendations.extend(trending_recs)
            
            # Deduplicate and rank
            final_recommendations = await self._rank_and_deduplicate(
                recommendations, preferences, context, limit
            )
            
            # Log recommendations for analytics
            await self._log_recommendations(
                user_id, session_id, final_recommendations
            )
            
            return {
                "recommendations": final_recommendations,
                "total_count": len(final_recommendations),
                "personalization_level": await self._calculate_personalization_level(
                    user_id, preferences
                ),
                "context_applied": context is not None,
                "recommendation_types": self._get_recommendation_types(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # Return fallback recommendations
            return await self._get_fallback_recommendations(resource_type, limit)
    
    async def _get_user_preferences(
        self, 
        user_id: Optional[str]
    ) -> Optional[UserPreferenceProfile]:
        """Get or create user preference profile"""
        if not user_id:
            return None
        
        try:
            profile = await UserPreferenceProfile.find_one(
                UserPreferenceProfile.user_id == user_id
            )
            return profile
        except Exception as e:
            logger.error(f"Error fetching user preferences: {e}")
            return None
    
    async def _get_user_behavior(
        self,
        user_id: Optional[str],
        session_id: str
    ) -> List[UserBehaviorEvent]:
        """Get recent user behavior"""
        try:
            query = {"session_id": session_id}
            if user_id:
                query["user_id"] = user_id
            
            events = await UserBehaviorEvent.find(query).limit(50).to_list()
            return events
        except Exception as e:
            logger.error(f"Error fetching user behavior: {e}")
            return []
    
    async def _collaborative_filtering(
        self,
        user_id: Optional[str],
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Collaborative filtering recommendations"""
        if not user_id:
            return []
        
        try:
            # Find similar users based on behavior
            similar_users = await self._find_similar_users(user_id, limit=20)
            
            # Get items liked by similar users
            recommendations = []
            for similar_user_id in similar_users:
                user_items = await self._get_user_favorite_items(
                    similar_user_id, resource_type
                )
                for item in user_items:
                    recommendations.append({
                        **item,
                        "recommendation_type": RecommendationType.COLLABORATIVE,
                        "score": item.get("score", 0.5) * 0.8  # Weight
                    })
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    async def _content_based_filtering(
        self,
        preferences: Optional[UserPreferenceProfile],
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Content-based filtering recommendations"""
        if not preferences:
            return []
        
        try:
            recommendations = []
            
            # Get items matching user's category preferences
            if preferences.category_preferences:
                for category, score in preferences.category_preferences.items():
                    if score > 0.3:  # Threshold
                        items = await self._get_items_by_category(
                            category, resource_type, limit // len(preferences.category_preferences)
                        )
                        for item in items:
                            recommendations.append({
                                **item,
                                "recommendation_type": RecommendationType.CONTENT_BASED,
                                "score": score * 0.9
                            })
            
            # Match preferred locations
            if preferences.preferred_locations:
                for location in preferences.preferred_locations[:3]:
                    items = await self._get_items_by_location(
                        location, resource_type, limit // 3
                    )
                    for item in items:
                        recommendations.append({
                            **item,
                            "recommendation_type": RecommendationType.CONTENT_BASED,
                            "score": 0.7
                        })
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    async def _contextual_recommendations(
        self,
        context: Dict[str, Any],
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Context-aware recommendations"""
        try:
            recommendations = []
            
            # Weather-based recommendations
            if "weather" in context:
                weather = context["weather"]
                if weather.get("condition") == "rain":
                    # Recommend indoor attractions
                    items = await self._get_indoor_attractions(limit)
                elif weather.get("temperature", 0) > 30:
                    # Recommend beaches or air-conditioned places
                    items = await self._get_cool_places(limit)
                else:
                    items = []
                
                for item in items:
                    recommendations.append({
                        **item,
                        "recommendation_type": RecommendationType.CONTEXTUAL,
                        "score": 0.8,
                        "context_reason": "weather"
                    })
            
            # Location-based recommendations
            if "location" in context:
                lat = context["location"].get("latitude")
                lon = context["location"].get("longitude")
                if lat and lon:
                    nearby = await self._get_nearby_items(lat, lon, resource_type, limit)
                    for item in nearby:
                        recommendations.append({
                            **item,
                            "recommendation_type": RecommendationType.CONTEXTUAL,
                            "score": 0.9,
                            "context_reason": "nearby"
                        })
            
            # Time-based recommendations
            if "time" in context:
                hour = context["time"].get("hour", 12)
                if 6 <= hour < 11:
                    # Morning: sunrise spots, breakfast places
                    items = await self._get_morning_recommendations(resource_type, limit)
                elif 18 <= hour < 22:
                    # Evening: sunset spots, dinner places
                    items = await self._get_evening_recommendations(resource_type, limit)
                else:
                    items = []
                
                for item in items:
                    recommendations.append({
                        **item,
                        "recommendation_type": RecommendationType.CONTEXTUAL,
                        "score": 0.7,
                        "context_reason": "time_of_day"
                    })
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error in contextual recommendations: {e}")
            return []
    
    async def _get_trending_items(
        self,
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get trending/popular items"""
        try:
            recommendations = []
            
            # Get from attractions
            if not resource_type or resource_type == "attraction":
                attractions = await Attraction.find(
                    Attraction.is_active == True
                ).sort(-Attraction.popularity_score).limit(limit).to_list()
                
                for attraction in attractions:
                    recommendations.append({
                        "resource_id": str(attraction.id),
                        "resource_type": "attraction",
                        "name": attraction.name.en,
                        "category": attraction.category,
                        "rating": attraction.average_rating,
                        "popularity": attraction.popularity_score,
                        "recommendation_type": RecommendationType.TRENDING,
                        "score": attraction.popularity_score / 100
                    })
            
            # Get from hotels
            if not resource_type or resource_type == "hotel":
                hotels = await Hotel.find(
                    Hotel.is_active == True
                ).sort(-Hotel.popularity_score).limit(limit).to_list()
                
                for hotel in hotels:
                    recommendations.append({
                        "resource_id": str(hotel.id),
                        "resource_type": "hotel",
                        "name": hotel.name.en,
                        "rating": hotel.average_rating,
                        "popularity": hotel.popularity_score,
                        "recommendation_type": RecommendationType.TRENDING,
                        "score": hotel.popularity_score / 100
                    })
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending items: {e}")
            return []
    
    async def _rank_and_deduplicate(
        self,
        recommendations: List[Dict[str, Any]],
        preferences: Optional[UserPreferenceProfile],
        context: Optional[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Rank and deduplicate recommendations"""
        # Remove duplicates
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = (rec.get("resource_type"), rec.get("resource_id"))
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        
        # Sort by score
        unique_recs.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Apply diversity (ensure variety of types and categories)
        diverse_recs = self._apply_diversity(unique_recs, limit)
        
        return diverse_recs[:limit]
    
    def _apply_diversity(
        self,
        recommendations: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Apply diversity to recommendations"""
        diverse = []
        seen_categories = set()
        seen_types = set()
        
        # First pass: pick highest scoring items with category diversity
        for rec in recommendations:
            category = rec.get("category")
            resource_type = rec.get("resource_type")
            
            # Prefer items from new categories/types
            if len(diverse) < limit:
                if category not in seen_categories or resource_type not in seen_types:
                    diverse.append(rec)
                    if category:
                        seen_categories.add(category)
                    if resource_type:
                        seen_types.add(resource_type)
        
        # Second pass: fill remaining slots
        for rec in recommendations:
            if len(diverse) >= limit:
                break
            if rec not in diverse:
                diverse.append(rec)
        
        return diverse
    
    async def _find_similar_users(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[str]:
        """Find users with similar preferences/behavior"""
        # Simplified: In production, use cosine similarity on user vectors
        try:
            # Get users who viewed similar items
            user_events = await UserBehaviorEvent.find(
                UserBehaviorEvent.user_id == user_id
            ).limit(50).to_list()
            
            viewed_items = {e.resource_id for e in user_events if e.resource_id}
            
            # Find other users who viewed these items
            similar_user_ids = set()
            for item_id in list(viewed_items)[:10]:
                events = await UserBehaviorEvent.find(
                    UserBehaviorEvent.resource_id == item_id,
                    UserBehaviorEvent.user_id != user_id
                ).limit(5).to_list()
                
                for event in events:
                    if event.user_id:
                        similar_user_ids.add(event.user_id)
            
            return list(similar_user_ids)[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []
    
    async def _get_user_favorite_items(
        self,
        user_id: str,
        resource_type: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get items favorited/highly rated by user"""
        # Placeholder implementation
        return []
    
    async def _get_items_by_category(
        self,
        category: str,
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get items by category"""
        items = []
        
        if not resource_type or resource_type == "attraction":
            try:
                attractions = await Attraction.find(
                    Attraction.category == category,
                    Attraction.is_active == True
                ).limit(limit).to_list()
                
                items.extend([{
                    "resource_id": str(a.id),
                    "resource_type": "attraction",
                    "name": a.name.en,
                    "category": a.category,
                    "rating": a.average_rating
                } for a in attractions])
            except:
                pass
        
        return items
    
    async def _get_items_by_location(
        self,
        location: str,
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get items by location"""
        items = []
        
        if not resource_type or resource_type == "attraction":
            try:
                attractions = await Attraction.find(
                    Attraction.location.city == location,
                    Attraction.is_active == True
                ).limit(limit).to_list()
                
                items.extend([{
                    "resource_id": str(a.id),
                    "resource_type": "attraction",
                    "name": a.name.en,
                    "category": a.category,
                    "location": location
                } for a in attractions])
            except:
                pass
        
        return items
    
    async def _get_indoor_attractions(self, limit: int) -> List[Dict[str, Any]]:
        """Get indoor attractions (for rainy weather)"""
        try:
            attractions = await Attraction.find(
                Attraction.category.in_(["museum", "temple", "cultural"]),
                Attraction.is_active == True
            ).limit(limit).to_list()
            
            return [{
                "resource_id": str(a.id),
                "resource_type": "attraction",
                "name": a.name.en,
                "category": a.category
            } for a in attractions]
        except:
            return []
    
    async def _get_cool_places(self, limit: int) -> List[Dict[str, Any]]:
        """Get cool places for hot weather"""
        try:
            # Beaches and hill country
            attractions = await Attraction.find(
                Attraction.category.in_(["beach", "mountain"]),
                Attraction.is_active == True
            ).limit(limit).to_list()
            
            return [{
                "resource_id": str(a.id),
                "resource_type": "attraction",
                "name": a.name.en,
                "category": a.category
            } for a in attractions]
        except:
            return []
    
    async def _get_nearby_items(
        self,
        latitude: float,
        longitude: float,
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get items near a location"""
        # Placeholder: Would use geospatial queries
        return []
    
    async def _get_morning_recommendations(
        self,
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get morning recommendations"""
        # Sunrise spots, breakfast places, etc.
        return []
    
    async def _get_evening_recommendations(
        self,
        resource_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get evening recommendations"""
        # Sunset spots, dinner places, etc.
        return []
    
    async def _calculate_personalization_level(
        self,
        user_id: Optional[str],
        preferences: Optional[UserPreferenceProfile]
    ) -> float:
        """Calculate how personalized the recommendations are (0-1)"""
        if not user_id:
            return 0.0
        
        if not preferences:
            return 0.2
        
        # Calculate based on amount of preference data
        score = 0.2  # Base for having user_id
        
        if preferences.category_preferences:
            score += 0.3
        if preferences.preferred_locations:
            score += 0.2
        if preferences.viewing_history:
            score += 0.3
        
        return min(score, 1.0)
    
    def _get_recommendation_types(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get counts of recommendation types"""
        types = {}
        for rec in recommendations:
            rec_type = rec.get("recommendation_type", "unknown")
            types[rec_type] = types.get(rec_type, 0) + 1
        return types
    
    async def _log_recommendations(
        self,
        user_id: Optional[str],
        session_id: str,
        recommendations: List[Dict[str, Any]]
    ):
        """Log recommendations for analytics"""
        try:
            for i, rec in enumerate(recommendations):
                result = RecommendationResult(
                    user_id=user_id,
                    session_id=session_id,
                    recommendation_type=rec.get("recommendation_type", RecommendationType.PERSONALIZED),
                    engine_id="default",
                    resource_type=rec.get("resource_type", "unknown"),
                    resource_id=rec.get("resource_id", "unknown"),
                    relevance_score=rec.get("score", 0.0),
                    confidence_score=rec.get("score", 0.0),
                    ranking_position=i + 1
                )
                await result.insert()
        except Exception as e:
            logger.error(f"Error logging recommendations: {e}")
    
    async def _get_fallback_recommendations(
        self,
        resource_type: Optional[str],
        limit: int
    ) -> Dict[str, Any]:
        """Get fallback recommendations when personalization fails"""
        try:
            recommendations = await self._get_trending_items(resource_type, limit)
            
            return {
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "personalization_level": 0.0,
                "context_applied": False,
                "recommendation_types": {"trending": len(recommendations)},
                "fallback": True
            }
        except:
            return {
                "recommendations": [],
                "total_count": 0,
                "personalization_level": 0.0,
                "fallback": True,
                "error": "Unable to generate recommendations"
            }

