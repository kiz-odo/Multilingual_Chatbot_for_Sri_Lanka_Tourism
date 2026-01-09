"""
Database configuration and initialization for MongoDB
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.conversation import Conversation
from backend.app.models.attraction import Attraction
from backend.app.models.restaurant import Restaurant
from backend.app.models.hotel import Hotel
from backend.app.models.transport import Transport
from backend.app.models.emergency import Emergency
from backend.app.models.event import Event
from backend.app.models.feedback import Feedback
from backend.app.models.analytics import (
    UserBehaviorEvent,
    ConversationAnalytics,
    DailyMetrics,
    ResourcePopularity,
    UserSegmentProfile
)
from backend.app.models.recommendation import (
    UserPreferenceProfile,
    RecommendationEngine,
    RecommendationResult,
    ItemSimilarity,
    CollaborativeFilter,
    ContextualFactor
)
from backend.app.models.notification import (
    NotificationTemplate,
    Notification,
    UserNotificationPreferences,
    NotificationCampaign
)
from backend.app.models.security import (
    UserMFA,
    AuditLog,
    APIKey,
    SessionToken,
    SecurityAlert,
    RateLimitEntry,
    DataAccessLog,
    EmailVerificationToken
)
from backend.app.models.itinerary import (
    TripItinerary,
    BookingTracking
)
from backend.app.models.safety import (
    SOSAlert,
    LocationSharing,
    SafetyScore,
    TravelAlert,
    UserSafetyProfile,
    SafetyCheckIn
)
from backend.app.models.forum import ForumPost, Comment
from backend.app.models.challenge import Challenge, ChallengeCheckIn, UserChallengeProgress

logger = logging.getLogger(__name__)


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    """Get database instance"""
    return db.database


async def init_database():
    """Initialize database connection and setup with connection pooling"""
    try:
        # Create MongoDB client with optimized connection pooling
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            maxIdleTimeMS=settings.MONGODB_MAX_IDLE_TIME_MS,
            serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
            retryWrites=True,  # Enable retryable writes
            retryReads=True,  # Enable retryable reads
        )
        db.database = db.client[settings.DATABASE_NAME]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=db.database,
            document_models=[
                # Core Models
                User,
                Conversation,
                Attraction,
                Restaurant,
                Hotel,
                Transport,
                Emergency,
                Event,
                Feedback,
                # Analytics Models
                UserBehaviorEvent,
                ConversationAnalytics,
                DailyMetrics,
                ResourcePopularity,
                UserSegmentProfile,
                # Recommendation Models
                UserPreferenceProfile,
                RecommendationEngine,
                RecommendationResult,
                ItemSimilarity,
                CollaborativeFilter,
                ContextualFactor,
                # Notification Models
                NotificationTemplate,
                Notification,
                UserNotificationPreferences,
                NotificationCampaign,
                # Security Models
                UserMFA,
                AuditLog,
                APIKey,
                SessionToken,
                SecurityAlert,
                RateLimitEntry,
                DataAccessLog,
                EmailVerificationToken,
                # Itinerary Models
                TripItinerary,
                BookingTracking,
                # Safety Models
                SOSAlert,
                LocationSharing,
                SafetyScore,
                TravelAlert,
                UserSafetyProfile,
                SafetyCheckIn,
                # Forum Models
                ForumPost,
                Comment,
                # Challenge Models
                Challenge,
                ChallengeCheckIn,
                UserChallengeProgress
            ]
        )
        
        logger.info("Beanie initialized successfully")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Skip index creation if database is not properly initialized
        if db.database is None:
            logger.warning("Database not initialized, skipping index creation")
            return
            
        logger.info("Creating optimized compound indexes...")
        
        # Import and create compound indexes
        from backend.app.core.database_indexes import create_compound_indexes
        await create_compound_indexes(db.database)
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Index creation encountered issues: {e}")
        # Don't raise the exception to prevent startup failure
        # Indexes will be created by Beanie automatically as fallback


async def close_database():
    """Close database connection gracefully"""
    if db.client:
        try:
            # Wait for in-flight operations to complete
            logger.info("Closing database connections...")
            db.client.close()
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
