# 🌴 Sri Lanka Tourism Multilingual Chatbot - Full Project Overview

## **Project Summary**

An **enterprise-grade, production-ready** AI-powered multilingual chatbot system for Sri Lanka Tourism. Built with modern technologies including FastAPI, Next.js, MongoDB, and hybrid AI (Rasa NLU + LLM).

---

## **🎯 Core Capabilities**

### **Multilingual Support**
- **7 Languages**: Sinhala (සිංහල), Tamil (தமிழ்), English, German, French, Chinese, Japanese
- Auto language detection
- Real-time translation (Google Translate API + fallback to deep-translator)

### **Hybrid AI System**
- **Dual AI Engine**: Combines Rasa NLU (structured intents) with LLM (complex queries)
- **Multi-LLM Chain**: Gemini → Qwen → Mistral (100% free fallback chain)
- **CrewAI Multi-Agent**: 5 specialized agents for complex tourism queries
- **RAG (Retrieval Augmented Generation)**: Context-aware responses with FAISS vector search
- **Tavily AI Search**: Real-time web search integration

### **Tourism Features**
- 🏛️ **Attractions & Landmarks**: Discovery, recognition, recommendations
- 🏨 **Hotels & Restaurants**: Search, booking info, reviews
- 📅 **Itinerary Planning**: AI-generated personalized trip plans with PDF/Calendar export
- 🗺️ **Maps Integration**: Google Maps API (8 endpoints - geocoding, places, directions, nearby search)
- 🌤️ **Weather**: Real-time weather data
- 🚗 **Transport**: Transport information and routes
- 🎭 **Events**: Cultural events and festivals
- 💱 **Currency**: Exchange rates
- 🚨 **Safety & Emergency**: Emergency contacts, SOS features, safety tips

---

## **🏗️ Technical Architecture**

### **Backend** (Python/FastAPI)
```
backend/
├── app/
│   ├── api/v1/              # 25+ REST API endpoints
│   ├── graphql/             # GraphQL API
│   ├── services/            # 28+ business logic services
│   ├── models/              # MongoDB ODM models (Beanie)
│   ├── middleware/          # 8+ middleware components
│   ├── core/                # Config, database, auth, logging
│   └── tasks/               # Celery background tasks
├── rasa/                    # Rasa NLU chatbot engine
└── tests/                   # Comprehensive test suite
```

**Key Technologies**:
- FastAPI 0.109.2 (async web framework)
- MongoDB 6.0 + Beanie ODM
- Redis (caching & queue)
- Celery (background tasks)
- WebSocket (real-time chat)
- JWT authentication + OAuth

### **Frontend** (Next.js)
```
frontend/
├── app/                    # Next.js 16 App Router
│   ├── auth/              # Authentication
│   ├── chat/              # Chat interface
│   ├── explore/           # Tourism discovery
│   ├── planner/           # Itinerary planning
│   ├── safety/            # Emergency features
│   └── dashboard/         # User dashboard
├── components/            # React components
├── store/                 # Zustand state management
└── lib/                   # API client, i18n, utils
```

**Tech Stack**:
- Next.js 16 (React framework)
- Tailwind CSS v4
- TypeScript
- Zustand (state management)
- TanStack Query (data fetching)

### **Infrastructure**
- **Docker & Docker Compose**: Containerization
- **Kubernetes**: Orchestration configs
- **Prometheus + Grafana**: Monitoring
- **MongoDB**: Primary database
- **Redis**: Caching layer

---

## **📡 API Endpoints (25+ Categories)**

### **Main Endpoint Categories**:
1. **Chat** - `/api/v1/chat/*` + `/ws/chat` (WebSocket)
2. **Authentication** - `/api/v1/auth/*` (login, register, OAuth)
3. **Attractions** - `/api/v1/attractions/*`
4. **Hotels** - `/api/v1/hotels/*`
5. **Restaurants** - `/api/v1/restaurants/*`
6. **Itinerary** - `/api/v1/itinerary/*` (planning, PDF export)
7. **Maps** - `/api/v1/maps/*` (8 endpoints - geocode, places, directions)
8. **Safety** - `/api/v1/safety/*`
9. **Emergency** - `/api/v1/emergency/*`
10. **Weather** - `/api/v1/weather/*`
11. **Transport** - `/api/v1/transport/*`
12. **Events** - `/api/v1/events/*`
13. **Currency** - `/api/v1/currency/*`
14. **Recommendations** - `/api/v1/recommendations/*`
15. **Landmarks** - `/api/v1/landmarks/*` (image recognition)
16. **Forum** - `/api/v1/forum/*`
17. **Feedback** - `/api/v1/feedback/*`
18. **Users** - `/api/v1/users/*`
19. **Health** - `/api/v1/health/*` (liveness, readiness)
20. **GraphQL** - `/graphql`

---

## **🤖 AI Services (28+ Services)**

### **Core AI Services**:
1. **HybridChatService** - Intelligent query routing (Rasa vs LLM)
2. **LLMService** - Multi-LLM orchestration (Gemini, Qwen, Mistral)
3. **RasaService** - Rasa NLU integration
4. **CrewAIService** - 5-agent multi-agent system
5. **TranslationService** - Multi-language translation
6. **TavilySearchService** - AI-optimized web search
7. **RecommendationService** - Personalized recommendations
8. **ItineraryService** - Trip planning
9. **LandmarkRecognitionService** - Image recognition

### **Supporting Services**:
10. **AuthService** - Authentication/authorization
11. **UserService** - User management
12. **ChatService** - Conversation management
13. **MapsService** - Google Maps integration
14. **WeatherService** - Weather data
15. **CurrencyService** - Exchange rates
16. **SafetyService** - Safety information
17. **EmailVerificationService** - Email verification
18. **OAuthService** - OAuth integration
19. **CacheService** - Redis caching
20. **SpeechService** - Text-to-speech
21. **PDFExportService** - PDF generation
22. **CalendarExportService** - Calendar export
23. **GDPRExportService** - Data export
24. **AttractionService** - Attraction data
25. **GeminiService** - Google Gemini API
26. **MistralService** - Mistral AI API
27. **QwenService** - Qwen AI API

---

## **🔒 Security & Middleware**

### **Security Features**:
- JWT authentication + refresh tokens
- OAuth 2.0 support
- Password hashing (bcrypt)
- MFA/2FA support (TOTP)
- XSS protection (bleach)
- HTTPS/TLS encryption
- API key management
- Input validation (Pydantic)

### **Middleware Components**:
1. **RateLimitMiddleware** - 100 req/min per IP
2. **CORSMiddleware** - Cross-origin requests
3. **SecurityHeadersMiddleware** - Security headers
4. **ErrorHandlerMiddleware** - Centralized error handling
5. **RequestIdMiddleware** - Request tracing
6. **APIVersioningMiddleware** - API versioning
7. **RequestTimeoutMiddleware** - Timeout handling
8. **CacheHeadersMiddleware** - HTTP caching

---

## **📊 Database Models**

### **Core Models** (MongoDB/Beanie):
- **User** - User profiles with authentication
- **Conversation** - Chat conversations
- **Message** - Chat messages
- **Attraction** - Tourist attractions
- **Hotel** - Hotel listings
- **Restaurant** - Restaurant listings
- **Itinerary** - Trip plans
- **Event** - Cultural events
- **ForumPost** - Community forum
- **Feedback** - User feedback
- **EmergencyContact** - Emergency services

---

## **🚀 Development Setup**

### **Current Mode**: Local Development
- **Backend**: Runs locally (Python/FastAPI) with hot-reload
- **Infrastructure**: Docker containers (MongoDB, Redis, Prometheus)
- **Frontend**: Next.js dev server

### **Quick Start**:
```bash
# 1. Start infrastructure
docker-compose up -d mongodb redis

# 2. Configure environment
cp env.example .env

# 3. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Start backend
uvicorn backend.app.main:app --reload

# 5. Start frontend
cd frontend
npm install
npm run dev
```

### **Access Points**:
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`
- **API Docs**: `http://localhost:8000/docs`
- **GraphQL**: `http://localhost:8000/graphql`
- **MongoDB**: `localhost:27017`
- **Redis**: `localhost:6379`
- **Prometheus**: `http://localhost:9090`

---

## **📝 Key Documentation Files**

### **Main Documentation**:
- **README.md** - Project overview
- **backend/ARCHITECTURE.md** - System architecture
- **backend/API_DOCUMENTATION.md** - API reference
- **backend/SERVICES.md** - Services documentation
- **backend/TESTING.md** - Testing guide
- **backend/DEPLOYMENT.md** - Deployment guide
- **backend/FEATURE_INTEGRATION_STATUS.md** - Feature status
- **frontend/README.md** - Frontend documentation

### **Configuration**:
- **env.example** - Environment variables template
- **docker-compose.yml** - Docker setup
- **requirements.txt** - Python dependencies
- **frontend/package.json** - Node dependencies

---

## **✨ Feature Status**

### ✅ **Fully Integrated & Active**:
- ✅ Rasa NLU (structured intent handling)
- ✅ CrewAI Multi-Agent (complex queries)
- ✅ Google Translate API
- ✅ Google Maps API (8 endpoints)
- ✅ Tavily AI Search
- ✅ Multi-LLM support (Gemini, Qwen, Mistral)
- ✅ WebSocket real-time chat
- ✅ GraphQL API
- ✅ OAuth authentication
- ✅ PDF/Calendar export
- ✅ Image recognition (landmarks)
- ✅ REST API (25+ endpoint categories)
- ✅ MongoDB + Redis integration
- ✅ Middleware suite (8+ components)
- ✅ JWT authentication + MFA
- ✅ Rate limiting & security
- ✅ Background tasks (Celery)
- ✅ Monitoring (Prometheus)

### 🚧 **In Development**:
- 🚧 Frontend UI completion
- 🚧 Advanced analytics dashboard
- 🚧 Voice assistant integration
- 🚧 Mobile app (future)

---

## **📊 Project Statistics**

- **Backend Services**: 28+ services
- **API Endpoints**: 25+ categories, 100+ endpoints
- **Languages Supported**: 7 languages
- **AI Models**: Rasa NLU + 3 LLMs (Gemini, Qwen, Mistral)
- **Database Models**: 15+ models
- **Middleware Components**: 8+ components
- **Test Coverage**: Comprehensive test suite
- **Documentation**: 15+ markdown files

---

## **🎯 Use Cases**

1. **Tourist Information**: Get information about attractions, hotels, restaurants
2. **Trip Planning**: AI-generated personalized itineraries
3. **Navigation**: Directions, maps, nearby places
4. **Language Support**: Communicate in native language
5. **Emergency Assistance**: Emergency contacts, safety tips, SOS
6. **Weather Updates**: Real-time weather information
7. **Event Discovery**: Find cultural events and festivals
8. **Local Recommendations**: Personalized suggestions
9. **Transport Info**: Public transport, routes, schedules
10. **Currency Exchange**: Live exchange rates

---

## **🌟 Key Differentiators**

1. **Hybrid AI**: Combines rule-based (Rasa) + LLM for optimal responses
2. **Multi-Agent System**: CrewAI with 5 specialized agents
3. **True Multilingual**: Not just translation - native language understanding
4. **Enterprise-Ready**: Production-grade architecture, security, monitoring
5. **Comprehensive**: End-to-end tourism solution (chat, planning, booking, safety)
6. **Modern Stack**: Latest technologies (FastAPI, Next.js 16, MongoDB, GraphQL)
7. **Scalable**: Docker, Kubernetes, microservices-ready
8. **Well-Documented**: 15+ documentation files

---

## **🔮 Future Roadmap**

- [ ] Mobile apps (iOS/Android)
- [ ] Voice assistant integration
- [ ] AR/VR experiences
- [ ] Advanced analytics dashboard
- [ ] Payment gateway integration
- [ ] Social media integration
- [ ] Advanced personalization with ML
- [ ] Offline mode support
- [ ] Multi-platform (WhatsApp, Telegram, etc.)

---

## **📞 Project Information**

- **Status**: Production-Ready Backend, Frontend in Development
- **Version**: V1
- **License**: MIT
- **Python Version**: 3.9+
- **Node Version**: 18+
- **Database**: MongoDB 6.0+
- **Cache**: Redis 7.0+

---

**Built with ❤️ for Sri Lanka Tourism**
