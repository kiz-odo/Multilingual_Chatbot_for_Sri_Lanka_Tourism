"""
Unit tests for GDPR export service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.app.services.gdpr_export_service import GDPRExportService


class TestGDPRExportService:
    """Test GDPR export service methods"""
    
    @pytest.fixture
    def gdpr_service(self):
        """Create GDPR export service instance"""
        return GDPRExportService()
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        user = MagicMock()
        user.id = "user123"
        user.username = "testuser"
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.phone_number = "+94771234567"
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        user.is_active = True
        user.is_verified = True
        user.role = MagicMock(value="user")
        user.preferences = MagicMock(
            preferred_language="en",
            notification_settings={},
            privacy_settings={}
        )
        user.stats = MagicMock(
            total_conversations=5,
            total_queries=25,
            favorite_attractions=["attr1", "attr2"],
            visited_places=["place1"],
            last_activity=datetime.utcnow()
        )
        return user
    
    @pytest.fixture
    def mock_conversation(self):
        """Create mock conversation"""
        conv = MagicMock()
        conv.session_id = "session123"
        conv.created_at = datetime.utcnow()
        conv.primary_language = "en"
        conv.messages = [
            MagicMock(
                sender=MagicMock(value="user"),
                content="Hello",
                timestamp=datetime.utcnow(),
                detected_language="en"
            ),
            MagicMock(
                sender=MagicMock(value="bot"),
                content="Hi there!",
                timestamp=datetime.utcnow(),
                detected_language="en"
            )
        ]
        return conv
    
    def test_gdpr_service_initialization(self, gdpr_service):
        """Test GDPR service initializes correctly"""
        assert gdpr_service.export_version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_export_user_data_structure(self, gdpr_service, mock_user):
        """Test exported data has correct structure"""
        with patch('backend.app.models.user.User.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_user
            
            with patch('backend.app.models.conversation.Conversation.find') as mock_conv_find:
                mock_conv_find.return_value.to_list = AsyncMock(return_value=[])
                
                with patch('backend.app.models.feedback.Feedback.find') as mock_fb_find:
                    mock_fb_find.return_value.to_list = AsyncMock(return_value=[])
                    
                    with patch('backend.app.models.itinerary.TripItinerary.find') as mock_it_find:
                        mock_it_find.return_value.to_list = AsyncMock(return_value=[])
                        
                        export_data = await gdpr_service.export_user_data("user123")
        
        # Check structure
        assert "export_info" in export_data
        assert "personal_data" in export_data
        assert "conversations" in export_data
        assert "feedback" in export_data
        assert "itineraries" in export_data
        
        # Check export info
        assert export_data["export_info"]["user_id"] == "user123"
        assert export_data["export_info"]["version"] == "1.0.0"
        assert export_data["export_info"]["format"] == "JSON"
    
    @pytest.mark.asyncio
    async def test_export_personal_data(self, gdpr_service, mock_user):
        """Test personal data export"""
        personal_data = await gdpr_service._export_personal_data(mock_user)
        
        assert "account_info" in personal_data
        assert "preferences" in personal_data
        assert "statistics" in personal_data
        
        # Check account info
        assert personal_data["account_info"]["username"] == "testuser"
        assert personal_data["account_info"]["email"] == "test@example.com"
        assert personal_data["account_info"]["full_name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_export_conversations(self, gdpr_service, mock_conversation):
        """Test conversation export"""
        with patch('backend.app.models.conversation.Conversation.find') as mock_find:
            mock_query = MagicMock()
            mock_query.to_list = AsyncMock(return_value=[mock_conversation])
            mock_find.return_value = mock_query
            
            conversations = await gdpr_service._export_conversations("user123")
        
        assert len(conversations) == 1
        assert conversations[0]["session_id"] == "session123"
        assert len(conversations[0]["messages"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_export_archive(self, gdpr_service, mock_user):
        """Test ZIP archive creation"""
        with patch.object(gdpr_service, 'export_user_data', new_callable=AsyncMock) as mock_export:
            mock_export.return_value = {
                "export_info": {"user_id": "user123", "version": "1.0.0"},
                "personal_data": {"account_info": {"email": "test@example.com"}},
                "conversations": [],
                "feedback": [],
                "itineraries": []
            }
            
            zip_data = await gdpr_service.create_export_archive("user123")
        
        # Verify it's a valid ZIP file (starts with PK)
        assert zip_data[:2] == b'PK'
        assert len(zip_data) > 0
    
    @pytest.mark.asyncio
    async def test_delete_user_data(self, gdpr_service):
        """Test user data deletion"""
        with patch('backend.app.models.conversation.Conversation.find') as mock_conv:
            mock_result = MagicMock()
            mock_result.deleted_count = 5
            mock_conv.return_value.delete = AsyncMock(return_value=mock_result)
            
            with patch('backend.app.models.feedback.Feedback.find') as mock_fb:
                mock_fb.return_value.delete = AsyncMock(return_value=mock_result)
                
                with patch('backend.app.models.itinerary.TripItinerary.find') as mock_it:
                    mock_it.return_value.delete = AsyncMock(return_value=mock_result)
                    
                    with patch('backend.app.models.user.User.get', new_callable=AsyncMock) as mock_user_get:
                        mock_user = MagicMock()
                        mock_user.save = AsyncMock()
                        mock_user_get.return_value = mock_user
                        
                        deletion_summary = await gdpr_service.delete_user_data("user123")
        
        assert deletion_summary["user_id"] == "user123"
        assert "deleted_items" in deletion_summary
        assert deletion_summary["deleted_items"]["conversations"] == 5


class TestGDPRExportDataProtection:
    """Test GDPR data protection requirements"""
    
    @pytest.fixture
    def gdpr_service(self):
        return GDPRExportService()
    
    def test_no_password_in_export(self, gdpr_service):
        """Ensure passwords are never exported"""
        mock_user = MagicMock()
        mock_user.hashed_password = "secret_hash"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.phone_number = None
        mock_user.created_at = None
        mock_user.updated_at = None
        mock_user.is_active = True
        mock_user.role = MagicMock(value="user")
        mock_user.preferences = None
        mock_user.stats = None
        
        import asyncio
        personal_data = asyncio.get_event_loop().run_until_complete(
            gdpr_service._export_personal_data(mock_user)
        )
        
        # Flatten to string and check no password
        data_str = str(personal_data)
        assert "secret_hash" not in data_str
        assert "password" not in data_str.lower() or "hashed" not in data_str.lower()
    
    def test_no_oauth_tokens_in_export(self, gdpr_service):
        """Ensure OAuth tokens are not exported"""
        mock_user = MagicMock()
        mock_user.oauth_providers = [
            MagicMock(
                provider="google",
                access_token="secret_token",
                refresh_token="secret_refresh",
                connected_at=datetime.utcnow()
            )
        ]
        
        oauth_info = gdpr_service._get_oauth_info(mock_user)
        
        for provider in oauth_info:
            assert "secret_token" not in str(provider)
            assert "secret_refresh" not in str(provider)
            assert "access_token" not in provider
            assert "refresh_token" not in provider
