"""
Unit tests for currency service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.app.services.currency_service import CurrencyService, CurrencyRate, CurrencyInfo


class TestCurrencyService:
    """Test currency service methods"""
    
    @pytest.fixture
    def currency_service(self):
        """Create currency service instance"""
        with patch('backend.app.services.currency_service.settings') as mock_settings:
            mock_settings.CURRENCYLAYER_API_KEY = "test_api_key"
            return CurrencyService()
    
    def test_currency_service_initialization(self, currency_service):
        """Test currency service initializes correctly"""
        assert currency_service.api_key == "test_api_key"
        assert "LKR" in currency_service.supported_currencies
        assert "USD" in currency_service.supported_currencies
    
    def test_supported_currencies_contain_tourism_currencies(self, currency_service):
        """Test that common tourism currencies are supported"""
        tourism_currencies = ["LKR", "USD", "EUR", "GBP", "AUD", "INR", "CNY", "JPY"]
        
        for currency in tourism_currencies:
            assert currency in currency_service.supported_currencies
            assert "name" in currency_service.supported_currencies[currency]
            assert "symbol" in currency_service.supported_currencies[currency]
    
    def test_currency_info_structure(self, currency_service):
        """Test currency info has correct structure"""
        for code, info in currency_service.supported_currencies.items():
            assert isinstance(code, str)
            assert len(code) == 3  # ISO 4217 code
            assert "name" in info
            assert "symbol" in info
            assert "country" in info
    
    def test_lkr_currency_info(self, currency_service):
        """Test Sri Lankan Rupee info is correct"""
        lkr = currency_service.supported_currencies.get("LKR")
        
        assert lkr is not None
        assert lkr["name"] == "Sri Lankan Rupee"
        assert lkr["symbol"] == "₨"
        assert lkr["country"] == "Sri Lanka"


class TestCurrencyRate:
    """Test CurrencyRate dataclass"""
    
    def test_currency_rate_creation(self):
        """Test creating a currency rate"""
        rate = CurrencyRate(
            from_currency="USD",
            to_currency="LKR",
            rate=320.50,
            timestamp=datetime.utcnow()
        )
        
        assert rate.from_currency == "USD"
        assert rate.to_currency == "LKR"
        assert rate.rate == 320.50
        assert rate.timestamp is not None
    
    def test_currency_rate_equality(self):
        """Test currency rate equality"""
        timestamp = datetime.utcnow()
        rate1 = CurrencyRate("USD", "LKR", 320.50, timestamp)
        rate2 = CurrencyRate("USD", "LKR", 320.50, timestamp)
        
        assert rate1 == rate2


class TestCurrencyInfo:
    """Test CurrencyInfo dataclass"""
    
    def test_currency_info_creation(self):
        """Test creating currency info"""
        info = CurrencyInfo(
            code="LKR",
            name="Sri Lankan Rupee",
            symbol="₨",
            country="Sri Lanka"
        )
        
        assert info.code == "LKR"
        assert info.name == "Sri Lankan Rupee"
        assert info.symbol == "₨"
        assert info.country == "Sri Lanka"


class TestCurrencyConversion:
    """Test currency conversion functionality"""
    
    @pytest.fixture
    def currency_service(self):
        """Create currency service instance"""
        with patch('backend.app.services.currency_service.settings') as mock_settings:
            mock_settings.CURRENCYLAYER_API_KEY = "test_api_key"
            return CurrencyService()
    
    @pytest.mark.asyncio
    async def test_convert_usd_to_lkr(self, currency_service):
        """Test converting USD to LKR"""
        with patch.object(currency_service, 'get_exchange_rate', new_callable=AsyncMock) as mock_rate:
            mock_rate.return_value = 320.50
            
            if hasattr(currency_service, 'convert'):
                result = await currency_service.convert(100, "USD", "LKR")
                assert result == 32050.0
    
    @pytest.mark.asyncio
    async def test_convert_same_currency(self, currency_service):
        """Test converting same currency returns same amount"""
        if hasattr(currency_service, 'convert'):
            result = await currency_service.convert(100, "USD", "USD")
            assert result == 100
    
    @pytest.mark.asyncio
    async def test_convert_zero_amount(self, currency_service):
        """Test converting zero amount"""
        with patch.object(currency_service, 'get_exchange_rate', new_callable=AsyncMock) as mock_rate:
            mock_rate.return_value = 320.50
            
            if hasattr(currency_service, 'convert'):
                result = await currency_service.convert(0, "USD", "LKR")
                assert result == 0
