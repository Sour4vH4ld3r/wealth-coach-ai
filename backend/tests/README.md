# Backend Test Suite

Comprehensive test suite for the Wealth Coach AI backend.

## Test Structure

```
backend/tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Shared fixtures and configuration
├── test_auth.py          # Authentication endpoint tests
├── test_chat.py          # Chat endpoint tests
└── test_security.py      # Security function tests
```

## Running Tests

### Run All Tests
```bash
pytest backend/tests/ -v
```

### Run Specific Test File
```bash
pytest backend/tests/test_auth.py -v
pytest backend/tests/test_chat.py -v
pytest backend/tests/test_security.py -v
```

### Run Specific Test
```bash
pytest backend/tests/test_auth.py::test_user_registration_success -v
```

### Run Tests with Coverage
```bash
pytest backend/tests/ -v --cov=backend --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
pytest backend/tests/ --cov=backend --cov-report=html
open htmlcov/index.html  # View coverage report in browser
```

### Run Tests by Marker
```bash
pytest -m auth      # Run only auth tests
pytest -m chat      # Run only chat tests
pytest -m security  # Run only security tests
```

## Test Categories

### Authentication Tests (test_auth.py)
- **Registration**: User creation, duplicate email handling, password validation
- **Login**: Credential validation, account lockout, inactive user handling
- **Token Refresh**: Token renewal, invalid token handling
- **JWT Validation**: Token expiration, signature verification

**Key Test Cases:**
- ✓ `test_user_registration_success` - Valid registration
- ✓ `test_user_registration_duplicate_email` - Duplicate email rejected
- ✓ `test_user_registration_weak_password` - Weak passwords rejected
- ✓ `test_login_success` - Valid login works
- ✓ `test_login_invalid_credentials` - Wrong password fails
- ✓ `test_login_account_lockout` - 5 failed attempts = lockout
- ✓ `test_token_refresh_success` - Refresh token works
- ✓ `test_jwt_token_expiration` - Expired tokens rejected

### Chat Tests (test_chat.py)
- **Message Sending**: Authenticated/unauthenticated requests, message validation
- **Session Management**: Session creation, retrieval, pagination
- **History**: Conversation history, message persistence
- **Caching**: Response caching for identical queries

**Key Test Cases:**
- ✓ `test_send_message_authenticated` - Chat works for logged-in users
- ✓ `test_send_message_unauthenticated` - Chat blocked without auth
- ✓ `test_chat_history_retrieval` - Get conversation history
- ✓ `test_chat_session_management` - Create/list sessions
- ✓ `test_send_message_saves_to_database` - Messages persisted
- ✓ `test_chat_response_caching` - Identical queries cached

### Security Tests (test_security.py)
- **Password Hashing**: bcrypt hashing, verification
- **Password Validation**: Strength requirements enforcement
- **JWT Tokens**: Creation, validation, expiration
- **Token Types**: Access vs refresh token verification

**Key Test Cases:**
- ✓ `test_hash_password` - Password hashing works
- ✓ `test_verify_password_correct` - Password verification
- ✓ `test_validate_password_strength_valid` - Valid passwords accepted
- ✓ `test_validate_password_too_short` - Short passwords rejected
- ✓ `test_create_access_token` - JWT creation
- ✓ `test_decode_token_expired` - Expired tokens fail
- ✓ `test_verify_access_token_with_refresh_token` - Token type validation

## Test Fixtures

### Database Fixtures
- `db`: Fresh in-memory SQLite database for each test
- `test_user`: Pre-created user with known credentials
- `test_user_token`: Valid JWT token for test user
- `auth_headers`: Authorization headers with Bearer token

### Mock Fixtures
- `mock_redis`: Mock Redis client (no Redis server required)
- `mock_llm_client`: Mock LLM client (no OpenAI API calls)
- `mock_rag_retriever`: Mock RAG retriever (no vector DB required)

### Client Fixtures
- `client`: FastAPI TestClient with all dependencies mocked
- `async_client`: Async version of test client

## Test Database

Tests use an **in-memory SQLite database** for speed and isolation:
- Each test gets a fresh database
- No cleanup required
- Tests run in parallel
- No production data affected

## Mocking Strategy

### Why Mock?
- **Speed**: Tests run faster without external services
- **Reliability**: Tests don't fail due to network issues
- **Cost**: No API charges during testing
- **Isolation**: Tests are independent

### What's Mocked?
- **Redis**: Mock in-memory cache
- **LLM (OpenAI)**: Mock responses
- **RAG Retriever**: Mock document retrieval
- **Vector Database**: Not needed with mock RAG

## Coverage Goals

Target: **70-80%** code coverage for critical paths

### Critical Paths (Must Test):
- ✓ User authentication (registration, login)
- ✓ Password hashing and validation
- ✓ JWT token creation and verification
- ✓ Chat message sending (authenticated)
- ✓ Database persistence
- ✓ Error handling

### Non-Critical (Optional):
- Logging utilities
- Configuration loading
- Middleware (tested via integration)

## Common Issues

### Issue: Import Errors
**Solution**: Ensure you're in the project root directory
```bash
cd /Users/souravhalder/Downloads/wealthWarriors
pytest backend/tests/
```

### Issue: "No module named backend"
**Solution**: Add project root to PYTHONPATH
```bash
export PYTHONPATH=/Users/souravhalder/Downloads/wealthWarriors:$PYTHONPATH
pytest backend/tests/
```

### Issue: Database Errors
**Solution**: Tests use SQLite in-memory, but if you see PostgreSQL errors, check that fixtures are being used correctly.

### Issue: Async Warnings
**Solution**: Already configured in pytest.ini with `asyncio_mode = auto`

## CI/CD Integration

To run tests in CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: pytest backend/tests/ -v --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Test names explain what they test
3. **AAA Pattern**: Arrange, Act, Assert
4. **One Assertion**: Test one thing per test (mostly)
5. **Mock External Services**: Don't call real APIs in tests
6. **Fast Tests**: Keep tests fast (< 1s each)

## Test Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tests | 15+ | 30+ |
| Coverage | 70% | TBD |
| Speed | < 30s | TBD |
| Pass Rate | 100% | TBD |

## Next Steps

1. Run the test suite
2. Review coverage report
3. Add missing tests for edge cases
4. Set up CI/CD integration
5. Add performance tests
