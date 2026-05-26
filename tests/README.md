# ZenithOne Explorer - Test Suite

Comprehensive test suite for the ZenithOne Explorer project.

## Test Structure

```
tests/
├── conftest.py              # Shared pytest configuration and fixtures
├── unit/                    # Unit tests for individual components
│   ├── test_workload_manager.py
│   ├── test_container_orchestrator.py
│   └── test_api_endpoints.py
├── integration/             # Integration tests
│   └── test_backend_cli_integration.py
├── performance/             # Performance and load tests
│   └── test_load_testing.py
└── security/                # Security audit tests
    └── test_security_audit.py
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio requests

# Ensure backend is running for integration tests
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Run All Tests

```bash
# From project root
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v -m performance

# Security tests
pytest tests/security/ -v -m security
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=backend --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Run Specific Tests

```bash
# Run single test file
pytest tests/unit/test_workload_manager.py -v

# Run specific test
pytest tests/unit/test_workload_manager.py::TestWorkloadManager::test_create_workload_success -v

# Run tests matching pattern
pytest tests/ -k "workload" -v
```

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.slow` - Slow-running tests

### Run by Marker

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run all except slow tests
pytest tests/ -m "not slow" -v

# Run performance and security tests
pytest tests/ -m "performance or security" -v
```

## Test Configuration

### pytest.ini

Create a `pytest.ini` file in the project root:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
    slow: Slow-running tests
addopts = 
    -v
    --strict-markers
    --tb=short
    --disable-warnings
```

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    @pytest.fixture
    def component(self):
        return MyComponent()
    
    def test_something(self, component):
        # Arrange
        expected = "result"
        
        # Act
        result = component.do_something()
        
        # Assert
        assert result == expected
```

### Integration Test Example

```python
import pytest
import requests

@pytest.fixture(scope="module")
def backend_server():
    # Setup: Start server
    process = start_server()
    yield process
    # Teardown: Stop server
    process.terminate()

def test_api_integration(backend_server):
    response = requests.get("http://localhost:8000/api/v1/health")
    assert response.status_code == 200
```

## Continuous Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

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
          python-version: '3.14'
      - run: pip install -r backend/requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=backend
```

## Test Coverage Goals

- **Unit Tests**: >80% code coverage
- **Integration Tests**: All major workflows covered
- **Performance Tests**: Handle 100+ concurrent operations
- **Security Tests**: No critical vulnerabilities

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in PYTHONPATH
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Backend Not Running**: Start backend before integration tests
   ```bash
   cd backend && python -m uvicorn main:app &
   ```

3. **Port Already in Use**: Change test port in conftest.py

4. **Timeout Errors**: Increase timeout in test configuration

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies
3. **Fixtures**: Use fixtures for common setup
4. **Naming**: Use descriptive test names
5. **Documentation**: Add docstrings to complex tests
6. **Cleanup**: Always cleanup resources in teardown

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
