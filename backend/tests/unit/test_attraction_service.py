"""
Unit tests for attraction service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from types import SimpleNamespace

from backend.app.services.attraction_service import AttractionService
from backend.app.models.attraction import AttractionCategory


class TestAttractionService:
    """Test attraction service methods"""
    
    @pytest.fixture
    def attraction_service(self):
        """Create attraction service instance"""
        return AttractionService()
    
    @pytest.fixture
    def sample_attraction(self):
        """Sample attraction data"""
        attr = SimpleNamespace(
            id="attr123",
            name={"en": "Sigiriya Rock Fortress", "si": "සීගිරිය"},
            category=AttractionCategory.HISTORICAL,
            location=SimpleNamespace(city="Sigiriya", province="Central"),
            is_active=True,
            is_featured=True,
            popularity_score=9.5
        )
        return attr
    
    @pytest.mark.asyncio
    async def test_get_attractions_no_filters(self, attraction_service, sample_attraction):
        """Test getting attractions without filters"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.skip = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.get_attractions()
            
            assert len(attractions) == 1
            assert attractions[0].name["en"] == "Sigiriya Rock Fortress"
    
    @pytest.mark.asyncio
    async def test_get_attractions_with_category(self, attraction_service, sample_attraction):
        """Test getting attractions with category filter"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.find = MagicMock(return_value=mock_query)
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.skip = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.get_attractions(
                category=AttractionCategory.HISTORICAL
            )
            
            assert len(attractions) == 1
    
    @pytest.mark.asyncio
    async def test_get_attractions_with_city(self, attraction_service, sample_attraction):
        """Test getting attractions with city filter"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.find = MagicMock(return_value=mock_query)
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.skip = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.get_attractions(city="Sigiriya")
            
            assert len(attractions) == 1
    
    @pytest.mark.asyncio
    async def test_get_attractions_featured_only(self, attraction_service, sample_attraction):
        """Test getting only featured attractions"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.find = MagicMock(return_value=mock_query)
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.skip = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.get_attractions(featured_only=True)
            
            assert len(attractions) == 1
            assert attractions[0].is_featured is True
    
    @pytest.mark.asyncio
    async def test_get_attractions_pagination(self, attraction_service):
        """Test attractions pagination"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.skip = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[])
            mock_find.return_value = mock_query
            
            await attraction_service.get_attractions(skip=10, limit=5)
            
            mock_query.skip.assert_called_with(10)
            mock_query.limit.assert_called_with(5)
    
    @pytest.mark.asyncio
    async def test_search_attractions(self, attraction_service, sample_attraction):
        """Test searching attractions"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.find = MagicMock(return_value=mock_query)
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.search_attractions(query="Sigiriya")
            
            assert len(attractions) == 1
    
    @pytest.mark.asyncio
    async def test_get_attraction_by_id_success(self, attraction_service, sample_attraction):
        """Test getting attraction by ID"""
        with patch('backend.app.models.attraction.Attraction.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_attraction
            
            attraction = await attraction_service.get_attraction_by_id("attr123")
            
            assert attraction is not None
            assert attraction.id == "attr123"
    
    @pytest.mark.asyncio
    async def test_get_attraction_by_id_not_found(self, attraction_service):
        """Test getting non-existent attraction by ID"""
        with patch('backend.app.models.attraction.Attraction.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Not found")
            
            attraction = await attraction_service.get_attraction_by_id("nonexistent")
            
            assert attraction is None
    
    @pytest.mark.asyncio
    async def test_get_attraction_by_slug(self, attraction_service, sample_attraction):
        """Test getting attraction by slug"""
        with patch('backend.app.models.attraction.Attraction.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = sample_attraction
            
            attraction = await attraction_service.get_attraction_by_slug("sigiriya-rock-fortress")
            
            assert attraction is not None
    
    @pytest.mark.asyncio
    async def test_get_featured_attractions(self, attraction_service, sample_attraction):
        """Test getting featured attractions"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.get_featured_attractions(limit=6)
            
            assert len(attractions) == 1
    
    @pytest.mark.asyncio
    async def test_get_popular_attractions(self, attraction_service, sample_attraction):
        """Test getting popular attractions"""
        with patch('backend.app.models.attraction.Attraction.find') as mock_find:
            mock_query = AsyncMock()
            mock_query.sort = MagicMock(return_value=mock_query)
            mock_query.limit = MagicMock(return_value=mock_query)
            mock_query.to_list = AsyncMock(return_value=[sample_attraction])
            mock_find.return_value = mock_query
            
            attractions = await attraction_service.get_popular_attractions(limit=10)
            
            assert len(attractions) == 1
            assert attractions[0].popularity_score == 9.5
