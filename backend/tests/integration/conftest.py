"""
Pytest configuration for integration tests
"""

import pytest
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.main import app


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
