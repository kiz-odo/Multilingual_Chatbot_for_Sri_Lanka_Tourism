# 🧪 Testing Documentation

Complete guide to testing the backend application.

## Overview

The backend uses **pytest** for testing with comprehensive test coverage including unit tests, integration tests, and API tests.

## Test Structure

```
backend/tests/
├── unit/              # Unit tests for services and models
├── integration/       # Integration tests
├── api/               # API endpoint tests
├── security_tests/    # Security tests
├── load_tests/        # Load testing (Locust)
├── conftest.py        # Pytest configuration and fixtures
└── run_tests.py       # Test runner script
```

## Running Tests

### Run All Tests

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/unit/test_chat_service.py -v

# Run specific test
pytest backend/tests/unit/test_chat_service.py::test_send_message -v
```

### Run Test Categories

```bash
# Unit tests only
pytest backend/tests/unit/ -v

# Integration tests
pytest backend/tests/integration/ -v

# API tests
pytest backend/tests/api/ -v

# Security tests
pytest backend/tests/security_tests/ -v
```

### Run with Coverage Report

```bash
# Generate HTML coverage report
pytest backend/tests/ --cov=backend --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

## Test Types

### 1. Unit Tests

**Location**: `backend/tests/unit/`

**Purpose**: Test individual functions and methods in isolation.

**Example**:
```python
import pytest
from backend.app.services.chat_service import ChatService

@pytest.mark.asyncio
async def test_send_message():
    """Test sending a chat message"""
    service = ChatService()
    response = await service.send_message(
        message="Hello",
        user_id="test_user",
        language="en"
    )
    assert response is not None
    assert "response" in response
```

**Best Practices**:
- Test one thing at a time
- Use mocks for external dependencies
- Test edge cases and error conditions
- Keep tests fast and isolated

### 2. Integration Tests

**Location**: `backend/tests/integration/`

**Purpose**: Test interactions between components.

**Example**:
```python
import pytest
from backend.app.models.user import User

@pytest.mark.asyncio
async def test_user_creation():
    """Test user creation and retrieval"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    await user.insert()
    
    retrieved = await User.find_one(User.email == "test@example.com")
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
    
    await user.delete()
```

**Best Practices**:
- Use test database
- Clean up after tests
- Test real database operations
- Test error scenarios

### 3. API Tests

**Location**: `backend/tests/api/`

**Purpose**: Test API endpoints end-to-end.

**Example**:
```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_attractions():
    """Test GET /api/v1/attractions"""
    response = client.get("/api/v1/attractions")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_create_user():
    """Test POST /api/v1/auth/register"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
```

**Best Practices**:
- Test all HTTP methods
- Test authentication/authorization
- Test error responses
- Test response formats

### 4. Security Tests

**Location**: `backend/tests/security_tests/`

**Purpose**: Test security features and vulnerabilities.

**Example**:
```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_rate_limiting():
    """Test rate limiting"""
    # Make many requests
    for _ in range(101):
        response = client.get("/api/v1/attractions")
    
    # 101st request should be rate limited
    assert response.status_code == 429

def test_sql_injection():
    """Test SQL injection protection"""
    # MongoDB is NoSQL, but test for injection attempts
    response = client.get("/api/v1/attractions?search=<script>alert('xss')</script>")
    assert response.status_code == 200
    # Should sanitize input
```

## Test Fixtures

### Common Fixtures

**Location**: `backend/tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
async def test_user():
    """Create test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test User"
    )
    await user.insert()
    yield user
    await user.delete()

@pytest.fixture
def auth_headers(test_user):
    """Get auth headers for test user"""
    # Create token for test user
    token = create_test_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}
```

### Database Fixtures

```python
import pytest
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture
async def test_db():
    """Test database fixture"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_database
    yield db
    await client.drop_database("test_database")
    client.close()
```

## Mocking

### Mock External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_llm_service_with_mock():
    """Test LLM service with mocked API"""
    with patch('backend.app.services.llm_service.GeminiService.generate') as mock_generate:
        mock_generate.return_value = "Mocked response"
        
        service = LLMService()
        response = await service.generate("test prompt")
        
        assert response == "Mocked response"
        mock_generate.assert_called_once()
```

### Mock Database

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_user_service_with_mock_db():
    """Test user service with mocked database"""
    mock_user = User(email="test@example.com", full_name="Test")
    
    with patch('backend.app.models.user.User.find_one') as mock_find:
        mock_find.return_value = mock_user
        
        service = UserService()
        user = await service.get_user_by_email("test@example.com")
        
        assert user.email == "test@example.com"
```

## Test Coverage

### Coverage Goals

- **Overall**: > 80%
- **Critical Services**: > 90%
- **API Endpoints**: > 85%
- **Models**: > 75%

### View Coverage

```bash
# Generate coverage report
pytest backend/tests/ --cov=backend --cov-report=html

# View in browser
open htmlcov/index.html
```

### Coverage Configuration

**Location**: `pyproject.toml`

```toml
[tool.coverage.run]
source = ["backend"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

## Test Data

### Fixtures for Test Data

```python
@pytest.fixture
def sample_attraction():
    """Sample attraction data"""
    return {
        "name": "Test Attraction",
        "description": "Test description",
        "category": "beach",
        "location": {
            "address": "Test Address",
            "city": "Colombo",
            "coordinates": [79.8612, 6.9271]
        }
    }
```

### Database Seeding

```python
@pytest.fixture
async def seeded_database():
    """Seed test database with sample data"""
    # Create test data
    attractions = [
        Attraction(**attraction_data) for attraction_data in SAMPLE_ATTRACTIONS
    ]
    await Attraction.insert_many(attractions)
    yield
    # Cleanup
    await Attraction.delete_all()
```

## Async Testing

### Async Test Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await async_function()
    assert result is not None
```

### Async Fixtures

```python
@pytest.fixture
async def async_fixture():
    """Async fixture"""
    result = await setup_async_resource()
    yield result
    await cleanup_async_resource()
```

## Load Testing

### Locust Load Tests

**Location**: `backend/tests/load_tests/locustfile.py`

```python
from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_attractions(self):
        self.client.get("/api/v1/attractions")
    
    @task(3)
    def send_chat_message(self):
        self.client.post(
            "/api/v1/chat/message",
            json={"message": "Hello", "language": "en"}
        )
```

### Running Load Tests

```bash
# Start Locust
locust -f backend/tests/load_tests/locustfile.py

# Access web UI at http://localhost:8089
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest backend/tests/ --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Best Practices

### 1. Test Organization

- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Independence

- Tests should not depend on each other
- Clean up after each test
- Use fixtures for setup/teardown

### 3. Test Data

- Use factories for test data
- Keep test data minimal
- Use realistic data

### 4. Assertions

- Use specific assertions
- Test both success and failure cases
- Test edge cases

### 5. Performance

- Keep tests fast
- Use mocks for slow operations
- Run tests in parallel when possible

## Common Issues

### 1. Database State

**Problem**: Tests affecting each other due to shared database state.

**Solution**: Use test database and clean up after each test.

```python
@pytest.fixture(autouse=True)
async def clean_database():
    """Clean database before each test"""
    yield
    await User.delete_all()
```

### 2. Async Operations

**Problem**: Forgetting to await async operations.

**Solution**: Always use `@pytest.mark.asyncio` and `await`.

```python
@pytest.mark.asyncio
async def test_async():
    result = await async_function()  # Don't forget await!
```

### 3. Mock Configuration

**Problem**: Mocks not working as expected.

**Solution**: Patch at the correct location.

```python
# Correct: Patch where it's used
@patch('backend.app.services.chat_service.LLMService.generate')
async def test_chat(mock_generate):
    pass
```

## Test Commands Reference

```bash
# Run all tests
pytest backend/tests/

# Run with verbose output
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/unit/test_chat_service.py

# Run specific test
pytest backend/tests/unit/test_chat_service.py::test_send_message

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run only failed tests
pytest backend/tests/ --lf

# Run in parallel
pytest backend/tests/ -n auto

# Stop on first failure
pytest backend/tests/ -x

# Show print statements
pytest backend/tests/ -s
```

## Future Enhancements

1. **E2E Tests**: Full end-to-end tests with Selenium
2. **Performance Tests**: Automated performance benchmarks
3. **Contract Tests**: API contract testing
4. **Mutation Testing**: Test quality validation
5. **Visual Regression**: UI regression tests (for frontend)

