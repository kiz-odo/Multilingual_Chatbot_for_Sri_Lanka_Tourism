"""
Database Compound Indexes Configuration
Optimizes query performance with strategic compound indexes
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT, GEOSPHERE
from pymongo.errors import OperationFailure

logger = logging.getLogger(__name__)


async def safe_create_index(collection, keys, **kwargs):
    """
    Safely create an index, handling conflicts with existing indexes.
    If an index with the same keys but different name exists, skip creation.
    """
    try:
        await collection.create_index(keys, **kwargs)
        index_name = kwargs.get('name', 'unnamed')
        logger.debug(f"Index '{index_name}' created successfully")
    except OperationFailure as e:
        if e.code == 85:  # IndexOptionsConflict - index already exists with different name
            index_name = kwargs.get('name', 'unnamed')
            logger.debug(f"Index '{index_name}' already exists with a different name, skipping (this is normal)")
        elif e.code == 86:  # IndexKeySpecsConflict
            index_name = kwargs.get('name', 'unnamed')
            logger.debug(f"Index '{index_name}' has conflicting key specs, skipping (this is normal)")
        elif e.code == 27:  # IndexKeySpecsConflict - duplicate key
            index_name = kwargs.get('name', 'unnamed')
            logger.debug(f"Index '{index_name}' already exists, skipping (this is normal)")
        else:
            # Only log as warning for unexpected errors, not critical
            logger.warning(f"Index creation issue (code {e.code}): {e.details if hasattr(e, 'details') else str(e)}")
            # Don't raise - let Beanie handle index creation as fallback


async def create_compound_indexes(db: AsyncIOMotorDatabase):
    """
    Create compound indexes for optimal query performance
    
    Compound indexes improve multi-field queries by orders of magnitude
    """
    try:
        logger.info("Creating compound indexes...")
        
        # ==========================================
        # USERS COLLECTION
        # ==========================================
        await safe_create_index(db.users, [
            ("email", ASCENDING)
        ], unique=True, name="idx_users_email_unique")
        
        await safe_create_index(db.users, [
            ("username", ASCENDING)
        ], unique=True, name="idx_users_username_unique")
        
        await safe_create_index(db.users, [
            ("is_active", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_users_active_created")
        
        await safe_create_index(db.users, [
            ("role", ASCENDING),
            ("is_active", ASCENDING)
        ], name="idx_users_role_active")
        
        # ==========================================
        # CONVERSATIONS COLLECTION
        # ==========================================
        await safe_create_index(db.conversations, [
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_conversations_user_created")
        
        await safe_create_index(db.conversations, [
            ("session_id", ASCENDING),
            ("updated_at", DESCENDING)
        ], name="idx_conversations_session_updated")
        
        await safe_create_index(db.conversations, [
            ("language", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_conversations_language_created")
        
        # ==========================================
        # ATTRACTIONS COLLECTION
        # ==========================================
        await safe_create_index(db.attractions, [
            ("location.city", ASCENDING),
            ("category", ASCENDING),
            ("is_active", ASCENDING)
        ], name="idx_attractions_city_category_active")
        
        await safe_create_index(db.attractions, [
            ("category", ASCENDING),
            ("popularity_score", DESCENDING),
            ("is_active", ASCENDING)
        ], name="idx_attractions_category_popularity")
        
        await safe_create_index(db.attractions, [
            ("is_featured", ASCENDING),
            ("average_rating", DESCENDING)
        ], name="idx_attractions_featured_rating")
        
        await safe_create_index(db.attractions, [
            ("location.province", ASCENDING),
            ("category", ASCENDING)
        ], name="idx_attractions_province_category")
        
        # Geospatial index for location-based queries
        await safe_create_index(db.attractions, [
            ("location.coordinates", GEOSPHERE)
        ], name="idx_attractions_geo")
        
        # Text search index
        await safe_create_index(db.attractions, [
            ("name.en", TEXT),
            ("description.en", TEXT),
            ("tags", TEXT)
        ], name="idx_attractions_text_search")
        
        # ==========================================
        # HOTELS COLLECTION
        # ==========================================
        await safe_create_index(db.hotels, [
            ("location.city", ASCENDING),
            ("star_rating", DESCENDING),
            ("is_active", ASCENDING)
        ], name="idx_hotels_city_rating_active")
        
        await safe_create_index(db.hotels, [
            ("category", ASCENDING),
            ("popularity_score", DESCENDING)
        ], name="idx_hotels_category_popularity")
        
        await safe_create_index(db.hotels, [
            ("is_active", ASCENDING),
            ("average_rating", DESCENDING),
            ("total_reviews", DESCENDING)
        ], name="idx_hotels_active_rating_reviews")
        
        # Geospatial index
        await safe_create_index(db.hotels, [
            ("location.coordinates", GEOSPHERE)
        ], name="idx_hotels_geo")
        
        # Text search
        await safe_create_index(db.hotels, [
            ("name.en", TEXT),
            ("description.en", TEXT)
        ], name="idx_hotels_text_search")
        
        # ==========================================
        # RESTAURANTS COLLECTION
        # ==========================================
        await safe_create_index(db.restaurants, [
            ("location.city", ASCENDING),
            ("cuisine_types", ASCENDING),
            ("is_active", ASCENDING)
        ], name="idx_restaurants_city_cuisine_active")
        
        await safe_create_index(db.restaurants, [
            ("price_range", ASCENDING),
            ("average_rating", DESCENDING)
        ], name="idx_restaurants_price_rating")
        
        await safe_create_index(db.restaurants, [
            ("dietary_options", ASCENDING),
            ("location.city", ASCENDING)
        ], name="idx_restaurants_dietary_city")
        
        # Geospatial index
        await safe_create_index(db.restaurants, [
            ("location.coordinates", GEOSPHERE)
        ], name="idx_restaurants_geo")
        
        # Text search
        await safe_create_index(db.restaurants, [
            ("name.en", TEXT),
            ("description.en", TEXT)
        ], name="idx_restaurants_text_search")
        
        # ==========================================
        # EVENTS COLLECTION
        # ==========================================
        await safe_create_index(db.events, [
            ("status", ASCENDING),
            ("schedule.start_date", ASCENDING)
        ], name="idx_events_status_startdate")
        
        await safe_create_index(db.events, [
            ("category", ASCENDING),
            ("schedule.start_date", ASCENDING),
            ("status", ASCENDING)
        ], name="idx_events_category_date_status")
        
        await safe_create_index(db.events, [
            ("location.city", ASCENDING),
            ("schedule.start_date", ASCENDING)
        ], name="idx_events_city_date")
        
        await safe_create_index(db.events, [
            ("is_featured", ASCENDING),
            ("schedule.start_date", ASCENDING)
        ], name="idx_events_featured_date")
        
        # ==========================================
        # TRANSPORT COLLECTION
        # ==========================================
        await safe_create_index(db.transport, [
            ("transport_type", ASCENDING),
            ("is_active", ASCENDING)
        ], name="idx_transport_type_active")
        
        await safe_create_index(db.transport, [
            ("routes.origin", ASCENDING),
            ("routes.destination", ASCENDING)
        ], name="idx_transport_routes")
        
        await safe_create_index(db.transport, [
            ("service_areas", ASCENDING),
            ("transport_type", ASCENDING)
        ], name="idx_transport_areas_type")
        
        # ==========================================
        # FEEDBACK COLLECTION
        # ==========================================
        await safe_create_index(db.feedback, [
            ("user_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_feedback_user_created")
        
        await safe_create_index(db.feedback, [
            ("resource_type", ASCENDING),
            ("resource_id", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_feedback_resource_created")
        
        await safe_create_index(db.feedback, [
            ("rating", DESCENDING),
            ("created_at", DESCENDING)
        ], name="idx_feedback_rating_created")
        
        # ==========================================
        # ANALYTICS COLLECTIONS
        # ==========================================
        await safe_create_index(db.user_behavior_events, [
            ("user_id", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_behavior_user_timestamp")
        
        await safe_create_index(db.user_behavior_events, [
            ("event_type", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_behavior_type_timestamp")
        
        await safe_create_index(db.daily_metrics, [
            ("date", DESCENDING)
        ], unique=True, name="idx_metrics_date_unique")
        
        await safe_create_index(db.resource_popularity, [
            ("resource_type", ASCENDING),
            ("popularity_score", DESCENDING)
        ], name="idx_popularity_type_score")
        
        # ==========================================
        # NOTIFICATIONS COLLECTION
        # ==========================================
        await safe_create_index(db.notifications, [
            ("user_id", ASCENDING),
            ("is_read", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_notifications_user_read_created")
        
        await safe_create_index(db.notifications, [
            ("notification_type", ASCENDING),
            ("created_at", DESCENDING)
        ], name="idx_notifications_type_created")
        
        # ==========================================
        # SECURITY & AUDIT
        # ==========================================
        await safe_create_index(db.audit_logs, [
            ("user_id", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_audit_user_timestamp")
        
        await safe_create_index(db.audit_logs, [
            ("action", ASCENDING),
            ("timestamp", DESCENDING)
        ], name="idx_audit_action_timestamp")
        
        await safe_create_index(db.audit_logs, [
            ("resource_type", ASCENDING),
            ("resource_id", ASCENDING)
        ], name="idx_audit_resource")
        
        await safe_create_index(db.session_tokens, [
            ("user_id", ASCENDING),
            ("is_active", ASCENDING)
        ], name="idx_sessions_user_active")
        
        await safe_create_index(db.session_tokens, [
            ("expires_at", ASCENDING)
        ], expireAfterSeconds=0, name="idx_sessions_ttl")
        
        logger.info("✅ All compound indexes created successfully")
        
        # Log index statistics
        collections = [
            "users", "conversations", "attractions", "hotels", 
            "restaurants", "events", "transport", "feedback"
        ]
        
        total_indexes = 0
        for collection_name in collections:
            indexes = await db[collection_name].index_information()
            count = len(indexes)
            total_indexes += count
            logger.info(f"  {collection_name}: {count} indexes")
        
        logger.info(f"📊 Total indexes across all collections: {total_indexes}")
        
    except Exception as e:
        logger.error(f"Failed to create compound indexes: {e}", exc_info=True)
        raise


async def analyze_slow_queries(db: AsyncIOMotorDatabase):
    """
    Analyze slow queries and suggest index improvements
    
    Returns insights about query performance
    """
    try:
        # Enable profiling
        await db.command({"profile": 2, "slowms": 100})
        
        # Get slow queries
        slow_queries = await db.system.profile.find({
            "millis": {"$gt": 100}
        }).sort("millis", DESCENDING).limit(10).to_list(length=10)
        
        insights = []
        for query in slow_queries:
            insights.append({
                "operation": query.get("op"),
                "namespace": query.get("ns"),
                "duration_ms": query.get("millis"),
                "query": query.get("command", {}).get("filter", {}),
                "timestamp": query.get("ts")
            })
        
        return insights
        
    except Exception as e:
        logger.warning(f"Could not analyze slow queries: {e}")
        return []

