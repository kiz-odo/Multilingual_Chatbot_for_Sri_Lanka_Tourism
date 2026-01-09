"""
Database Migration System for MongoDB
Handles schema migrations, data migrations, and version tracking
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Callable
from enum import Enum
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class MigrationStatus(str, Enum):
    """Migration execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.executed_at = None
        self.status = MigrationStatus.PENDING
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Apply migration (must be implemented by subclass)"""
        raise NotImplementedError("Migration must implement up() method")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback migration (optional, for reversible migrations)"""
        logger.warning(f"Migration {self.version} does not implement down() - rollback not available")


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
        self.migrations: List[Migration] = []
        self.migrations_collection = "schema_migrations"
    
    async def connect(self):
        """Connect to database"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Migration manager connected to database")
            
            # Ensure migrations collection exists
            await self._ensure_migrations_collection()
            
        except Exception as e:
            logger.error(f"Failed to connect migration manager: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.client:
            self.client.close()
            logger.info("Migration manager disconnected")
    
    async def _ensure_migrations_collection(self):
        """Create migrations tracking collection if it doesn't exist"""
        collections = await self.db.list_collection_names()
        if self.migrations_collection not in collections:
            await self.db.create_collection(self.migrations_collection)
            logger.info(f"Created {self.migrations_collection} collection")
    
    def register_migration(self, migration: Migration):
        """Register a migration"""
        self.migrations.append(migration)
        logger.debug(f"Registered migration: {migration.version} - {migration.description}")
    
    async def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations from database"""
        cursor = self.db[self.migrations_collection].find().sort("version", 1)
        return await cursor.to_list(length=None)
    
    async def is_migration_applied(self, version: str) -> bool:
        """Check if a migration has been applied"""
        result = await self.db[self.migrations_collection].find_one({"version": version})
        return result is not None
    
    async def record_migration(self, migration: Migration, status: MigrationStatus, error: str = None):
        """Record migration execution in database"""
        record = {
            "version": migration.version,
            "description": migration.description,
            "status": status.value,
            "executed_at": datetime.utcnow(),
            "error": error
        }
        
        await self.db[self.migrations_collection].update_one(
            {"version": migration.version},
            {"$set": record},
            upsert=True
        )
    
    async def run_pending_migrations(self) -> Dict[str, Any]:
        """Run all pending migrations"""
        if not self.db:
            await self.connect()
        
        logger.info("Checking for pending migrations...")
        
        applied_migrations = await self.get_applied_migrations()
        applied_versions = {m["version"] for m in applied_migrations}
        
        pending_migrations = [
            m for m in self.migrations
            if m.version not in applied_versions
        ]
        
        if not pending_migrations:
            logger.info("No pending migrations")
            return {
                "status": "success",
                "message": "No pending migrations",
                "applied": 0
            }
        
        logger.info(f"Found {len(pending_migrations)} pending migration(s)")
        
        results = {
            "total": len(pending_migrations),
            "success": 0,
            "failed": 0,
            "migrations": []
        }
        
        for migration in pending_migrations:
            try:
                logger.info(f"Applying migration {migration.version}: {migration.description}")
                
                # Update status to running
                await self.record_migration(migration, MigrationStatus.RUNNING)
                
                # Execute migration
                await migration.up(self.db)
                
                # Record success
                await self.record_migration(migration, MigrationStatus.COMPLETED)
                
                results["success"] += 1
                results["migrations"].append({
                    "version": migration.version,
                    "status": "success"
                })
                
                logger.info(f"✓ Migration {migration.version} completed successfully")
                
            except Exception as e:
                logger.error(f"✗ Migration {migration.version} failed: {e}", exc_info=True)
                
                # Record failure
                await self.record_migration(migration, MigrationStatus.FAILED, str(e))
                
                results["failed"] += 1
                results["migrations"].append({
                    "version": migration.version,
                    "status": "failed",
                    "error": str(e)
                })
                
                # Stop on first failure
                logger.error("Stopping migration process due to failure")
                break
        
        return results
    
    async def rollback_migration(self, version: str) -> Dict[str, Any]:
        """Rollback a specific migration"""
        if not self.db:
            await self.connect()
        
        # Find the migration
        migration = next((m for m in self.migrations if m.version == version), None)
        
        if not migration:
            return {
                "status": "error",
                "message": f"Migration {version} not found"
            }
        
        # Check if migration was applied
        if not await self.is_migration_applied(version):
            return {
                "status": "error",
                "message": f"Migration {version} was not applied"
            }
        
        try:
            logger.info(f"Rolling back migration {version}")
            
            # Execute rollback
            await migration.down(self.db)
            
            # Record rollback
            await self.record_migration(migration, MigrationStatus.ROLLED_BACK)
            
            logger.info(f"✓ Migration {version} rolled back successfully")
            
            return {
                "status": "success",
                "message": f"Migration {version} rolled back successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Rollback failed: {str(e)}"
            }
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        if not self.db:
            await self.connect()
        
        applied = await self.get_applied_migrations()
        applied_versions = {m["version"] for m in applied}
        
        pending = [
            {
                "version": m.version,
                "description": m.description
            }
            for m in self.migrations
            if m.version not in applied_versions
        ]
        
        return {
            "total_migrations": len(self.migrations),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "applied": applied,
            "pending": pending
        }


# Global migration manager instance
migration_manager = MigrationManager()


# ==========================================
# PRODUCTION MIGRATIONS
# ==========================================

class Migration_001_InitialSchema(Migration):
    """Initial database schema setup - Create all compound indexes"""
    
    def __init__(self):
        super().__init__("001", "Initial schema - Create all compound indexes")
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Create all compound indexes for optimal query performance"""
        logger.info("Creating all compound indexes...")
        
        # Import the index creation function
        from backend.app.core.database_indexes import create_compound_indexes
        
        # Create all indexes
        await create_compound_indexes(db)
        
        logger.info("✅ Initial schema migration completed - All indexes created")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback: Remove indexes (use with caution in production)"""
        logger.warning("Rollback: Index removal not implemented for safety")
        # In production, index removal should be done manually if needed
        # to prevent accidental data loss


class Migration_002_ItineraryIndexes(Migration):
    """Add indexes for itinerary collections"""
    
    def __init__(self):
        super().__init__("002", "Add itinerary and recommendation indexes")
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Create indexes for itinerary and recommendation collections"""
        logger.info("Creating itinerary and recommendation indexes...")
        
        from backend.app.core.database_indexes import safe_create_index
        from pymongo import ASCENDING, DESCENDING
        
        # Itinerary indexes
        await safe_create_index(db.trip_itineraries, [
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_itineraries_user_created")
        
        await safe_create_index(db.trip_itineraries, [
            ("travel_dates.start", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_itineraries_dates_status")
        
        await safe_create_index(db.trip_itineraries, [
            ("share_token", ASCENDING)
        ], unique=True, name="idx_itineraries_share_token")
        
        # Recommendation indexes
        await safe_create_index(db.recommendation_results, [
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_recommendations_user_created")
        
        await safe_create_index(db.recommendation_results, [
            ("resource_type", ASCENDING),
            ("score", DESCENDING)
        ], name="idx_recommendations_type_score")
        
        logger.info("✅ Itinerary and recommendation indexes created")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback: Remove itinerary indexes"""
        logger.warning("Rollback: Index removal not implemented for safety")


class Migration_003_SafetyIndexes(Migration):
    """Add indexes for safety and emergency collections"""
    
    def __init__(self):
        super().__init__("003", "Add safety and emergency indexes")
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Create indexes for safety collections"""
        logger.info("Creating safety and emergency indexes...")
        
        from backend.app.core.database_indexes import safe_create_index
        from pymongo import ASCENDING, DESCENDING, GEOSPHERE
        
        # SOS Alerts indexes
        await safe_create_index(db.sos_alerts, [
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_sos_user_created")
        
        await safe_create_index(db.sos_alerts, [
            ("status", ASCENDING),
            ("severity", DESCENDING)
        ], name="idx_sos_status_severity")
        
        # Location Sharing indexes
        await safe_create_index(db.location_sharing, [
            ("user_id", ASCENDING),
            ("is_active", ASCENDING)
        ], name="idx_location_sharing_user_active")
        
        await safe_create_index(db.location_sharing, [
            ("share_token", ASCENDING)
        ], unique=True, name="idx_location_sharing_token")
        
        # Safety Scores indexes
        await safe_create_index(db.safety_scores, [
            ("city", ASCENDING),
            ("updated_at", DESCENDING)
        ], name="idx_safety_scores_city_updated")
        
        # Travel Alerts indexes
        await safe_create_index(db.travel_alerts, [
            ("city", ASCENDING),
            ("is_active", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_travel_alerts_city_active")
        
        logger.info("✅ Safety and emergency indexes created")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback: Remove safety indexes"""
        logger.warning("Rollback: Index removal not implemented for safety")


class Migration_004_ForumIndexes(Migration):
    """Add indexes for forum and challenge collections"""
    
    def __init__(self):
        super().__init__("004", "Add forum and challenge indexes")
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Create indexes for forum and challenge collections"""
        logger.info("Creating forum and challenge indexes...")
        
        from backend.app.core.database_indexes import safe_create_index
        from pymongo import ASCENDING, DESCENDING, TEXT
        
        # Forum Posts indexes
        await safe_create_index(db.forum_posts, [
            ("author_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_forum_posts_author_created")
        
        await safe_create_index(db.forum_posts, [
            ("category", ASCENDING),
            ("is_pinned", DESCENDING),
            ("created_at", DESCENDING)
        ], name="idx_forum_posts_category_pinned")
        
        await safe_create_index(db.forum_posts, [
            ("title", TEXT),
            ("content", TEXT)
        ], name="idx_forum_posts_text_search")
        
        # Comments indexes
        await safe_create_index(db.comments, [
            ("post_id", ASCENDING),
            ("created_at", ASCENDING)
        ], name="idx_comments_post_created")
        
        await safe_create_index(db.comments, [
            ("author_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_comments_author_created")
        
        # Challenges indexes
        await safe_create_index(db.challenges, [
            ("status", ASCENDING),
            ("start_date", ASCENDING)
        ], name="idx_challenges_status_start")
        
        await safe_create_index(db.challenge_check_ins, [
            ("challenge_id", ASCENDING),
            ("user_id", ASCENDING),
            ("check_in_date", DESCENDING)
        ], name="idx_challenge_checkins_challenge_user")
        
        await safe_create_index(db.user_challenge_progress, [
            ("user_id", ASCENDING),
            ("challenge_id", ASCENDING)
        ], unique=True, name="idx_user_challenge_progress_unique")
        
        logger.info("✅ Forum and challenge indexes created")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback: Remove forum indexes"""
        logger.warning("Rollback: Index removal not implemented for safety")


# Register all migrations
migration_manager.register_migration(Migration_001_InitialSchema())
migration_manager.register_migration(Migration_002_ItineraryIndexes())
migration_manager.register_migration(Migration_003_SafetyIndexes())
migration_manager.register_migration(Migration_004_ForumIndexes())


# ==========================================
# CLI Functions
# ==========================================

async def run_migrations():
    """Run all pending migrations"""
    try:
        await migration_manager.connect()
        results = await migration_manager.run_pending_migrations()
        await migration_manager.disconnect()
        return results
    except Exception as e:
        logger.error(f"Migration execution failed: {e}")
        raise


async def get_migration_status():
    """Get migration status"""
    try:
        await migration_manager.connect()
        status = await migration_manager.get_migration_status()
        await migration_manager.disconnect()
        return status
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise


if __name__ == "__main__":
    # Run migrations when executed directly
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "migrate":
            asyncio.run(run_migrations())
        elif command == "status":
            status = asyncio.run(get_migration_status())
            print(f"\nMigration Status:")
            print(f"  Total: {status['total_migrations']}")
            print(f"  Applied: {status['applied_count']}")
            print(f"  Pending: {status['pending_count']}")
        else:
            print("Usage: python -m backend.app.core.migrations [migrate|status]")
    else:
        asyncio.run(run_migrations())

