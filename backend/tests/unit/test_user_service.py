"""
Unit tests for user service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.app.services.user_service import UserService
from backend.app.models.user import UserCreate, UserUpdate, UserRole


class TestUserService:
    """Test user service methods"""
    
    @pytest.fixture
    def user_service(self):
        """Create user service instance"""
        return UserService()
    
    @pytest.fixture
    def sample_user_create(self):
        """Sample user creation data"""
        return UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
            full_name="Test User",
            phone_number="+94771234567",
            preferred_language="en"
        )
    
    @pytest.fixture
    def sample_user_update(self):
        """Sample user update data"""
        return UserUpdate(
            full_name="Updated User",
            phone_number="+94779876543"
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, sample_user_create):
        """Test successful user creation"""
        with patch('backend.app.models.user.User.save', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = None
            
            user = await user_service.create_user(
                sample_user_create,
                "hashed_password_here"
            )
            
            assert user is not None
            assert user.email == sample_user_create.email
            assert user.username == sample_user_create.username
            assert user.full_name == sample_user_create.full_name
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_service):
        """Test getting user by email"""
        with patch('backend.app.models.user.User.find_one', new_callable=AsyncMock) as mock_find:
            mock_user = MagicMock()
            mock_user.email = "test@example.com"
            mock_find.return_value = mock_user
            
            user = await user_service.get_user_by_email("test@example.com")
            
            assert user is not None
            assert user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_service):
        """Test getting non-existent user by email"""
        with patch('backend.app.models.user.User.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            
            user = await user_service.get_user_by_email("nonexistent@example.com")
            
            assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, user_service):
        """Test getting user by username"""
        with patch('backend.app.models.user.User.find_one', new_callable=AsyncMock) as mock_find:
            mock_user = MagicMock()
            mock_user.username = "testuser"
            mock_find.return_value = mock_user
            
            user = await user_service.get_user_by_username("testuser")
            
            assert user is not None
            assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, sample_user_update):
        """Test successful user update"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_user = MagicMock()
            mock_user.save = AsyncMock()
            mock_get.return_value = mock_user
            
            updated_user = await user_service.update_user("user123", sample_user_update)
            
            assert updated_user is not None
            mock_user.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_service, sample_user_update):
        """Test updating non-existent user"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            updated_user = await user_service.update_user("nonexistent", sample_user_update)
            
            assert updated_user is None
    
    @pytest.mark.asyncio
    async def test_delete_user_soft_delete(self, user_service):
        """Test soft delete user"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_user = MagicMock()
            mock_user.is_active = True
            mock_user.save = AsyncMock()
            mock_get.return_value = mock_user
            
            result = await user_service.delete_user("user123")
            
            assert result is True
            assert mock_user.is_active is False
            mock_user.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_service):
        """Test deleting non-existent user"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            result = await user_service.delete_user("nonexistent")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_update_user_stats_conversations(self, user_service):
        """Test incrementing conversation stats"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_user = MagicMock()
            mock_user.stats.total_conversations = 5
            mock_user.save = AsyncMock()
            mock_get.return_value = mock_user
            
            result = await user_service.update_user_stats(
                "user123",
                increment_conversations=True
            )
            
            assert result is not None
            assert mock_user.stats.total_conversations == 6
    
    @pytest.mark.asyncio
    async def test_update_user_stats_queries(self, user_service):
        """Test incrementing query stats"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_user = MagicMock()
            mock_user.stats.total_queries = 10
            mock_user.save = AsyncMock()
            mock_get.return_value = mock_user
            
            result = await user_service.update_user_stats(
                "user123",
                increment_queries=True
            )
            
            assert result is not None
            assert mock_user.stats.total_queries == 11
    
    @pytest.mark.asyncio
    async def test_add_favorite_attraction(self, user_service):
        """Test adding favorite attraction"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_user = MagicMock()
            mock_user.stats.favorite_attractions = []
            mock_user.save = AsyncMock()
            mock_get.return_value = mock_user
            
            result = await user_service.add_favorite_attraction("user123", "attraction456")
            
            assert result is not None
            assert "attraction456" in mock_user.stats.favorite_attractions
    
    @pytest.mark.asyncio
    async def test_add_favorite_attraction_duplicate(self, user_service):
        """Test adding duplicate favorite attraction"""
        with patch.object(user_service, 'get_user_by_id', new_callable=AsyncMock) as mock_get:
            mock_user = MagicMock()
            mock_user.stats.favorite_attractions = ["attraction456"]
            mock_user.save = AsyncMock()
            mock_get.return_value = mock_user
            
            result = await user_service.add_favorite_attraction("user123", "attraction456")
            
            assert result is not None
            # Should not add duplicate
            assert mock_user.stats.favorite_attractions.count("attraction456") == 1
