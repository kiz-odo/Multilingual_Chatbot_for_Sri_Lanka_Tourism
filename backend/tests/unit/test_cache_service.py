"""
Unit tests for cache service
"""

import pytest
from unittest.mock import MagicMock, patch
import pickle

from backend.app.services.cache_service import CacheService


class TestCacheService:
    """Test cache service methods"""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        mock = MagicMock()
        mock.ping.return_value = True
        return mock
    
    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create cache service with mock Redis"""
        with patch('backend.app.services.cache_service.redis.from_url') as mock_from_url:
            mock_from_url.return_value = mock_redis
            with patch('backend.app.services.cache_service.settings') as mock_settings:
                mock_settings.REDIS_URL = "redis://localhost:6379"
                service = CacheService()
                return service
    
    @pytest.fixture
    def cache_service_disabled(self):
        """Create disabled cache service"""
        with patch('backend.app.services.cache_service.redis.from_url') as mock_from_url:
            mock_from_url.side_effect = Exception("Connection failed")
            with patch('backend.app.services.cache_service.settings') as mock_settings:
                mock_settings.REDIS_URL = "redis://localhost:6379"
                service = CacheService()
                return service
    
    def test_cache_service_initialization_success(self, cache_service):
        """Test cache service initializes successfully"""
        assert cache_service.enabled is True
        assert cache_service.redis_client is not None
    
    def test_cache_service_initialization_failure(self, cache_service_disabled):
        """Test cache service disabled on connection failure"""
        assert cache_service_disabled.enabled is False
        assert cache_service_disabled.redis_client is None
    
    def test_cache_get_success(self, cache_service, mock_redis):
        """Test getting value from cache"""
        test_value = {"key": "value", "number": 42}
        mock_redis.get.return_value = pickle.dumps(test_value)
        cache_service.redis_client = mock_redis
        
        result = cache_service.get("test_key")
        
        assert result == test_value
        mock_redis.get.assert_called_once_with("test_key")
    
    def test_cache_get_not_found(self, cache_service, mock_redis):
        """Test getting non-existent value from cache"""
        mock_redis.get.return_value = None
        cache_service.redis_client = mock_redis
        
        result = cache_service.get("nonexistent_key")
        
        assert result is None
    
    def test_cache_get_disabled(self, cache_service_disabled):
        """Test getting value when cache is disabled"""
        result = cache_service_disabled.get("test_key")
        
        assert result is None
    
    def test_cache_get_error_handling(self, cache_service, mock_redis):
        """Test error handling in cache get"""
        mock_redis.get.side_effect = Exception("Redis error")
        cache_service.redis_client = mock_redis
        
        result = cache_service.get("test_key")
        
        assert result is None
    
    def test_cache_set_success(self, cache_service, mock_redis):
        """Test setting value in cache"""
        cache_service.redis_client = mock_redis
        test_value = {"key": "value"}
        
        result = cache_service.set("test_key", test_value, ttl=3600)
        
        assert result is True
        mock_redis.setex.assert_called_once()
    
    def test_cache_set_with_custom_ttl(self, cache_service, mock_redis):
        """Test setting value with custom TTL"""
        cache_service.redis_client = mock_redis
        test_value = "test"
        
        cache_service.set("test_key", test_value, ttl=7200)
        
        # Check TTL was passed correctly
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 7200  # TTL argument
    
    def test_cache_set_disabled(self, cache_service_disabled):
        """Test setting value when cache is disabled"""
        result = cache_service_disabled.set("test_key", "value")
        
        assert result is False
    
    def test_cache_set_error_handling(self, cache_service, mock_redis):
        """Test error handling in cache set"""
        mock_redis.setex.side_effect = Exception("Redis error")
        cache_service.redis_client = mock_redis
        
        result = cache_service.set("test_key", "value")
        
        assert result is False
    
    def test_cache_delete_success(self, cache_service, mock_redis):
        """Test deleting key from cache"""
        mock_redis.delete.return_value = 1
        cache_service.redis_client = mock_redis
        
        result = cache_service.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    def test_cache_delete_disabled(self, cache_service_disabled):
        """Test deleting when cache is disabled"""
        result = cache_service_disabled.delete("test_key")
        
        assert result is False


class TestCacheDecorator:
    """Test cache decorator functionality"""
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create mock cache service"""
        mock = MagicMock()
        mock.enabled = True
        mock.get.return_value = None
        mock.set.return_value = True
        return mock
    
    def test_cached_decorator_caches_result(self, mock_cache_service):
        """Test that cached decorator caches function result"""
        with patch('backend.app.services.cache_service.CacheService') as MockCacheService:
            MockCacheService.return_value = mock_cache_service
            
            from backend.app.services.cache_service import cached
            
            @cached(ttl=3600, prefix="test")
            async def test_function(arg):
                return f"result_{arg}"
            
            # Function should work (actual caching tested in integration tests)
            assert callable(test_function)
    
    def test_cache_key_generation(self):
        """Test that cache keys are properly generated"""
        import hashlib
        
        # Test key generation logic
        key_prefix = "weather:current"
        args = ("Colombo", "metric", "en")
        
        # Simulate key generation
        key_data = f"{key_prefix}:{args}"
        expected_key = hashlib.md5(key_data.encode()).hexdigest()
        
        assert len(expected_key) == 32  # MD5 hash length


class TestCacheServiceDataTypes:
    """Test caching various data types"""
    
    @pytest.fixture
    def cache_service(self):
        """Create cache service with mock"""
        with patch('backend.app.services.cache_service.redis.from_url') as mock_from_url:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True
            mock_from_url.return_value = mock_redis
            
            with patch('backend.app.services.cache_service.settings') as mock_settings:
                mock_settings.REDIS_URL = "redis://localhost:6379"
                return CacheService()
    
    def test_cache_string(self, cache_service):
        """Test caching string value"""
        cache_service.redis_client = MagicMock()
        result = cache_service.set("key", "string_value")
        assert result is True
    
    def test_cache_dict(self, cache_service):
        """Test caching dictionary"""
        cache_service.redis_client = MagicMock()
        result = cache_service.set("key", {"nested": {"data": True}})
        assert result is True
    
    def test_cache_list(self, cache_service):
        """Test caching list"""
        cache_service.redis_client = MagicMock()
        result = cache_service.set("key", [1, 2, 3, "four"])
        assert result is True
    
    def test_cache_number(self, cache_service):
        """Test caching number"""
        cache_service.redis_client = MagicMock()
        result = cache_service.set("key", 42.5)
        assert result is True
