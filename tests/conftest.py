"""
ZenithOne Explorer - Test Configuration
Pytest configuration and shared fixtures
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Test configuration
TEST_DATABASE = ":memory:"  # Use in-memory SQLite for tests
TEST_API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "database_url": TEST_DATABASE,
        "api_base_url": TEST_API_BASE_URL,
        "timeout": TEST_TIMEOUT,
        "debug": True
    }


@pytest.fixture(scope="function")
def clean_database():
    """Provide a clean database for each test"""
    # Setup: Create fresh database
    from database.connection import init_db
    db = init_db(TEST_DATABASE)
    
    yield db
    
    # Teardown: Close and cleanup
    db.close()


@pytest.fixture(scope="function")
def mock_ollama():
    """Mock Ollama AI service for testing"""
    class MockOllama:
        def generate(self, prompt, model="qwen2.5:latest"):
            return {
                "response": "Mock AI response",
                "model": model,
                "done": True
            }
        
        def chat(self, messages, model="qwen2.5:latest"):
            return {
                "message": {
                    "role": "assistant",
                    "content": "Mock AI chat response"
                },
                "done": True
            }
    
    return MockOllama()


@pytest.fixture(scope="function")
def sample_workload():
    """Sample workload data for testing"""
    return {
        "name": "test-workload",
        "type": "batch",
        "image": "python:3.14",
        "command": "python -c 'print(\"Hello World\")'",
        "priority": "normal",
        "cpu_limit": 1.0,
        "memory_limit": 512
    }


@pytest.fixture(scope="function")
def sample_container():
    """Sample container data for testing"""
    return {
        "name": "test-container",
        "image": "alpine:latest",
        "command": "sleep 3600",
        "environment": {"TEST": "true"},
        "ports": {"8080": "8080"}
    }


@pytest.fixture(scope="function")
def sample_user():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "role": "user"
    }


@pytest.fixture(scope="function")
def admin_user():
    """Sample admin user data for testing"""
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "role": "admin"
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
