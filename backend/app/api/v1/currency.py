"""
CurrencyLayer API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, Path
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from backend.app.models.user import User
from backend.app.core.auth import get_optional_user
from backend.app.services.currency_service import CurrencyService, CurrencyInfo

router = APIRouter()


class CurrencyConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str


class CurrencyConversionResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    rate: float
    timestamp: datetime


class CurrencyInfoResponse(BaseModel):
    code: str
    name: str
    symbol: str
    country: str


class ExchangeRatesResponse(BaseModel):
    base_currency: str
    rates: Dict[str, float]
    timestamp: datetime


@router.post("/convert", response_model=CurrencyConversionResponse)
async def convert_currency(
    conversion_request: CurrencyConversionRequest,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Convert currency from one to another"""
    try:
        currency_service = CurrencyService()
        
        # Validate currencies
        if not currency_service.is_currency_supported(conversion_request.from_currency):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency {conversion_request.from_currency} is not supported"
            )
        
        if not currency_service.is_currency_supported(conversion_request.to_currency):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency {conversion_request.to_currency} is not supported"
            )
        
        # Get conversion rate
        rates = await currency_service.get_live_rates(conversion_request.from_currency)
        
        if not rates:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Currency conversion service is currently unavailable"
            )
        
        # Calculate conversion
        rate_key = f"{conversion_request.from_currency}{conversion_request.to_currency}"
        rate = rates.get(rate_key)
        
        if not rate:
            # Try reverse conversion
            reverse_rate_key = f"{conversion_request.to_currency}{conversion_request.from_currency}"
            reverse_rate = rates.get(reverse_rate_key)
            if reverse_rate:
                rate = 1 / reverse_rate
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Conversion rate not available for {conversion_request.from_currency} to {conversion_request.to_currency}"
                )
        
        converted_amount = conversion_request.amount * rate
        
        return CurrencyConversionResponse(
            amount=conversion_request.amount,
            from_currency=conversion_request.from_currency,
            to_currency=conversion_request.to_currency,
            converted_amount=converted_amount,
            rate=rate,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting currency: {str(e)}"
        )


@router.get("/rates", response_model=ExchangeRatesResponse)
async def get_exchange_rates(
    base_currency: str = Query("USD", description="Base currency code"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get live exchange rates"""
    try:
        currency_service = CurrencyService()
        
        if not currency_service.is_currency_supported(base_currency):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency {base_currency} is not supported"
            )
        
        rates = await currency_service.get_live_rates(base_currency)
        
        if not rates:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Exchange rates are currently unavailable"
            )
        
        return ExchangeRatesResponse(
            base_currency=base_currency,
            rates=rates,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting exchange rates: {str(e)}"
        )


@router.get("/sri-lanka-rates", response_model=ExchangeRatesResponse)
async def get_sri_lanka_rates(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get exchange rates for Sri Lankan Rupee"""
    try:
        currency_service = CurrencyService()
        rates = await currency_service.get_sri_lanka_rates()
        
        if not rates:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sri Lanka exchange rates are currently unavailable"
            )
        
        return ExchangeRatesResponse(
            base_currency="LKR",
            rates=rates,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Sri Lanka rates: {str(e)}"
        )


@router.get("/currencies", response_model=List[CurrencyInfoResponse])
async def get_supported_currencies(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get list of supported currencies"""
    try:
        currency_service = CurrencyService()
        currencies = await currency_service.get_tourist_currencies()
        
        return [
            CurrencyInfoResponse(
                code=currency.code,
                name=currency.name,
                symbol=currency.symbol,
                country=currency.country
            )
            for currency in currencies.values()
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting supported currencies: {str(e)}"
        )


@router.get("/currency/{currency_code}", response_model=CurrencyInfoResponse)
async def get_currency_info(
    currency_code: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get information about a specific currency"""
    try:
        currency_service = CurrencyService()
        currency_info = await currency_service.get_currency_info(currency_code)
        
        if not currency_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency {currency_code} not found"
            )
        
        return CurrencyInfoResponse(
            code=currency_info.code,
            name=currency_info.name,
            symbol=currency_info.symbol,
            country=currency_info.country
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting currency info: {str(e)}"
        )


@router.get("/recommendations")
async def get_currency_recommendations(
    user_currency: str = Query("USD", description="User's currency code"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get currency recommendations for tourists"""
    try:
        currency_service = CurrencyService()
        recommendations = await currency_service.get_currency_recommendations(user_currency)
        
        return {"recommendations": recommendations}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting currency recommendations: {str(e)}"
        )


@router.get("/summary")
async def get_currency_summary(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Get comprehensive currency summary for tourists"""
    try:
        currency_service = CurrencyService()
        summary = await currency_service.get_currency_summary_for_tourism()
        
        return {"summary": summary}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting currency summary: {str(e)}"
        )


@router.get("/format/{amount}")
async def format_currency_amount(
    amount: float = Path(..., description="Amount to format"),
    currency_code: str = Query("USD", description="Currency code"),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Format currency amount for display"""
    try:
        currency_service = CurrencyService()
        formatted_amount = currency_service.format_currency_amount(amount, currency_code)
        
        return {"formatted_amount": formatted_amount}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error formatting currency amount: {str(e)}"
        )


@router.get("/check/{currency_code}")
async def check_currency_support(
    currency_code: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Check if a currency is supported"""
    try:
        currency_service = CurrencyService()
        is_supported = currency_service.is_currency_supported(currency_code)
        
        return {"currency_code": currency_code, "is_supported": is_supported}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking currency support: {str(e)}"
        )
