"""
GraphQL Schema for Sri Lanka Tourism Chatbot
Complete GraphQL API with queries and mutations
"""

from typing import List, Optional
from datetime import datetime, date
import strawberry
from strawberry.fastapi import GraphQLRouter

from backend.app.graphql.types import (
    AttractionType,
    HotelType,
    RestaurantType,
    EventType,
    ItineraryType,
    UserType,
    ConversationType,
    AuthPayload,
    MessageInput,
    ItineraryInput
)
from backend.app.graphql.resolvers import (
    AttractionResolver,
    HotelResolver,
    RestaurantResolver,
    ItineraryResolver,
    UserResolver,
    ChatResolver,
    AuthResolver
)


@strawberry.type
class Query:
    """GraphQL Queries"""
    
    # ==========================================
    # ATTRACTIONS
    # ==========================================
    
    @strawberry.field
    async def attractions(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[AttractionType]:
        """Get list of attractions with optional filters"""
        return await AttractionResolver.get_attractions(city, category, limit)
    
    @strawberry.field
    async def attraction(self, id: str) -> Optional[AttractionType]:
        """Get single attraction by ID"""
        return await AttractionResolver.get_attraction_by_id(id)
    
    @strawberry.field
    async def search_attractions(
        self,
        query: str,
        limit: int = 10
    ) -> List[AttractionType]:
        """Search attractions by text"""
        return await AttractionResolver.search_attractions(query, limit)
    
    # ==========================================
    # HOTELS
    # ==========================================
    
    @strawberry.field
    async def hotels(
        self,
        city: Optional[str] = None,
        star_rating: Optional[str] = None,
        limit: int = 10
    ) -> List[HotelType]:
        """Get list of hotels with optional filters"""
        return await HotelResolver.get_hotels(city, star_rating, limit)
    
    @strawberry.field
    async def hotel(self, id: str) -> Optional[HotelType]:
        """Get single hotel by ID"""
        return await HotelResolver.get_hotel_by_id(id)
    
    # ==========================================
    # RESTAURANTS
    # ==========================================
    
    @strawberry.field
    async def restaurants(
        self,
        city: Optional[str] = None,
        cuisine: Optional[str] = None,
        limit: int = 10
    ) -> List[RestaurantType]:
        """Get list of restaurants"""
        return await RestaurantResolver.get_restaurants(city, cuisine, limit)
    
    @strawberry.field
    async def restaurant(self, id: str) -> Optional[RestaurantType]:
        """Get single restaurant by ID"""
        return await RestaurantResolver.get_restaurant_by_id(id)
    
    # ==========================================
    # EVENTS
    # ==========================================
    
    @strawberry.field
    async def events(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[EventType]:
        """Get upcoming events"""
        from backend.app.models.event import Event
        
        query = {}
        if city:
            query["city"] = city
        if category:
            query["category"] = category
        
        events = await Event.find(query).limit(limit).to_list()
        return [EventType.from_model(event) for event in events]
    
    # ==========================================
    # ITINERARIES
    # ==========================================
    
    @strawberry.field
    async def my_itineraries(
        self,
        info: strawberry.types.Info
    ) -> List[ItineraryType]:
        """Get current user's itineraries (requires authentication)"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        return await ItineraryResolver.get_user_itineraries(user.id)
    
    @strawberry.field
    async def itinerary(
        self,
        id: str,
        info: strawberry.types.Info
    ) -> Optional[ItineraryType]:
        """Get single itinerary by ID"""
        return await ItineraryResolver.get_itinerary_by_id(id)
    
    # ==========================================
    # USER
    # ==========================================
    
    @strawberry.field
    async def me(self, info: strawberry.types.Info) -> Optional[UserType]:
        """Get current user (requires authentication)"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        return await UserResolver.get_user_by_id(str(user.id))
    
    @strawberry.field
    async def user(self, id: str) -> Optional[UserType]:
        """Get user by ID (public info only)"""
        return await UserResolver.get_user_by_id(id)
    
    # ==========================================
    # CONVERSATIONS
    # ==========================================
    
    @strawberry.field
    async def my_conversations(
        self,
        info: strawberry.types.Info,
        limit: int = 10
    ) -> List[ConversationType]:
        """Get current user's chat conversations"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        from backend.app.models.conversation import Conversation
        
        conversations = await Conversation.find(
            Conversation.user_id == str(user.id)
        ).sort(-Conversation.created_at).limit(limit).to_list()
        
        return [ConversationType.from_model(conv) for conv in conversations]
    
    # ==========================================
    # STATISTICS
    # ==========================================
    
    @strawberry.field
    async def stats(self) -> str:
        """Get platform statistics"""
        return "Stats coming soon"


@strawberry.type
class Mutation:
    """GraphQL Mutations"""
    
    # ==========================================
    # AUTHENTICATION
    # ==========================================
    
    @strawberry.mutation
    async def login(
        self,
        email: str,
        password: str
    ) -> AuthPayload:
        """Login with email and password"""
        return await AuthResolver.login(email, password)
    
    @strawberry.mutation
    async def register(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None
    ) -> AuthPayload:
        """Register new user"""
        return await AuthResolver.register(email, username, password, full_name)
    
    @strawberry.mutation
    async def oauth_login(
        self,
        provider: str,
        access_token: str
    ) -> AuthPayload:
        """Login with OAuth (Google/Facebook)"""
        return await AuthResolver.oauth_login(provider, access_token)
    
    # ==========================================
    # CHAT
    # ==========================================
    
    @strawberry.mutation
    async def send_message(
        self,
        info: strawberry.types.Info,
        message_input: MessageInput
    ) -> ConversationType:
        """Send a chat message"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        return await ChatResolver.send_message(str(user.id), message_input)
    
    # ==========================================
    # ITINERARY
    # ==========================================
    
    @strawberry.mutation
    async def generate_itinerary(
        self,
        info: strawberry.types.Info,
        input: ItineraryInput
    ) -> ItineraryType:
        """Generate AI-powered itinerary"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        return await ItineraryResolver.generate_itinerary(str(user.id), input)
    
    @strawberry.mutation
    async def delete_itinerary(
        self,
        info: strawberry.types.Info,
        id: str
    ) -> bool:
        """Delete an itinerary"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        return await ItineraryResolver.delete_itinerary(id, str(user.id))
    
    # ==========================================
    # USER PROFILE
    # ==========================================
    
    @strawberry.mutation
    async def update_profile(
        self,
        info: strawberry.types.Info,
        full_name: Optional[str] = None,
        bio: Optional[str] = None
    ) -> UserType:
        """Update user profile"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        return await UserResolver.update_profile(str(user.id), full_name, bio)
    
    # ==========================================
    # FAVORITES
    # ==========================================
    
    @strawberry.mutation
    async def add_favorite(
        self,
        info: strawberry.types.Info,
        resource_type: str,
        resource_id: str
    ) -> bool:
        """Add attraction/hotel/restaurant to favorites"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")
        
        from backend.app.models.user import User
        
        # Update user's favorites list
        db_user = await User.get(str(user.id))
        if db_user:
            if not hasattr(db_user, 'favorites'):
                db_user.favorites = {}
            if resource_type not in db_user.favorites:
                db_user.favorites[resource_type] = []
            if resource_id not in db_user.favorites[resource_type]:
                db_user.favorites[resource_type].append(resource_id)
                await db_user.save()
        
        return True


# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[]
)

