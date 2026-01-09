"""
Unit tests for ItineraryService
Tests the AI-powered itinerary generation logic
"""

import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, Mock, patch

from backend.app.services.itinerary_service import ItineraryService
from backend.app.models.itinerary import BudgetLevel, TripInterest
from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel


@pytest.fixture
def itinerary_service():
    """Create ItineraryService instance"""
    return ItineraryService()


@pytest.fixture
def mock_attractions():
    """Mock attractions data"""
    from types import SimpleNamespace
    
    attr1 = SimpleNamespace(
        id="attr1",
        name={"en": "Temple of the Tooth"},
        description={"en": "Sacred Buddhist temple"},
        category="temple",
        location=SimpleNamespace(city="Kandy"),
        average_rating=4.8,
        photos=["photo1.jpg"],
        entry_fee=10,
        pricing=[{"type": "adult", "amount": 1500}, {"type": "child", "amount": 750}]
    )
    
    attr2 = SimpleNamespace(
        id="attr2",
        name={"en": "Royal Botanical Gardens"},
        description={"en": "Beautiful gardens"},
        category="nature",
        location=SimpleNamespace(city="Kandy"),
        average_rating=4.5,
        photos=[],
        entry_fee=5,
        pricing=[{"type": "adult", "amount": 500}, {"type": "child", "amount": 250}]
    )
    
    return [attr1, attr2]


@pytest.fixture
def mock_hotels():
    """Mock hotels data"""
    from types import SimpleNamespace
    
    return [
        SimpleNamespace(
            id="hotel1",
            name={"en": "Kandy Hotel"},
            description={"en": "Comfortable stay"},
            star_rating="three_star",
            location=SimpleNamespace(city="Kandy"),
            average_rating=4.2
        )
    ]


@pytest.mark.asyncio
async def test_generate_itinerary(itinerary_service, mock_attractions, mock_hotels):
    """Test basic itinerary generation"""
    with patch.object(itinerary_service, '_fetch_attractions', return_value=mock_attractions):
        with patch.object(itinerary_service, '_fetch_hotels', return_value=mock_hotels):
            with patch.object(itinerary_service, '_fetch_restaurants', return_value=[]):
                with patch.object(itinerary_service, '_fetch_transport', return_value=[]):
                    with patch.object(itinerary_service, '_generate_with_llm', return_value={"text": "Mock itinerary"}):
                        with patch('backend.app.models.itinerary.TripItinerary.insert', new_callable=AsyncMock):
                            itinerary = await itinerary_service.generate_itinerary(
                                user_id="user123",
                                destination="Kandy",
                                duration_days=3,
                                start_date=date.today(),
                                budget_level=BudgetLevel.MID_RANGE,
                                interests=[TripInterest.CULTURE],
                                travelers_count=2
                            )
                            
                            assert itinerary is not None
                            assert itinerary.destination == "Kandy"
                            assert itinerary.duration_days == 3
                            assert len(itinerary.days) == 3


@pytest.mark.asyncio
async def test_fetch_attractions_filters_by_destination(itinerary_service):
    """Test that attractions are filtered by destination"""
    with patch('backend.app.models.attraction.Attraction.find') as mock_find:
        mock_query = Mock()
        mock_query.find = Mock(return_value=mock_query)
        mock_query.sort = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.to_list = AsyncMock(return_value=[])
        mock_find.return_value = mock_query
        
        await itinerary_service._fetch_attractions(
            "Kandy",
            [TripInterest.CULTURE],
            10
        )
        
        mock_find.assert_called_once()


def test_budget_limits_defined(itinerary_service):
    """Test that budget limits are properly defined"""
    assert BudgetLevel.BUDGET in itinerary_service.budget_limits
    assert BudgetLevel.MID_RANGE in itinerary_service.budget_limits
    assert BudgetLevel.LUXURY in itinerary_service.budget_limits
    
    # Check structure
    budget = itinerary_service.budget_limits[BudgetLevel.MID_RANGE]
    assert "max" in budget
    assert "accommodation" in budget
    assert "food" in budget
    assert "activities" in budget


def test_booking_partners_defined(itinerary_service):
    """Test that booking partners are configured"""
    assert "booking.com" in itinerary_service.booking_partners
    assert "agoda.com" in itinerary_service.booking_partners
    
    # Check commission rates
    assert itinerary_service.booking_partners["booking.com"]["commission"] > 0


def test_add_booking_links(itinerary_service):
    """Test that booking links are added to activities"""
    from backend.app.models.itinerary import DayItinerary, ActivityItem
    
    activity = ActivityItem(
        time_slot="09:00 AM - 12:00 PM",
        activity_type="hotel",
        title="Test Hotel",
        description="Test",
        location="Kandy",
        estimated_cost=100,
        duration_minutes=0
    )
    
    day = DayItinerary(
        day_number=1,
        date=date.today(),
        location="Kandy",
        title="Day 1",
        activities=[activity]
    )
    
    result = itinerary_service._add_booking_links([day])
    
    assert result[0].activities[0].booking_url is not None
    assert result[0].activities[0].booking_partner == "booking.com"
    assert result[0].activities[0].commission_rate == 0.25


@pytest.mark.asyncio
async def test_track_booking(itinerary_service):
    """Test booking tracking"""
    from backend.app.models.itinerary import ActivityItem
    
    activity = ActivityItem(
        time_slot="09:00 AM",
        activity_type="hotel",
        title="Test Hotel",
        description="Test",
        location="Kandy",
        estimated_cost=200,
        duration_minutes=0,
        booking_url="https://booking.com",
        booking_partner="booking.com",
        commission_rate=0.25
    )
    
    with patch('backend.app.models.itinerary.BookingTracking.insert', new_callable=AsyncMock):
        with patch('backend.app.models.itinerary.TripItinerary.get', new_callable=AsyncMock) as mock_get:
            mock_itinerary = Mock()
            mock_itinerary.id = "itin123"
            mock_itinerary.bookings_made = 0
            mock_itinerary.total_revenue = 0
            mock_itinerary.save = AsyncMock()
            mock_get.return_value = mock_itinerary
            
            booking = await itinerary_service.track_booking(
                itinerary_id="itin123",
                user_id="user123",
                activity=activity,
                booking_reference="BOOK-123",
                booking_amount=200
            )
            
            assert booking.commission_amount == 50  # 200 * 0.25
            assert booking.booking_partner == "booking.com"

