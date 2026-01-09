# 🔧 Disabled/Optional Features Guide

Complete list of features that are currently disabled or optional in the backend.

## Currently Disabled Features

### 1. **Rasa NLU** ❌ Disabled by Default

**Status**: `RASA_ENABLED: bool = False`

**What it does**:
- Intent classification for chat messages
- Structured intent handling
- Fast responses for simple queries

**How to Enable**:
```bash
# In .env file
RASA_ENABLED=true
RASA_SERVER_URL="http://localhost:5005"
```

**Requirements**:
1. Start Rasa server:
   ```bash
   cd backend/rasa
   rasa train
   rasa run --enable-api --cors "*" --port 5005
   ```

2. Start Rasa actions server (separate terminal):
   ```bash
   rasa run actions --port 5055
   ```

**Note**: Rasa is optional - the system works with LLM fallback, but Rasa provides faster, more structured responses.

---

### 2. **CrewAI Multi-Agent** ❌ Disabled by Default

**Status**: `USE_CREWAI: bool = False`

**What it does**:
- Multi-agent orchestration for complex queries
- Specialized agents for different tasks
- Advanced itinerary planning and recommendations

**How to Enable**:
```bash
# In .env file
USE_CREWAI=true
CREWAI_VERBOSE=false  # Set to true for debugging
```

**Requirements**:
```bash
pip install crewai crewai-tools nest-asyncio
```

**See**: [CREWAI_SETUP.md](./CREWAI_SETUP.md) for detailed guide

---

### 3. **HTTPS Redirect** ❌ Disabled by Default

**Status**: `ENABLE_HTTPS_REDIRECT: bool = False`

**What it does**:
- Automatically redirects HTTP requests to HTTPS
- Security best practice for production

**How to Enable**:
```bash
# In .env file (PRODUCTION ONLY)
ENABLE_HTTPS_REDIRECT=true
```

**Note**: Only enable in production with valid SSL certificate.

---

## Optional Features (Require API Keys)

### 4. **Google Translate API** ⚠️ Optional

**Status**: Requires `GOOGLE_TRANSLATE_API_KEY`

**What it does**:
- High-quality translation between languages
- Better than free translation services

**How to Enable**:
```bash
# Get API key from: https://console.cloud.google.com/
GOOGLE_TRANSLATE_API_KEY="your-api-key"
```

**Fallback**: System uses `deep-translator` (free) if not configured.

---

### 5. **Google Maps API** ⚠️ Optional

**Status**: Requires `GOOGLE_MAPS_API_KEY`

**What it does**:
- Geocoding (address to coordinates)
- Reverse geocoding
- Directions and routing
- Place search

**How to Enable**:
```bash
# Get API key from: https://console.cloud.google.com/
GOOGLE_MAPS_API_KEY="your-api-key"
```

**Impact**: Maps features will be limited without this.

---

### 6. **Google Speech API** ⚠️ Optional

**Status**: Requires `GOOGLE_SPEECH_API_KEY`

**What it does**:
- Speech-to-text conversion
- Voice message processing

**How to Enable**:
```bash
# Get API key from: https://console.cloud.google.com/
GOOGLE_SPEECH_API_KEY="your-api-key"
```

**Fallback**: Basic speech recognition available without API key.

---

### 7. **Google Text-to-Speech API** ⚠️ Optional

**Status**: Requires `GOOGLE_TTS_API_KEY`

**What it does**:
- Text-to-speech conversion
- Audio responses

**How to Enable**:
```bash
# Get API key from: https://console.cloud.google.com/
GOOGLE_TTS_API_KEY="your-api-key"
```

---

### 8. **Tavily AI Search** ⚠️ Optional (Recommended)

**Status**: Requires `TAVILY_API_KEY`

**What it does**:
- AI-optimized web search
- Better for chatbot queries
- 1,000 searches/month FREE

**How to Enable**:
```bash
# Get free API key from: https://tavily.com
TAVILY_API_KEY="your-api-key"
```

**Note**: Highly recommended for better search results.

---

### 9. **OpenWeather API** ⚠️ Optional

**Status**: Requires `OPENWEATHER_API_KEY`

**What it does**:
- Current weather information
- Weather forecasts
- Weather alerts

**How to Enable**:
```bash
# Get API key from: https://openweathermap.org/api
OPENWEATHER_API_KEY="your-api-key"
```

**Impact**: Weather features will not work without this.

---

### 10. **CurrencyLayer API** ⚠️ Optional

**Status**: Requires `CURRENCYLAYER_API_KEY`

**What it does**:
- Currency conversion
- Exchange rates
- Real-time currency data

**How to Enable**:
```bash
# Get API key from: https://currencylayer.com/
CURRENCYLAYER_API_KEY="your-api-key"
```

**Impact**: Currency conversion features will be limited.

---

### 11. **Firebase** ⚠️ Optional

**Status**: Requires `FIREBASE_CREDENTIALS`

**What it does**:
- Push notifications
- Cloud messaging
- User notifications

**How to Enable**:
```bash
# Download credentials from Firebase Console
FIREBASE_CREDENTIALS="path/to/firebase-credentials.json"
```

---

### 12. **Email (SMTP)** ⚠️ Optional

**Status**: Requires `SMTP_USERNAME` and `SMTP_PASSWORD`

**What it does**:
- Email verification
- Password reset emails
- Notification emails

**How to Enable**:
```bash
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
```

**Note**: For Gmail, use App Password (not regular password).

---

### 13. **OAuth2 Social Login** ⚠️ Optional

**Status**: Requires OAuth credentials

**What it does**:
- Google OAuth login
- Facebook OAuth login
- Social authentication

**How to Enable**:

**Google OAuth**:
```bash
# Get from: https://console.cloud.google.com/
GOOGLE_OAUTH_CLIENT_ID="your-client-id"
GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"
```

**Facebook OAuth**:
```bash
# Get from: https://developers.facebook.com/
FACEBOOK_APP_ID="your-app-id"
FACEBOOK_APP_SECRET="your-app-secret"
```

---

### 14. **Sentry Error Tracking** ⚠️ Optional

**Status**: Requires `SENTRY_DSN`

**What it does**:
- Error tracking and monitoring
- Performance monitoring
- Production error alerts

**How to Enable**:
```bash
# Get DSN from: https://sentry.io/
SENTRY_DSN="your-sentry-dsn"
SENTRY_ENVIRONMENT="production"
```

**Note**: Highly recommended for production.

---

### 15. **LLM Providers** ⚠️ Optional (But Recommended)

**Status**: Requires API keys for LLM providers

**What it does**:
- AI-powered responses
- Complex query handling
- Natural language understanding

**How to Enable**:

**Gemini (Primary - FREE)**:
```bash
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY="your-api-key"
```

**Qwen (Fallback 1 - FREE)**:
```bash
# Get from: https://dashscope.console.aliyun.com/
QWEN_API_KEY="your-api-key"
```

**Mistral (Fallback 2)**:
```bash
# Get from: https://console.mistral.ai/
MISTRAL_API_KEY="your-api-key"
```

**Note**: At least one LLM provider is recommended for full functionality.

---

### 16. **AES-256 Encryption** ⚠️ Optional

**Status**: Requires `ENCRYPTION_KEY`

**What it does**:
- Encrypt sensitive data at rest
- Additional security layer

**How to Enable**:
```bash
# Generate key: python -c "import secrets; print(secrets.token_urlsafe(32))"
ENCRYPTION_KEY="your-32-byte-encryption-key"
```

---

## Feature Status Summary

| Feature | Status | Required | Impact if Disabled |
|---------|--------|----------|-------------------|
| Rasa NLU | ❌ Disabled | No | Slower intent classification |
| CrewAI | ❌ Disabled | No | No multi-agent processing |
| HTTPS Redirect | ❌ Disabled | No | HTTP not redirected (dev only) |
| Google Translate | ⚠️ Optional | No | Uses free translator |
| Google Maps | ⚠️ Optional | No | Limited map features |
| Google Speech | ⚠️ Optional | No | Basic speech recognition |
| Google TTS | ⚠️ Optional | No | No text-to-speech |
| Tavily Search | ⚠️ Optional | No | Limited search quality |
| OpenWeather | ⚠️ Optional | No | No weather features |
| CurrencyLayer | ⚠️ Optional | No | Limited currency features |
| Firebase | ⚠️ Optional | No | No push notifications |
| SMTP Email | ⚠️ Optional | No | No email features |
| OAuth2 | ⚠️ Optional | No | No social login |
| Sentry | ⚠️ Optional | No | No error tracking |
| LLM Providers | ⚠️ Optional | Recommended | Limited AI features |
| Encryption | ⚠️ Optional | No | Less secure data storage |

## Quick Enable Guide

### Minimum Setup (Basic Functionality)
```bash
# Required
SECRET_KEY="your-secret-key"
MONGODB_URL="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379"

# Recommended
GEMINI_API_KEY="your-gemini-key"  # For AI features
```

### Recommended Setup (Full Features)
```bash
# Core
SECRET_KEY="your-secret-key"
MONGODB_URL="mongodb://localhost:27017"
REDIS_URL="redis://localhost:6379"

# AI Features
RASA_ENABLED=true
USE_CREWAI=true
GEMINI_API_KEY="your-key"
QWEN_API_KEY="your-key"  # Fallback

# External APIs
TAVILY_API_KEY="your-key"  # Better search
GOOGLE_MAPS_API_KEY="your-key"  # Maps
OPENWEATHER_API_KEY="your-key"  # Weather
CURRENCYLAYER_API_KEY="your-key"  # Currency

# Email
SMTP_USERNAME="your-email"
SMTP_PASSWORD="your-password"

# Monitoring
SENTRY_DSN="your-sentry-dsn"
```

### Production Setup (All Features)
```bash
# Enable all recommended features
RASA_ENABLED=true
USE_CREWAI=true
ENABLE_HTTPS_REDIRECT=true

# All API keys configured
# All services enabled
# Monitoring configured
```

## Testing Disabled Features

To test if a feature is working:

```python
from backend.app.core.config import settings

# Check Rasa
if settings.RASA_ENABLED:
    print("Rasa is enabled")

# Check CrewAI
if settings.USE_CREWAI:
    print("CrewAI is enabled")

# Check API keys
api_status = settings.validate_external_apis()
print(f"Configured APIs: {api_status}")
```

## Priority Recommendations

### High Priority (Enable These First)
1. ✅ **LLM Provider** (Gemini/Qwen) - Core AI functionality
2. ✅ **Rasa NLU** - Faster intent classification
3. ✅ **Tavily Search** - Better search results

### Medium Priority
4. ⚠️ **Google Maps API** - Maps features
5. ⚠️ **OpenWeather API** - Weather features
6. ⚠️ **SMTP Email** - Email verification

### Low Priority (Nice to Have)
7. 📌 **CrewAI** - Advanced multi-agent processing
8. 📌 **Sentry** - Error tracking (production)
9. 📌 **OAuth2** - Social login
10. 📌 **Firebase** - Push notifications

---

**Note**: Most features have fallbacks, so the system works even without optional APIs. Enable features based on your needs!

