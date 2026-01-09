# 💻 Development Guide

Complete guide for developers working on the backend.

## Overview

This guide covers development setup, coding standards, Git workflow, and best practices for contributing to the backend.

## Development Setup

### Prerequisites

- **Python**: 3.9 or higher
- **MongoDB**: 6.0+ (via Docker)
- **Redis**: 7.0+ (via Docker)
- **Docker & Docker Compose**: Latest version
- **Git**: Version control
- **VS Code**: Recommended IDE (optional)

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd Multilingual_Chatbot_for_Sri_Lanka_Tourism_V1

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Download NLP models
python -m spacy download en_core_web_sm

# 5. Configure environment
cp env.example .env
# Edit .env with your settings

# 6. Start infrastructure
docker-compose up -d mongodb redis

# 7. Run migrations
python -m backend.app.core.migrations migrate

# 8. Start backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### VS Code Setup

**Recommended Extensions**:
- Python
- Pylance
- Black Formatter
- Ruff
- Python Test Explorer

**Settings** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/        # REST API endpoints
│   ├── core/          # Core functionality
│   ├── graphql/       # GraphQL API
│   ├── middleware/    # Middleware components
│   ├── models/        # Data models
│   ├── services/     # Business logic
│   ├── tasks/         # Celery tasks
│   └── main.py        # Application entry point
├── tests/            # Test suite
├── logs/             # Application logs
└── README.md         # Documentation
```

## Coding Standards

### Python Style Guide

Follow **PEP 8** with modifications:

- **Line Length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Imports**: Grouped and sorted (isort)
- **Type Hints**: Required for all functions

### Code Formatting

#### Black

```bash
# Format code
black backend/

# Check formatting
black --check backend/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'
```

#### isort

```bash
# Sort imports
isort backend/

# Check imports
isort --check backend/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.isort]
profile = "black"
line_length = 100
```

### Linting

#### Ruff

```bash
# Lint code
ruff check backend/

# Auto-fix issues
ruff check --fix backend/
```

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "DTZ", "T10", "EM", "ISC", "ICN", "PIE", "PT", "Q", "RSE", "RET", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PD", "PGH", "PL", "TRY", "NPY", "RUF"]
ignore = ["E501"]  # Line length handled by Black
```

### Type Checking

#### mypy

```bash
# Type check
mypy backend/

# Check specific file
mypy backend/app/services/chat_service.py
```

**Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Code Organization

### File Structure

```
backend/app/services/chat_service.py
├── Imports (standard library, third-party, local)
├── Constants
├── Classes
│   ├── Docstrings
│   ├── Methods
│   └── Properties
└── Functions
```

### Naming Conventions

- **Classes**: PascalCase (`ChatService`)
- **Functions/Methods**: snake_case (`send_message`)
- **Variables**: snake_case (`user_id`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Private**: Leading underscore (`_internal_method`)

### Docstrings

Use Google-style docstrings:

```python
def send_message(self, message: str, user_id: str) -> dict:
    """
    Send a chat message and get AI response.
    
    Args:
        message: User message text
        user_id: User identifier
        
    Returns:
        Dictionary containing response and metadata
        
    Raises:
        ValidationError: If message is invalid
        NotFoundError: If user not found
    """
    pass
```

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Development branch
- **feature/**: Feature branches
- **bugfix/**: Bug fix branches
- **hotfix/**: Hotfix branches

### Commit Messages

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

**Examples**:
```
feat(chat): Add voice message support

Add support for voice messages in chat API with speech-to-text conversion.

Closes #123
```

```
fix(auth): Fix token expiration issue

Token expiration was not being checked correctly. Fixed validation logic.

Fixes #456
```

### Pull Request Process

1. **Create Branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**:
   - Write code
   - Add tests
   - Update documentation

3. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat(api): Add new endpoint"
   ```

4. **Push Branch**:
   ```bash
   git push origin feature/new-feature
   ```

5. **Create Pull Request**:
   - Fill out PR template
   - Request review
   - Address feedback

6. **Merge**:
   - After approval
   - Squash and merge
   - Delete branch

## Testing

### Writing Tests

**Location**: `backend/tests/`

**Structure**:
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

### Running Tests

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run specific test
pytest backend/tests/unit/test_chat_service.py::test_send_message
```

### Test Coverage

- **Target**: > 80% overall
- **Critical Services**: > 90%
- **API Endpoints**: > 85%

## API Development

### Adding New Endpoint

1. **Create Route**:
   ```python
   # backend/app/api/v1/new_feature.py
   from fastapi import APIRouter, Depends
   from backend.app.core.auth import get_current_user
   
   router = APIRouter()
   
   @router.get("/endpoint")
   async def get_endpoint(
       current_user: User = Depends(get_current_user)
   ):
       return {"message": "Hello"}
   ```

2. **Register Route**:
   ```python
   # backend/app/api/v1/__init__.py
   from backend.app.api.v1 import new_feature
   
   api_router.include_router(
       new_feature.router,
       prefix="/new-feature",
       tags=["New Feature"]
   )
   ```

3. **Add Tests**:
   ```python
   # backend/tests/api/test_new_feature.py
   def test_get_endpoint(client, auth_headers):
       response = client.get(
           "/api/v1/new-feature/endpoint",
           headers=auth_headers
       )
       assert response.status_code == 200
   ```

## Service Development

### Creating New Service

1. **Create Service File**:
   ```python
   # backend/app/services/new_service.py
   from typing import Optional
   import logging
   
   logger = logging.getLogger(__name__)
   
   class NewService:
       """Service for new feature"""
       
       def __init__(self):
           pass
       
       async def do_something(self, param: str) -> dict:
           """Do something"""
           logger.info(f"Doing something with {param}")
           return {"result": "success"}
   ```

2. **Add Tests**:
   ```python
   # backend/tests/unit/test_new_service.py
   @pytest.mark.asyncio
   async def test_do_something():
       service = NewService()
       result = await service.do_something("test")
       assert result["result"] == "success"
   ```

## Database Development

### Adding New Model

1. **Create Model**:
   ```python
   # backend/app/models/new_model.py
   from beanie import Document
   from pydantic import BaseModel
   from datetime import datetime
   
   class NewModel(Document):
       """New model"""
       name: str
       description: str
       created_at: datetime = datetime.utcnow()
       
       class Settings:
           name = "new_models"
   ```

2. **Register Model**:
   ```python
   # backend/app/core/database.py
   from backend.app.models.new_model import NewModel
   
   await init_beanie(
       database=client[settings.DATABASE_NAME],
       document_models=[
           # ... existing models
           NewModel,
       ]
   )
   ```

3. **Create Migration**:
   ```python
   # backend/app/core/migrations/versions/xxx_add_new_model.py
   async def upgrade():
       await NewModel.create_index([("name", 1)])
   ```

## Debugging

### VS Code Debugging

**Launch Configuration** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI: Backend Server",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "backend.app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Debugging Tips

1. **Use Breakpoints**: Set breakpoints in VS Code
2. **Print Statements**: Use `print()` for quick debugging
3. **Logging**: Use structured logging
4. **API Testing**: Use Swagger UI or Postman
5. **Database Queries**: Use MongoDB Compass

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

### Optimization Tips

1. **Use Async**: All I/O operations should be async
2. **Caching**: Cache frequently accessed data
3. **Database Indexes**: Index frequently queried fields
4. **Pagination**: Always paginate large result sets
5. **Connection Pooling**: Reuse database connections

## Documentation

### Code Documentation

- **Docstrings**: All public functions/classes
- **Type Hints**: All function signatures
- **Comments**: Explain why, not what

### API Documentation

- **Swagger UI**: Auto-generated from code
- **ReDoc**: Alternative documentation
- **Examples**: Include request/response examples

## Common Tasks

### Adding Dependencies

```bash
# Add to requirements.txt
pip install package-name
pip freeze > requirements.txt
```

### Database Migration

```bash
# Create migration
python -m backend.app.core.migrations create "migration_name"

# Run migration
python -m backend.app.core.migrations migrate

# Rollback
python -m backend.app.core.migrations rollback
```

### Seed Data

```bash
# Run seed script
python scripts/seed_data.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Check PYTHONPATH and virtual environment
2. **Database Connection**: Verify MongoDB is running
3. **Port Already in Use**: Change port or kill process
4. **Module Not Found**: Install dependencies

### Getting Help

1. **Check Logs**: `logs/app.log`
2. **Check Documentation**: This guide and other .md files
3. **Search Issues**: GitHub issues
4. **Ask Team**: Slack/Discord

## Best Practices

1. **Write Tests First**: TDD approach
2. **Small Commits**: Commit often, small changes
3. **Code Review**: Always get code reviewed
4. **Documentation**: Keep docs updated
5. **Performance**: Consider performance implications
6. **Security**: Follow security best practices
7. **Error Handling**: Handle errors gracefully
8. **Logging**: Log important events

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Beanie Docs**: https://beanie-odm.dev/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Pytest Docs**: https://docs.pytest.org/

