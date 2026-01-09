"""
Celery Application Configuration
Background task processing for async operations
"""

from celery import Celery
from celery.schedules import crontab
import logging

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "tourism_bot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "backend.app.tasks.email_tasks",
        "backend.app.tasks.data_tasks",
        "backend.app.tasks.notification_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Result settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Broker settings
    broker_connection_retry_on_startup=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-old-sessions': {
            'task': 'backend.app.tasks.data_tasks.cleanup_old_sessions',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'generate-daily-analytics': {
            'task': 'backend.app.tasks.data_tasks.generate_daily_analytics',
            'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
        },
        'update-trending-items': {
            'task': 'backend.app.tasks.data_tasks.update_trending_items',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
    }
)

# Optional: Configure different queues for different priorities
celery_app.conf.task_routes = {
    'backend.app.tasks.email_tasks.*': {'queue': 'emails'},
    'backend.app.tasks.notification_tasks.*': {'queue': 'notifications'},
    'backend.app.tasks.data_tasks.*': {'queue': 'data_processing'},
}

logger.info("Celery app configured")

