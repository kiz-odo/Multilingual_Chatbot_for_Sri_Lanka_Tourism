"""
GDPR Data Export Service
Provides user data export functionality for GDPR compliance
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import zipfile
import io

from backend.app.models.user import User
from backend.app.models.conversation import Conversation
from backend.app.models.feedback import Feedback
from backend.app.models.itinerary import TripItinerary

logger = logging.getLogger(__name__)


class GDPRExportService:
    """Service for GDPR-compliant data export"""
    
    def __init__(self):
        """Initialize GDPR export service"""
        self.export_version = "1.0.0"
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data in GDPR-compliant format
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dictionary containing all user data
        """
        logger.info(f"Starting GDPR data export for user: {user_id}")
        
        export_data = {
            "export_info": {
                "version": self.export_version,
                "exported_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "format": "JSON"
            },
            "personal_data": {},
            "conversations": [],
            "feedback": [],
            "itineraries": [],
            "activity_logs": []
        }
        
        # Get user personal data
        user = await User.get(user_id)
        if user:
            export_data["personal_data"] = await self._export_personal_data(user)
        
        # Get conversation history
        export_data["conversations"] = await self._export_conversations(user_id)
        
        # Get feedback submissions
        export_data["feedback"] = await self._export_feedback(user_id)
        
        # Get itineraries
        export_data["itineraries"] = await self._export_itineraries(user_id)
        
        logger.info(f"GDPR data export completed for user: {user_id}")
        
        return export_data
    
    async def _export_personal_data(self, user: User) -> Dict[str, Any]:
        """Export personal data fields"""
        return {
            "account_info": {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
                "is_active": user.is_active,
                "is_verified": user.is_verified if hasattr(user, 'is_verified') else None,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
            },
            "preferences": {
                "preferred_language": user.preferences.preferred_language if user.preferences else "en",
                "notification_settings": user.preferences.notification_settings if hasattr(user.preferences, 'notification_settings') else {},
                "privacy_settings": user.preferences.privacy_settings if hasattr(user.preferences, 'privacy_settings') else {}
            } if user.preferences else {},
            "statistics": {
                "total_conversations": user.stats.total_conversations if user.stats else 0,
                "total_queries": user.stats.total_queries if user.stats else 0,
                "favorite_attractions": user.stats.favorite_attractions if user.stats else [],
                "visited_places": user.stats.visited_places if user.stats else [],
                "last_activity": user.stats.last_activity.isoformat() if user.stats and user.stats.last_activity else None
            } if user.stats else {},
            "oauth_connections": self._get_oauth_info(user) if hasattr(user, 'oauth_providers') else []
        }
    
    def _get_oauth_info(self, user: User) -> List[Dict[str, Any]]:
        """Get OAuth provider connections (without tokens)"""
        oauth_info = []
        if hasattr(user, 'oauth_providers') and user.oauth_providers:
            for provider in user.oauth_providers:
                oauth_info.append({
                    "provider": provider.provider if hasattr(provider, 'provider') else str(provider),
                    "connected_at": provider.connected_at.isoformat() if hasattr(provider, 'connected_at') and provider.connected_at else None
                })
        return oauth_info
    
    async def _export_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Export all conversation history"""
        conversations = await Conversation.find(
            Conversation.user_id == user_id
        ).to_list()
        
        exported = []
        for conv in conversations:
            conv_data = {
                "session_id": conv.session_id,
                "started_at": conv.created_at.isoformat() if conv.created_at else None,
                "primary_language": conv.primary_language,
                "messages": []
            }
            
            if conv.messages:
                for msg in conv.messages:
                    conv_data["messages"].append({
                        "sender": msg.sender.value if hasattr(msg.sender, 'value') else str(msg.sender),
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                        "language": msg.detected_language if hasattr(msg, 'detected_language') else None
                    })
            
            exported.append(conv_data)
        
        return exported
    
    async def _export_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """Export all feedback submissions"""
        try:
            feedbacks = await Feedback.find(
                Feedback.user_id == user_id
            ).to_list()
            
            return [
                {
                    "type": fb.feedback_type if hasattr(fb, 'feedback_type') else None,
                    "content": fb.content if hasattr(fb, 'content') else None,
                    "rating": fb.rating if hasattr(fb, 'rating') else None,
                    "submitted_at": fb.created_at.isoformat() if fb.created_at else None,
                    "related_entity": fb.related_entity if hasattr(fb, 'related_entity') else None
                }
                for fb in feedbacks
            ]
        except Exception as e:
            logger.warning(f"Error exporting feedback: {e}")
            return []
    
    async def _export_itineraries(self, user_id: str) -> List[Dict[str, Any]]:
        """Export all itineraries"""
        try:
            itineraries = await TripItinerary.find(
                TripItinerary.user_id == user_id
            ).to_list()
            
            return [
                {
                    "title": it.title if hasattr(it, 'title') else None,
                    "start_date": it.start_date.isoformat() if hasattr(it, 'start_date') and it.start_date else None,
                    "end_date": it.end_date.isoformat() if hasattr(it, 'end_date') and it.end_date else None,
                    "destinations": it.destinations if hasattr(it, 'destinations') else [],
                    "created_at": it.created_at.isoformat() if it.created_at else None,
                    "status": it.status if hasattr(it, 'status') else None
                }
                for it in itineraries
            ]
        except Exception as e:
            logger.warning(f"Error exporting itineraries: {e}")
            return []
    
    async def create_export_archive(self, user_id: str) -> bytes:
        """
        Create a ZIP archive containing all user data
        
        Args:
            user_id: The user's ID
            
        Returns:
            Bytes of the ZIP file
        """
        export_data = await self.export_user_data(user_id)
        
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Main data file
            zf.writestr(
                'user_data.json',
                json.dumps(export_data, indent=2, ensure_ascii=False)
            )
            
            # Separate files for readability
            zf.writestr(
                'personal_info.json',
                json.dumps(export_data['personal_data'], indent=2, ensure_ascii=False)
            )
            
            zf.writestr(
                'conversations.json',
                json.dumps(export_data['conversations'], indent=2, ensure_ascii=False)
            )
            
            zf.writestr(
                'feedback.json',
                json.dumps(export_data['feedback'], indent=2, ensure_ascii=False)
            )
            
            zf.writestr(
                'itineraries.json',
                json.dumps(export_data['itineraries'], indent=2, ensure_ascii=False)
            )
            
            # Add README
            readme_content = """# GDPR Data Export

This archive contains all your personal data stored by Sri Lanka Tourism Chatbot.

## Contents

- `user_data.json` - Complete export in single file
- `personal_info.json` - Your account information and preferences
- `conversations.json` - Your chat history with the bot
- `feedback.json` - Feedback you've submitted
- `itineraries.json` - Trip itineraries you've created

## Data Retention

You can request deletion of your data at any time by contacting support
or using the account deletion feature in the app.

## Questions?

Contact: privacy@srilanka-tourism.com

Export Date: {date}
Export Version: {version}
""".format(
                date=datetime.utcnow().isoformat(),
                version=self.export_version
            )
            
            zf.writestr('README.md', readme_content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    async def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all user data (Right to Erasure)
        
        Args:
            user_id: The user's ID
            
        Returns:
            Summary of deleted data
        """
        logger.info(f"Starting GDPR data deletion for user: {user_id}")
        
        deletion_summary = {
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted_items": {}
        }
        
        try:
            # Delete conversations
            conv_result = await Conversation.find(
                Conversation.user_id == user_id
            ).delete()
            deletion_summary["deleted_items"]["conversations"] = conv_result.deleted_count if conv_result else 0
            
            # Delete feedback
            fb_result = await Feedback.find(
                Feedback.user_id == user_id
            ).delete()
            deletion_summary["deleted_items"]["feedback"] = fb_result.deleted_count if fb_result else 0
            
            # Delete itineraries
            it_result = await TripItinerary.find(
                TripItinerary.user_id == user_id
            ).delete()
            deletion_summary["deleted_items"]["itineraries"] = it_result.deleted_count if it_result else 0
            
            # Anonymize user record instead of deleting (for audit trail)
            user = await User.get(user_id)
            if user:
                user.email = f"deleted_{user_id}@anonymized.local"
                user.username = f"deleted_user_{user_id[:8]}"
                user.full_name = "Deleted User"
                user.phone_number = None
                user.is_active = False
                user.preferences = None
                await user.save()
                deletion_summary["deleted_items"]["user_anonymized"] = True
            
            logger.info(f"GDPR data deletion completed for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error during GDPR deletion: {e}")
            deletion_summary["error"] = str(e)
        
        return deletion_summary


# Singleton instance
gdpr_export_service = GDPRExportService()
