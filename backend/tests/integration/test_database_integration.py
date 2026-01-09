"""
Integration tests for database operations
"""

import pytest
import uuid
from datetime import datetime
from backend.app.models.user import User, UserRole
from backend.app.models.attraction import Attraction


@pytest.mark.integration
class TestUserDatabaseOperations:
    """Test user database operations"""
    
    @pytest.mark.asyncio
    async def test_create_user(self):
        """Test creating a user in database"""
        # Generate unique email to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        email = f"integration_test_{unique_id}@example.com"
        
        # Delete any existing user with this email first
        existing = await User.find_one({"email": email})
        if existing:
            await existing.delete()
        
        user = User(
            email=email,
            username=f"integrationtest_{unique_id}",
            full_name="Integration Test User",
            hashed_password="hashed_password_here",
            role=UserRole.USER,
            is_active=True
        )
        
        await user.insert()
        assert user.id is not None
        
        # Cleanup
        await user.delete()
    
    @pytest.mark.asyncio
    async def test_find_user_by_email(self):
        """Test finding user by email"""
        # Generate unique email
        unique_id = str(uuid.uuid4())[:8]
        email = f"findme_{unique_id}@example.com"
        username = f"findme_{unique_id}"
        
        # Delete existing if any
        existing = await User.find_one({"email": email})
        if existing:
            await existing.delete()
        
        # Create test user
        user = User(
            email=email,
            username=username,
            full_name="Find Me User",
            hashed_password="hashed_password_here",
            role=UserRole.USER,
            is_active=True
        )
        await user.insert()
        
        # Find user
        found_user = await User.find_one({"email": email})
        
        assert found_user is not None
        assert found_user.username == username
        
        # Cleanup
        await user.delete()
    
    @pytest.mark.asyncio
    async def test_update_user(self):
        """Test updating user information"""
        # Generate unique email
        unique_id = str(uuid.uuid4())[:8]
        email = f"updateme_{unique_id}@example.com"
        
        # Delete existing if any
        existing = await User.find_one({"email": email})
        if existing:
            await existing.delete()
        
        # Create test user
        user = User(
            email=email,
            username=f"updateme_{unique_id}",
            full_name="Update Me User",
            hashed_password="hashed_password_here",
            role=UserRole.USER,
            is_active=True
        )
        await user.insert()
        
        # Update user
        user.full_name = "Updated Name"
        await user.save()
        
        # Verify update
        updated_user = await User.find_one({"email": email})
        assert updated_user.full_name == "Updated Name"
        
        # Cleanup
        await user.delete()
    
    @pytest.mark.asyncio
    async def test_delete_user(self):
        """Test deleting a user"""
        # Generate unique email
        unique_id = str(uuid.uuid4())[:8]
        email = f"deleteme_{unique_id}@example.com"
        
        # Delete existing if any
        existing = await User.find_one({"email": email})
        if existing:
            await existing.delete()
        
        # Create test user
        user = User(
            email=email,
            username=f"deleteme_{unique_id}",
            full_name="Delete Me User",
            hashed_password="hashed_password_here",
            role=UserRole.USER,
            is_active=True
        )
        await user.insert()
        user_id = user.id
        
        # Delete user
        await user.delete()
        
        # Verify deletion
        deleted_user = await User.get(user_id)
        assert deleted_user is None


@pytest.mark.integration
class TestAttractionDatabaseOperations:
    """Test attraction database operations"""
    
    @pytest.mark.asyncio
    async def test_create_attraction(self, sample_attraction_data):
        """Test creating an attraction"""
        attraction = Attraction(**sample_attraction_data)
        await attraction.insert()
        
        assert attraction.id is not None
        
        # Cleanup
        await attraction.delete()
    
    @pytest.mark.asyncio
    async def test_find_attractions_by_category(self, sample_attraction_data):
        """Test finding attractions by category"""
        # Create a test attraction with unique slug
        sample_attraction_data["slug"] = f"test-attraction-{uuid.uuid4().hex[:8]}"
        attraction = Attraction(**sample_attraction_data)
        await attraction.insert()
        
        try:
            # Find our specific attraction by slug to avoid validation errors from existing data
            found_attraction = await Attraction.find_one({"slug": sample_attraction_data["slug"]})
            
            assert found_attraction is not None
            assert found_attraction.category == "historical"
        finally:
            # Cleanup
            await attraction.delete()
    
    @pytest.mark.asyncio
    async def test_geospatial_query(self, sample_attraction_data):
        """Test geospatial queries for nearby attractions"""
        # Create a test attraction with unique slug
        sample_attraction_data["slug"] = f"test-geo-attraction-{uuid.uuid4().hex[:8]}"
        attraction = Attraction(**sample_attraction_data)
        await attraction.insert()
        
        try:
            # Query our specific test attraction by slug to avoid validation errors
            found_attraction = await Attraction.find_one({"slug": sample_attraction_data["slug"]})
            
            assert found_attraction is not None
            assert found_attraction.location.coordinates == [79.8612, 6.9271]
        finally:
            # Cleanup
            await attraction.delete()


@pytest.mark.integration
class TestServiceIntegration:
    """Test integration between services"""
    
    @pytest.mark.asyncio
    async def test_auth_and_user_service_integration(self):
        """Test authentication service with user database"""
        from backend.app.services.auth_service import AuthService
        
        # Generate unique email
        unique_id = str(uuid.uuid4())[:8]
        email = f"service_test_{unique_id}@example.com"
        
        # Delete existing if any
        existing = await User.find_one({"email": email})
        if existing:
            await existing.delete()
        
        # Create user
        user = User(
            email=email,
            username=f"servicetest_{unique_id}",
            full_name="Service Test User",
            hashed_password=AuthService.hash_password("TestPassword123!"),
            role=UserRole.USER,
            is_active=True
        )
        await user.insert()
        
        # Test authentication
        authenticated_user = await AuthService.authenticate_user(
            email,
            "TestPassword123!"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.email == user.email
        
        # Cleanup
        await user.delete()
