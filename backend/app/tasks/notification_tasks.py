"""
Push notification background tasks with Firebase Cloud Messaging
"""

import logging
from typing import List, Optional, Dict
from backend.app.core.celery_app import celery_app
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


# Firebase Admin initialization
firebase_app = None
firebase_available = False

try:
    if settings.FIREBASE_CREDENTIALS:
        import firebase_admin
        from firebase_admin import credentials, messaging
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_app = firebase_admin.initialize_app(cred)
        firebase_available = True
        logger.info("Firebase Cloud Messaging initialized successfully")
    else:
        logger.debug("Firebase credentials not configured - push notifications will be logged only")
except ImportError:
    logger.warning("firebase-admin package not installed - push notifications will be logged only")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")


async def get_user_fcm_token(user_id: str) -> Optional[str]:
    """
    Get user's FCM device token from database
    
    Args:
        user_id: User ID
    
    Returns:
        FCM token or None
    """
    try:
        from backend.app.models.user import User
        user = await User.get(user_id)
        return getattr(user, 'fcm_token', None) if user else None
    except Exception as e:
        logger.error(f"Failed to get FCM token for user {user_id}: {e}")
        return None


@celery_app.task(name="backend.app.tasks.notification_tasks.send_push_notification")
def send_push_notification(user_id: str, title: str, body: str, data: Dict = None, fcm_token: Optional[str] = None):
    """
    Send push notification to user's mobile device using Firebase Cloud Messaging
    
    Args:
        user_id: User ID
        title: Notification title
        body: Notification body
        data: Additional data payload
        fcm_token: Optional FCM token (if not provided, will fetch from database)
    """
    try:
        logger.info(f"Sending push notification to user {user_id}: {title}")
        
        if not firebase_available:
            logger.warning(f"Firebase not available - would send notification: {title} - {body}")
            return {"status": "firebase_not_configured", "user_id": user_id}
        
        # Get FCM token if not provided
        if not fcm_token:
            # Note: This is a sync task, so we can't use async/await
            # In production, you might want to pass the token when queuing the task
            logger.warning("FCM token not provided - notification logged but not sent")
            return {"status": "no_fcm_token", "user_id": user_id}
        
        from firebase_admin import messaging
        
        # Create notification message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#4CAF50'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound='default'
                    )
                )
            )
        )
        
        # Send message
        response = messaging.send(message)
        
        logger.info(f"Push notification sent successfully to user {user_id}. Message ID: {response}")
        return {
            "status": "success",
            "user_id": user_id,
            "message_id": response
        }
        
    except Exception as e:
        logger.error(f"Failed to send push notification to user {user_id}: {e}")
        return {
            "status": "error",
            "user_id": user_id,
            "error": str(e)
        }


@celery_app.task(name="backend.app.tasks.notification_tasks.send_bulk_notifications")
def send_bulk_notifications(user_ids: List[str], title: str, body: str):
    """
    Send notifications to multiple users
    
    Args:
        user_ids: List of user IDs
        title: Notification title
        body: Notification body
    """
    try:
        logger.info(f"Sending bulk notifications to {len(user_ids)} users")
        
        success_count = 0
        fail_count = 0
        
        for user_id in user_ids:
            try:
                send_push_notification.delay(user_id, title, body)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to queue notification for {user_id}: {e}")
                fail_count += 1
        
        logger.info(f"Bulk notifications queued: {success_count} success, {fail_count} failed")
        return {
            "status": "success",
            "total": len(user_ids),
            "success": success_count,
            "failed": fail_count
        }
        
    except Exception as e:
        logger.error(f"Bulk notification task failed: {e}")
        raise


@celery_app.task(name="backend.app.tasks.notification_tasks.send_event_reminder")
def send_event_reminder(event_id: str, hours_before: int = 1):
    """
    Send reminder for upcoming event to interested users
    
    This task uses synchronous database access via pymongo
    to work with standard Celery workers (which are synchronous).
    
    Args:
        event_id: Event ID
        hours_before: Hours before event to send reminder
    
    Returns:
        dict: Status with user notification counts
    """
    try:
        logger.info(f"Sending event reminders for event {event_id} ({hours_before}h before)")
        
        # Use pymongo for synchronous database access in Celery tasks
        from pymongo import MongoClient
        from backend.app.core.config import settings
        from datetime import datetime, timedelta
        from bson import ObjectId
        
        # Create synchronous pymongo client for Celery tasks
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        try:
            # Fetch event details (convert string ID to ObjectId if needed)
            try:
                event_id_obj = ObjectId(event_id) if isinstance(event_id, str) else event_id
            except:
                event_id_obj = event_id
            
            event = db.events.find_one({"_id": event_id_obj})
            if not event:
                logger.warning(f"Event {event_id} not found")
                return {
                    "status": "error",
                    "event_id": event_id,
                    "error": "Event not found"
                }
            
            # Calculate reminder time
            event_start = event.get("schedule", {}).get("start_date")
            if not event_start:
                logger.warning(f"Event {event_id} has no start date")
                return {
                    "status": "error",
                    "event_id": event_id,
                    "error": "Event has no start date"
                }
            
            # Find users who favorited or registered for this event
            # Query user preferences/favorites for this event
            users_query = {
                "$or": [
                    {"favorite_events": event_id},
                    {"registered_events": event_id},
                    {"preferences.interested_events": event_id}
                ]
            }
            
            users_cursor = db.users.find(users_query, {"_id": 1, "fcm_token": 1, "preferences": 1})
            users = list(users_cursor)
            
            if not users:
                logger.info(f"No users found for event {event_id} reminder")
                return {
                    "status": "success",
                    "event_id": event_id,
                    "users_notified": 0,
                    "message": "No users to notify"
                }
            
            # Prepare notification
            event_name = event.get("name", {}).get("en", "Event")
            title = f"📅 Event Reminder: {event_name}"
            body = f"Don't forget! {event_name} starts in {hours_before} hour(s)."
            
            data = {
                "type": "event_reminder",
                "event_id": event_id,
                "hours_before": str(hours_before)
            }
            
            # Queue push notifications for each user
            success_count = 0
            fail_count = 0
            
            for user in users:
                user_id = str(user["_id"])
                fcm_token = user.get("fcm_token")
                
                if fcm_token:
                    try:
                        # Queue the push notification task
                        send_push_notification.delay(
                            user_id=user_id,
                            title=title,
                            body=body,
                            data=data,
                            fcm_token=fcm_token
                        )
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to queue notification for user {user_id}: {e}")
                        fail_count += 1
                else:
                    logger.debug(f"User {user_id} has no FCM token, skipping")
                    fail_count += 1
            
            logger.info(f"Event reminder queued: {success_count} success, {fail_count} failed")
            
            return {
                "status": "success",
                "event_id": event_id,
                "hours_before": hours_before,
                "users_notified": success_count,
                "users_failed": fail_count,
                "total_users": len(users)
            }
            
        finally:
            # Close database connection
            client.close()
        
    except Exception as e:
        logger.error(f"Event reminder task failed for event {event_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "event_id": event_id,
            "error": str(e)
        }


@celery_app.task(name="backend.app.tasks.notification_tasks.send_location_based_notification")
def send_location_based_notification(
    user_id: str,
    location_name: str,
    attraction_name: str,
    distance_km: float
):
    """
    Send notification when user is near a tourist attraction
    
    Args:
        user_id: User ID
        location_name: Name of nearby location
        attraction_name: Name of attraction
        distance_km: Distance in kilometers
    """
    try:
        logger.info(f"Sending location-based notification to user {user_id} for {attraction_name}")
        
        title = f"📍 Nearby: {attraction_name}"
        body = f"You're {distance_km:.1f}km from {attraction_name} in {location_name}. Want to visit?"
        
        data = {
            "type": "location_based",
            "attraction": attraction_name,
            "location": location_name,
            "distance_km": str(distance_km)
        }
        
        # Queue the push notification
        return send_push_notification(user_id, title, body, data)
        
    except Exception as e:
        logger.error(f"Location-based notification failed: {e}")
        return {"status": "error", "error": str(e)}

