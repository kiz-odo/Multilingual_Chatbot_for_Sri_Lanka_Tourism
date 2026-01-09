"""
Google Maps API Integration Service
Provides directions, places, and distance calculations
"""

import logging
from typing import List, Dict, Optional, Tuple
import httpx

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    logging.warning("googlemaps library not installed. Map features will be limited.")

from backend.app.core.config import settings
from backend.app.services.cache_service import cached

logger = logging.getLogger(__name__)


class MapsService:
    """Google Maps API service"""
    
    def __init__(self):
        """Initialize Google Maps client"""
        if GOOGLEMAPS_AVAILABLE and settings.GOOGLE_MAPS_API_KEY:
            try:
                self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                self.enabled = True
                logger.info("Google Maps service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps: {e}")
                self.gmaps = None
                self.enabled = False
        else:
            self.gmaps = None
            self.enabled = False
            logger.warning("Google Maps not available - check API key and library")
    
    @cached(ttl=3600, prefix="maps:directions")
    async def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        language: str = "en"
    ) -> Optional[Dict]:
        """
        Get directions between two locations
        
        Args:
            origin: Starting location (address or lat,lng)
            destination: Ending location (address or lat,lng)
            mode: Travel mode (driving, walking, bicycling, transit)
            language: Response language
            
        Returns:
            Dictionary with route information or None
        """
        if not self.enabled:
            return self._get_mock_directions(origin, destination)
        
        try:
            result = self.gmaps.directions(
                origin,
                destination,
                mode=mode,
                language=language,
                departure_time="now"
            )
            
            if not result:
                logger.warning(f"No route found from {origin} to {destination}")
                return None
            
            route = result[0]
            leg = route['legs'][0]
            
            return {
                "distance": {
                    "text": leg['distance']['text'],
                    "value": leg['distance']['value']  # meters
                },
                "duration": {
                    "text": leg['duration']['text'],
                    "value": leg['duration']['value']  # seconds
                },
                "start_address": leg['start_address'],
                "end_address": leg['end_address'],
                "steps": [
                    {
                        "instruction": step['html_instructions'],
                        "distance": step['distance']['text'],
                        "duration": step['duration']['text'],
                        "travel_mode": step.get('travel_mode', 'DRIVING')
                    }
                    for step in leg['steps'][:10]  # Limit to 10 steps
                ],
                "overview_polyline": route['overview_polyline']['points']
            }
        except Exception as e:
            logger.error(f"Maps API error: {e}")
            return None
    
    @cached(ttl=1800, prefix="maps:nearby")
    async def find_nearby_places(
        self,
        latitude: float,
        longitude: float,
        place_type: str = "tourist_attraction",
        radius: int = 5000,
        language: str = "en"
    ) -> List[Dict]:
        """
        Find nearby places
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            place_type: Type of place to search for
            radius: Search radius in meters (max 50000)
            language: Response language
            
        Returns:
            List of nearby places
        """
        if not self.enabled:
            return []
        
        try:
            result = self.gmaps.places_nearby(
                location=(latitude, longitude),
                radius=min(radius, 50000),  # Max 50km
                type=place_type,
                language=language
            )
            
            places = []
            for place in result.get('results', [])[:20]:  # Limit to 20 results
                places.append({
                    "name": place['name'],
                    "address": place.get('vicinity', ''),
                    "rating": place.get('rating'),
                    "user_ratings_total": place.get('user_ratings_total'),
                    "location": {
                        "lat": place['geometry']['location']['lat'],
                        "lng": place['geometry']['location']['lng']
                    },
                    "place_id": place['place_id'],
                    "types": place.get('types', []),
                    "open_now": place.get('opening_hours', {}).get('open_now')
                })
            
            return places
        except Exception as e:
            logger.error(f"Places API error: {e}")
            return []
    
    @cached(ttl=3600, prefix="maps:distance")
    async def calculate_distance(
        self,
        origins: List[str],
        destinations: List[str],
        mode: str = "driving"
    ) -> Optional[Dict]:
        """
        Calculate distance matrix between multiple origins and destinations
        
        Args:
            origins: List of origin addresses
            destinations: List of destination addresses
            mode: Travel mode
            
        Returns:
            Distance matrix data
        """
        if not self.enabled:
            return None
        
        try:
            result = self.gmaps.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode=mode
            )
            
            return {
                "origin_addresses": result['origin_addresses'],
                "destination_addresses": result['destination_addresses'],
                "rows": [
                    {
                        "elements": [
                            {
                                "distance": elem.get('distance', {}),
                                "duration": elem.get('duration', {}),
                                "status": elem['status']
                            }
                            for elem in row['elements']
                        ]
                    }
                    for row in result['rows']
                ]
            }
        except Exception as e:
            logger.error(f"Distance Matrix API error: {e}")
            return None
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates
        
        Args:
            address: Address string
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        if not self.enabled:
            return None
        
        try:
            result = self.gmaps.geocode(address)
            
            if result:
                location = result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Formatted address string or None
        """
        if not self.enabled:
            return None
        
        try:
            result = self.gmaps.reverse_geocode((latitude, longitude))
            
            if result:
                return result[0]['formatted_address']
            
            return None
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    def _get_mock_directions(self, origin: str, destination: str) -> Dict:
        """Mock directions when Google Maps is not available"""
        return {
            "distance": {"text": "25 km", "value": 25000},
            "duration": {"text": "45 mins", "value": 2700},
            "start_address": origin,
            "end_address": destination,
            "steps": [
                {
                    "instruction": f"Head towards {destination}",
                    "distance": "25 km",
                    "duration": "45 mins",
                    "travel_mode": "DRIVING"
                }
            ],
            "mock": True
        }


# Singleton instance
maps_service = MapsService()
