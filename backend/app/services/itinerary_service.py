"""
AI-Powered Itinerary Generation Service
Uses Mistral-7B LLM to create personalized travel itineraries with booking integration
"""

import logging
import secrets
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from backend.app.models.itinerary import (
    TripItinerary, DayItinerary, ActivityItem,
    BudgetLevel, TripInterest, BookingTracking, BookingStatus
)
from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.transport import Transport
from backend.app.services.llm_service import get_llm_service
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class ItineraryService:
    """Service for AI-powered itinerary generation"""
    
    def __init__(self):
        self.llm_service = get_llm_service()
        
        # Budget constraints (USD per day)
        self.budget_limits = {
            BudgetLevel.BUDGET: {"min": 0, "max": 30, "accommodation": 15, "food": 10, "activities": 5},
            BudgetLevel.MID_RANGE: {"min": 30, "max": 100, "accommodation": 50, "food": 30, "activities": 20},
            BudgetLevel.LUXURY: {"min": 100, "max": 500, "accommodation": 200, "food": 100, "activities": 200}
        }
        
        # Booking partners and commission rates
        self.booking_partners = {
            "booking.com": {"commission": 0.25, "types": ["hotel", "guesthouse"]},
            "agoda.com": {"commission": 0.20, "types": ["hotel"]},
            "uber.com": {"commission": 0.15, "types": ["transport"]},
            "pickme.lk": {"commission": 0.12, "types": ["transport"]},
            "getyourguide.com": {"commission": 0.20, "types": ["activity", "tour"]},
        }
    
    async def generate_itinerary(
        self,
        user_id: str,
        destination: str,
        duration_days: int,
        start_date: date,
        budget_level: BudgetLevel,
        interests: List[TripInterest],
        travelers_count: int = 1,
        custom_requirements: Optional[str] = None
    ) -> TripItinerary:
        """
        Generate AI-powered itinerary using LLM and database
        
        This is the core monetization feature!
        """
        logger.info(f"Generating itinerary for {user_id}: {destination}, {duration_days} days, {budget_level}")
        
        try:
            # 1. Fetch relevant resources from database
            attractions = await self._fetch_attractions(destination, interests, duration_days * 3)
            hotels = await self._fetch_hotels(destination, budget_level, duration_days)
            restaurants = await self._fetch_restaurants(destination, budget_level, duration_days * 3)
            transport = await self._fetch_transport(destination)
            
            # 2. Build context for LLM
            context = self._build_llm_context(
                destination, duration_days, budget_level, interests,
                attractions, hotels, restaurants, transport,
                travelers_count, custom_requirements
            )
            
            # 3. Generate itinerary with LLM
            llm_response = await self._generate_with_llm(context)
            
            # 4. Structure the itinerary
            days = await self._structure_itinerary(
                llm_response, start_date, duration_days,
                attractions, hotels, restaurants, transport,
                budget_level
            )
            
            # 5. Add booking links and calculate commissions
            days = self._add_booking_links(days)
            
            # 6. Create itinerary document
            itinerary = TripItinerary(
                user_id=user_id,
                title=f"{duration_days}-Day {destination} Adventure",
                destination=destination,
                duration_days=duration_days,
                start_date=start_date,
                end_date=start_date + timedelta(days=duration_days - 1),
                budget_level=budget_level,
                interests=interests,
                travelers_count=travelers_count,
                days=days,
                generated_by_ai=True,
                generation_prompt=custom_requirements,
                share_token=secrets.token_urlsafe(16)
            )
            
            # Calculate totals
            itinerary.calculate_totals()
            
            # Save to database
            await itinerary.insert()
            
            logger.info(f"✅ Generated itinerary {itinerary.id} - Potential commission: ${itinerary.total_potential_commission:.2f}")
            
            return itinerary
            
        except Exception as e:
            logger.error(f"Failed to generate itinerary: {e}", exc_info=True)
            raise
    
    async def _fetch_attractions(
        self,
        destination: str,
        interests: List[TripInterest],
        limit: int = 10
    ) -> List[Attraction]:
        """Fetch relevant attractions"""
        # Map interests to attraction categories
        category_mapping = {
            TripInterest.CULTURE: ["cultural", "temple"],
            TripInterest.HISTORY: ["historical", "museum"],
            TripInterest.ADVENTURE: ["adventure", "hiking"],
            TripInterest.BEACH: ["beach", "coastal"],
            TripInterest.WILDLIFE: ["wildlife", "nature"],
        }
        
        categories = []
        for interest in interests:
            categories.extend(category_mapping.get(interest, []))
        
        query = Attraction.find(
            Attraction.location.city == destination,
            Attraction.is_active == True
        )
        
        if categories:
            query = query.find({"$or": [{"category": cat} for cat in categories]})
        
        attractions = await query.sort(-Attraction.popularity_score).limit(limit).to_list()
        
        logger.info(f"Found {len(attractions)} attractions in {destination}")
        return attractions
    
    async def _fetch_hotels(
        self,
        destination: str,
        budget_level: BudgetLevel,
        nights: int
    ) -> List[Hotel]:
        """Fetch hotels within budget"""
        budget = self.budget_limits[budget_level]
        max_price = budget["accommodation"]
        
        hotels = await Hotel.find(
            Hotel.location.city == destination,
            Hotel.is_active == True
        ).sort(-Hotel.average_rating).limit(10).to_list()
        
        # Filter by price (if price info available)
        suitable_hotels = [h for h in hotels if self._is_hotel_in_budget(h, max_price)]
        
        logger.info(f"Found {len(suitable_hotels)} hotels in budget for {destination}")
        return suitable_hotels
    
    async def _fetch_restaurants(
        self,
        destination: str,
        budget_level: BudgetLevel,
        limit: int = 10
    ) -> List[Restaurant]:
        """Fetch restaurants within budget"""
        price_range_map = {
            BudgetLevel.BUDGET: "budget",
            BudgetLevel.MID_RANGE: "moderate",
            BudgetLevel.LUXURY: "expensive"
        }
        
        restaurants = await Restaurant.find(
            Restaurant.location.city == destination,
            Restaurant.is_active == True,
            Restaurant.price_range == price_range_map.get(budget_level, "moderate")
        ).sort(-Restaurant.average_rating).limit(limit).to_list()
        
        logger.info(f"Found {len(restaurants)} restaurants in {destination}")
        return restaurants
    
    async def _fetch_transport(self, destination: str) -> List[Transport]:
        """Fetch transport options"""
        transport = await Transport.find(
            Transport.is_active == True
        ).limit(5).to_list()
        
        return transport
    
    def _is_hotel_in_budget(self, hotel: Hotel, max_price: float) -> bool:
        """Check if hotel is within budget"""
        # This would check actual pricing if available
        # For now, use star rating as proxy
        if hotel.star_rating in ["one_star", "two_star"]:
            return max_price >= 15
        elif hotel.star_rating in ["three_star"]:
            return max_price >= 30
        elif hotel.star_rating in ["four_star"]:
            return max_price >= 80
        else:
            return max_price >= 150
    
    def _build_llm_context(
        self,
        destination: str,
        duration_days: int,
        budget_level: BudgetLevel,
        interests: List[TripInterest],
        attractions: List[Attraction],
        hotels: List[Hotel],
        restaurants: List[Restaurant],
        transport: List[Transport],
        travelers_count: int,
        custom_requirements: Optional[str]
    ) -> str:
        """Build context for LLM"""
        
        # Format attractions
        attractions_text = "\n".join([
            f"- {a.name.en if hasattr(a.name, 'en') else 'Unknown'}: {a.description.en[:100] if hasattr(a.description, 'en') else ''}... "
            f"(Category: {a.category.value if hasattr(a.category, 'value') else a.category}, Rating: {a.average_rating}/5)"
            for a in attractions[:15]
        ])
        
        # Format hotels
        hotels_text = "\n".join([
            f"- {h.name.en if hasattr(h.name, 'en') else 'Unknown'}: {h.star_rating.value if hasattr(h.star_rating, 'value') else h.star_rating} star "
            f"(Rating: {h.average_rating}/5)"
            for h in hotels[:5]
        ])
        
        # Format restaurants
        restaurants_text = "\n".join([
            f"- {r.name.en if hasattr(r.name, 'en') else 'Unknown'}: {', '.join([c.value for c in r.cuisine_types])} "
            f"(Price: {r.price_range.value}, Rating: {r.average_rating}/5)"
            for r in restaurants[:8]
        ])
        
        budget = self.budget_limits[budget_level]
        interests_text = ", ".join([i.value for i in interests])
        
        prompt = f"""You are an expert travel planner for Sri Lanka. Create a detailed {duration_days}-day itinerary for {destination}.

TRAVELER PROFILE:
- Number of travelers: {travelers_count}
- Budget: {budget_level.value} (${budget['max']}/day per person)
- Interests: {interests_text}
- Custom requirements: {custom_requirements or 'None'}

AVAILABLE ATTRACTIONS:
{attractions_text}

AVAILABLE HOTELS:
{hotels_text}

AVAILABLE RESTAURANTS:
{restaurants_text}

INSTRUCTIONS:
1. Create a day-by-day itinerary with specific times (e.g., 09:00 AM - 11:00 AM)
2. Include morning, afternoon, and evening activities
3. Suggest breakfast, lunch, and dinner spots
4. Stay within the daily budget of ${budget['max']}
5. Optimize travel time between locations
6. Include variety and balance
7. Add helpful tips for each activity

Format each day as:
Day X - [Title]:
- [Time]: [Activity] at [Location] - [Brief description]

Be specific, practical, and engaging. Create a story-like flow."""
        
        return prompt
    
    async def _generate_with_llm(self, context: str) -> Dict[str, Any]:
        """Generate itinerary using Mistral-7B LLM"""
        try:
            # Ensure LLM is initialized
            await self.llm_service.ensure_initialized()
            
            if self.llm_service.enabled:
                response = await self.llm_service.get_response(
                    message=context,
                    language="en",
                    context=None,
                    conversation_history=[]
                )
                return response
            else:
                # Fallback to template-based generation
                logger.warning("LLM not available, using template-based generation")
                return {"text": "Template-based itinerary generation"}
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return {"text": "Error generating itinerary"}
    
    async def _structure_itinerary(
        self,
        llm_response: Dict[str, Any],
        start_date: date,
        duration_days: int,
        attractions: List[Attraction],
        hotels: List[Hotel],
        restaurants: List[Restaurant],
        transport: List[Transport],
        budget_level: BudgetLevel
    ) -> List[DayItinerary]:
        """Structure LLM response into day itineraries"""
        
        days = []
        llm_text = llm_response.get("text", "")
        
        # Parse LLM response and map to actual resources
        for day_num in range(1, duration_days + 1):
            day_date = start_date + timedelta(days=day_num - 1)
            
            # Create sample activities (in production, parse LLM response better)
            activities = []
            
            # Morning activity (attraction)
            if attractions:
                attr = attractions[(day_num - 1) % len(attractions)]
                # Get entry fee from pricing or default
                entry_fee = 0
                if attr.pricing and len(attr.pricing) > 0:
                    entry_fee = attr.pricing[0].price if hasattr(attr.pricing[0], 'price') else 0
                elif not attr.is_free:
                    entry_fee = 10  # Default fee
                
                # Extract image URLs safely
                photos = []
                if hasattr(attr, 'images') and attr.images:
                    for img in attr.images[:2]:
                        if isinstance(img, dict):
                            # Handle dict format from database
                            url = img.get('url') or img.get('_url', '')
                            if url:
                                photos.append(str(url))
                        elif hasattr(img, 'url'):
                            photos.append(str(img.url))
                
                activities.append(ActivityItem(
                    time_slot="09:00 AM - 12:00 PM",
                    activity_type="attraction",
                    title=attr.name.en if hasattr(attr.name, 'en') else "Attraction",
                    description=attr.description.en[:200] if hasattr(attr.description, 'en') else "",
                    location=attr.location.city,
                    estimated_cost=entry_fee,
                    duration_minutes=180,
                    resource_id=str(attr.id),
                    rating=attr.average_rating,
                    photos=photos
                ))
            
            # Lunch
            if restaurants:
                rest = restaurants[(day_num - 1) % len(restaurants)]
                activities.append(ActivityItem(
                    time_slot="12:30 PM - 01:30 PM",
                    activity_type="meal",
                    title=f"Lunch at {rest.name.en if hasattr(rest.name, 'en') else 'Restaurant'}",
                    description=f"Enjoy {', '.join([c.value for c in rest.cuisine_types])} cuisine",
                    location=rest.location.city,
                    estimated_cost=15 if budget_level == BudgetLevel.BUDGET else 30,
                    duration_minutes=60,
                    resource_id=str(rest.id),
                    rating=rest.average_rating
                ))
            
            # Afternoon activity
            if len(attractions) > day_num:
                attr = attractions[day_num % len(attractions)]
                # Get entry fee from pricing or default
                entry_fee = 0
                if attr.pricing and len(attr.pricing) > 0:
                    entry_fee = attr.pricing[0].price if hasattr(attr.pricing[0], 'price') else 0
                elif not attr.is_free:
                    entry_fee = 10  # Default fee
                
                activities.append(ActivityItem(
                    time_slot="02:00 PM - 05:00 PM",
                    activity_type="attraction",
                    title=attr.name.en if hasattr(attr.name, 'en') else "Attraction",
                    description=attr.description.en[:200] if hasattr(attr.description, 'en') else "",
                    location=attr.location.city,
                    estimated_cost=entry_fee,
                    duration_minutes=180,
                    resource_id=str(attr.id),
                    rating=attr.average_rating
                ))
            
            # Dinner
            if len(restaurants) > day_num:
                rest = restaurants[day_num % len(restaurants)]
                activities.append(ActivityItem(
                    time_slot="07:00 PM - 08:30 PM",
                    activity_type="meal",
                    title=f"Dinner at {rest.name.en if hasattr(rest.name, 'en') else 'Restaurant'}",
                    description=rest.description.en[:150] if hasattr(rest.description, 'en') else "",
                    location=rest.location.city,
                    estimated_cost=20 if budget_level == BudgetLevel.BUDGET else 40,
                    duration_minutes=90,
                    resource_id=str(rest.id),
                    rating=rest.average_rating
                ))
            
            # Hotel (for first and last day)
            if day_num == 1 and hotels:
                hotel = hotels[0]
                activities.append(ActivityItem(
                    time_slot="Check-in: 02:00 PM",
                    activity_type="hotel",
                    title=f"Stay at {hotel.name.en if hasattr(hotel.name, 'en') else 'Hotel'}",
                    description=hotel.description.en[:150] if hasattr(hotel.description, 'en') else '',
                    location=hotel.location.city,
                    estimated_cost=self.budget_limits[budget_level]["accommodation"],
                    duration_minutes=0,
                    resource_id=str(hotel.id),
                    rating=hotel.average_rating
                ))
            
            day = DayItinerary(
                day_number=day_num,
                date=day_date,
                location=attractions[0].location.city if attractions else "Unknown",
                title=f"Day {day_num} - Exploring",
                activities=activities,
                highlights=[a.title for a in activities[:2]]
            )
            
            days.append(day)
        
        return days
    
    def _add_booking_links(self, days: List[DayItinerary]) -> List[DayItinerary]:
        """Add booking links and commission tracking"""
        
        for day in days:
            for activity in day.activities:
                if activity.activity_type == "hotel":
                    # Add hotel booking link
                    activity.booking_url = f"https://www.booking.com/hotel/lk/search.html"
                    activity.booking_partner = "booking.com"
                    activity.commission_rate = 0.25
                    
                elif activity.activity_type == "transport":
                    # Add transport booking
                    activity.booking_url = "https://pickme.lk"
                    activity.booking_partner = "pickme.lk"
                    activity.commission_rate = 0.12
                    
                elif activity.activity_type == "attraction":
                    # Add tour booking if available
                    activity.booking_url = "https://www.getyourguide.com"
                    activity.booking_partner = "getyourguide.com"
                    activity.commission_rate = 0.20
        
        return days
    
    async def track_booking(
        self,
        itinerary_id: str,
        user_id: str,
        activity: ActivityItem,
        booking_reference: str,
        booking_amount: float
    ) -> BookingTracking:
        """Track a booking made through itinerary"""
        
        commission_amount = booking_amount * (activity.commission_rate or 0)
        
        booking = BookingTracking(
            itinerary_id=itinerary_id,
            user_id=user_id,
            activity_item=activity,
            booking_partner=activity.booking_partner or "unknown",
            booking_reference=booking_reference,
            booking_status=BookingStatus.CONFIRMED,
            booking_amount=booking_amount,
            commission_amount=commission_amount,
            commission_rate=activity.commission_rate or 0
        )
        
        await booking.insert()
        
        # Update itinerary stats
        itinerary = await TripItinerary.get(itinerary_id)
        if itinerary:
            itinerary.bookings_made += 1
            itinerary.total_revenue += commission_amount
            await itinerary.save()
        
        logger.info(f"💰 Booking tracked: ${booking_amount} - Commission: ${commission_amount}")
        
        return booking
    
    async def get_user_itineraries(self, user_id: str) -> List[TripItinerary]:
        """Get user's itineraries"""
        return await TripItinerary.find(
            TripItinerary.user_id == user_id,
            TripItinerary.is_active == True
        ).sort(-TripItinerary.created_at).to_list()
    
    async def get_itinerary_by_id(self, itinerary_id: str) -> Optional[TripItinerary]:
        """Get itinerary by ID"""
        return await TripItinerary.get(itinerary_id)
    
    async def get_shared_itinerary(self, share_token: str) -> Optional[TripItinerary]:
        """Get itinerary by share token"""
        itinerary = await TripItinerary.find_one(TripItinerary.share_token == share_token)
        if itinerary:
            itinerary.views += 1
            itinerary.last_viewed_at = datetime.utcnow()
            await itinerary.save()
        return itinerary

