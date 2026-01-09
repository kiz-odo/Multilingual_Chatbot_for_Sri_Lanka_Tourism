"""
OpenWeatherMap API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.app.models.user import User
from backend.app.core.auth import get_optional_user
from backend.app.services.weather_service import WeatherService

router = APIRouter()


class WeatherResponse(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    visibility: int
    wind_speed: float
    wind_direction: int
    condition: Dict[str, str]
    timestamp: datetime


class ForecastResponse(BaseModel):
    date: datetime
    temperature_min: float
    temperature_max: float
    condition: Dict[str, str]
    humidity: int
    wind_speed: float
    precipitation_chance: float


class WeatherAlertResponse(BaseModel):
    sender_name: str
    event: str
    start: datetime
    end: datetime
    description: str
    tags: List[str]


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    city: str = Query("colombo", description="City name"),
    latitude: Optional[float] = Query(None, description="Latitude"),
    longitude: Optional[float] = Query(None, description="Longitude"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get current weather for a city or coordinates"""
    try:
        weather_service = WeatherService()
        
        coordinates = None
        if latitude and longitude:
            coordinates = {"lat": latitude, "lon": longitude}
        
        weather = await weather_service.get_current_weather(city, coordinates)
        
        if not weather:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weather data not available"
            )
        
        return WeatherResponse(
            temperature=weather.temperature,
            feels_like=weather.feels_like,
            humidity=weather.humidity,
            pressure=weather.pressure,
            visibility=weather.visibility,
            wind_speed=weather.wind_speed,
            wind_direction=weather.wind_direction,
            condition={
                "main": weather.condition.main,
                "description": weather.condition.description,
                "icon": weather.condition.icon
            },
            timestamp=weather.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting current weather: {str(e)}"
        )


@router.get("/forecast", response_model=List[ForecastResponse])
async def get_weather_forecast(
    city: str = Query("colombo", description="City name"),
    latitude: Optional[float] = Query(None, description="Latitude"),
    longitude: Optional[float] = Query(None, description="Longitude"),
    days: int = Query(5, description="Number of forecast days"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get weather forecast for a city or coordinates"""
    try:
        weather_service = WeatherService()
        
        coordinates = None
        if latitude and longitude:
            coordinates = {"lat": latitude, "lon": longitude}
        
        forecast = await weather_service.get_weather_forecast(city, coordinates, days)
        
        return [
            ForecastResponse(
                date=day.date,
                temperature_min=day.temperature_min,
                temperature_max=day.temperature_max,
                condition={
                    "main": day.condition.main,
                    "description": day.condition.description,
                    "icon": day.condition.icon
                },
                humidity=day.humidity,
                wind_speed=day.wind_speed,
                precipitation_chance=day.precipitation_chance
            )
            for day in forecast
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weather forecast: {str(e)}"
        )


@router.get("/alerts", response_model=List[WeatherAlertResponse])
async def get_weather_alerts(
    city: str = Query("colombo", description="City name"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get weather alerts for a city"""
    try:
        weather_service = WeatherService()
        alerts = await weather_service.get_weather_alerts(city)
        
        return [
            WeatherAlertResponse(
                sender_name=alert.get("sender_name", ""),
                event=alert.get("event", ""),
                start=datetime.fromtimestamp(alert.get("start", 0)),
                end=datetime.fromtimestamp(alert.get("end", 0)),
                description=alert.get("description", ""),
                tags=alert.get("tags", [])
            )
            for alert in alerts
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weather alerts: {str(e)}"
        )


@router.get("/summary")
async def get_weather_summary(
    city: str = Query("colombo", description="City name"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get comprehensive weather summary for tourists"""
    try:
        weather_service = WeatherService()
        summary = await weather_service.get_weather_summary_for_tourism(city)
        
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weather summary: {str(e)}"
        )


@router.get("/cities")
async def get_sri_lanka_cities():
    """Get list of major Sri Lankan cities with coordinates"""
    try:
        weather_service = WeatherService()
        cities = weather_service.get_sri_lanka_cities()
        
        return {"cities": cities}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cities: {str(e)}"
        )


@router.get("/recommendations")
async def get_weather_recommendations(
    city: str = Query("colombo", description="City name"),
    latitude: Optional[float] = Query(None, description="Latitude"),
    longitude: Optional[float] = Query(None, description="Longitude"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get weather-based recommendations for tourists"""
    try:
        weather_service = WeatherService()
        
        coordinates = None
        if latitude and longitude:
            coordinates = {"lat": latitude, "lon": longitude}
        
        weather = await weather_service.get_current_weather(city, coordinates)
        
        if not weather:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weather data not available"
            )
        
        recommendations = weather_service.get_weather_recommendations(weather)
        
        return {"recommendations": recommendations}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weather recommendations: {str(e)}"
        )


@router.get("/icon/{icon_code}")
async def get_weather_icon(icon_code: str):
    """Get weather icon URL"""
    try:
        weather_service = WeatherService()
        icon_url = weather_service.get_weather_icon_url(icon_code)
        
        return {"icon_url": icon_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weather icon: {str(e)}"
        )
