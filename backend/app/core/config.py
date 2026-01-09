"""
Configuration settings for the Sri Lanka Tourism Chatbot
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationError
from typing import List, Optional
import os
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Sri Lanka Tourism Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "CHANGE-THIS-TO-A-SECURE-RANDOM-KEY-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30-minute access tokens
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7-day refresh tokens
    
    @field_validator('SECRET_KEY', mode='after')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that SECRET_KEY is secure in production"""
        # Check DEBUG from environment directly since fields may not be validated yet
        debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
        if not debug_mode:
            if v == "CHANGE-THIS-TO-A-SECURE-RANDOM-KEY-IN-PRODUCTION" or len(v) < 32:
                logger.error("CRITICAL: Insecure SECRET_KEY detected in production mode!")
                logger.error("Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
                raise ValueError("SECRET_KEY must be changed and be at least 32 characters in production mode")
        return v
    
    @field_validator('PORT')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number"""
        if not 1 <= v <= 65535:
            raise ValueError("PORT must be between 1 and 65535")
        return v
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sri_lanka_tourism_bot"
    
    @field_validator('MONGODB_URL')
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB URL format"""
        if not v.startswith('mongodb://') and not v.startswith('mongodb+srv://'):
            raise ValueError("MONGODB_URL must start with 'mongodb://' or 'mongodb+srv://'")
        return v
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    @field_validator('REDIS_URL')
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Validate Redis URL format"""
        if not v.startswith('redis://') and not v.startswith('rediss://'):
            raise ValueError("REDIS_URL must start with 'redis://' or 'rediss://'")
        return v
    
    # Celery (Task Queue)
    CELERY_BROKER_URL: Optional[str] = None  # Defaults to REDIS_URL if not set
    CELERY_RESULT_BACKEND: Optional[str] = None  # Defaults to REDIS_URL if not set
    
    # Rasa
    RASA_ENABLED: bool = False  # Set to True if Rasa server is available
    RASA_SERVER_URL: str = "http://localhost:5005"
    
    # Google Cloud APIs
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    GOOGLE_SPEECH_API_KEY: Optional[str] = None
    GOOGLE_TTS_API_KEY: Optional[str] = None
    
    # External APIs
    OPENWEATHER_API_KEY: Optional[str] = None
    CURRENCYLAYER_API_KEY: Optional[str] = None
    
    # Search APIs (AI-optimized)
    TAVILY_API_KEY: Optional[str] = None  # Recommended: AI-optimized search
    
    # Firebase
    FIREBASE_CREDENTIALS: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Email Verification
    EMAIL_VERIFICATION_SECRET: str = "your-email-verification-secret-change-this"
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # OAuth2 Configuration
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # CORS - For API access and future frontend integration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Supported Languages
    SUPPORTED_LANGUAGES: List[str] = [
        "si",  # Sinhala
        "ta",  # Tamil
        "en",  # English
        "de",  # German
        "fr",  # French
        "zh",  # Chinese
        "ja"   # Japanese
    ]
    
    # Default Language
    DEFAULT_LANGUAGE: str = "en"
    
    # LLM Configuration (100% FREE Multi-LLM Orchestration)
    # Hybrid AI System: Rasa (NLU) + FREE LLM fallback chain
    # Fallback Order: Gemini (FREE) → Qwen (FREE) → Mistral (FREE)
    LLM_ENABLED: bool = True  # Enable/disable LLM service
    LLM_PROVIDER: str = "gemini"  # Primary: Gemini (FREE)
    LLM_FALLBACK_PROVIDER_1: str = "qwen"  # Fallback 1: Qwen AI (FREE)
    LLM_FALLBACK_PROVIDER_2: str = "mistral"  # Fallback 2: Mistral AI (FREE)
    
    # CrewAI Multi-Agent Configuration
    USE_CREWAI: bool = False  # Enable/disable CrewAI multi-agent orchestration
    CREWAI_VERBOSE: bool = False  # Enable verbose logging for CrewAI agents
    
    # Google Gemini API (Primary)
    GEMINI_API_KEY: Optional[str] = None
    
    
    # Distributed Tracing & Monitoring
    ENABLE_TRACING: bool = True
    JAEGER_AGENT_HOST: str = "localhost"
    JAEGER_AGENT_PORT: int = 6831
    OTEL_SERVICE_NAME: str = "tourism-chatbot"
    OTEL_EXPORTER_JAEGER_ENDPOINT: str = "http://localhost:14268/api/traces"
    
    # Sentry Error Tracking
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Options: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash
    
    # Qwen AI API (Fallback 1 - Alibaba Cloud FREE)
    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-plus"  # Options: qwen-plus, qwen-turbo, qwen-max
    
    # Mistral AI API (Fallback 2)
    MISTRAL_API_KEY: Optional[str] = None
    MISTRAL_MODEL: str = "mistral-medium"  # Options: mistral-medium, mistral-small
    
    # Anthropic Claude API (Optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # LLM Generation Settings
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_P: float = 0.9
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "audio/wav", "audio/mp3"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True  # Enable/disable rate limiting
    RATE_LIMIT_DEFAULT: int = 100  # Default requests per window
    RATE_LIMIT_WINDOW: int = 60  # Default window in seconds
    RATE_LIMIT_PER_MINUTE: int = 60  # Per-minute limit per user
    RATE_LIMIT_PER_HOUR: int = 1000  # Per-hour limit per user
    RATE_LIMIT_PER_DAY: int = 10000  # Per-day limit per user
    RATE_LIMIT_IP_PER_MINUTE: int = 100  # Per-minute limit per IP (unauthenticated)
    
    # Per-endpoint rate limits
    RATE_LIMIT_CHAT_PER_MINUTE: int = 30
    RATE_LIMIT_AUTH: int = 10  # Auth endpoints (login, register)
    RATE_LIMIT_UPLOAD: int = 20  # Upload endpoints
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 5
    RATE_LIMIT_REGISTER_PER_MINUTE: int = 3
    
    # Security Headers
    ENABLE_HSTS: bool = True  # Enable HTTP Strict Transport Security
    ENABLE_CSP: bool = True  # Enable Content Security Policy
    ENABLE_HTTPS_REDIRECT: bool = False  # Redirect HTTP to HTTPS (enable in production)
    ALLOWED_HOSTS: Optional[str] = None  # Comma-separated list of allowed hosts
    
    # Request Configuration
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB max request body size
    REQUEST_TIMEOUT_SECONDS: int = 30  # Default request timeout
    
    # Database Connection Pooling
    MONGODB_MAX_POOL_SIZE: int = 50  # Maximum connections in pool
    MONGODB_MIN_POOL_SIZE: int = 10  # Minimum connections in pool
    MONGODB_MAX_IDLE_TIME_MS: int = 45000  # Max idle time before closing connection
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5000  # Server selection timeout
    MONGODB_CONNECT_TIMEOUT_MS: int = 20000  # Connection timeout
    
    # Database Retry Configuration
    DB_RETRY_MAX_ATTEMPTS: int = 3  # Maximum retry attempts
    DB_RETRY_INITIAL_DELAY: float = 0.1  # Initial retry delay in seconds
    DB_RETRY_MAX_DELAY: float = 2.0  # Maximum retry delay in seconds
    DB_RETRY_EXPONENTIAL_BASE: float = 2.0  # Exponential backoff base
    
    # Graceful Shutdown
    SHUTDOWN_TIMEOUT_SECONDS: int = 30  # Time to wait for in-flight requests
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = False  # Optional
    
    # AES-256 Encryption (for sensitive data)
    ENCRYPTION_KEY: Optional[str] = None  # 32-byte key for AES-256
    
    def validate_external_apis(self) -> dict:
        """Check which external APIs are configured"""
        configured = {
            'google_translate': bool(self.GOOGLE_TRANSLATE_API_KEY),
            'google_maps': bool(self.GOOGLE_MAPS_API_KEY),
            'google_speech': bool(self.GOOGLE_SPEECH_API_KEY),
            'google_tts': bool(self.GOOGLE_TTS_API_KEY),
            'tavily_search': bool(self.TAVILY_API_KEY),
            'openweather': bool(self.OPENWEATHER_API_KEY),
            'currencylayer': bool(self.CURRENCYLAYER_API_KEY),
            'firebase': bool(self.FIREBASE_CREDENTIALS),
            'smtp': bool(self.SMTP_USERNAME and self.SMTP_PASSWORD),
            'gemini': bool(self.GEMINI_API_KEY),
            'qwen': bool(self.QWEN_API_KEY),
            'mistral': bool(self.MISTRAL_API_KEY),
            'anthropic': bool(self.ANTHROPIC_API_KEY)
        }
        return configured
    
    def get_llm_provider_status(self) -> dict:
        """Check LLM provider configuration status (100% FREE providers)"""
        return {
            'llm_enabled': self.LLM_ENABLED,
            'primary_provider': self.LLM_PROVIDER,
            'fallback_provider_1': self.LLM_FALLBACK_PROVIDER_1,
            'fallback_provider_2': self.LLM_FALLBACK_PROVIDER_2,
            'gemini_configured': bool(self.GEMINI_API_KEY),
            'qwen_configured': bool(self.QWEN_API_KEY),
            'mistral_configured': bool(self.MISTRAL_API_KEY),
            'anthropic_configured': bool(self.ANTHROPIC_API_KEY)
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG


# Create settings instance with error handling
try:
    settings = Settings()
    logger.info("Configuration loaded successfully")
    
    # Log configuration status
    if settings.DEBUG:
        logger.warning("Running in DEBUG mode - not suitable for production!")
    
    # Check external API configuration
    api_status = settings.validate_external_apis()
    configured_apis = [k for k, v in api_status.items() if v]
    logger.info(f"Configured external APIs: {', '.join(configured_apis) if configured_apis else 'None'}")
    
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise


# Create logs directory if it doesn't exist
try:
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
except Exception as e:
    logger.warning(f"Failed to create logs directory: {e}")
