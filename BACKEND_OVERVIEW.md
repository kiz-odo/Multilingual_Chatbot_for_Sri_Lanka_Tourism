# 🚀 Backend Overview - Sri Lanka Tourism Multilingual Chatbot

## **Project Summary**

A **production-ready, enterprise-grade** FastAPI backend for the Sri Lanka Tourism Multilingual Chatbot system. Built with modern Python technologies, featuring async/await architecture, hybrid AI (Rasa NLU + LLM), and comprehensive tourism APIs.

---

## **🎯 Core Capabilities**

### **AI & Intelligence**
- 🤖 **Hybrid AI System**: Rasa NLU (structured) + LLM (complex queries)
- 🔄 **Multi-LLM Fallback**: Gemini → Qwen → Mistral (100% free chain)
- 🤝 **CrewAI Multi-Agent**: 5 specialized agents for complex tourism queries
- 🧠 **RAG (Retrieval Augmented Generation)**: Context-aware responses with FAISS
- 🔍 **Tavily AI Search**: Real-time web search integration

### **Multilingual Support**
- 🌍 **7 Languages**: English, Sinhala (සිංහල), Tamil (தமிழ்), German, French, Chinese, Japanese
- 🔄 **Auto Language Detection**: NLP-based language identification
- 🌐 **Google Translate API**: Real-time translation with free fallback

### **Tourism Features**
- 🏛️ **Attractions**: 200+ Sri Lankan attractions with details
- 🏨 **Hotels**: Hotel search, recommendations, booking info
- 🍽️ **Restaurants**: Restaurant search with cuisine filtering
- 📅 **Itinerary Planning**: AI-generated personalized trip plans
- 🗺️ **Maps Integration**: Google Maps (geocoding, places, directions, nearby)
- 🌤️ **Weather**: Real-time weather data and forecasts
- 🚗 **Transport**: Transport options and routes
- 🎭 **Events**: Cultural events and festivals
- 💱 **Currency**: Live exchange rates
- 🚨 **Emergency**: Emergency contacts, SOS, safety tips

---

## **🏗️ Technical Architecture**

### **Layered Architecture**

```
┌─────────────────────────────────────────────────┐
│        API Layer (FastAPI Routes)              │
│   REST (v1) │ GraphQL │ WebSocket              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Middleware Layer                      │
│   Auth │ Rate Limit │ CORS │ Error Handling    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Service Layer (Business Logic)          │
│   Chat │ Auth │ Translation │ LLM │ Rasa       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          Data Access Layer                      │
│   Models (Beanie ODM) │ Cache (Redis)          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Infrastructure Layer                     │
│   MongoDB │ Redis │ Celery │ External APIs      │
└─────────────────────────────────────────────────┘
```

### **Project Structure**

```
backend/
├── app/
│   ├── api/v1/                  # REST API endpoints (versioned)
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── chat.py             # Chat endpoints
│   │   ├── websocket.py        # WebSocket chat
│   │   ├── attractions.py      # Attraction endpoints
│   │   ├── hotels.py           # Hotel endpoints
│   │   ├── restaurants.py      # Restaurant endpoints
│   │   ├── itinerary.py        # Itinerary planning
│   │   ├── maps.py             # Maps integration (8 endpoints)
│   │   ├── weather.py          # Weather data (7 endpoints)
│   │   ├── currency.py         # Currency conversion (8 endpoints)
│   │   ├── transport.py        # Transport information
│   │   ├── events.py           # Events & festivals
│   │   ├── safety.py           # Safety information
│   │   ├── emergency.py        # Emergency services
│   │   ├── landmarks.py        # Landmark recognition
│   │   ├── recommendations.py  # Personalized recommendations
│   │   ├── forum.py            # Community forum
│   │   ├── feedback.py         # User feedback
│   │   ├── users.py            # User management
│   │   ├── oauth.py            # OAuth social login
│   │   ├── email_verification.py # Email verification
│   │   └── health.py           # Health checks
│   │
│   ├── graphql/                 # GraphQL API
│   │   ├── schema.py           # GraphQL schema
│   │   ├── resolvers.py        # Query/Mutation resolvers
│   │   └── types.py            # GraphQL types
│   │
│   ├── services/                # Business logic (28+ services)
│   │   ├── hybrid_chat_service.py      # AI query routing
│   │   ├── llm_service.py              # LLM orchestration
│   │   ├── rasa_service.py             # Rasa NLU integration
│   │   ├── crewai_service.py           # Multi-agent system
│   │   ├── translation_service.py      # Multi-language
│   │   ├── tavily_search_service.py    # AI search
│   │   ├── gemini_service.py           # Google Gemini API
│   │   ├── qwen_service.py             # Qwen AI API
│   │   ├── mistral_service.py          # Mistral AI API
│   │   ├── chat_service.py             # Chat management
│   │   ├── auth_service.py             # Authentication
│   │   ├── user_service.py             # User management
│   │   ├── maps_service.py             # Google Maps
│   │   ├── weather_service.py          # Weather API
│   │   ├── currency_service.py         # Currency API
│   │   ├── itinerary_service.py        # Trip planning
│   │   ├── recommendation_service.py   # Recommendations
│   │   ├── safety_service.py           # Safety info
│   │   ├── landmark_recognition_service.py # Image recognition
│   │   ├── email_verification_service.py # Email verification
│   │   ├── oauth_service.py            # OAuth integration
│   │   ├── speech_service.py           # Speech-to-text/TTS
│   │   ├── pdf_export_service.py       # PDF generation
│   │   ├── calendar_export_service.py  # Calendar export
│   │   ├── gdpr_export_service.py      # Data export
│   │   ├── cache_service.py            # Redis caching
│   │   └── attraction_service.py       # Attraction data
│   │
│   ├── models/                  # MongoDB ODM models (Beanie)
│   │   ├── user.py             # User model
│   │   ├── conversation.py     # Conversation & messages
│   │   ├── attraction.py       # Attraction model
│   │   ├── hotel.py            # Hotel model
│   │   ├── restaurant.py       # Restaurant model
│   │   ├── itinerary.py        # Itinerary model
│   │   ├── event.py            # Event model
│   │   ├── transport.py        # Transport model
│   │   ├── safety.py           # Safety info model
│   │   ├── emergency.py        # Emergency contact model
│   │   ├── forum.py            # Forum post model
│   │   ├── feedback.py         # Feedback model
│   │   ├── recommendation.py   # Recommendation model
│   │   ├── challenge.py        # Gamification challenges
│   │   ├── notification.py     # Notification model
│   │   ├── analytics.py        # Analytics model
│   │   └── security.py         # Security logs
│   │
│   ├── middleware/              # Middleware components
│   │   ├── request_id.py       # Request ID tracing
│   │   ├── rate_limit.py       # Rate limiting
│   │   ├── distributed_rate_limit.py # Distributed rate limiting
│   │   ├── cors_middleware.py  # CORS handling
│   │   ├── security_headers.py # Security headers
│   │   ├── error_handler.py    # Error handling
│   │   ├── api_versioning.py   # API versioning
│   │   ├── request_timeout.py  # Request timeout
│   │   ├── cache_headers.py    # HTTP caching
│   │   └── websocket_security.py # WebSocket security
│   │
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Configuration (Pydantic Settings)
│   │   ├── database.py         # MongoDB connection
│   │   ├── database_indexes.py # Database indexes
│   │   ├── migrations.py       # Database migrations
│   │   ├── auth.py             # JWT authentication
│   │   ├── logging_config.py   # Logging configuration
│   │   ├── metrics.py          # Prometheus metrics
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   ├── db_retry.py         # Database retry logic
│   │   ├── cache_decorator.py  # Caching decorator
│   │   └── celery_app.py       # Celery configuration
│   │
│   ├── tasks/                   # Celery background tasks
│   │   ├── email_tasks.py      # Email sending
│   │   ├── notification_tasks.py # Push notifications
│   │   ├── analytics_tasks.py  # Analytics processing
│   │   └── data_tasks.py       # Data processing
│   │
│   └── main.py                  # FastAPI app entry point
│
├── rasa/                        # Rasa NLU chatbot
│   ├── config.yml              # Rasa configuration
│   ├── domain.yml              # Rasa domain
│   ├── data/                   # Training data
│   │   ├── nlu.yml            # NLU training data
│   │   └── stories.yml        # Conversation stories
│   └── models/                 # Trained models
│
├── tests/                       # Comprehensive test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── api/                    # API endpoint tests
│   ├── security_tests/         # Security tests
│   └── conftest.py             # Pytest configuration
│
└── logs/                        # Application logs
    ├── app.log                 # Main application log
    └── app_errors.log          # Error log
```

---

## **🛠️ Technology Stack**

### **Core Framework**
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.109.2 | High-performance async API framework |
| **Uvicorn** | 0.27.1 | ASGI server |
| **Pydantic** | 2.7.4+ | Data validation & settings |
| **Python** | 3.9+ | Programming language |

### **Database & Storage**
| Technology | Version | Purpose |
|------------|---------|---------|
| **MongoDB** | 6.0+ | Document database |
| **Beanie** | 1.24.0 | Async MongoDB ODM |
| **Motor** | 3.3.2 | Async MongoDB driver |
| **Redis** | 7.0+ | Caching & sessions |

### **AI & Machine Learning**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Rasa** | 3.6 | NLU intent classification |
| **LangChain** | 0.3.1+ | LLM orchestration |
| **Google Gemini** | Latest | Primary LLM |
| **Qwen** | Latest | Fallback LLM #1 |
| **Mistral** | Latest | Fallback LLM #2 |
| **CrewAI** | 0.1.0+ | Multi-agent framework |
| **FAISS** | 1.8.0 | Vector similarity search |
| **sentence-transformers** | 2.3.1 | Semantic embeddings |
| **spaCy** | 3.7.2 | NLP processing |
| **NLTK** | 3.8.1 | Natural language toolkit |

### **External APIs**
| API | Purpose |
|-----|---------|
| **Google Translate** | Translation (with free fallback) |
| **Google Maps** | Maps, geocoding, places, directions |
| **Tavily AI** | AI-optimized web search |
| **OpenWeather** | Weather data & forecasts |
| **CurrencyLayer** | Exchange rates |
| **Google OAuth** | Social login |
| **Sentry** | Error tracking |

### **Background Processing**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Celery** | 5.3.4 | Distributed task queue |
| **Redis** | 7.0+ | Celery broker |

### **Authentication & Security**
| Technology | Version | Purpose |
|------------|---------|---------|
| **python-jose** | 3.3.0 | JWT tokens |
| **passlib** | 1.7.4 | Password hashing |
| **bcrypt** | 4.1.2 | Hashing algorithm |
| **pyotp** | 2.9.0 | MFA/2FA (TOTP) |
| **bleach** | 6.1.0 | XSS sanitization |

### **Monitoring & Observability**
| Technology | Purpose |
|------------|---------|
| **Prometheus** | Metrics collection |
| **Grafana** | Metrics visualization |
| **Sentry** | Error tracking |
| **OpenTelemetry** | Distributed tracing |
| **Structured Logging** | JSON logs |

---

## **📡 API Endpoints (100+ Endpoints)**

### **Endpoint Categories (25+)**

#### **1. Authentication** (`/api/v1/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /refresh` - Token refresh
- `GET /me` - Get current user
- `PUT /me` - Update current user
- `POST /change-password` - Change password
- `POST /enable-mfa` - Enable MFA/2FA
- `POST /verify-mfa` - Verify MFA code
- `POST /disable-mfa` - Disable MFA

#### **2. Chat** (`/api/v1/chat`)
- `POST /message` - Send chat message
- `GET /conversations` - Get conversations
- `POST /conversations` - Create conversation
- `GET /conversations/{id}` - Get conversation details
- `DELETE /conversations/{id}` - Delete conversation
- `PUT /conversations/{id}` - Update conversation
- `POST /detect-language` - Detect message language
- `WebSocket /ws/chat` - Real-time chat

#### **3. Attractions** (`/api/v1/attractions`)
- `GET /` - List all attractions
- `GET /{id}` - Get attraction details
- `GET /search` - Search attractions
- `GET /categories` - Get categories
- `GET /popular` - Get popular attractions
- `GET /nearby` - Get nearby attractions
- `POST /recommend` - Get recommendations

#### **4. Hotels** (`/api/v1/hotels`)
- `GET /` - List hotels
- `GET /{id}` - Get hotel details
- `GET /search` - Search hotels
- `GET /popular` - Popular hotels
- `POST /recommend` - Hotel recommendations

#### **5. Restaurants** (`/api/v1/restaurants`)
- `GET /` - List restaurants
- `GET /{id}` - Get restaurant details
- `GET /search` - Search restaurants
- `GET /cuisines` - Get cuisines
- `POST /recommend` - Restaurant recommendations

#### **6. Itinerary** (`/api/v1/itinerary`)
- `POST /generate` - Generate AI itinerary
- `GET /my-trips` - Get user trips
- `POST /save` - Save trip
- `GET /{id}` - Get trip details
- `PUT /{id}` - Update trip
- `DELETE /{id}` - Delete trip
- `GET /{id}/pdf` - Export to PDF
- `GET /{id}/calendar` - Export to calendar

#### **7. Maps** (`/api/v1/maps`) - **8 Endpoints**
- `POST /geocode` - Geocode address
- `POST /reverse-geocode` - Reverse geocode coordinates
- `GET /search-places` - Search places
- `GET /place/{place_id}` - Get place details
- `POST /directions` - Get directions
- `GET /nearby-attractions` - Nearby attractions
- `GET /nearby-restaurants` - Nearby restaurants
- `GET /nearby-hotels` - Nearby hotels

#### **8. Weather** (`/api/v1/weather`) - **7 Endpoints**
- `GET /current` - Current weather
- `GET /forecast` - Weather forecast
- `GET /alerts` - Weather alerts
- `GET /summary` - Weather summary
- `GET /cities` - Available cities
- `POST /recommendations` - Weather-based recommendations
- `GET /icon/{icon_code}` - Weather icons

#### **9. Currency** (`/api/v1/currency`) - **8 Endpoints**
- `POST /convert` - Convert currency
- `GET /rates` - Get exchange rates
- `GET /sri-lanka-rates` - Sri Lanka specific rates
- `GET /currencies` - List currencies
- `GET /currency/{code}` - Get currency details
- `POST /recommendations` - Currency recommendations
- `GET /summary` - Currency summary
- `POST /format/{amount}` - Format amount

#### **10. Transport** (`/api/v1/transport`)
- `GET /` - List transport options
- `GET /routes` - Get routes
- `GET /schedule` - Get schedules
- `POST /recommend` - Transport recommendations

#### **11. Events** (`/api/v1/events`)
- `GET /` - List events
- `GET /{id}` - Get event details
- `GET /upcoming` - Upcoming events
- `GET /categories` - Event categories

#### **12. Safety** (`/api/v1/safety`)
- `GET /tips` - Safety tips
- `GET /guidelines` - Safety guidelines
- `GET /regions` - Region-specific safety
- `GET /warnings` - Travel warnings

#### **13. Emergency** (`/api/v1/emergency`)
- `GET /contacts` - Emergency contacts
- `POST /sos` - Send SOS alert
- `GET /services` - Emergency services
- `GET /hospitals` - Nearby hospitals

#### **14. Landmarks** (`/api/v1/landmarks`)
- `POST /recognize` - Recognize landmark from image
- `GET /popular` - Popular landmarks

#### **15. Recommendations** (`/api/v1/recommendations`)
- `POST /personalized` - Get personalized recommendations
- `GET /trending` - Trending places
- `POST /similar` - Similar places

#### **16. Forum** (`/api/v1/forum`)
- `GET /posts` - List forum posts
- `POST /posts` - Create post
- `GET /posts/{id}` - Get post
- `POST /posts/{id}/reply` - Reply to post

#### **17. Feedback** (`/api/v1/feedback`)
- `POST /` - Submit feedback
- `GET /` - Get feedback (admin)

#### **18. Users** (`/api/v1/users`)
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile
- `GET /bookmarks` - Get bookmarks
- `POST /bookmarks` - Add bookmark
- `DELETE /bookmarks/{id}` - Remove bookmark
- `GET /history` - Get trip history

#### **19. OAuth** (`/api/v1/oauth`)
- `POST /login` - OAuth login (Google)
- `GET /providers` - List OAuth providers

#### **20. Email Verification** (`/api/v1/email-verification`)
- `POST /send` - Send verification email
- `POST /verify` - Verify email code

#### **21. Health** (`/api/v1/health`)
- `GET /` - Basic health check
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe
- `GET /detailed` - Detailed system status

#### **22. GraphQL** (`/graphql`)
- GraphQL Playground
- Queries & Mutations
- Real-time subscriptions (future)

---

## **🤖 AI Services (28+ Services)**

### **Core AI Services**

#### **1. HybridChatService** - Intelligent Query Routing
```python
# Routes queries based on complexity:
- Simple/structured → Rasa NLU
- Complex/open-ended → LLM
- Very complex → CrewAI Multi-Agent
```

#### **2. LLMService** - Multi-LLM Orchestration
```python
# Fallback chain:
Gemini (Primary) → Qwen (Fallback 1) → Mistral (Fallback 2)
```

#### **3. RasaService** - Rasa NLU Integration
- Intent classification
- Entity extraction
- Dialogue management
- Structured responses

#### **4. CrewAIService** - Multi-Agent System
- **5 Specialized Agents**:
  1. Tourism Expert
  2. Itinerary Planner
  3. Weather Advisor
  4. Transport Coordinator
  5. Safety Specialist

#### **5. TranslationService** - Multi-Language
- Google Translate API (primary)
- deep-translator (free fallback)
- 7 languages supported

#### **6. TavilySearchService** - AI Search
- AI-optimized web search
- Real-time information
- Fallback for low-confidence responses

### **LLM Provider Services**

#### **7. GeminiService** - Google Gemini API
- Primary LLM provider
- Latest Gemini models
- High-quality responses

#### **8. QwenService** - Qwen AI API
- First fallback LLM
- Good for multilingual tasks

#### **9. MistralService** - Mistral AI API
- Second fallback LLM
- Efficient inference

### **Tourism Services**

#### **10. ChatService** - Chat Management
- Conversation management
- Message handling
- History tracking

#### **11. ItineraryService** - Trip Planning
- AI-generated itineraries
- Personalized planning
- PDF/Calendar export

#### **12. RecommendationService** - Recommendations
- Personalized suggestions
- Collaborative filtering
- Content-based filtering

#### **13. AttractionService** - Attraction Data
- Attraction CRUD operations
- Search & filtering
- Popular attractions

#### **14. LandmarkRecognitionService** - Image Recognition
- Image-based landmark recognition
- OpenCV + ML models
- Visual search

### **Integration Services**

#### **15. MapsService** - Google Maps Integration
- Geocoding & reverse geocoding
- Place search & details
- Directions & routes
- Nearby places

#### **16. WeatherService** - Weather Integration
- Current weather
- Forecasts
- Alerts
- Weather-based recommendations

#### **17. CurrencyService** - Currency Integration
- Live exchange rates
- Currency conversion
- Multi-currency support

### **Authentication & User Services**

#### **18. AuthService** - Authentication
- JWT token generation
- Token validation
- MFA/2FA
- Session management

#### **19. UserService** - User Management
- User CRUD operations
- Profile management
- Preferences

#### **20. OAuthService** - OAuth Integration
- Google OAuth
- Social login
- Token exchange

#### **21. EmailVerificationService** - Email Verification
- Send verification emails
- Verify codes
- Email confirmation

### **Utility Services**

#### **22. SafetyService** - Safety Information
- Safety tips
- Travel warnings
- Emergency information

#### **23. SpeechService** - Speech Services
- Speech-to-text
- Text-to-speech
- Voice recognition

#### **24. CacheService** - Redis Caching
- Cache management
- Cache invalidation
- TTL management

#### **25. PDFExportService** - PDF Generation
- Itinerary PDF export
- Document generation

#### **26. CalendarExportService** - Calendar Export
- iCalendar format
- Trip scheduling

#### **27. GDPRExportService** - Data Export
- User data export
- GDPR compliance

#### **28. NotificationService** - Notifications
- Push notifications
- Email notifications
- SMS notifications (future)

---

## **🔒 Security & Middleware**

### **Security Features**

#### **Authentication**
- ✅ JWT-based authentication
- ✅ Access & refresh tokens
- ✅ Token revocation (Redis blacklist)
- ✅ MFA/2FA support (TOTP)
- ✅ OAuth 2.0 (Google)

#### **Password Security**
- ✅ bcrypt hashing
- ✅ Minimum complexity requirements
- ✅ Password history
- ✅ Rate limiting on login

#### **Data Protection**
- ✅ Input validation (Pydantic)
- ✅ XSS prevention (bleach)
- ✅ SQL injection prevention (ODM)
- ✅ CSRF protection
- ✅ Security headers (HSTS, CSP, X-Frame-Options)

#### **API Security**
- ✅ Rate limiting (100 req/min per IP)
- ✅ Distributed rate limiting (Redis)
- ✅ CORS protection
- ✅ Request timeout
- ✅ Request size limits

### **Middleware Components (10+)**

#### **1. RequestIdMiddleware**
- Adds unique request ID to each request
- Request tracing across services
- Logging correlation

#### **2. RateLimitMiddleware**
- 100 requests per minute per IP
- Configurable limits
- Redis-backed

#### **3. DistributedRateLimitMiddleware**
- Distributed rate limiting
- Multi-instance support
- Redis coordination

#### **4. CORSMiddleware**
- Cross-origin resource sharing
- Configurable origins
- Preflight handling

#### **5. SecurityHeadersMiddleware**
- Security headers (HSTS, CSP, X-Frame-Options)
- XSS protection
- Content type sniffing prevention

#### **6. ErrorHandlerMiddleware**
- Centralized error handling
- Consistent error format
- Error logging

#### **7. APIVersioningMiddleware**
- API version management
- Version routing
- Deprecation warnings

#### **8. RequestTimeoutMiddleware**
- Request timeout handling
- Configurable timeout
- Graceful timeout response

#### **9. CacheHeadersMiddleware**
- HTTP caching headers
- Cache-Control, ETag
- Conditional requests

#### **10. WebSocketSecurityMiddleware**
- WebSocket authentication
- Token validation
- Connection security

---

## **📊 Database Models (17+ Models)**

### **Core Models** (MongoDB/Beanie)

#### **1. User**
```python
- email: str (unique, indexed)
- password_hash: str
- full_name: str
- preferred_language: str
- is_verified: bool
- mfa_enabled: bool
- oauth_provider: Optional[str]
- created_at: datetime
- updated_at: datetime
```

#### **2. Conversation**
```python
- user_id: ObjectId
- title: str
- language: str
- messages: List[Message]
- created_at: datetime
- updated_at: datetime
```

#### **3. Attraction**
```python
- name: str (indexed)
- description: str
- category: str
- location: GeoJSON
- images: List[str]
- rating: float
- reviews_count: int
- opening_hours: dict
- entry_fee: float
```

#### **4. Hotel**
```python
- name: str
- description: str
- location: GeoJSON
- star_rating: int
- amenities: List[str]
- room_types: List[dict]
- price_range: dict
```

#### **5. Restaurant**
```python
- name: str
- cuisine: List[str]
- location: GeoJSON
- rating: float
- price_level: int
- opening_hours: dict
- menu_items: List[dict]
```

#### **6. Itinerary**
```python
- user_id: ObjectId
- title: str
- days: List[dict]
- destinations: List[str]
- budget: float
- travelers: int
- preferences: dict
- status: str
```

#### **7. Event**
```python
- name: str
- description: str
- category: str
- location: GeoJSON
- start_date: datetime
- end_date: datetime
- ticket_price: float
```

#### **8-17. Additional Models**
- **Transport** - Transport options
- **Safety** - Safety information
- **Emergency** - Emergency contacts
- **Forum** - Forum posts
- **Feedback** - User feedback
- **Recommendation** - Recommendations
- **Challenge** - Gamification
- **Notification** - Notifications
- **Analytics** - Analytics data
- **Security** - Security logs

---

## **🚀 Getting Started**

### **Prerequisites**
- Python 3.9+
- MongoDB 6.0+
- Redis 7.0+
- Docker & Docker Compose

### **Installation**

```bash
# 1. Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. Download NLP models
python -m spacy download en_core_web_sm

# 4. Configure environment
cp env.example .env
# Edit .env with your settings

# 5. Start infrastructure
docker-compose up -d mongodb redis

# 6. Run database migrations
python -m backend.app.core.migrations migrate

# 7. Start backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Access Points**
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **GraphQL Playground**: http://localhost:8000/graphql
- **Health Check**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:9090

---

## **🧪 Testing**

### **Test Structure**
```bash
tests/
├── unit/              # Unit tests (services, models)
├── integration/       # Integration tests (API + DB)
├── api/              # API endpoint tests
└── security_tests/   # Security tests
```

### **Running Tests**

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run specific test types
pytest backend/tests/unit/           # Unit tests
pytest backend/tests/integration/    # Integration tests
pytest backend/tests/api/            # API tests
pytest backend/tests/security_tests/ # Security tests
```

### **Test Coverage**
- Unit Tests: 85%+ coverage
- Integration Tests: 70%+ coverage
- API Tests: 90%+ coverage
- Overall: 80%+ coverage

---

## **📈 Performance Optimization**

### **Optimization Techniques**

#### **1. Async/Await**
- Non-blocking I/O throughout
- Concurrent request handling
- High throughput

#### **2. Caching Strategy**
```python
# Redis caching layers:
- User data: 1 hour TTL
- Attraction data: 24 hours TTL
- Conversation cache: 1 hour TTL
- Rate limit counters: 1 minute TTL
- API response cache: Configurable
```

#### **3. Database Optimization**
- Strategic indexes on frequent queries
- Connection pooling
- Query optimization
- Aggregation pipelines

#### **4. API Optimization**
- Response compression (GZip)
- Pagination for large datasets
- Field selection (GraphQL)
- Batch operations

### **Performance Benchmarks**
- **Average Response Time**: < 200ms (cached)
- **Average Response Time**: < 1s (uncached)
- **LLM Response Time**: 2-5s (varies by model)
- **Concurrent Users**: 1000+ (single instance)
- **Requests/Second**: 500+ (single instance)

---

## **📊 Monitoring & Observability**

### **Logging**
- **Format**: Structured JSON logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Storage**: `logs/app.log`, `logs/app_errors.log`
- **Rotation**: Daily rotation with retention

### **Metrics** (Prometheus)
```
# System Metrics:
- http_requests_total
- http_request_duration_seconds
- http_request_size_bytes
- http_response_size_bytes
- mongodb_connections
- redis_connections
- celery_tasks_total
- llm_requests_total
- llm_request_duration_seconds
```

### **Health Checks**
```bash
# Basic health
GET /health

# Readiness probe (K8s)
GET /health/ready

# Liveness probe (K8s)
GET /health/live

# Detailed system status
GET /health/detailed
```

### **Error Tracking** (Sentry)
- Automatic error capture
- Stack traces
- User context
- Performance monitoring

---

## **🔧 Configuration**

### **Environment Variables**

#### **Core Settings**
```env
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key-here

# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=sri_lanka_tourism_bot

# Redis
REDIS_URL=redis://localhost:6379
```

#### **AI Services**
```env
# Rasa
RASA_ENABLED=true
RASA_URL=http://localhost:5005

# CrewAI
USE_CREWAI=true

# LLM APIs
GEMINI_API_KEY=your-gemini-key
QWEN_API_KEY=your-qwen-key
MISTRAL_API_KEY=your-mistral-key
```

#### **External APIs**
```env
# Google Services
GOOGLE_TRANSLATE_API_KEY=your-key
GOOGLE_MAPS_API_KEY=your-key
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

# Other APIs
TAVILY_API_KEY=your-key
OPENWEATHER_API_KEY=your-key
CURRENCYLAYER_API_KEY=your-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## **🐳 Docker Deployment**

### **Docker Compose**

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### **Production Deployment**

```bash
# Build production image
docker build -t sri-lanka-tourism-backend:latest -f docker/backend/Dockerfile .

# Run production container
docker run -d \
  --name tourism-backend \
  -p 8000:8000 \
  --env-file .env \
  sri-lanka-tourism-backend:latest
```

---

## **✨ Feature Status**

### ✅ **Fully Integrated & Active**
- ✅ Rasa NLU (structured intent handling)
- ✅ CrewAI Multi-Agent (complex queries)
- ✅ Google Translate API (translation)
- ✅ Google Maps API (8 endpoints)
- ✅ Tavily AI Search (fallback search)
- ✅ OpenWeather API (7 endpoints)
- ✅ CurrencyLayer API (8 endpoints)
- ✅ Google OAuth (social login)
- ✅ Sentry (error tracking)
- ✅ SMTP Email (verification, notifications)
- ✅ Multi-LLM (Gemini, Qwen, Mistral)
- ✅ REST API (100+ endpoints)
- ✅ GraphQL API
- ✅ WebSocket (real-time chat)
- ✅ JWT Authentication + MFA
- ✅ Rate Limiting & Security
- ✅ Redis Caching
- ✅ Celery Background Tasks
- ✅ Prometheus Monitoring
- ✅ Database Migrations
- ✅ Circuit Breaker Pattern
- ✅ Comprehensive Logging

### 🚧 **In Development**
- 🚧 Advanced analytics dashboard
- 🚧 ML-based personalization
- 🚧 Voice assistant (full conversation)
- 🚧 Payment gateway integration

### 📋 **Planned Features**
- 📋 Microservices architecture
- 📋 Event-driven architecture
- 📋 API Gateway
- 📋 Service mesh
- 📋 GraphQL subscriptions

---

## **📊 Project Statistics**

- **API Endpoints**: 100+ endpoints across 25+ categories
- **Services**: 28+ service classes
- **Database Models**: 17+ models
- **Middleware Components**: 10+ middleware
- **External APIs**: 10+ integrations
- **Languages Supported**: 7 languages
- **AI Models**: Rasa NLU + 3 LLMs + CrewAI
- **Test Coverage**: 80%+ overall
- **Documentation**: 15+ markdown files
- **Lines of Code**: 25,000+ LOC

---

## **🎯 Key Design Patterns**

1. **Dependency Injection** - FastAPI dependency system
2. **Repository Pattern** - Beanie ODM abstraction
3. **Service Pattern** - Business logic encapsulation
4. **Strategy Pattern** - LLM provider selection
5. **Circuit Breaker** - External service resilience
6. **Factory Pattern** - Service instance creation
7. **Middleware Chain** - Request/response processing
8. **Observer Pattern** - Event handling
9. **Singleton Pattern** - Service instances
10. **Async/Await** - Non-blocking operations

---

## **🌟 Best Practices**

### **Code Quality**
- ✅ Type hints throughout
- ✅ Pydantic validation
- ✅ Comprehensive docstrings
- ✅ Clean code principles
- ✅ SOLID principles
- ✅ DRY (Don't Repeat Yourself)

### **Security**
- ✅ Input validation
- ✅ Output encoding
- ✅ Authentication required
- ✅ Authorization checks
- ✅ Rate limiting
- ✅ Security headers

### **Performance**
- ✅ Async operations
- ✅ Connection pooling
- ✅ Caching strategies
- ✅ Query optimization
- ✅ Response compression

### **Monitoring**
- ✅ Structured logging
- ✅ Metrics collection
- ✅ Error tracking
- ✅ Health checks
- ✅ Performance monitoring

---

## **📚 Documentation**

### **Backend Documentation**
- **README.md** - Project overview
- **ARCHITECTURE.md** - System architecture
- **API_DOCUMENTATION.md** - Complete API reference
- **SERVICES.md** - Services documentation
- **MODELS.md** - Data models
- **MIDDLEWARE.md** - Middleware components
- **DATABASE.md** - Database schema
- **CONFIGURATION.md** - Configuration guide
- **SECURITY.md** - Security features
- **TESTING.md** - Testing guide
- **DEVELOPMENT.md** - Development guidelines
- **DEPLOYMENT.md** - Deployment guide
- **FEATURE_INTEGRATION_STATUS.md** - Feature status
- **GRAPHQL.md** - GraphQL documentation
- **BACKEND_OVERVIEW.md** - This document

---

## **📞 Backend Information**

- **Version**: 1.0.0
- **Framework**: FastAPI 0.109.2
- **Python Version**: 3.9+
- **Database**: MongoDB 6.0+
- **Cache**: Redis 7.0+
- **License**: MIT
- **Status**: Production-Ready

---

**Built with ❤️ for Sri Lanka Tourism**

*Enterprise-Grade Backend | Production-Ready | Scalable Architecture*
