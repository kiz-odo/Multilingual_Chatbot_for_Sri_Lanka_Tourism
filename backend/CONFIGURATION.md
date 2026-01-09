# ⚙️ Configuration Documentation

Complete guide to configuring the backend application.

## Overview

Configuration is managed through environment variables using Pydantic Settings for validation and type safety.

## Configuration File

### Environment File

**Location**: `.env` (root directory)

**Template**: `env.example`

```bash
# Copy template
cp env.example .env

# Edit configuration
nano .env
```

## Configuration Categories

### 1. Application Settings

```bash
# Application
APP_NAME="Sri Lanka Tourism Chatbot"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production  # development, staging, production
HOST=0.0.0.0
PORT=8000
MAX_REQUEST_SIZE=10485760  # 10MB
```

### 2. Security Settings

```bash
# Security (IMPORTANT: Change in production!)
SECRET_KEY="<generate-secure-key>"  # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate Secret Key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Database Configuration

```bash
# MongoDB
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="sri_lanka_tourism_bot"

# MongoDB with Authentication
MONGODB_URL="mongodb://username:password@host:27017/dbname?authSource=admin"

# MongoDB Atlas (Cloud)
MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority"
```

### 4. Redis Configuration

```bash
# Redis
REDIS_URL="redis://localhost:6379"

# Redis with Password
REDIS_URL="redis://:password@localhost:6379"

# Redis Cloud
REDIS_URL="rediss://username:password@host:6379"
```

### 5. Celery Configuration

```bash
# Celery (Task Queue)
CELERY_BROKER_URL="redis://localhost:6379/0"  # Defaults to REDIS_URL if not set
CELERY_RESULT_BACKEND="redis://localhost:6379/0"  # Defaults to REDIS_URL if not set
```

### 6. Rasa Configuration

```bash
# Rasa (NLU Chatbot)
RASA_ENABLED=true
RASA_SERVER_URL="http://localhost:5005"
```

### 7. External APIs

```bash
# Google Cloud APIs
GOOGLE_CLOUD_PROJECT_ID=""
GOOGLE_APPLICATION_CREDENTIALS=""
GOOGLE_TRANSLATE_API_KEY=""
GOOGLE_MAPS_API_KEY=""
GOOGLE_SPEECH_API_KEY=""
GOOGLE_TTS_API_KEY=""

# Weather API
OPENWEATHER_API_KEY=""

# Currency API
CURRENCYLAYER_API_KEY=""
```

### 8. Email Configuration

```bash
# Email (SMTP)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""
SMTP_FROM_EMAIL="noreply@yourdomain.com"
SMTP_USE_TLS=true
```

### 9. Monitoring Configuration

```bash
# Sentry (Error Tracking)
SENTRY_DSN=""
SENTRY_ENVIRONMENT="production"

# Prometheus
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# OpenTelemetry
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

### 10. CORS Configuration

```bash
# CORS
ALLOWED_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
ALLOWED_ORIGINS_WILDCARD=false
```

### 11. Rate Limiting

```bash
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_AUTHENTICATED=200
RATE_LIMIT_ADMIN=1000
```

### 12. LLM Configuration

```bash
# LLM Providers
LLM_ENABLED=true
LLM_PROVIDER=gemini  # gemini, qwen, mistral
GEMINI_API_KEY=""
QWEN_API_KEY=""
MISTRAL_API_KEY=""

# LLM Settings
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.9
```

### 13. Cache Configuration

```bash
# Cache
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600  # 1 hour
CACHE_PREFIX="slt_chatbot:"
```

### 14. Logging Configuration

```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json, text
LOG_FILE="logs/app.log"
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=10
```

## Configuration Validation

### Pydantic Settings

Configuration is validated using Pydantic:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

### Validation Errors

Invalid configuration will raise errors at startup:

```bash
# Example error
ValueError: SECRET_KEY must be at least 32 characters
```

## Environment-Specific Configuration

### Development

```bash
# .env.development
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

### Staging

```bash
# .env.staging
DEBUG=false
ENVIRONMENT=staging
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["https://staging.yourdomain.com"]
```

### Production

```bash
# .env.production
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## Configuration Loading

### Priority Order

1. **Environment Variables**: Highest priority
2. **.env File**: Project root
3. **Default Values**: In Settings class

### Loading Configuration

```python
from backend.app.core.config import settings

# Access configuration
database_url = settings.MONGODB_URL
secret_key = settings.SECRET_KEY
```

## Docker Configuration

### Environment Variables in Docker

**docker-compose.yml**:
```yaml
services:
  backend:
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env
```

### Docker Secrets

For sensitive data, use Docker secrets:

```yaml
services:
  backend:
    secrets:
      - secret_key
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key

secrets:
  secret_key:
    file: ./secrets/secret_key.txt
```

## Kubernetes Configuration

### ConfigMap

**kubernetes/configmap.yaml**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  APP_NAME: "Sri Lanka Tourism Chatbot"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
```

### Secrets

**kubernetes/secret.yaml**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  SECRET_KEY: "<base64-encoded-secret>"
  MONGODB_URL: "<mongodb-connection-string>"
```

## Configuration Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.local
.env.production
secrets/
```

### 2. Use Environment Variables

- Never hardcode secrets
- Use environment variables for all sensitive data
- Use different values for each environment

### 3. Validate Configuration

- Use Pydantic for validation
- Check required variables at startup
- Provide clear error messages

### 4. Document Configuration

- Document all configuration options
- Provide examples
- Explain purpose of each setting

### 5. Secure Storage

- Use secret management services (AWS Secrets Manager, etc.)
- Encrypt secrets at rest
- Rotate secrets regularly

## Configuration Examples

### Minimal Configuration

```bash
# Minimum required for development
SECRET_KEY="dev-secret-key-change-in-production"
MONGODB_URL="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379"
DATABASE_NAME="sri_lanka_tourism_bot"
```

### Full Production Configuration

```bash
# Application
APP_NAME="Sri Lanka Tourism Chatbot"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY="<secure-32-char-key>"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
MONGODB_URL="mongodb://user:pass@host:27017/db?authSource=admin"
DATABASE_NAME="sri_lanka_tourism_bot"

# Redis
REDIS_URL="redis://:password@host:6379"

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com"]

# Monitoring
SENTRY_DSN="<sentry-dsn>"
PROMETHEUS_ENABLED=true

# External APIs
GOOGLE_TRANSLATE_API_KEY="<api-key>"
GOOGLE_MAPS_API_KEY="<api-key>"
OPENWEATHER_API_KEY="<api-key>"
```

## Troubleshooting

### Configuration Not Loading

1. Check `.env` file exists
2. Verify environment variable names
3. Check for typos in variable names
4. Verify file encoding (UTF-8)

### Validation Errors

1. Check error message for specific issue
2. Verify required variables are set
3. Check value formats (URLs, numbers, etc.)
4. Review validation rules in Settings class

### Environment-Specific Issues

1. Verify correct `.env` file is loaded
2. Check environment variable priority
3. Verify Docker/Kubernetes configuration
4. Check for conflicting values

## Configuration Reference

See `backend/app/core/config.py` for complete configuration options and validation rules.

