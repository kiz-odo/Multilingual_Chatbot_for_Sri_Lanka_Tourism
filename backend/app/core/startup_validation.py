"""
Startup Environment Validation Module
Validates all required services and configurations before application startup

Industry Standard: Fail-fast approach to prevent runtime errors
"""

import logging
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Validation result severity levels"""
    CRITICAL = "critical"  # App cannot start without this
    WARNING = "warning"    # App can start but with reduced functionality
    INFO = "info"          # Informational only


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Optional[str] = None


@dataclass
class StartupValidationReport:
    """Complete startup validation report"""
    results: List[ValidationResult] = field(default_factory=list)
    
    @property
    def has_critical_failures(self) -> bool:
        return any(
            not r.passed and r.severity == ValidationSeverity.CRITICAL 
            for r in self.results
        )
    
    @property
    def has_warnings(self) -> bool:
        return any(
            not r.passed and r.severity == ValidationSeverity.WARNING 
            for r in self.results
        )
    
    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    def add_result(self, result: ValidationResult):
        self.results.append(result)
    
    def get_summary(self) -> str:
        """Get human-readable summary"""
        lines = [
            "=" * 60,
            "STARTUP VALIDATION REPORT",
            "=" * 60,
            f"Total Checks: {len(self.results)}",
            f"Passed: {self.passed_count}",
            f"Failed: {self.failed_count}",
            "-" * 60,
        ]
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            severity_icon = {
                ValidationSeverity.CRITICAL: "🔴",
                ValidationSeverity.WARNING: "🟡",
                ValidationSeverity.INFO: "🔵"
            }.get(result.severity, "")
            
            lines.append(f"{status} {severity_icon} {result.name}: {result.message}")
            if result.details and not result.passed:
                lines.append(f"   └── {result.details}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class StartupValidator:
    """Validates environment and services on application startup"""
    
    def __init__(self):
        self.report = StartupValidationReport()
    
    async def validate_all(self) -> StartupValidationReport:
        """Run all validation checks"""
        logger.info("Starting environment validation...")
        
        # Configuration validations (sync)
        self._validate_secret_key()
        self._validate_environment_mode()
        self._validate_required_settings()
        self._validate_api_keys()
        self._validate_security_settings()
        
        # Service validations (async)
        await self._validate_mongodb()
        await self._validate_redis()
        await self._validate_rasa()
        await self._validate_llm_providers()
        
        # Log summary
        logger.info(self.report.get_summary())
        
        return self.report
    
    def _validate_secret_key(self):
        """Validate SECRET_KEY is properly configured"""
        insecure_keys = [
            "CHANGE-THIS-TO-A-SECURE-RANDOM-KEY-IN-PRODUCTION",
            "secret",
            "password",
            "changeme",
        ]
        
        is_insecure = (
            settings.SECRET_KEY in insecure_keys or 
            len(settings.SECRET_KEY) < 32
        )
        
        if is_insecure and not settings.DEBUG:
            self.report.add_result(ValidationResult(
                name="SECRET_KEY",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Insecure SECRET_KEY in production mode",
                details="Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            ))
        else:
            self.report.add_result(ValidationResult(
                name="SECRET_KEY",
                passed=True,
                severity=ValidationSeverity.CRITICAL,
                message="Secret key is properly configured"
            ))
    
    def _validate_environment_mode(self):
        """Validate environment configuration"""
        if settings.DEBUG and settings.ENVIRONMENT == "production":
            self.report.add_result(ValidationResult(
                name="ENVIRONMENT_MODE",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="DEBUG=True in production environment",
                details="Set DEBUG=False for production deployment"
            ))
        else:
            self.report.add_result(ValidationResult(
                name="ENVIRONMENT_MODE",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Environment: {settings.ENVIRONMENT}, Debug: {settings.DEBUG}"
            ))
    
    def _validate_required_settings(self):
        """Validate required configuration settings"""
        required = {
            "MONGODB_URL": settings.MONGODB_URL,
            "REDIS_URL": settings.REDIS_URL,
            "DATABASE_NAME": settings.DATABASE_NAME,
        }
        
        for name, value in required.items():
            if not value:
                self.report.add_result(ValidationResult(
                    name=name,
                    passed=False,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"{name} is not configured",
                    details=f"Set {name} in environment variables or .env file"
                ))
            else:
                self.report.add_result(ValidationResult(
                    name=name,
                    passed=True,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"{name} is configured"
                ))
    
    def _validate_api_keys(self):
        """Validate external API keys"""
        api_keys = {
            "GEMINI_API_KEY": (settings.GEMINI_API_KEY, ValidationSeverity.WARNING),
            "GOOGLE_MAPS_API_KEY": (settings.GOOGLE_MAPS_API_KEY, ValidationSeverity.INFO),
            "OPENWEATHER_API_KEY": (settings.OPENWEATHER_API_KEY, ValidationSeverity.INFO),
        }
        
        for name, (value, severity) in api_keys.items():
            if value:
                self.report.add_result(ValidationResult(
                    name=name,
                    passed=True,
                    severity=severity,
                    message=f"{name} is configured"
                ))
            else:
                feature_impact = {
                    "GEMINI_API_KEY": "LLM chat features may be limited",
                    "GOOGLE_MAPS_API_KEY": "Maps & location features will use fallback data",
                    "OPENWEATHER_API_KEY": "Weather features will use mock data"
                }.get(name, "Some features may be unavailable")
                
                self.report.add_result(ValidationResult(
                    name=name,
                    passed=False,
                    severity=severity,
                    message=f"{name} is not configured",
                    details=feature_impact
                ))
    
    def _validate_security_settings(self):
        """Validate security-related settings"""
        # Password policy
        if settings.PASSWORD_MIN_LENGTH < 8:
            self.report.add_result(ValidationResult(
                name="PASSWORD_POLICY",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Password minimum length is below recommended (8)",
                details=f"Current: {settings.PASSWORD_MIN_LENGTH}"
            ))
        else:
            self.report.add_result(ValidationResult(
                name="PASSWORD_POLICY",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Password policy meets minimum requirements"
            ))
        
        # Rate limiting
        if not settings.RATE_LIMIT_ENABLED:
            self.report.add_result(ValidationResult(
                name="RATE_LIMITING",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="Rate limiting is disabled",
                details="Enable rate limiting for production"
            ))
        else:
            self.report.add_result(ValidationResult(
                name="RATE_LIMITING",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Rate limiting is enabled"
            ))
    
    async def _validate_mongodb(self):
        """Validate MongoDB connection"""
        client = None
        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            
            # Create client with timeout
            client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=3000
            )
            
            # Test connection with timeout
            await asyncio.wait_for(
                client.admin.command('ping'),
                timeout=5.0
            )
            
            self.report.add_result(ValidationResult(
                name="MONGODB",
                passed=True,
                severity=ValidationSeverity.CRITICAL,
                message="MongoDB connection successful"
            ))
        except asyncio.TimeoutError:
            self.report.add_result(ValidationResult(
                name="MONGODB",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="MongoDB connection timed out",
                details="Start MongoDB with: docker-compose up -d mongodb"
            ))
        except Exception as e:
            self.report.add_result(ValidationResult(
                name="MONGODB",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="MongoDB connection failed",
                details=f"{str(e)} - Start with: docker-compose up -d mongodb"
            ))
        finally:
            # Ensure client is closed properly
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass  # Ignore close errors
    
    async def _validate_redis(self):
        """Validate Redis connection"""
        try:
            import asyncio
            import redis.asyncio as redis
            
            async def check_redis():
                client = redis.from_url(
                    settings.REDIS_URL,
                    socket_connect_timeout=3
                )
                try:
                    await client.ping()
                finally:
                    await client.close()
            
            # Add overall timeout protection
            await asyncio.wait_for(check_redis(), timeout=5.0)
            
            self.report.add_result(ValidationResult(
                name="REDIS",
                passed=True,
                severity=ValidationSeverity.CRITICAL,
                message="Redis connection successful"
            ))
        except asyncio.TimeoutError:
            self.report.add_result(ValidationResult(
                name="REDIS",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Redis connection timed out",
                details="Start Redis with: docker-compose up -d redis"
            ))
        except Exception as e:
            self.report.add_result(ValidationResult(
                name="REDIS",
                passed=False,
                severity=ValidationSeverity.CRITICAL,
                message="Redis connection failed",
                details=f"{str(e)} - Start with: docker-compose up -d redis"
            ))
    
    async def _validate_rasa(self):
        """Validate Rasa server connection"""
        # Skip validation if Rasa is not enabled
        if not settings.RASA_ENABLED:
            self.report.add_result(ValidationResult(
                name="RASA_SERVER",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="Rasa NLU disabled - using LLM-only mode (recommended)"
            ))
            return
            
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.RASA_SERVER_URL}/")
                
                if response.status_code == 200:
                    self.report.add_result(ValidationResult(
                        name="RASA_SERVER",
                        passed=True,
                        severity=ValidationSeverity.INFO,
                        message="Rasa server is accessible"
                    ))
                else:
                    raise Exception(f"Status code: {response.status_code}")
                    
        except Exception as e:
            self.report.add_result(ValidationResult(
                name="RASA_SERVER",
                passed=False,
                severity=ValidationSeverity.INFO,
                message="Rasa server unavailable (LLM fallback active)",
                details=f"This is OK - app will use LLM for NLU. Error: {str(e)}"
            ))
    
    async def _validate_llm_providers(self):
        """Validate LLM provider configuration"""
        if not settings.LLM_ENABLED:
            self.report.add_result(ValidationResult(
                name="LLM_PROVIDERS",
                passed=True,
                severity=ValidationSeverity.INFO,
                message="LLM is disabled by configuration"
            ))
            return
        
        # Check if at least one LLM provider is configured
        providers_configured = [
            ("Gemini", bool(settings.GEMINI_API_KEY)),
            ("Qwen", bool(settings.QWEN_API_KEY)),
            ("Mistral", bool(settings.MISTRAL_API_KEY)),
        ]
        
        configured_count = sum(1 for _, configured in providers_configured if configured)
        configured_names = [name for name, configured in providers_configured if configured]
        
        if configured_count == 0:
            self.report.add_result(ValidationResult(
                name="LLM_PROVIDERS",
                passed=False,
                severity=ValidationSeverity.WARNING,
                message="No LLM providers configured",
                details="Configure at least one: GEMINI_API_KEY, QWEN_API_KEY, or MISTRAL_API_KEY"
            ))
        else:
            self.report.add_result(ValidationResult(
                name="LLM_PROVIDERS",
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"LLM providers configured: {', '.join(configured_names)}"
            ))


async def validate_startup_environment() -> bool:
    """
    Main entry point for startup validation
    
    Returns:
        True if validation passed, False if critical failures exist
    
    Raises:
        SystemExit: If critical failures exist and DEBUG=False
    """
    validator = StartupValidator()
    report = await validator.validate_all()
    
    if report.has_critical_failures:
        logger.error("CRITICAL: Startup validation failed!")
        logger.error("The following critical issues must be resolved:")
        
        for result in report.results:
            if not result.passed and result.severity == ValidationSeverity.CRITICAL:
                logger.error(f"  - {result.name}: {result.message}")
                if result.details:
                    logger.error(f"    Fix: {result.details}")
        
        if not settings.DEBUG:
            raise SystemExit(1)
        else:
            logger.warning("Continuing in DEBUG mode despite critical failures...")
            return False
    
    if report.has_warnings:
        logger.info("Startup validation completed with optional service warnings")
        logger.info("App will run with available services - check logs for details")
    else:
        logger.info("✅ All startup validations passed successfully")
    
    return True
