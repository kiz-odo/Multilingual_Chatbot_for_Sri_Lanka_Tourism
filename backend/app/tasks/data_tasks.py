"""
Data processing background tasks
"""

import logging
from datetime import datetime, timedelta
from backend.app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.app.tasks.data_tasks.cleanup_old_sessions")
async def cleanup_old_sessions():
    """
    Clean up old conversation sessions and expired tokens
    Runs daily at 2 AM
    """
    try:
        logger.info("Starting cleanup of old sessions")
        
        from backend.app.models.conversation import Conversation
        from backend.app.models.security import SessionToken
        
        # Calculate cutoff date (30 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Delete old conversations
        deleted_conversations = await Conversation.find(
            Conversation.updated_at < cutoff_date,
            Conversation.is_active == False
        ).delete()
        
        # Delete expired session tokens
        deleted_tokens = await SessionToken.find(
            SessionToken.expires_at < datetime.utcnow()
        ).delete()
        
        # Delete expired email verification tokens
        from backend.app.models.security import EmailVerificationToken
        deleted_email_tokens = await EmailVerificationToken.find(
            EmailVerificationToken.expires_at < datetime.utcnow()
        ).delete()
        
        logger.info(f"Cleanup completed: {deleted_conversations.deleted_count} conversations, "
                   f"{deleted_tokens.deleted_count} tokens, "
                   f"{deleted_email_tokens.deleted_count} email tokens")
        
        return {
            "status": "success",
            "deleted_conversations": deleted_conversations.deleted_count,
            "deleted_tokens": deleted_tokens.deleted_count,
            "deleted_email_tokens": deleted_email_tokens.deleted_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        raise


@celery_app.task(name="backend.app.tasks.data_tasks.generate_daily_analytics")
async def generate_daily_analytics():
    """
    Generate daily analytics reports
    Runs daily at 1 AM
    """
    try:
        logger.info("Starting daily analytics generation")
        
        from backend.app.models.analytics import DailyMetrics, UserBehaviorEvent
        from backend.app.models.user import User
        from backend.app.models.conversation import Conversation
        
        # Yesterday's date
        yesterday = datetime.utcnow() - timedelta(days=1)
        start_of_day = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Count active users (users who had activity yesterday)
        active_users = await UserBehaviorEvent.find(
            UserBehaviorEvent.timestamp >= start_of_day,
            UserBehaviorEvent.timestamp <= end_of_day
        ).distinct("user_id")
        
        # Count conversations
        total_conversations = await Conversation.find(
            Conversation.created_at >= start_of_day,
            Conversation.created_at <= end_of_day
        ).count()
        
        # Count total messages
        total_messages = 0
        conversations = await Conversation.find(
            Conversation.created_at >= start_of_day,
            Conversation.created_at <= end_of_day
        ).to_list()
        
        for conv in conversations:
            total_messages += len(conv.messages) if hasattr(conv, 'messages') else 0
        
        # Create daily metrics
        metrics = DailyMetrics(
            date=yesterday.date(),
            total_users=len(active_users),
            total_conversations=total_conversations,
            total_messages=total_messages,
            avg_response_time=0.0,  # Calculate from conversation timestamps if needed
            metadata={
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        await metrics.insert()
        
        logger.info(f"Daily analytics generated: {len(active_users)} active users, "
                   f"{total_conversations} conversations, {total_messages} messages")
        
        return {
            "status": "success",
            "date": yesterday.date().isoformat(),
            "active_users": len(active_users),
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analytics generation failed: {e}")
        raise


@celery_app.task(name="backend.app.tasks.data_tasks.update_trending_items")
async def update_trending_items():
    """
    Update trending attractions, hotels, restaurants
    Runs every 30 minutes
    """
    try:
        logger.info("Updating trending items")
        
        from backend.app.models.analytics import UserBehaviorEvent, ResourcePopularity
        from backend.app.services.cache_service import CacheService
        
        cache = CacheService()
        
        # Calculate trending based on recent views (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Get view events for attractions
        attraction_views = await UserBehaviorEvent.find(
            UserBehaviorEvent.event_type == "view",
            UserBehaviorEvent.resource_type == "attraction",
            UserBehaviorEvent.timestamp >= cutoff_date
        ).to_list()
        
        # Count views per attraction (with recency weighting)
        attraction_scores = {}
        for event in attraction_views:
            resource_id = event.resource_id
            # Weight more recent views higher
            days_ago = (datetime.utcnow() - event.timestamp).days
            weight = 1.0 / (1 + days_ago * 0.1)  # Decay factor
            attraction_scores[resource_id] = attraction_scores.get(resource_id, 0) + weight
        
        # Sort by score and get top 10
        trending_attractions = sorted(
            attraction_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Similar for hotels
        hotel_views = await UserBehaviorEvent.find(
            UserBehaviorEvent.event_type == "view",
            UserBehaviorEvent.resource_type == "hotel",
            UserBehaviorEvent.timestamp >= cutoff_date
        ).to_list()
        
        hotel_scores = {}
        for event in hotel_views:
            resource_id = event.resource_id
            days_ago = (datetime.utcnow() - event.timestamp).days
            weight = 1.0 / (1 + days_ago * 0.1)
            hotel_scores[resource_id] = hotel_scores.get(resource_id, 0) + weight
        
        trending_hotels = sorted(
            hotel_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Cache trending lists (TTL: 30 minutes)
        await cache.set('trending:attractions', [item[0] for item in trending_attractions], ttl=1800)
        await cache.set('trending:hotels', [item[0] for item in trending_hotels], ttl=1800)
        
        logger.info(f"Trending items updated: {len(trending_attractions)} attractions, {len(trending_hotels)} hotels")
        
        return {
            "status": "success",
            "trending_attractions": len(trending_attractions),
            "trending_hotels": len(trending_hotels),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trending update failed: {e}")
        raise


@celery_app.task(name="backend.app.tasks.data_tasks.process_image_upload")
async def process_image_upload(image_path: str, user_id: str):
    """
    Process uploaded images for landmark recognition
    
    Args:
        image_path: Path to uploaded image
        user_id: User who uploaded the image
    """
    try:
        logger.info(f"Processing image upload: {image_path} for user: {user_id}")
        
        from backend.app.services.landmark_recognition_service import LandmarkRecognitionService
        from PIL import Image
        import os
        
        # Check if file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Resize/optimize image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 1920x1080)
            max_size = (1920, 1080)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=85, optimize=True)
        
        # Run landmark recognition
        landmark_service = LandmarkRecognitionService()
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        result = await landmark_service.recognize_landmark(image_data)
        
        logger.info(f"Image processed successfully: {image_path}, landmarks found: {len(result.get('landmarks', []))}")
        
        return {
            "status": "success",
            "path": image_path,
            "user_id": user_id,
            "landmarks": result.get('landmarks', []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise


@celery_app.task(name="backend.app.tasks.data_tasks.backup_database")
async def backup_database():
    """
    Create database backup
    Should be scheduled via Celery Beat
    """
    try:
        logger.info("Starting database backup")
        
        import subprocess
        import os
        import gzip
        import shutil
        from backend.app.core.config import settings
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        compressed_path = f"{backup_path}.tar.gz"
        
        # Create MongoDB dump using mongodump
        # Extract connection details from MONGODB_URL
        mongo_url = settings.MONGODB_URL
        db_name = settings.DATABASE_NAME
        
        try:
            # Run mongodump command
            cmd = [
                "mongodump",
                "--uri", mongo_url,
                "--db", db_name,
                "--out", backup_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"mongodump failed: {result.stderr}")
                raise Exception(f"Backup command failed: {result.stderr}")
            
            # Compress the backup
            shutil.make_archive(backup_path, 'gztar', backup_path)
            
            # Remove uncompressed backup
            shutil.rmtree(backup_path)
            
            # Get file size
            backup_size = os.path.getsize(compressed_path)
            backup_size_mb = backup_size / (1024 * 1024)
            
            # Clean old backups (keep last 7 days)
            cleanup_old_backups(backup_dir, days_to_keep=7)
            
            logger.info(f"Database backup created: {compressed_path} ({backup_size_mb:.2f} MB)")
            
            return {
                "status": "success",
                "backup": os.path.basename(compressed_path),
                "size_mb": round(backup_size_mb, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Backup timeout (5 minutes)")
            raise Exception("Backup operation timed out")
        except FileNotFoundError:
            logger.warning("mongodump not found. Install MongoDB tools for backup functionality.")
            return {
                "status": "skipped",
                "message": "mongodump not installed",
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise


def cleanup_old_backups(backup_dir: str, days_to_keep: int = 7):
    """Clean up backups older than specified days"""
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
        
        for filename in os.listdir(backup_dir):
            if filename.startswith("backup_") and filename.endswith(".tar.gz"):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    logger.info(f"Removed old backup: {filename}")
    except Exception as e:
        logger.warning(f"Backup cleanup failed: {e}")

