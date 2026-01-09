"""
GraphQL Resolvers
Business logic for GraphQL queries and mutations
"""

import logging
from typing import List, Optional
from datetime import datetime

from backend.app.models.attraction import Attraction
from backend.app.models.hotel import Hotel
from backend.app.models.restaurant import Restaurant
from backend.app.models.itinerary import TripItinerary
from backend.app.models.user import User
from backend.app.services.itinerary_service import ItineraryService
from backend.app.services.auth_service import AuthService
from backend.app.services.oauth_service import get_oauth_service
from backend.app.graphql.types import (
    AttractionType, HotelType, RestaurantType,
    ItineraryType, UserType, ConversationType,
    MultilingualText, LocationType, DayItineraryType,
    ActivityItemType, AuthPayload, MessageInput, ItineraryInput
)

logger = logging.getLogger(__name__)


class AttractionResolver:
    """Resolvers for Attraction queries"""
    
    @staticmethod
    async def get_attractions(
        city: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[AttractionType]:
        """Get attractions with filters"""
        query = Attraction.find(Attraction.is_active == True)
        
        if city:
            query = query.find(Attraction.location.city == city)
        
        if category:
            query = query.find(Attraction.category == category)
        
        attractions = await query.sort(-Attraction.popularity_score).limit(limit).to_list()
        
        return [AttractionResolver._to_graphql_type(attr) for attr in attractions]
    
    @staticmethod
    async def get_attraction_by_id(attraction_id: str) -> Optional[AttractionType]:
        """Get single attraction"""
        attraction = await Attraction.get(attraction_id)
        
        if not attraction:
            return None
        
        return AttractionResolver._to_graphql_type(attraction)
    
    @staticmethod
    async def search_attractions(query: str, limit: int = 10) -> List[AttractionType]:
        """Search attractions by text"""
        # Simple search - in production, use text index
        attractions = await Attraction.find(
            Attraction.is_active == True
        ).limit(limit).to_list()
        
        # Filter by query (basic implementation)
        results = [
            attr for attr in attractions
            if query.lower() in attr.name.get("en", "").lower()
            or query.lower() in attr.description.get("en", "").lower()
        ]
        
        return [AttractionResolver._to_graphql_type(attr) for attr in results[:limit]]
    
    @staticmethod
    def _to_graphql_type(attraction: Attraction) -> AttractionType:
        """Convert Attraction model to GraphQL type"""
        return AttractionType(
            id=str(attraction.id),
            name=MultilingualText(**attraction.name),
            description=MultilingualText(**attraction.description),
            short_description=MultilingualText(**attraction.short_description),
            category=attraction.category.value,
            location=LocationType(
                city=attraction.location.city,
                province=attraction.location.province,
                address=attraction.location.address,
                latitude=attraction.location.coordinates[1] if len(attraction.location.coordinates) > 1 else None,
                longitude=attraction.location.coordinates[0] if len(attraction.location.coordinates) > 0 else None
            ),
            average_rating=attraction.average_rating,
            total_reviews=attraction.total_reviews,
            photos=attraction.photos,
            tags=attraction.tags,
            is_free=attraction.is_free,
            popularity_score=attraction.popularity_score,
            is_active=attraction.is_active
        )


class HotelResolver:
    """Resolvers for Hotel queries"""
    
    @staticmethod
    async def get_hotels(
        city: Optional[str] = None,
        star_rating: Optional[str] = None,
        limit: int = 10
    ) -> List[HotelType]:
        """Get hotels with filters"""
        query = Hotel.find(Hotel.is_active == True)
        
        if city:
            query = query.find(Hotel.location.city == city)
        
        if star_rating:
            query = query.find(Hotel.star_rating == star_rating)
        
        hotels = await query.sort(-Hotel.average_rating).limit(limit).to_list()
        
        return [HotelResolver._to_graphql_type(hotel) for hotel in hotels]
    
    @staticmethod
    async def get_hotel_by_id(hotel_id: str) -> Optional[HotelType]:
        """Get single hotel"""
        hotel = await Hotel.get(hotel_id)
        
        if not hotel:
            return None
        
        return HotelResolver._to_graphql_type(hotel)
    
    @staticmethod
    def _to_graphql_type(hotel: Hotel) -> HotelType:
        """Convert Hotel model to GraphQL type"""
        return HotelType(
            id=str(hotel.id),
            name=MultilingualText(**hotel.name),
            description=MultilingualText(**hotel.description),
            short_description=MultilingualText(**hotel.short_description),
            category=hotel.category.value,
            star_rating=hotel.star_rating.value,
            location=LocationType(
                city=hotel.location.city,
                province=hotel.location.province,
                address=hotel.location.address,
                latitude=hotel.location.coordinates[1] if len(hotel.location.coordinates) > 1 else None,
                longitude=hotel.location.coordinates[0] if len(hotel.location.coordinates) > 0 else None
            ),
            average_rating=hotel.average_rating,
            total_reviews=hotel.total_reviews,
            photos=hotel.photos,
            amenities=[a.value for a in hotel.amenities],
            is_active=hotel.is_active
        )


class RestaurantResolver:
    """Resolvers for Restaurant queries"""
    
    @staticmethod
    async def get_restaurants(
        city: Optional[str] = None,
        cuisine: Optional[str] = None,
        limit: int = 10
    ) -> List[RestaurantType]:
        """Get restaurants with filters"""
        query = Restaurant.find(Restaurant.is_active == True)
        
        if city:
            query = query.find(Restaurant.location.city == city)
        
        restaurants = await query.sort(-Restaurant.average_rating).limit(limit).to_list()
        
        return [RestaurantResolver._to_graphql_type(rest) for rest in restaurants]
    
    @staticmethod
    async def get_restaurant_by_id(restaurant_id: str) -> Optional[RestaurantType]:
        """Get single restaurant"""
        restaurant = await Restaurant.get(restaurant_id)
        
        if not restaurant:
            return None
        
        return RestaurantResolver._to_graphql_type(restaurant)
    
    @staticmethod
    def _to_graphql_type(restaurant: Restaurant) -> RestaurantType:
        """Convert Restaurant model to GraphQL type"""
        return RestaurantType(
            id=str(restaurant.id),
            name=MultilingualText(**restaurant.name),
            description=MultilingualText(**restaurant.description),
            short_description=MultilingualText(**restaurant.short_description),
            cuisine_types=[c.value for c in restaurant.cuisine_types],
            restaurant_type=restaurant.restaurant_type.value,
            price_range=restaurant.price_range.value,
            location=LocationType(
                city=restaurant.location.city,
                province=restaurant.location.province,
                address=restaurant.location.address,
                latitude=restaurant.location.coordinates[1] if len(restaurant.location.coordinates) > 1 else None,
                longitude=restaurant.location.coordinates[0] if len(restaurant.location.coordinates) > 0 else None
            ),
            average_rating=restaurant.average_rating,
            total_reviews=restaurant.total_reviews,
            photos=restaurant.photos,
            dietary_options=[d.value for d in restaurant.dietary_options],
            is_active=restaurant.is_active
        )


class ItineraryResolver:
    """Resolvers for Itinerary queries and mutations"""
    
    @staticmethod
    async def get_user_itineraries(user_id: str) -> List[ItineraryType]:
        """Get user's itineraries"""
        itinerary_service = ItineraryService()
        itineraries = await itinerary_service.get_user_itineraries(user_id)
        
        return [ItineraryResolver._to_graphql_type(itin) for itin in itineraries]
    
    @staticmethod
    async def get_itinerary_by_id(itinerary_id: str) -> Optional[ItineraryType]:
        """Get itinerary by ID"""
        itinerary_service = ItineraryService()
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary:
            return None
        
        return ItineraryResolver._to_graphql_type(itinerary)
    
    @staticmethod
    async def generate_itinerary(user_id: str, input: ItineraryInput) -> ItineraryType:
        """Generate new itinerary"""
        from backend.app.models.itinerary import BudgetLevel, TripInterest
        
        itinerary_service = ItineraryService()
        
        # Convert GraphQL enums to Python enums
        budget_level = BudgetLevel(input.budget_level.value)
        interests = [TripInterest(i.value) for i in input.interests]
        
        itinerary = await itinerary_service.generate_itinerary(
            user_id=user_id,
            destination=input.destination,
            duration_days=input.duration_days,
            start_date=input.start_date,
            budget_level=budget_level,
            interests=interests,
            travelers_count=input.travelers_count,
            custom_requirements=input.custom_requirements
        )
        
        return ItineraryResolver._to_graphql_type(itinerary)
    
    @staticmethod
    async def delete_itinerary(itinerary_id: str, user_id: str) -> bool:
        """Delete itinerary"""
        itinerary_service = ItineraryService()
        itinerary = await itinerary_service.get_itinerary_by_id(itinerary_id)
        
        if not itinerary or str(itinerary.user_id) != user_id:
            return False
        
        itinerary.is_active = False
        await itinerary.save()
        
        return True
    
    @staticmethod
    def _to_graphql_type(itinerary: TripItinerary) -> ItineraryType:
        """Convert TripItinerary to GraphQL type"""
        return ItineraryType(
            id=str(itinerary.id),
            title=itinerary.title,
            destination=itinerary.destination,
            duration_days=itinerary.duration_days,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            budget_level=itinerary.budget_level.value,
            interests=[i.value for i in itinerary.interests],
            travelers_count=itinerary.travelers_count,
            days=[
                DayItineraryType(
                    day_number=day.day_number,
                    date=day.date,
                    location=day.location,
                    title=day.title,
                    activities=[
                        ActivityItemType(
                            time_slot=act.time_slot,
                            activity_type=act.activity_type,
                            title=act.title,
                            description=act.description,
                            location=act.location,
                            estimated_cost=act.estimated_cost,
                            duration_minutes=act.duration_minutes,
                            rating=act.rating,
                            booking_url=act.booking_url,
                            booking_partner=act.booking_partner,
                            tips=act.tips
                        )
                        for act in day.activities
                    ],
                    total_cost=day.total_cost,
                    highlights=day.highlights
                )
                for day in itinerary.days
            ],
            total_estimated_cost=itinerary.total_estimated_cost,
            currency=itinerary.currency,
            share_url=f"https://your-domain.com/itinerary/share/{itinerary.share_token}" if itinerary.share_token else None,
            created_at=itinerary.created_at,
            bookings_made=itinerary.bookings_made,
            total_revenue=itinerary.total_revenue
        )


class UserResolver:
    """Resolvers for User queries"""
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserType]:
        """Get user by ID"""
        user = await User.get(user_id)
        
        if not user:
            return None
        
        return UserResolver._to_graphql_type(user)
    
    @staticmethod
    async def update_profile(
        user_id: str,
        full_name: Optional[str] = None,
        bio: Optional[str] = None
    ) -> UserType:
        """Update user profile"""
        user = await User.get(user_id)
        
        if not user:
            raise Exception("User not found")
        
        if full_name:
            user.full_name = full_name
        
        if bio:
            user.bio = bio
        
        user.updated_at = datetime.utcnow()
        await user.save()
        
        return UserResolver._to_graphql_type(user)
    
    @staticmethod
    def _to_graphql_type(user: User) -> UserType:
        """Convert User model to GraphQL type"""
        return UserType(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            profile_picture=user.profile_picture,
            role=user.role.value,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            oauth_provider=user.oauth_provider,
            created_at=user.created_at,
            last_login=user.last_login
        )


class ChatResolver:
    """Resolvers for Chat mutations"""
    
    @staticmethod
    async def send_message(user_id: str, message_input: MessageInput) -> ConversationType:
        """Send chat message"""
        from backend.app.services.hybrid_chat_service import HybridChatService
        from backend.app.models.conversation import Conversation, Message
        
        # Get or create conversation
        conversation = await Conversation.find_one(
            Conversation.user_id == user_id,
            Conversation.is_active == True
        )
        
        if not conversation:
            conversation = Conversation(
                user_id=user_id,
                session_id=f"graphql_{user_id}_{datetime.utcnow().timestamp()}",
                language=message_input.language or "en",
                messages=[],
                is_active=True
            )
            await conversation.insert()
        
        # Process message through hybrid chat service
        chat_service = HybridChatService()
        response = await chat_service.process_message(
            message=message_input.message,
            user_id=user_id,
            session_id=conversation.session_id,
            language=message_input.language or conversation.language
        )
        
        # Add user message to conversation
        user_message = Message(
            sender="user",
            message=message_input.message,
            timestamp=datetime.utcnow(),
            language=message_input.language or conversation.language
        )
        
        # Add bot response to conversation
        bot_message = Message(
            sender="bot",
            message=response.get("response", ""),
            timestamp=datetime.utcnow(),
            language=message_input.language or conversation.language,
            metadata=response.get("metadata", {})
        )
        
        conversation.messages.append(user_message)
        conversation.messages.append(bot_message)
        conversation.updated_at = datetime.utcnow()
        
        await conversation.save()
        
        return conversation


class AuthResolver:
    """Resolvers for Authentication"""
    
    @staticmethod
    async def login(email: str, password: str) -> AuthPayload:
        """Login with email and password"""
        user = await AuthService.authenticate_user(email, password)
        
        if not user:
            raise Exception("Invalid credentials")
        
        access_token = AuthService.create_access_token(
            data={"user_id": str(user.id), "email": user.email}
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"user_id": str(user.id)}
        )
        
        return AuthPayload(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResolver._to_graphql_type(user)
        )
    
    @staticmethod
    async def register(
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> AuthPayload:
        """Register new user"""
        from backend.app.services.user_service import UserService
        
        user_service = UserService()
        user = await user_service.create_user(
            email=email,
            username=username,
            password=password,
            full_name=full_name
        )
        
        access_token = AuthService.create_access_token(
            data={"user_id": str(user.id), "email": user.email}
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"user_id": str(user.id)}
        )
        
        return AuthPayload(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResolver._to_graphql_type(user)
        )
    
    @staticmethod
    async def oauth_login(provider: str, access_token: str) -> AuthPayload:
        """OAuth login"""
        oauth_service = get_oauth_service()
        result = await oauth_service.authenticate_with_oauth(provider, access_token)
        
        if not result:
            raise Exception("OAuth authentication failed")
        
        # Get user from database
        from backend.app.models.user import User as UserModel
        user = await UserModel.find_one(UserModel.email == result["user"]["email"])
        
        return AuthPayload(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            user=UserResolver._to_graphql_type(user)
        )

