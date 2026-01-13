"""
API v1 router
"""

from fastapi import APIRouter

from backend.app.api.v1 import (
    auth,
    users,
    chat,
    attractions,
    restaurants,
    hotels,
    transport,
    emergency,
    events,
    feedback,
    admin,
    maps,
    weather,
    currency,
    email_verification,
    itinerary,
    safety,
    oauth,
    challenges,
    forum,
    recommendations,
    landmarks,
    speech
)

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat & AI"])
api_router.include_router(attractions.router, prefix="/attractions", tags=["Attractions"])
api_router.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
api_router.include_router(transport.router, prefix="/transport", tags=["Transport"])
api_router.include_router(emergency.router, prefix="/emergency", tags=["Emergency Services"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(maps.router, prefix="/maps", tags=["Maps & Location"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(currency.router, prefix="/currency", tags=["Currency"])
api_router.include_router(email_verification.router, prefix="/email", tags=["Email Verification"])
api_router.include_router(itinerary.router, prefix="/itinerary", tags=["Itinerary & Trip Planning"])
api_router.include_router(safety.router, prefix="/safety", tags=["Safety & Emergency"])
api_router.include_router(oauth.router, tags=["OAuth2 Social Login"])
api_router.include_router(challenges.router, tags=["Challenges"])
api_router.include_router(forum.router, tags=["Forum"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(landmarks.router, tags=["Landmarks"])
api_router.include_router(speech.router, prefix="/speech", tags=["Speech & Voice"])
