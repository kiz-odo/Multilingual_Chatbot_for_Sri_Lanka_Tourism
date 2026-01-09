# 🚀 Backend - Sri Lanka Tourism Multilingual Chatbot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready, enterprise-grade FastAPI backend for the Sri Lanka Tourism Multilingual Chatbot system.

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| **[API Documentation](./API_DOCUMENTATION.md)** | Complete REST API reference with examples |
| **[GraphQL API](./GRAPHQL.md)** | GraphQL API documentation and examples |
| **[Architecture](./ARCHITECTURE.md)** | System architecture and design patterns |
| **[Services](./SERVICES.md)** | Service layer documentation |
| **[Models](./MODELS.md)** | Data models and schemas |
| **[Middleware](./MIDDLEWARE.md)** | Middleware components documentation |
| **[Database](./DATABASE.md)** | Database schema and migrations |
| **[Configuration](./CONFIGURATION.md)** | Configuration guide |
| **[Security](./SECURITY.md)** | Security features and best practices |
| **[Testing](./TESTING.md)** | Testing guide and best practices |
| **[Development](./DEVELOPMENT.md)** | Development setup and guidelines |
| **[Deployment](./DEPLOYMENT.md)** | Production deployment guide |

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/              # REST API endpoints (versioned)
│   ├── core/                # Core functionality (config, database, auth)
│   ├── graphql/             # GraphQL API implementation
│   ├── middleware/          # Custom middleware components
│   ├── models/              # MongoDB ODM models (Beanie)
│   ├── services/            # Business logic layer
│   ├── tasks/               # Celery background tasks
│   └── main.py              # FastAPI application entry point
├── rasa/                    # Rasa NLU chatbot engine
├── tests/                   # Comprehensive test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── api/                 # API endpoint tests
│   └── security_tests/      # Security tests
└── logs/                    # Application logs
```

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.9 or higher
- **MongoDB**: 6.0+ (via Docker)
- **Redis**: 7.0+ (via Docker)
- **Docker & Docker Compose**: Latest version

### Local Development Setup

```bash
# 1. Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. Download NLP models
python -m spacy download en_core_web_sm

# 4. Configure environment
cp ../env.example ../.env
# Edit .env with your settings

# 5. Start infrastructure (MongoDB, Redis)
docker-compose up -d mongodb redis

# 6. Run database migrations
python -m backend.app.core.migrations migrate

# 7. Start the backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Using VS Code Debugger

1. Press `F5` in VS Code
2. Select "FastAPI: Backend Server"
3. Server starts with hot-reload and debugging enabled

## 🌐 API Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: Configure via `HOST` and `PORT` environment variables

### Interactive Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GraphQL Playground**: http://localhost:8000/graphql

### Key Endpoints

```
POST   /api/v1/auth/register          - User registration
POST   /api/v1/auth/login             - User login
POST   /api/v1/chat/message           - Send chat message
GET    /api/v1/attractions            - List attractions
GET    /api/v1/hotels                 - List hotels
GET    /api/v1/restaurants            - List restaurants
GET    /api/v1/transport               - Transport options
GET    /api/v1/weather/{city}         - Weather information
GET    /health/ready                  - Health check
GET    /health/detailed               - Detailed system status
```

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference.

## 🛠️ Technology Stack

### Core Framework
- **FastAPI** 0.109.2 - High-performance async API framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and settings management

### Database & Storage
- **MongoDB** 6.0+ - Document database
- **Beanie** 1.24.0 - Async MongoDB ODM
- **Redis** 7.0+ - Caching and session storage

### AI & Machine Learning
- **Rasa** 3.6 - NLU for intent classification
- **LangChain** - LLM orchestration
- **Mistral-7B / Gemini / Qwen** - LLM providers
- **FAISS** - Vector similarity search (RAG)
- **sentence-transformers** - Semantic embeddings

### Background Processing
- **Celery** 5.3.4 - Distributed task queue
- **Redis** - Celery broker and result backend

### Authentication & Security
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing
- **python-jose** - JWT encoding/decoding
- **pyotp** - Multi-factor authentication

### Monitoring & Observability
- **Prometheus** - Metrics collection
- **Sentry** - Error tracking
- **OpenTelemetry** - Distributed tracing
- **Structured Logging** - JSON logging

## 📦 Key Features

### 🌍 Multilingual Support
- **7 Languages**: Sinhala (සිංහල), Tamil (தமிழ்), English, German, French, Chinese, Japanese
- Auto language detection
- Real-time translation

### 🤖 Hybrid AI System
- **Rasa NLU** for structured intent handling
- **LLM (Mistral/Gemini/Qwen)** for complex queries
- Intelligent query routing based on complexity
- Context-aware responses with RAG

### 🔐 Security Features
- JWT-based authentication with refresh tokens
- Multi-factor authentication (MFA)
- Rate limiting (100 req/min per IP)
- CORS protection
- Input validation and sanitization
- XSS and injection prevention

### 📊 Production Features
- Async/await throughout (non-blocking I/O)
- Redis caching for performance
- Database connection pooling
- Response compression (GZip)
- Circuit breakers for external services
- Health checks and readiness probes

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run specific test categories
pytest backend/tests/unit/        # Unit tests
pytest backend/tests/integration/ # Integration tests
pytest backend/tests/api/         # API tests
```

See [TESTING.md](./TESTING.md) for detailed testing guide.

## 📊 Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/health/ready

# Detailed system status
curl http://localhost:8000/health/detailed
```

### Logs

Logs are stored in `logs/` directory:
- `app.log` - All application logs
- `app_errors.log` - Error logs only

### Metrics (Prometheus)

Access Prometheus at http://localhost:9090

### Error Tracking (Sentry)

Configure `SENTRY_DSN` in `.env` for error tracking

## 🔧 Configuration

See [CONFIGURATION.md](./CONFIGURATION.md) for detailed configuration guide.

Key environment variables:
- `MONGODB_URL` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key (generate securely)
- `DEBUG` - Debug mode (false in production)

## 🚀 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment guide.

### Quick Docker Deployment

```bash
# Build production image
docker build -t sri-lanka-tourism-chatbot:latest -f docker/backend/Dockerfile .

# Run with docker-compose
docker-compose up -d
```

## 📝 Development Guidelines

See [DEVELOPMENT.md](./DEVELOPMENT.md) for:
- Code style and formatting
- Git workflow
- Pull request process
- Code review guidelines

## 🔐 Security

See [SECURITY.md](./SECURITY.md) for:
- Security features
- Best practices
- Vulnerability management
- Security checklist

## 📈 Performance

### Optimization Features
- Async/await throughout (non-blocking I/O)
- Redis caching for frequent queries
- Database indexing on common queries
- Connection pooling
- Response compression (GZip)
- Pagination for large datasets

### Benchmarks
- Average response time: < 200ms (cached)
- Average response time: < 1s (uncached)
- LLM response time: 2-5s (CPU), < 1s (GPU)
- Concurrent users: 1000+ (single instance)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run linters (`black`, `isort`, `ruff`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Sri Lanka Tourism Development Authority
- Open source community
- Contributors and testers

---

**Built with ❤️ for Sri Lanka Tourism | Production-Ready Backend | Enterprise-Grade Architecture**

