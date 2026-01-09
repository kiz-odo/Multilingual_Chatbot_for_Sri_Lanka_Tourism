# Test Coverage Improvement Plan

## Current Status
- **Current Coverage**: 54.83%
- **Target Coverage**: 80.0%
- **Gap**: 25.17%
- **Tests Passing**: 369/372 (99.2%)

## Critical Files with 0% Coverage (High Priority)

### 1. Core Infrastructure (Should be excluded or tested)
- `backend/app/__main__.py` (0%) - 7 statements
- `backend/app/core/metrics.py` (0%) - 102 statements
- `backend/app/core/migrations.py` (0%) - 195 statements
- `backend/app/core/secrets.py` (0%) - 218 statements
- `backend/app/core/db_retry.py` (0%) - 71 statements
- `backend/app/core/structured_logging.py` (0%) - 61 statements

### 2. Services (Need Tests)
- `backend/app/services/calendar_export_service.py` (0%) - 132 statements
- `backend/app/services/pdf_export_service.py` (0%) - 108 statements

### 3. Tasks (Need Tests)
- `backend/app/tasks/data_tasks.py` (9%) - 150 statements
- `backend/app/tasks/email_tasks.py` (21%) - 68 statements
- `backend/app/tasks/notification_tasks.py` (14%) - 128 statements

## Moderate Priority (Under 30% Coverage)

- `backend/app/services/speech_service.py` (14%) - 117 statements
- `backend/app/middleware/distributed_rate_limit.py` (16%) - 98 statements
- `backend/app/services/crewai_service.py` (18%) - 294 statements
- `backend/app/api/v1/itinerary.py` (20%) - 192 statements
- `backend/app/api/v1/websocket.py` (21%) - 96 statements
- `backend/app/services/landmark_recognition_service.py` (22%) - 170 statements
- `backend/app/services/translation_service.py` (27%) - 99 statements
- `backend/app/api/v1/feedback.py` (28%) - 36 statements
- `backend/app/api/v1/transport.py` (29%) - 40 statements

## Recommended Actions

### Immediate Actions (Quick Wins)

#### 1. Exclude Non-Critical Infrastructure from Coverage
Add to `pyproject.toml`:
```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*",
    "*/conftest.py",
    "*/.venv/*",
    "*/venv/*",
    "backend/app/__main__.py",           # Entry point
    "backend/app/core/migrations.py",     # Migration scripts
    "backend/app/core/secrets.py",        # Secret management
    "backend/app/core/metrics.py",        # Prometheus metrics
    "backend/app/core/structured_logging.py",  # Logging infrastructure
]
```

This would immediately improve coverage by ~10-12%.

#### 2. Create Tests for Export Services (High Impact)
- Create `backend/tests/unit/test_calendar_export_service.py`
- Create `backend/tests/unit/test_pdf_export_service.py`

These are important user-facing features and should have tests.

#### 3. Create Tests for Task Modules
- Improve `test_data_tasks.py`
- Improve `test_email_tasks.py`  
- Improve `test_notification_tasks.py`

#### 4. Fix Gemini Model Name
Update `backend/app/services/gemini_service.py` to use correct model:
- Change `gemini-pro` → `gemini-1.5-pro` or `gemini-2.0-flash-exp`

### Medium-Term Actions

1. **Add Integration Tests for Itinerary Export**
   - PDF export functionality
   - ICS calendar export functionality
   - Test both success and error cases

2. **Add WebSocket Tests**
   - Connection tests
   - Message handling tests
   - Security tests

3. **Add Transport/Feedback API Tests**
   - Complete CRUD operations
   - Validation tests

4. **Add Service Layer Tests**
   - Speech service tests
   - Translation service tests
   - Landmark recognition tests

## Estimated Coverage After Changes

| Action | Current | After | Gain |
|--------|---------|-------|------|
| Exclude infrastructure | 54.83% | ~65% | +10% |
| Add export service tests | 65% | ~70% | +5% |
| Add task tests | 70% | ~75% | +5% |
| Add API endpoint tests | 75% | ~82% | +7% |
| **Total** | **54.83%** | **~82%** | **+27%** |

## Implementation Order

1. **Week 1**: Exclude infrastructure files, fix Gemini model (Quick)
2. **Week 2**: Add export service tests (High user impact)
3. **Week 3**: Add task module tests (Background jobs)
4. **Week 4**: Complete API endpoint coverage (User-facing)
5. **Week 5**: Add service layer tests (Core functionality)

## Test Writing Guidelines

### For Services
- Test initialization with/without dependencies
- Test success cases
- Test error handling
- Test edge cases (empty input, invalid input)
- Mock external dependencies (APIs, databases)

### For API Endpoints
- Test authenticated and unauthenticated access
- Test input validation
- Test success responses
- Test error responses (400, 401, 403, 404, 500)
- Test pagination where applicable

### For Tasks
- Test task execution success
- Test retry logic
- Test error handling
- Mock external services (email, notifications)

## Quick Start Commands

```bash
# Run tests with coverage for specific module
pytest backend/tests/unit/test_calendar_export_service.py -v --cov=backend/app/services/calendar_export_service.py

# Run all tests excluding slow tests
pytest backend/tests -v -m "not slow" --cov=backend/app

# Generate HTML coverage report
pytest backend/tests --cov=backend/app --cov-report=html
# Then open: htmlcov/index.html

# Check coverage for specific files
pytest backend/tests --cov=backend/app/services --cov-report=term-missing
```

## Notes

- Current 369/372 tests passing is excellent (99.2%)
- Focus on high-impact, user-facing features first
- Infrastructure code can be excluded from coverage if it's bootstrapping/setup code
- Aim for 80-85% coverage, not 100% (diminishing returns)
