"""
User service for managing user operations
"""

from typing import Optional, List
from datetime import datetime

from backend.app.models.user import User, UserCreate, UserUpdate, UserPreferences


class UserService:
    """User service class"""
    
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            hashed_password=hashed_password,
            preferences=UserPreferences(
                preferred_language=user_data.preferred_language
            )
        )
        
        await user.save()
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(user_id)
        except:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await User.find_one({"email": email})
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return await User.find_one({"username": username})
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await user.save()
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by deactivating)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await user.save()
        return True
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users"""
        return await User.find({"is_active": True}).skip(skip).limit(limit).to_list()
    
    async def update_user_stats(self, user_id: str, increment_conversations: bool = False, 
                              increment_queries: bool = False) -> Optional[User]:
        """Update user statistics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if increment_conversations:
            user.stats.total_conversations += 1
        
        if increment_queries:
            user.stats.total_queries += 1
        
        user.stats.last_activity = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        await user.save()
        return user
    
    async def add_favorite_attraction(self, user_id: str, attraction_id: str) -> Optional[User]:
        """Add attraction to user's favorites"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if attraction_id not in user.stats.favorite_attractions:
            user.stats.favorite_attractions.append(attraction_id)
            user.updated_at = datetime.utcnow()
            await user.save()
        
        return user
    
    async def remove_favorite_attraction(self, user_id: str, attraction_id: str) -> Optional[User]:
        """Remove attraction from user's favorites"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if attraction_id in user.stats.favorite_attractions:
            user.stats.favorite_attractions.remove(attraction_id)
            user.updated_at = datetime.utcnow()
            await user.save()
        
        return user
    
    async def add_visited_place(self, user_id: str, place_id: str) -> Optional[User]:
        """Add place to user's visited places"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if place_id not in user.stats.visited_places:
            user.stats.visited_places.append(place_id)
            user.updated_at = datetime.utcnow()
            await user.save()
        
        return user
    
    async def verify_user(self, user_id: str) -> Optional[User]:
        """Verify user email"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        await user.save()
        return user
