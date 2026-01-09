"""
Unit tests for weather service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.app.services.weather_service import WeatherService


class TestWeatherService:
    """Test weather service methods"""
    
    @pytest.fixture
    def weather_service(self):
        """Create weather service instance"""
        with patch('backend.app.services.weather_service.settings') as mock_settings:
            mock_settings.OPENWEATHER_API_KEY = "test_api_key"
            service = WeatherService()
            return service
    
    @pytest.fixture
    def weather_service_disabled(self):
        """Create disabled weather service instance"""
        with patch('backend.app.services.weather_service.settings') as mock_settings:
            mock_settings.OPENWEATHER_API_KEY = None
            service = WeatherService()
            return service
    
    @pytest.fixture
    def sample_weather_response(self):
        """Sample OpenWeather API response"""
        return {
            "name": "Colombo",
            "sys": {
                "country": "LK",
                "sunrise": 1703558400,
                "sunset": 1703601600
            },
            "main": {
                "temp": 28.5,
                "feels_like": 32.0,
                "temp_min": 26.0,
                "temp_max": 30.0,
                "humidity": 75,
                "pressure": 1012
            },
            "weather": [
                {
                    "description": "partly cloudy",
                    "main": "Clouds",
                    "icon": "03d"
                }
            ],
            "wind": {
                "speed": 5.5,
                "deg": 180
            },
            "clouds": {
                "all": 40
            },
            "visibility": 10000,
            "dt": 1703580000
        }
    
    def test_weather_service_initialization_with_key(self, weather_service):
        """Test weather service initializes with API key"""
        assert weather_service.enabled is True
        assert weather_service.api_key == "test_api_key"
    
    def test_weather_service_initialization_without_key(self, weather_service_disabled):
        """Test weather service disabled without API key"""
        assert weather_service_disabled.enabled is False
    
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, weather_service, sample_weather_response):
        """Test getting current weather successfully"""
        with patch('backend.app.services.weather_service.call_external_api_with_circuit_breaker', 
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_weather_response
            
            weather = await weather_service.get_current_weather("Colombo")
            
            assert weather is not None
            assert weather["city"] == "Colombo"
            assert weather["country"] == "LK"
            assert weather["temperature"] == 28.5
            assert weather["humidity"] == 75
    
    @pytest.mark.asyncio
    async def test_get_current_weather_api_error(self, weather_service):
        """Test getting weather with API error falls back to mock"""
        with patch('backend.app.services.weather_service.call_external_api_with_circuit_breaker',
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = None
            
            weather = await weather_service.get_current_weather("Colombo")
            
            assert weather is not None
            # Should return mock data
            assert "city" in weather
    
    @pytest.mark.asyncio
    async def test_get_current_weather_disabled_service(self, weather_service_disabled):
        """Test getting weather when service is disabled"""
        weather = await weather_service_disabled.get_current_weather("Colombo")
        
        # Should return mock data
        assert weather is not None
        assert "city" in weather
    
    @pytest.mark.asyncio
    async def test_get_current_weather_different_cities(self, weather_service, sample_weather_response):
        """Test getting weather for different cities"""
        cities = ["Colombo", "Kandy", "Galle", "Jaffna", "Trincomalee"]
        
        with patch('backend.app.services.weather_service.call_external_api_with_circuit_breaker',
                   new_callable=AsyncMock) as mock_api:
            for city in cities:
                sample_weather_response["name"] = city
                mock_api.return_value = sample_weather_response
                
                weather = await weather_service.get_current_weather(city)
                
                assert weather is not None
                assert weather["city"] == city
    
    @pytest.mark.asyncio
    async def test_get_current_weather_different_units(self, weather_service, sample_weather_response):
        """Test getting weather with different units"""
        with patch('backend.app.services.weather_service.call_external_api_with_circuit_breaker',
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = sample_weather_response
            
            # Test metric
            weather_metric = await weather_service.get_current_weather("Colombo", units="metric")
            assert weather_metric is not None
            
            # Test imperial
            weather_imperial = await weather_service.get_current_weather("Colombo", units="imperial")
            assert weather_imperial is not None
    
    @pytest.mark.asyncio
    async def test_get_current_weather_exception_handling(self, weather_service):
        """Test exception handling in get current weather"""
        with patch('backend.app.services.weather_service.call_external_api_with_circuit_breaker',
                   new_callable=AsyncMock) as mock_api:
            mock_api.side_effect = Exception("Network error")
            
            weather = await weather_service.get_current_weather("Colombo")
            
            # Should return mock data on exception
            assert weather is not None


class TestWeatherServiceMockData:
    """Test weather service mock data functionality"""
    
    @pytest.fixture
    def weather_service(self):
        """Create weather service with disabled API"""
        with patch('backend.app.services.weather_service.settings') as mock_settings:
            mock_settings.OPENWEATHER_API_KEY = None
            return WeatherService()
    
    @pytest.mark.asyncio
    async def test_mock_weather_has_required_fields(self, weather_service):
        """Test mock weather data has all required fields"""
        weather = await weather_service.get_current_weather("Colombo")
        
        required_fields = [
            "city", "temperature", "humidity", "description"
        ]
        
        for field in required_fields:
            assert field in weather, f"Missing required field: {field}"
    
    @pytest.mark.asyncio
    async def test_mock_weather_reasonable_values(self, weather_service):
        """Test mock weather data has reasonable values"""
        weather = await weather_service.get_current_weather("Colombo")
        
        # Sri Lanka tropical climate checks
        assert 20 <= weather.get("temperature", 0) <= 40
        assert 0 <= weather.get("humidity", 0) <= 100
