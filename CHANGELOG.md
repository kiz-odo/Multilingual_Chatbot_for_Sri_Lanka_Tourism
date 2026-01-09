# Changelog

All notable changes to the Sri Lanka Tourism Chatbot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive unit tests for user, attraction, weather, currency, and cache services
- GDPR data export endpoint (`/api/v1/users/me/export`)
- GDPR data download as ZIP archive (`/api/v1/users/me/export/download`)
- GDPR data deletion endpoint (`/api/v1/users/me/data`)
- WebSocket security middleware with rate limiting and connection limits
- API versioning middleware with deprecation header support
- GitHub Actions CI/CD workflows (ci.yml, scheduled.yml)
- Contributing guidelines (CONTRIBUTING.md)
- This changelog file

### Changed
- Enhanced WebSocket connections with per-IP limits (max 5 per IP)
- Added message rate limiting to WebSocket (30 messages per minute)
- Improved test coverage targeting 80%+

### Security
- Added WebSocket authentication validation
- Implemented connection timeout (1 hour) for WebSocket
- Added IP blocking for abusive WebSocket connections

## [1.0.0] - 2024-12-27

### Added

#### Core Features
- FastAPI-based REST API with async support
- MongoDB database with Beanie ODM
- Redis caching layer
- Hybrid AI chat system (Rasa NLU + Multi-LLM fallback)
- Real-time WebSocket chat support
- Voice chat with speech-to-text/text-to-speech

#### Authentication & Security
- JWT-based authentication with access/refresh tokens
- OAuth2 social login (Google, Facebook)
- Multi-factor authentication (TOTP)
- Role-based access control (Guest, User, Moderator, Admin)
- Rate limiting (HTTP and distributed)
- Security headers middleware (CSP, HSTS, X-Frame-Options)
- XSS sanitization for user inputs

#### Tourism Features
- Attractions management with multilingual support
- Hotels and restaurant listings
- Transport information
- Emergency services directory
- Events calendar
- Interactive maps integration
- Weather information (OpenWeatherMap)
- Currency conversion (CurrencyLayer)
- Safety alerts and travel advisories
- Itinerary planning and generation
- PDF/Calendar export for itineraries
- Landmark recognition (image-based)
- Personalized recommendations

#### Multilingual Support
- 7 languages: English, Sinhala, Tamil, Hindi, Chinese, Japanese, French
- Automatic language detection
- Translation service integration

#### Community Features
- User feedback system
- Forum discussions
- Gamification challenges
- Achievement badges

#### Infrastructure
- Docker containerization with multi-stage builds
- Kubernetes deployment manifests
- Horizontal Pod Autoscaler (HPA)
- Network policies for security
- MongoDB replica set support
- Redis cluster support

#### Monitoring & Observability
- Prometheus metrics collection
- Grafana dashboards
- Jaeger distributed tracing
- Sentry error tracking
- Structured JSON logging
- Health check endpoints

#### Developer Experience
- OpenAPI 3.1 documentation
- Postman collection
- Comprehensive API documentation
- Environment configuration management

### Security
- Secret management (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, GCP Secret Manager)
- Database connection encryption (TLS)
- Password hashing with bcrypt
- Input validation and sanitization
- SQL injection prevention
- CORS configuration

## [0.9.0] - 2024-11-15 (Beta)

### Added
- Initial beta release
- Core chat functionality
- Basic attraction information
- User registration and login

### Known Issues
- Limited test coverage
- Missing GDPR compliance features
- WebSocket without rate limiting

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2024-12-27 | Production release with full feature set |
| 0.9.0 | 2024-11-15 | Beta release with core features |

## Upgrade Notes

### Upgrading to 1.0.0

1. **Database Migration**: Run migrations before deploying
   ```bash
   python -m backend.app.core.migrations upgrade
   ```

2. **Environment Variables**: New required variables:
   - `WS_MAX_CONNECTIONS_PER_IP` (default: 5)
   - `WS_RATE_LIMIT_MESSAGES` (default: 30)

3. **Breaking Changes**: None

## Deprecation Notices

Currently, there are no deprecated features. All v1 API endpoints are stable.

## Security Advisories

No security advisories at this time.

---

[Unreleased]: https://github.com/your-org/sri-lanka-tourism-chatbot/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/sri-lanka-tourism-chatbot/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/your-org/sri-lanka-tourism-chatbot/releases/tag/v0.9.0
