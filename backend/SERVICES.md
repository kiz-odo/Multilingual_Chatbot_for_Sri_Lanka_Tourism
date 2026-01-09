# 🔧 Services Documentation

Complete documentation of all service layer components in the backend.

## Overview

Services encapsulate business logic and provide a clean interface between the API layer and data access layer. All services follow the service pattern with dependency injection.

## Service Architecture

```
API Layer (Routes)
    ↓
Service Layer (Business Logic)
    ↓
Data Access Layer (Models/Repository)
    ↓
Database (MongoDB) / Cache (Redis)
```

## Core Services

### 1. ChatService

**Location**: `backend/app/services/chat_service.py`

**Purpose**: Manages chat conversations and messages.

**Key Methods**:
- `send_message()`: Process and respond to user messages
- `detect_language()`: Detect language of input text
- `get_conversations()`: Retrieve user conversations
- `create_conversation()`: Create new conversation
- `delete_conversation()`: Delete conversation

**Dependencies**:
- `HybridChatService`: AI query processing
- `UserService`: User data access
- `TranslationService`: Language translation

**Usage Example**:
```python
from backend.app.services.chat_service import ChatService

chat_service = ChatService()
response = await chat_service.send_message(
    message="What are the best beaches?",
    user_id="user123",
    language="en"
)
```

### 2. HybridChatService

**Location**: `backend/app/services/hybrid_chat_service.py`

**Purpose**: Intelligent query routing between Rasa NLU and LLM.

**Key Methods**:
- `process_message()`: Route query to appropriate AI system
- `should_use_llm()`: Determine if query requires LLM
- `get_rasa_response()`: Get response from Rasa
- `get_llm_response()`: Get response from LLM

**Routing Logic**:
- **Rasa**: Simple queries, structured intents (high confidence)
- **LLM**: Complex queries, open-ended questions, low confidence

**Dependencies**:
- `RasaService`: Rasa NLU integration
- `LLMService`: LLM orchestration
- `TranslationService`: Language translation

### 3. LLMService

**Location**: `backend/app/services/llm_service.py`

**Purpose**: Orchestrates multiple LLM providers with fallback chain.

**LLM Providers** (in order):
1. **Gemini** (Primary) - Google Gemini API
2. **Qwen** (Fallback 1) - Alibaba Qwen API
3. **Mistral** (Fallback 2) - Mistral AI API

**Key Methods**:
- `generate()`: Generate response using LLM
- `generate_with_context()`: Generate with conversation context
- `get_provider()`: Get available LLM provider

**Fallback Strategy**:
- Try providers in order
- Use circuit breaker to prevent cascading failures
- Cache responses for similar queries

**Dependencies**:
- `GeminiService`: Google Gemini integration
- `QwenService`: Qwen API integration
- `MistralService`: Mistral AI integration
- `CacheService`: Response caching

### 4. RasaService

**Location**: `backend/app/services/rasa_service.py`

**Purpose**: Integrates with Rasa NLU for intent classification.

**Key Methods**:
- `parse_message()`: Parse message and get intent
- `get_response()`: Get Rasa response
- `train_model()`: Trigger Rasa model training

**Rasa Integration**:
- Rasa server runs in separate Docker container
- Communication via HTTP API
- Supports 7 languages

**Dependencies**:
- HTTP client for Rasa API calls

### 5. AuthService

**Location**: `backend/app/services/auth_service.py`

**Purpose**: Handles authentication and authorization.

**Key Methods**:
- `register_user()`: Register new user
- `authenticate_user()`: Authenticate user credentials
- `create_access_token()`: Generate JWT access token
- `create_refresh_token()`: Generate JWT refresh token
- `verify_token()`: Verify JWT token
- `enable_mfa()`: Enable multi-factor authentication
- `verify_mfa()`: Verify MFA code

**Security Features**:
- Password hashing with bcrypt
- JWT token generation and validation
- MFA support (TOTP)
- Token refresh mechanism

**Dependencies**:
- `UserService`: User data access
- `CacheService`: Token storage and revocation

### 6. UserService

**Location**: `backend/app/services/user_service.py`

**Purpose**: Manages user data and profiles.

**Key Methods**:
- `get_user_by_id()`: Get user by ID
- `get_user_by_email()`: Get user by email
- `create_user()`: Create new user
- `update_user()`: Update user profile
- `delete_user()`: Delete user account
- `get_user_stats()`: Get user statistics

**Dependencies**:
- User model (Beanie ODM)
- `CacheService`: User data caching

### 7. TranslationService

**Location**: `backend/app/services/translation_service.py`

**Purpose**: Provides multi-language translation.

**Supported Languages**:
- Sinhala (si)
- Tamil (ta)
- English (en)
- German (de)
- French (fr)
- Chinese (zh)
- Japanese (ja)

**Key Methods**:
- `translate()`: Translate text between languages
- `detect_language()`: Detect language of text
- `get_supported_languages()`: Get list of supported languages

**Translation Providers**:
- Google Translate API (primary)
- Deep Translator (fallback)

**Dependencies**:
- Google Cloud Translate API
- Deep Translator library

### 8. RecommendationService

**Location**: `backend/app/services/recommendation_service.py`

**Purpose**: Provides personalized recommendations.

**Key Methods**:
- `get_recommendations()`: Get personalized recommendations
- `get_similar_items()`: Get similar items
- `get_location_based_recommendations()`: Recommendations based on location

**Recommendation Types**:
- Attraction recommendations
- Hotel recommendations
- Restaurant recommendations
- Itinerary suggestions

**Algorithm**:
- Collaborative filtering
- Content-based filtering
- Location-based filtering

**Dependencies**:
- Attraction, Hotel, Restaurant models
- User preferences
- `CacheService`: Recommendation caching

### 9. ItineraryService

**Location**: `backend/app/services/itinerary_service.py`

**Purpose**: Manages trip itineraries and planning.

**Key Methods**:
- `generate_itinerary()`: Generate itinerary using AI
- `get_itinerary()`: Get itinerary by ID
- `update_itinerary()`: Update itinerary
- `delete_itinerary()`: Delete itinerary
- `share_itinerary()`: Generate shareable link
- `export_pdf()`: Export itinerary as PDF
- `export_calendar()`: Export as calendar file

**Itinerary Generation**:
- Uses LLM to generate personalized itineraries
- Considers user preferences, budget, duration
- Includes attractions, hotels, restaurants, transport

**Dependencies**:
- `LLMService`: AI-powered itinerary generation
- `AttractionService`: Attraction data
- `HotelService`: Hotel data
- `RestaurantService`: Restaurant data

### 10. AttractionService

**Location**: `backend/app/services/attraction_service.py`

**Purpose**: Manages tourist attraction data.

**Key Methods**:
- `get_attractions()`: List attractions with filters
- `get_attraction_by_id()`: Get attraction details
- `search_attractions()`: Search attractions
- `get_nearby_attractions()`: Get attractions near location
- `get_featured_attractions()`: Get featured attractions

**Dependencies**:
- Attraction model (Beanie ODM)
- `CacheService`: Attraction data caching

### 11. WeatherService

**Location**: `backend/app/services/weather_service.py`

**Purpose**: Provides weather information.

**Key Methods**:
- `get_current_weather()`: Get current weather
- `get_forecast()`: Get weather forecast
- `get_weather_alerts()`: Get weather alerts
- `get_weather_recommendations()`: Get recommendations based on weather

**Weather Provider**:
- OpenWeatherMap API

**Dependencies**:
- OpenWeatherMap API client
- `CacheService`: Weather data caching (TTL: 1 hour)

### 12. CurrencyService

**Location**: `backend/app/services/currency_service.py`

**Purpose**: Provides currency conversion and exchange rates.

**Key Methods**:
- `convert_currency()`: Convert between currencies
- `get_exchange_rates()`: Get exchange rates
- `get_sri_lanka_rates()`: Get LKR exchange rates
- `format_currency()`: Format currency amount

**Currency Provider**:
- CurrencyLayer API

**Dependencies**:
- CurrencyLayer API client
- `CacheService`: Exchange rate caching (TTL: 1 hour)

### 13. MapsService

**Location**: `backend/app/services/maps_service.py`

**Purpose**: Provides maps and location services.

**Key Methods**:
- `geocode()`: Convert address to coordinates
- `reverse_geocode()`: Convert coordinates to address
- `search_places()`: Search for places
- `get_directions()`: Get directions between locations
- `get_nearby_places()`: Get nearby places

**Maps Provider**:
- Google Maps API

**Dependencies**:
- Google Maps API client
- `CacheService`: Geocoding result caching

### 14. SafetyService

**Location**: `backend/app/services/safety_service.py`

**Purpose**: Manages safety features and emergency services.

**Key Methods**:
- `send_sos_alert()`: Send SOS emergency alert
- `get_safety_score()`: Get safety score for location
- `get_travel_alerts()`: Get travel alerts
- `get_emergency_numbers()`: Get emergency contact numbers
- `start_location_sharing()`: Start location sharing

**Dependencies**:
- Emergency model
- Notification service
- Location tracking

### 15. CacheService

**Location**: `backend/app/services/cache_service.py`

**Purpose**: Provides caching functionality using Redis.

**Key Methods**:
- `get()`: Get value from cache
- `set()`: Set value in cache
- `delete()`: Delete value from cache
- `exists()`: Check if key exists
- `increment()`: Increment counter
- `get_or_set()`: Get or set with default

**Cache Patterns**:
- Write-through cache
- TTL-based expiration
- Cache invalidation

**Dependencies**:
- Redis client

### 16. EmailVerificationService

**Location**: `backend/app/services/email_verification_service.py`

**Purpose**: Handles email verification.

**Key Methods**:
- `send_verification_email()`: Send verification email
- `verify_email()`: Verify email with token
- `resend_verification()`: Resend verification email

**Dependencies**:
- Celery tasks for async email sending
- SMTP configuration

### 17. OAuthService

**Location**: `backend/app/services/oauth_service.py`

**Purpose**: Handles OAuth2 social login.

**Supported Providers**:
- Google OAuth2
- Facebook OAuth2 (future)
- Apple OAuth2 (future)

**Key Methods**:
- `authenticate_google()`: Authenticate with Google
- `get_user_info()`: Get user info from provider

**Dependencies**:
- Google Auth library
- OAuth2 configuration

### 18. LandmarkRecognitionService

**Location**: `backend/app/services/landmark_recognition_service.py`

**Purpose**: Recognizes landmarks from images.

**Key Methods**:
- `recognize_landmark()`: Recognize landmark from image
- `get_landmark_info()`: Get information about landmark

**Technology**:
- Computer vision (OpenCV)
- Machine learning models (optional)

**Dependencies**:
- OpenCV
- Image processing libraries

### 19. SpeechService

**Location**: `backend/app/services/speech_service.py`

**Purpose**: Handles speech-to-text and text-to-speech.

**Key Methods**:
- `speech_to_text()`: Convert speech to text
- `text_to_speech()`: Convert text to speech

**Providers**:
- Google Cloud Speech API
- Google Cloud Text-to-Speech API

**Dependencies**:
- Google Cloud Speech libraries

### 20. PDFExportService

**Location**: `backend/app/services/pdf_export_service.py`

**Purpose**: Exports data to PDF format.

**Key Methods**:
- `export_itinerary_pdf()`: Export itinerary as PDF
- `export_report_pdf()`: Export report as PDF

**Dependencies**:
- ReportLab library

### 21. CalendarExportService

**Location**: `backend/app/services/calendar_export_service.py`

**Purpose**: Exports data to calendar format (ICS, Google Calendar).

**Key Methods**:
- `export_ics()`: Export as ICS file
- `export_google_calendar()`: Export to Google Calendar

**Dependencies**:
- Google Calendar API
- ICS file generation

### 22. GDPRExportService

**Location**: `backend/app/services/gdpr_export_service.py`

**Purpose**: Exports user data for GDPR compliance.

**Key Methods**:
- `export_user_data()`: Export all user data
- `delete_user_data()`: Delete user data (GDPR right to be forgotten)

**Dependencies**:
- User model and related models

## Service Dependencies

### Dependency Graph

```
ChatService
  ├── HybridChatService
  │     ├── RasaService
  │     ├── LLMService
  │     │     ├── GeminiService
  │     │     ├── QwenService
  │     │     └── MistralService
  │     └── TranslationService
  └── UserService
        └── CacheService

ItineraryService
  ├── LLMService
  ├── AttractionService
  ├── HotelService
  └── RestaurantService

RecommendationService
  ├── AttractionService
  ├── HotelService
  └── RestaurantService
```

## Service Best Practices

### 1. Single Responsibility

Each service has a single, well-defined responsibility.

### 2. Dependency Injection

Services are injected via FastAPI's dependency system:

```python
from fastapi import Depends

def get_chat_service() -> ChatService:
    return ChatService()

@router.post("/message")
async def send_message(
    service: ChatService = Depends(get_chat_service)
):
    return await service.send_message(...)
```

### 3. Error Handling

Services raise domain-specific exceptions:

```python
from backend.app.core.exceptions import NotFoundError

async def get_user(user_id: str):
    user = await User.find_one(User.id == user_id)
    if not user:
        raise NotFoundError("User not found")
    return user
```

### 4. Caching

Services use caching for frequently accessed data:

```python
from backend.app.services.cache_service import CacheService

cache_key = f"user:{user_id}"
user = await cache_service.get_or_set(
    cache_key,
    lambda: await get_user_from_db(user_id),
    ttl=3600
)
```

### 5. Async Operations

All service methods are async for non-blocking I/O:

```python
async def get_attractions(self, filters: dict):
    return await Attraction.find_all(filters).to_list()
```

## Testing Services

Services are tested with unit tests:

```python
import pytest
from backend.app.services.chat_service import ChatService

@pytest.mark.asyncio
async def test_send_message():
    service = ChatService()
    response = await service.send_message(...)
    assert response is not None
```

See [TESTING.md](./TESTING.md) for detailed testing guide.

