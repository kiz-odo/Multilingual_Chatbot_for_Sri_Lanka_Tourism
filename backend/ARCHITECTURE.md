# 🏗️ Architecture Documentation

System architecture and design patterns for the Sri Lanka Tourism Multilingual Chatbot backend.

## Overview

The backend is built using a **layered architecture** with clear separation of concerns, following industry best practices for scalability, maintainability, and performance.

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│           API Layer (FastAPI Routes)            │
│  REST API (v1)  │  GraphQL  │  WebSocket      │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│          Middleware Layer                       │
│  Auth │ Rate Limit │ CORS │ Error Handling     │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│          Service Layer (Business Logic)         │
│  Chat │ Auth │ Translation │ LLM │ Rasa         │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│          Data Access Layer                      │
│  Models (Beanie ODM) │ Cache (Redis)           │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│          Infrastructure Layer                   │
│  MongoDB │ Redis │ Celery │ External APIs       │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. API Layer

**Location**: `backend/app/api/v1/`

- **REST API**: Versioned RESTful endpoints (`/api/v1/*`)
- **GraphQL API**: Flexible GraphQL queries (`/graphql`)
- **WebSocket**: Real-time chat communication (`/ws/chat`)

**Responsibilities**:
- Request/response handling
- Input validation (Pydantic models)
- Authentication/authorization checks
- Response formatting

**Design Pattern**: Controller pattern

### 2. Middleware Layer

**Location**: `backend/app/middleware/`

**Components**:
- **RequestIdMiddleware**: Adds unique request IDs for tracing
- **RateLimitMiddleware**: Rate limiting (100 req/min per IP)
- **CORSMiddleware**: Cross-origin resource sharing
- **SecurityHeadersMiddleware**: Security headers (XSS, CSRF protection)
- **ErrorHandlerMiddleware**: Centralized error handling
- **APIVersioningMiddleware**: API version management
- **RequestTimeoutMiddleware**: Request timeout handling
- **CacheHeadersMiddleware**: HTTP caching headers

**Design Pattern**: Chain of Responsibility

### 3. Service Layer

**Location**: `backend/app/services/`

**Key Services**:
- **ChatService**: Conversation management
- **HybridChatService**: AI query routing (Rasa + LLM)
- **AuthService**: Authentication and authorization
- **TranslationService**: Multi-language translation
- **LLMService**: LLM orchestration (Gemini, Qwen, Mistral)
- **RasaService**: Rasa NLU integration
- **RecommendationService**: Personalized recommendations
- **ItineraryService**: Trip planning

**Design Pattern**: Service pattern with dependency injection

### 4. Data Access Layer

**Location**: `backend/app/models/`

- **Beanie ODM**: Async MongoDB object-document mapping
- **Models**: User, Conversation, Attraction, Hotel, etc.
- **Indexes**: Optimized database indexes

**Design Pattern**: Repository pattern (via Beanie)

### 5. Core Infrastructure

**Location**: `backend/app/core/`

**Components**:
- **Config**: Environment-based configuration (Pydantic Settings)
- **Database**: MongoDB connection and initialization
- **Auth**: JWT token generation and validation
- **Logging**: Structured JSON logging
- **Tracing**: OpenTelemetry distributed tracing
- **Metrics**: Prometheus metrics collection
- **Circuit Breaker**: Resilience patterns for external services

## Design Patterns

### 1. Dependency Injection

Services are injected via FastAPI's dependency system:

```python
from fastapi import Depends
from backend.app.services.chat_service import ChatService

@router.post("/message")
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.send_message(request)
```

### 2. Repository Pattern

Data access is abstracted through Beanie models:

```python
from backend.app.models.user import User

# Repository operations
user = await User.find_one(User.email == email)
users = await User.find_all().to_list()
```

### 3. Service Pattern

Business logic is encapsulated in service classes:

```python
class ChatService:
    def __init__(self):
        self.hybrid_service = HybridChatService()
        self.translation_service = TranslationService()
    
    async def send_message(self, request: ChatRequest):
        # Business logic here
        pass
```

### 4. Strategy Pattern

Used for LLM provider selection and fallback:

```python
class LLMService:
    def __init__(self):
        self.providers = [
            GeminiService(),  # Primary
            QwenService(),    # Fallback 1
            MistralService()  # Fallback 2
        ]
    
    async def generate(self, prompt: str):
        for provider in self.providers:
            try:
                return await provider.generate(prompt)
            except Exception:
                continue  # Try next provider
```

### 5. Circuit Breaker Pattern

Protects against cascading failures:

```python
from backend.app.core.circuit_breaker import CircuitBreaker

@CircuitBreaker(failure_threshold=5, timeout=60)
async def call_external_api():
    # External API call
    pass
```

### 6. Factory Pattern

Used for creating service instances:

```python
def get_chat_service() -> ChatService:
    return ChatService()
```

## Data Flow

### Request Flow

```
1. Client Request
   ↓
2. Middleware (Auth, Rate Limit, CORS)
   ↓
3. API Route Handler
   ↓
4. Service Layer (Business Logic)
   ↓
5. Data Access Layer (Models/Repository)
   ↓
6. Database (MongoDB) / Cache (Redis)
   ↓
7. Response (Service → API → Middleware → Client)
```

### Chat Message Flow

```
1. User sends message
   ↓
2. API validates input
   ↓
3. ChatService receives message
   ↓
4. HybridChatService routes query:
   - Simple query → RasaService
   - Complex query → LLMService
   ↓
5. TranslationService (if needed)
   ↓
6. Response stored in Conversation model
   ↓
7. Response returned to user
```

## Database Architecture

### MongoDB Collections

- **users**: User accounts and profiles
- **conversations**: Chat conversations and messages
- **attractions**: Tourist attractions
- **hotels**: Hotel listings
- **restaurants**: Restaurant listings
- **transport**: Transport options
- **itineraries**: User trip plans
- **events**: Tourism events
- **feedback**: User feedback
- **analytics**: System analytics

### Indexes

Optimized indexes for common queries:

```python
# User model
class User(Document):
    email: Indexed(str, unique=True)
    # Index on email for fast lookups
```

## Caching Strategy

### Redis Caching

**Cache Keys**:
- `user:{user_id}`: User data (TTL: 1 hour)
- `attraction:{attraction_id}`: Attraction data (TTL: 24 hours)
- `conversation:{conversation_id}`: Conversation cache (TTL: 1 hour)
- `rate_limit:{ip}`: Rate limit counters (TTL: 1 minute)

**Cache Invalidation**:
- Write-through cache for user updates
- TTL-based expiration
- Manual invalidation on data updates

## Background Processing

### Celery Tasks

**Location**: `backend/app/tasks/`

**Task Types**:
- **Email Tasks**: Send verification emails, notifications
- **Data Tasks**: Data processing, analytics
- **Notification Tasks**: Push notifications

**Task Queue**: Redis (Celery broker)

## Security Architecture

### Authentication Flow

```
1. User registers/logs in
   ↓
2. AuthService validates credentials
   ↓
3. JWT tokens generated (access + refresh)
   ↓
4. Tokens stored in Redis (for revocation)
   ↓
5. Client stores tokens
   ↓
6. Subsequent requests include token in Authorization header
   ↓
7. Middleware validates token
   ↓
8. Request proceeds if valid
```

### Authorization

**Role-Based Access Control (RBAC)**:
- **Guest**: Read-only access, basic chat
- **User**: Full chat, history, favorites
- **Moderator**: Content moderation
- **Admin**: Full system access

## Scalability Considerations

### Horizontal Scaling

- **Stateless API**: All state in database/cache
- **Load Balancing**: Multiple API instances behind load balancer
- **Database Sharding**: MongoDB sharding for large datasets
- **Cache Clustering**: Redis cluster for high availability

### Vertical Scaling

- **Async Operations**: Non-blocking I/O throughout
- **Connection Pooling**: MongoDB and Redis connection pools
- **Caching**: Aggressive caching to reduce database load

## Monitoring & Observability

### Logging

- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Request Tracing**: Unique request IDs for tracing

### Metrics

- **Prometheus**: System metrics (request rate, latency, errors)
- **Custom Metrics**: Business metrics (chat messages, user registrations)

### Tracing

- **OpenTelemetry**: Distributed tracing across services
- **Jaeger**: Trace visualization

## Error Handling

### Error Hierarchy

```
BaseException
  └── APIException (Custom)
      ├── ValidationError (400)
      ├── AuthenticationError (401)
      ├── AuthorizationError (403)
      ├── NotFoundError (404)
      ├── RateLimitError (429)
      └── InternalServerError (500)
```

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "validation error details"
    }
  },
  "status": "error",
  "request_id": "unique-request-id"
}
```

## API Versioning Strategy

### URL Versioning

- Current version: `/api/v1/`
- Future versions: `/api/v2/`, `/api/v3/`, etc.

### Versioning Rules

- Breaking changes require new version
- Non-breaking changes can be added to current version
- Deprecated endpoints marked but not removed immediately
- Migration guide provided for version upgrades

## GraphQL Architecture

### Schema Design

**Location**: `backend/app/graphql/schema.py`

- **Queries**: Read operations
- **Mutations**: Write operations
- **Subscriptions**: Real-time updates (future)

### Resolvers

**Location**: `backend/app/graphql/resolvers.py`

- Field-level resolvers
- N+1 query prevention with DataLoader pattern

## Testing Architecture

### Test Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /____\
     /      \    Integration Tests (Some)
    /________\
   /          \   Unit Tests (Many)
  /____________\
```

### Test Types

- **Unit Tests**: Service and model tests
- **Integration Tests**: API endpoint tests with test database
- **E2E Tests**: Full system tests (future)

## Deployment Architecture

### Container Architecture

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
┌───▼───┐ ┌──▼───┐
│ API 1 │ │ API 2│  (Multiple instances)
└───┬───┘ └──┬───┘
    │        │
┌───┴────────┴───┐
│   MongoDB      │  (Replica Set)
└────────────────┘
┌─────────────────┐
│     Redis       │  (Cluster)
└─────────────────┘
┌─────────────────┐
│     Celery       │  (Workers)
└─────────────────┘
```

### Environment Separation

- **Development**: Local development with hot-reload
- **Staging**: Production-like environment for testing
- **Production**: Optimized, monitored, secure

## Performance Optimization

### Caching Strategy

1. **Application Cache**: Redis for frequently accessed data
2. **HTTP Cache**: Cache headers for static resources
3. **Database Query Cache**: MongoDB query result caching

### Database Optimization

1. **Indexes**: Strategic indexes on frequently queried fields
2. **Aggregation Pipelines**: Efficient data aggregation
3. **Connection Pooling**: Reuse database connections

### API Optimization

1. **Pagination**: Limit response sizes
2. **Field Selection**: GraphQL allows field selection
3. **Compression**: GZip compression for responses
4. **Async Operations**: Non-blocking I/O throughout

## Future Enhancements

1. **Microservices**: Split into smaller services if needed
2. **Event-Driven Architecture**: Event sourcing for audit trail
3. **API Gateway**: Centralized API management
4. **Service Mesh**: Inter-service communication management
5. **GraphQL Subscriptions**: Real-time updates via WebSocket

