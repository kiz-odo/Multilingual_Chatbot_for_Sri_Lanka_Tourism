"""
CurrencyLayer service for currency conversion
"""

import httpx
from typing import Optional, Dict, List, Any
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CurrencyRate:
    """Currency rate data structure"""
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime


@dataclass
class CurrencyInfo:
    """Currency information data structure"""
    code: str
    name: str
    symbol: str
    country: str


class CurrencyService:
    """CurrencyLayer service for currency conversion"""
    
    def __init__(self):
        self.api_key = settings.CURRENCYLAYER_API_KEY
        self.base_url = "http://api.currencylayer.com"
        
        # Common currencies for Sri Lankan tourism
        self.supported_currencies = {
            'LKR': {'name': 'Sri Lankan Rupee', 'symbol': '₨', 'country': 'Sri Lanka'},
            'USD': {'name': 'US Dollar', 'symbol': '$', 'country': 'United States'},
            'EUR': {'name': 'Euro', 'symbol': '€', 'country': 'European Union'},
            'GBP': {'name': 'British Pound', 'symbol': '£', 'country': 'United Kingdom'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'country': 'Australia'},
            'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'country': 'Canada'},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'country': 'Japan'},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'country': 'China'},
            'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'country': 'India'},
            'SGD': {'name': 'Singapore Dollar', 'symbol': 'S$', 'country': 'Singapore'},
            'MYR': {'name': 'Malaysian Ringgit', 'symbol': 'RM', 'country': 'Malaysia'},
            'THB': {'name': 'Thai Baht', 'symbol': '฿', 'country': 'Thailand'},
            'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'country': 'United Arab Emirates'},
            'SAR': {'name': 'Saudi Riyal', 'symbol': '﷼', 'country': 'Saudi Arabia'},
            'QAR': {'name': 'Qatari Riyal', 'symbol': '﷼', 'country': 'Qatar'},
            'KWD': {'name': 'Kuwaiti Dinar', 'symbol': 'د.ك', 'country': 'Kuwait'},
            'BHD': {'name': 'Bahraini Dinar', 'symbol': 'د.ب', 'country': 'Bahrain'},
            'OMR': {'name': 'Omani Rial', 'symbol': '﷼', 'country': 'Oman'},
            'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'country': 'South Africa'},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'country': 'New Zealand'},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'CHF', 'country': 'Switzerland'},
            'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'country': 'Sweden'},
            'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'country': 'Norway'},
            'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'country': 'Denmark'},
            'PLN': {'name': 'Polish Zloty', 'symbol': 'zł', 'country': 'Poland'},
            'CZK': {'name': 'Czech Koruna', 'symbol': 'Kč', 'country': 'Czech Republic'},
            'HUF': {'name': 'Hungarian Forint', 'symbol': 'Ft', 'country': 'Hungary'},
            'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'country': 'Russia'},
            'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'country': 'Brazil'},
            'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'country': 'Mexico'},
            'ARS': {'name': 'Argentine Peso', 'symbol': '$', 'country': 'Argentina'},
            'CLP': {'name': 'Chilean Peso', 'symbol': '$', 'country': 'Chile'},
            'COP': {'name': 'Colombian Peso', 'symbol': '$', 'country': 'Colombia'},
            'PEN': {'name': 'Peruvian Sol', 'symbol': 'S/', 'country': 'Peru'},
            'UYU': {'name': 'Uruguayan Peso', 'symbol': '$U', 'country': 'Uruguay'},
            'VEF': {'name': 'Venezuelan Bolivar', 'symbol': 'Bs', 'country': 'Venezuela'},
            'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'country': 'South Korea'},
            'TWD': {'name': 'Taiwan Dollar', 'symbol': 'NT$', 'country': 'Taiwan'},
            'HKD': {'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'country': 'Hong Kong'},
            'IDR': {'name': 'Indonesian Rupiah', 'symbol': 'Rp', 'country': 'Indonesia'},
            'PHP': {'name': 'Philippine Peso', 'symbol': '₱', 'country': 'Philippines'},
            'VND': {'name': 'Vietnamese Dong', 'symbol': '₫', 'country': 'Vietnam'},
            'BDT': {'name': 'Bangladeshi Taka', 'symbol': '৳', 'country': 'Bangladesh'},
            'PKR': {'name': 'Pakistani Rupee', 'symbol': '₨', 'country': 'Pakistan'},
            'NPR': {'name': 'Nepalese Rupee', 'symbol': '₨', 'country': 'Nepal'},
            'AFN': {'name': 'Afghan Afghani', 'symbol': '؋', 'country': 'Afghanistan'},
            'MMK': {'name': 'Myanmar Kyat', 'symbol': 'K', 'country': 'Myanmar'},
            'KHR': {'name': 'Cambodian Riel', 'symbol': '៛', 'country': 'Cambodia'},
            'LAK': {'name': 'Lao Kip', 'symbol': '₭', 'country': 'Laos'},
            'BND': {'name': 'Brunei Dollar', 'symbol': 'B$', 'country': 'Brunei'},
            'FJD': {'name': 'Fijian Dollar', 'symbol': 'FJ$', 'country': 'Fiji'},
            'PGK': {'name': 'Papua New Guinea Kina', 'symbol': 'K', 'country': 'Papua New Guinea'},
            'SBD': {'name': 'Solomon Islands Dollar', 'symbol': 'SI$', 'country': 'Solomon Islands'},
            'VUV': {'name': 'Vanuatu Vatu', 'symbol': 'Vt', 'country': 'Vanuatu'},
            'WST': {'name': 'Samoan Tala', 'symbol': 'WS$', 'country': 'Samoa'},
            'TOP': {'name': 'Tongan Pa\'anga', 'symbol': 'T$', 'country': 'Tonga'},
            'XPF': {'name': 'CFP Franc', 'symbol': '₣', 'country': 'French Polynesia'},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'country': 'New Zealand'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'country': 'Australia'}
        }
    
    async def get_live_rates(self, base_currency: str = 'USD') -> Optional[Dict[str, float]]:
        """Get live currency exchange rates"""
        
        if not self.api_key:
            logger.warning("CurrencyLayer API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    'access_key': self.api_key,
                    'source': base_currency,
                    'currencies': ','.join(self.supported_currencies.keys())
                }
                
                response = await client.get(
                    f"{self.base_url}/live",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        return data.get('quotes', {})
                    else:
                        logger.error(f"Currency API error: {data.get('error', {}).get('info', 'Unknown error')}")
                        return None
                
                logger.error(f"Currency API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Currency API error: {str(e)}")
            return None
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Get exchange rate between two currencies
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate or None if not available
        """
        if from_currency == to_currency:
            return 1.0
        
        rates = await self.get_live_rates(from_currency)
        
        if not rates:
            return None
        
        rate_key = f"{from_currency}{to_currency}"
        
        if rate_key in rates:
            return rates[rate_key]
        
        # Try reverse conversion
        reverse_rate_key = f"{to_currency}{from_currency}"
        if reverse_rate_key in rates:
            return 1.0 / rates[reverse_rate_key]
        
        return None
    
    async def convert_currency(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str
    ) -> Optional[float]:
        """Convert currency from one to another"""
        
        if from_currency == to_currency:
            return amount
        
        rates = await self.get_live_rates(from_currency)
        
        if not rates:
            return None
        
        # CurrencyLayer returns rates in format: {base_currency}{target_currency}: rate
        rate_key = f"{from_currency}{to_currency}"
        
        if rate_key in rates:
            return amount * rates[rate_key]
        
        # If direct rate not available, try reverse conversion
        reverse_rate_key = f"{to_currency}{from_currency}"
        if reverse_rate_key in rates:
            return amount / rates[reverse_rate_key]
        
        logger.error(f"Currency conversion rate not found: {from_currency} to {to_currency}")
        return None
    
    async def get_currency_info(self, currency_code: str) -> Optional[CurrencyInfo]:
        """Get currency information"""
        
        currency_code = currency_code.upper()
        
        if currency_code not in self.supported_currencies:
            return None
        
        info = self.supported_currencies[currency_code]
        
        return CurrencyInfo(
            code=currency_code,
            name=info['name'],
            symbol=info['symbol'],
            country=info['country']
        )
    
    async def get_sri_lanka_rates(self) -> Optional[Dict[str, float]]:
        """Get exchange rates for Sri Lankan Rupee"""
        
        rates = await self.get_live_rates('LKR')
        
        if not rates:
            return None
        
        # Filter rates to show LKR to other currencies
        sri_lanka_rates = {}
        for key, rate in rates.items():
            if key.startswith('LKR'):
                target_currency = key[3:]  # Remove 'LKR' prefix
                sri_lanka_rates[target_currency] = rate
        
        return sri_lanka_rates
    
    async def get_tourist_currencies(self) -> Dict[str, CurrencyInfo]:
        """Get currencies commonly used by tourists visiting Sri Lanka"""
        
        tourist_currencies = [
            'USD', 'EUR', 'GBP', 'AUD', 'CAD', 'JPY', 'CNY', 'INR', 
            'SGD', 'MYR', 'THB', 'AED', 'SAR', 'QAR', 'KWD', 'BHD', 
            'OMR', 'ZAR', 'NZD', 'CHF', 'KRW', 'TWD', 'HKD', 'IDR', 
            'PHP', 'VND', 'BDT', 'PKR', 'NPR'
        ]
        
        currencies = {}
        for code in tourist_currencies:
            if code in self.supported_currencies:
                info = self.supported_currencies[code]
                currencies[code] = CurrencyInfo(
                    code=code,
                    name=info['name'],
                    symbol=info['symbol'],
                    country=info['country']
                )
        
        return currencies
    
    def format_currency_amount(self, amount: float, currency_code: str) -> str:
        """Format currency amount for display"""
        
        currency_info = self.supported_currencies.get(currency_code.upper())
        
        if not currency_info:
            return f"{amount:.2f} {currency_code}"
        
        symbol = currency_info['symbol']
        
        # Format based on currency
        if currency_code in ['JPY', 'KRW', 'VND', 'IDR', 'PKR', 'BDT', 'NPR']:
            # No decimal places for these currencies
            return f"{symbol}{amount:,.0f}"
        else:
            # Two decimal places for most currencies
            return f"{symbol}{amount:,.2f}"
    
    def format_conversion_result(
        self, 
        amount: float, 
        from_currency: str, 
        to_currency: str, 
        converted_amount: float
    ) -> str:
        """Format currency conversion result for display"""
        
        from_formatted = self.format_currency_amount(amount, from_currency)
        to_formatted = self.format_currency_amount(converted_amount, to_currency)
        
        return f"💱 **Currency Conversion**\n{from_formatted} = {to_formatted}"
    
    def format_exchange_rates(self, rates: Dict[str, float], base_currency: str = 'LKR') -> str:
        """Format exchange rates for display"""
        
        if not rates:
            return "Exchange rates are currently unavailable."
        
        result = f"💱 **Exchange Rates (Base: {base_currency})**\n\n"
        
        # Sort rates by currency code
        sorted_rates = sorted(rates.items())
        
        for currency, rate in sorted_rates:
            currency_info = self.supported_currencies.get(currency)
            if currency_info:
                symbol = currency_info['symbol']
                result += f"**{currency}** ({symbol}): {rate:.4f}\n"
            else:
                result += f"**{currency}**: {rate:.4f}\n"
        
        return result
    
    async def get_currency_recommendations(self, user_currency: str) -> List[str]:
        """Get currency recommendations for tourists"""
        
        recommendations = []
        
        # Check if user's currency is supported
        if user_currency.upper() not in self.supported_currencies:
            recommendations.append(f"⚠️ {user_currency} is not directly supported. Consider exchanging to USD or EUR before traveling.")
        
        # Get current rates
        rates = await self.get_live_rates('LKR')
        
        if rates:
            # Check if LKR is strong or weak against user's currency
            user_rate_key = f"LKR{user_currency.upper()}"
            if user_rate_key in rates:
                rate = rates[user_rate_key]
                if rate > 0.1:  # LKR is relatively strong
                    recommendations.append("💪 Sri Lankan Rupee is currently strong - good time to exchange!")
                elif rate < 0.05:  # LKR is relatively weak
                    recommendations.append("📉 Sri Lankan Rupee is currently weak - consider exchanging gradually.")
        
        # General recommendations
        recommendations.extend([
            "💳 Consider using a travel-friendly credit card with no foreign transaction fees.",
            "🏦 Exchange money at banks or authorized dealers for better rates than hotels.",
            "💰 Keep some cash in LKR for small purchases and tips.",
            "📱 Use mobile payment apps where available for convenience.",
            "🔒 Keep your money secure and don't carry large amounts of cash."
        ])
        
        return recommendations
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currency codes"""
        return list(self.supported_currencies.keys())
    
    def is_currency_supported(self, currency_code: str) -> bool:
        """Check if currency is supported"""
        return currency_code.upper() in self.supported_currencies
    
    async def get_currency_summary_for_tourism(self) -> str:
        """Get a comprehensive currency summary for tourists"""
        
        rates = await self.get_sri_lanka_rates()
        tourist_currencies = await self.get_tourist_currencies()
        
        result = "💱 **Currency Information for Sri Lanka**\n\n"
        
        # Add LKR information
        lkr_info = self.supported_currencies['LKR']
        result += f"🇱🇰 **Local Currency: {lkr_info['name']} ({lkr_info['code']})**\n"
        result += f"Symbol: {lkr_info['symbol']}\n\n"
        
        # Add exchange rates for major tourist currencies
        if rates:
            major_currencies = ['USD', 'EUR', 'GBP', 'AUD', 'CAD', 'JPY', 'INR', 'SGD', 'AED']
            result += "📊 **Current Exchange Rates (1 LKR = ?):**\n"
            
            for currency in major_currencies:
                if currency in rates:
                    currency_info = self.supported_currencies.get(currency, {})
                    symbol = currency_info.get('symbol', '')
                    result += f"• {currency} ({symbol}): {rates[currency]:.4f}\n"
            
            result += "\n"
        
        # Add recommendations
        recommendations = await self.get_currency_recommendations('USD')
        if recommendations:
            result += "💡 **Tourist Recommendations:**\n"
            for rec in recommendations:
                result += f"• {rec}\n"
        
        return result
