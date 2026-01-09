"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator, Dict
import sys
from pathlib import Path
import os

# Set environment variables before importing app
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["DEBUG"] = "true"  # Enable DEBUG mode for tests
os.environ["ENVIRONMENT"] = "development"

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.main import app
from backend.app.core.database import init_database
from backend.app.models.user import User, UserRole
from backend.app.services.auth_service import AuthService


# Pytest asyncio configuration
pytest_plugins = ('pytest_asyncio',)


# Event loop configuration - use function scope to avoid loop attachment issues
@pytest.fixture(scope="function")
def event_loop():
    """Create event loop for each test function"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Clean up pending tasks
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def initialize_database():
    """Initialize database before each test"""
    await init_database()
    yield


@pytest.fixture(scope="function", autouse=True)
async def disable_rate_limiting(monkeypatch):
    """Disable rate limiting for all tests"""
    from backend.app.middleware.distributed_rate_limit import DistributedRateLimiter
    from backend.app.middleware.rate_limit import RateLimiter
    
    # Patch the distributed rate limiter is_allowed method
    async def mock_distributed_is_allowed(self, request):
        return True, {}
    
    # Patch the simple rate limiter is_allowed method with correct signature
    def mock_simple_is_allowed(self, identifier: str, path: str = None) -> bool:
        return True
    
    monkeypatch.setattr(DistributedRateLimiter, "is_allowed", mock_distributed_is_allowed)
    monkeypatch.setattr(RateLimiter, "is_allowed", mock_simple_is_allowed)
    yield


@pytest.fixture(scope="function", autouse=True)
async def clear_redis():
    """Clear Redis cache between tests"""
    try:
        from backend.app.core.cache import redis_client
        if redis_client and hasattr(redis_client, 'flushdb'):
            await redis_client.flushdb(asynchronous=True)
    except:
        pass  # Redis might not be available
    yield


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_user(event_loop) -> User:
    """Create a test user with unique email to avoid duplicates"""
    import uuid
    unique_suffix = uuid.uuid4().hex[:8]
    unique_email = f"test_{unique_suffix}@example.com"
    unique_username = f"testuser_{unique_suffix}"
    
    # Also cleanup old "test@example.com" users that might be left over
    try:
        old_test_user = await User.find_one({"email": "test@example.com"})
        if old_test_user:
            await old_test_user.delete()
    except:
        pass
    
    user = User(
        email=unique_email,
        username=unique_username,
        full_name="Test User",
        hashed_password=AuthService.hash_password("TestPassword123!"),
        role=UserRole.USER,
        is_active=True
    )
    await user.insert()
    yield user
    # Cleanup after test
    try:
        await user.delete()
    except:
        pass


@pytest.fixture(scope="function")
async def admin_user(event_loop) -> User:
    """Create an admin user with unique username to avoid duplicates"""
    import uuid
    unique_suffix = uuid.uuid4().hex[:8]
    unique_username = f"admin_{unique_suffix}"
    unique_email = f"admin_{unique_suffix}@example.com"
    
    # Delete any existing admin user first (by email and username)
    existing_by_email = await User.find_one({"email": unique_email})
    if existing_by_email:
        await existing_by_email.delete()
    
    existing_by_username = await User.find_one({"username": unique_username})
    if existing_by_username:
        await existing_by_username.delete()
    
    # Also cleanup old admin users that might be left over (cleanup all "admin" users)
    old_admins = await User.find({"username": {"$regex": "^admin"}}).to_list()
    for old_admin in old_admins:
        try:
            await old_admin.delete()
        except:
            pass
    
    user = User(
        email=unique_email,
        username=unique_username,
        full_name="Admin User",
        hashed_password=AuthService.hash_password("AdminPassword123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    await user.insert()
    yield user
    # Cleanup after test
    try:
        await user.delete()
    except:
        pass


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, test_user: User) -> Dict[str, str]:
    """Get authentication headers for test user"""
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123!"
        }
    )
    
    if response.status_code != 200:
        # If login fails, try to recreate test user
        import uuid
        unique_suffix = uuid.uuid4().hex[:8]
        try:
            await test_user.delete()
        except:
            pass
        new_user = await User(
            email=f"test_{unique_suffix}@example.com",
            username=f"testuser_{unique_suffix}",
            full_name="Test User",
            hashed_password=AuthService.hash_password("TestPassword123!"),
            role=UserRole.USER,
            is_active=True
        ).insert()
        
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": new_user.email,
                "password": "TestPassword123!"
            }
        )
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
async def authenticated_client(client: AsyncClient, test_user: User) -> AsyncClient:
    """Get authenticated HTTP client for test user"""
    # Login to get token
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123!"
        }
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    return client


@pytest.fixture(scope="function")
async def admin_headers(client: AsyncClient, admin_user: User) -> Dict[str, str]:
    """Get authentication headers for admin user"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": admin_user.email,
            "password": "AdminPassword123!"
        }
    )
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_attraction_data():
    """Sample attraction data for testing"""
    return {
        "name": {"en": "Test Attraction", "si": "පරීක්ෂණ ආකර්ෂණය", "ta": "சோதனை ஈர்ப்பு"},
        "description": {"en": "Test attraction description", "si": "පරීක්ෂණ විස්තරය", "ta": "சோதனை விளக்கம்"},
        "short_description": {"en": "Short test description", "si": "කෙටි විස්තරය", "ta": "குறுகிய விளக்கம்"},
        "category": "historical",
        "slug": "test-attraction",
        "location": {
            "address": "Test Address, Colombo",
            "city": "Colombo",
            "province": "Western",
            "coordinates": [79.8612, 6.9271]  # [longitude, latitude]
        },
        "how_to_get_there": {"en": "Test directions", "si": "පරීක්ෂණ මාර්ග", "ta": "சோதனை திசைகள்"},
        "is_active": True
    }


@pytest.fixture
def sample_hotel_data():
    """Sample hotel data for testing"""
    return {
        "name": {"en": "Test Hotel"},
        "category": "hotel",
        "star_rating": "four_star",
        "location": {
            "city": "Colombo",
            "latitude": 6.9271,
            "longitude": 79.8612
        },
        "is_active": True
    }


@pytest.fixture
def sample_itinerary_data():
    """Sample itinerary generation request data"""
    from datetime import date, timedelta
    return {
        "destination": "Kandy",
        "duration_days": 3,
        "budget_level": "mid_range",  # budget, mid_range, luxury
        "interests": ["culture", "history"],
        "start_date": (date.today() + timedelta(days=7)).isoformat(),  # Future date
        "travelers_count": 2,
        "custom_requirements": "Test requirements"
    }


@pytest.fixture
def sample_sos_data():
    """Sample SOS request data"""
    return {
        "emergency_type": "medical",  # medical, accident, theft, harassment, other
        "description": "Test emergency description",
        "severity": 3,  # 1-5
        "location": {
            "latitude": 6.9271,
            "longitude": 79.8612,
            "city": "Colombo"
        },
        "photo_urls": []
    }


@pytest.fixture
def sample_location_sharing_data():
    """Sample location sharing request data"""
    return {
        "duration_minutes": 60,
        "share_with": ["contact@example.com"]
    }


@pytest.fixture
def sample_password():
    """Sample password that meets validation requirements (8+ characters)"""
    return "SecurePassword123!"


@pytest.fixture
def sample_coordinates():
    """Sample coordinates for location-based tests (Colombo, Sri Lanka)"""
    return {"lat": 6.9271, "lng": 79.8612}


# Cleanup before and after tests
@pytest.fixture(scope="function", autouse=True)
async def cleanup_test_data():
    """Cleanup test data before and after each test"""
    # Cleanup BEFORE test to ensure clean state
    try:
        from backend.app.models.user import User
        # Remove any leftover test@example.com users from previous runs
        old_test_user = await User.find_one({"email": "test@example.com"})
        if old_test_user:
            await old_test_user.delete()
        
        # Also cleanup stale test users (older pattern)
        stale_users = await User.find({"email": {"$regex": "^test_[a-f0-9]{8}@example\\.com$"}}).to_list()
        for user in stale_users[:50]:  # Limit cleanup to avoid timeout
            try:
                await user.delete()
            except:
                pass
    except Exception as e:
        pass  # Database might not be ready yet
    
    yield
    
    # Cleanup AFTER test - optional, can be disabled if debugging
    # We rely on unique IDs now, so after-cleanup is less critical

