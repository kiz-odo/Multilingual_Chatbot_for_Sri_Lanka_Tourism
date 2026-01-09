"""
Weather API Integration Service
Provides weather data and forecasts for Sri Lankan locations
"""

import logging
from typing import List, Dict, Optional
import httpx
from datetime import datetime

from backend.app.core.config import settings
from backend.app.services.cache_service import cached
from backend.app.core.circuit_breaker import call_external_api_with_circuit_breaker, call_with_fallback

logger = logging.getLogger(__name__)


class WeatherService:
    """OpenWeatherMap API service"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        """Initialize weather service"""
        self.api_key = settings.OPENWEATHER_API_KEY
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info("Weather service initialized")
        else:
            logger.warning("Weather service disabled - no API key")
    
    @cached(ttl=1800, prefix="weather:current")  # Cache for 30 minutes
    async def get_current_weather(
        self,
        city: str = "Colombo",
        units: str = "metric",
        language: str = "en"
    ) -> Optional[Dict]:
        """
        Get current weather for a city
        
        Uses circuit breaker pattern to prevent cascading failures
        
        Args:
            city: City name (default: Colombo)
            units: Temperature units (metric, imperial, standard)
            language: Response language
            
        Returns:
            Current weather data or None
        """
        if not self.enabled:
            return self._get_mock_weather(city)
        
        try:
            # Call with circuit breaker protection
            result = await call_external_api_with_circuit_breaker(
                service_name="openweather",
                url=f"{self.BASE_URL}/weather",
                method="GET",
                timeout=10,
                params={
                    "q": f"{city},LK",  # LK for Sri Lanka
                    "appid": self.api_key,
                    "units": units,
                    "lang": language
                }
            )
            
            if result:
                return {
                    "city": result['name'],
                    "country": result['sys']['country'],
                    "temperature": result['main']['temp'],
                    "feels_like": result['main']['feels_like'],
                    "temp_min": result['main']['temp_min'],
                    "temp_max": result['main']['temp_max'],
                    "humidity": result['main']['humidity'],
                    "pressure": result['main']['pressure'],
                    "description": result['weather'][0]['description'],
                    "main": result['weather'][0]['main'],
                    "icon": result['weather'][0]['icon'],
                    "wind_speed": result['wind']['speed'],
                    "wind_direction": result['wind'].get('deg'),
                    "clouds": result['clouds']['all'],
                    "visibility": result.get('visibility'),
                    "sunrise": datetime.fromtimestamp(result['sys']['sunrise']).isoformat(),
                    "sunset": datetime.fromtimestamp(result['sys']['sunset']).isoformat(),
                    "timestamp": datetime.fromtimestamp(result['dt']).isoformat()
                }
            else:
                # Fallback to mock data if API fails
                logger.warning(f"Weather API unavailable for {city}, using mock data")
                return self._get_mock_weather(city)
                
        except Exception as e:
            logger.error(f"Weather API request error: {e}")
            return self._get_mock_weather(city)
    
    @cached(ttl=3600, prefix="weather:forecast")  # Cache for 1 hour
    async def get_forecast(
        self,
        city: str = "Colombo",
        days: int = 5,
        units: str = "metric",
        language: str = "en"
    ) -> List[Dict]:
        """
        Get weather forecast
        
        Args:
            city: City name
            days: Number of days (1-5)
            units: Temperature units
            language: Response language
            
        Returns:
            List of forecast data
        """
        if not self.enabled:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/forecast",
                    params={
                        "q": f"{city},LK",
                        "appid": self.api_key,
                        "units": units,
                        "lang": language,
                        "cnt": min(days * 8, 40)  # 8 forecasts per day, max 40
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    forecasts = []
                    
                    for item in data['list']:
                        forecasts.append({
                            "date": datetime.fromtimestamp(item['dt']).isoformat(),
                            "temperature": item['main']['temp'],
                            "feels_like": item['main']['feels_like'],
                            "temp_min": item['main']['temp_min'],
                            "temp_max": item['main']['temp_max'],
                            "humidity": item['main']['humidity'],
                            "description": item['weather'][0]['description'],
                            "main": item['weather'][0]['main'],
                            "icon": item['weather'][0]['icon'],
                            "wind_speed": item['wind']['speed'],
                            "clouds": item['clouds']['all'],
                            "rain_3h": item.get('rain', {}).get('3h', 0)
                        })
                    
                    return forecasts
                else:
                    logger.error(f"Forecast API error: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Forecast API request error: {e}")
            return []
    
    async def get_weather_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        units: str = "metric"
    ) -> Optional[Dict]:
        """
        Get weather by coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units
            
        Returns:
            Weather data or None
        """
        if not self.enabled:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/weather",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": units
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temperature": data['main']['temp'],
                        "description": data['weather'][0]['description'],
                        "humidity": data['main']['humidity'],
                        "wind_speed": data['wind']['speed']
                    }
                
                return None
        except Exception as e:
            logger.error(f"Weather by coordinates error: {e}")
            return None
    
    def get_weather_recommendation(self, weather_data: Dict) -> Dict:
        """
        Get recommendations based on weather
        
        Args:
            weather_data: Current weather data
            
        Returns:
            Dictionary with recommendations
        """
        temp = weather_data.get('temperature', 25)
        description = weather_data.get('description', '').lower()
        
        recommendations = {
            "suitable_for_outdoor": True,
            "clothing": [],
            "warnings": []
        }
        
        # Temperature recommendations
        if temp > 32:
            recommendations["clothing"].append("Light, breathable clothing")
            recommendations["clothing"].append("Sunscreen and hat")
            recommendations["warnings"].append("Very hot - stay hydrated")
        elif temp > 28:
            recommendations["clothing"].append("Light summer clothes")
            recommendations["clothing"].append("Sunglasses recommended")
        elif temp < 20:
            recommendations["clothing"].append("Light jacket recommended")
        
        # Weather condition recommendations
        if "rain" in description or "drizzle" in description:
            recommendations["suitable_for_outdoor"] = False
            recommendations["clothing"].append("Umbrella and raincoat")
            recommendations["warnings"].append("Rainy weather - indoor activities recommended")
        elif "thunderstorm" in description:
            recommendations["suitable_for_outdoor"] = False
            recommendations["warnings"].append("Thunderstorm - stay indoors")
        elif "cloud" in description:
            recommendations["suitable_for_outdoor"] = True
            recommendations["clothing"].append("Light layers")
        
        return recommendations
    
    def _get_mock_weather(self, city: str) -> Dict:
        """Mock weather data when API is not available"""
        return {
            "city": city,
            "country": "LK",
            "temperature": 28,
            "feels_like": 30,
            "temp_min": 26,
            "temp_max": 31,
            "humidity": 75,
            "description": "partly cloudy",
            "main": "Clouds",
            "icon": "02d",
            "wind_speed": 3.5,
            "mock": True
        }


# Singleton instance
weather_service = WeatherService()
