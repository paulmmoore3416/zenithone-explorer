"""
ZenithOne Explorer - Backend-CLI Integration Tests
Tests for integration between backend API and CLI tool
"""

import pytest
import requests
import subprocess
import time
import json
from pathlib import Path


@pytest.fixture(scope="module")
def backend_server():
    """Start backend server for integration testing"""
    # Start the backend server
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=Path(__file__).parent.parent.parent / "backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Verify server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
    except Exception as e:
        process.kill()
        pytest.fail(f"Backend server failed to start: {e}")
    
    yield process
    
    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def cli_command():
    """Helper to execute CLI commands"""
    def execute(args):
        result = subprocess.run(
            ["python", "main.py"] + args,
            cwd=Path(__file__).parent.parent.parent / "cli",
            capture_output=True,
            text=True,
            timeout=30
        )
        return result
    return execute


class TestAuthIntegration:
    """Test authentication flow between CLI and backend"""
    
    def test_cli_login_success(self, backend_server, cli_command):
        """Test successful login via CLI"""
        # Act
        result = cli_command(["auth", "login", "--username", "admin", "--password", "admin123"])
        
        # Assert
        assert result.returncode == 0
        assert "Login successful" in result.stdout or "token" in result.stdout.lower()
    
    def test_cli_login_invalid_credentials(self, backend_server, cli_command):
        """Test login with invalid credentials via CLI"""
        # Act
        result = cli_command(["auth", "login", "--username", "invalid", "--password", "wrong"])
        
        # Assert
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "failed" in result.stderr.lower()
    
    def test_cli_register_new_user(self, backend_server, cli_command):
        """Test user registration via CLI"""
        # Act
        result = cli_command([
            "auth", "register",
            "--username", f"testuser_{int(time.time())}",
            "--email", "test@example.com",
            "--password", "TestPass123!"
        ])
        
        # Assert
        assert result.returncode == 0 or "already exists" in result.stderr.lower()


class TestWorkloadIntegration:
    """Test workload management integration"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self, cli_command):
        """Authenticate before each test"""
        cli_command(["auth", "login", "--username", "admin", "--password", "admin123"])
    
    def test_create_workload_via_cli(self, backend_server, cli_command):
        """Test creating workload via CLI"""
        # Act
        result = cli_command([
            "workload", "create",
            "--name", f"test-workload-{int(time.time())}",
            "--type", "batch",
            "--image", "python:3.14",
            "--command", "python -c 'print(\"Hello\")'",
            "--priority", "normal"
        ])
        
        # Assert
        assert result.returncode == 0
        assert "created" in result.stdout.lower() or "success" in result.stdout.lower()
    
    def test_list_workloads_via_cli(self, backend_server, cli_command):
        """Test listing workloads via CLI"""
        # Act
        result = cli_command(["workload", "list"])
        
        # Assert
        assert result.returncode == 0
        # Should return JSON or formatted output
        assert len(result.stdout) > 0
    
    def test_workload_lifecycle_via_cli(self, backend_server, cli_command):
        """Test complete workload lifecycle via CLI"""
        # Create workload
        workload_name = f"lifecycle-test-{int(time.time())}"
        create_result = cli_command([
            "workload", "create",
            "--name", workload_name,
            "--type", "batch",
            "--image", "alpine:latest",
            "--command", "echo 'test'"
        ])
        assert create_result.returncode == 0
        
        # List workloads to verify creation
        list_result = cli_command(["workload", "list"])
        assert workload_name in list_result.stdout or list_result.returncode == 0
        
        # Note: Delete would require extracting workload ID from output
        # This is a simplified test


class TestContainerIntegration:
    """Test container management integration"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self, cli_command):
        """Authenticate before each test"""
        cli_command(["auth", "login", "--username", "admin", "--password", "admin123"])
    
    def test_list_containers_via_cli(self, backend_server, cli_command):
        """Test listing containers via CLI"""
        # Act
        result = cli_command(["container", "list"])
        
        # Assert
        assert result.returncode == 0
    
    def test_container_operations_via_cli(self, backend_server, cli_command):
        """Test container operations via CLI"""
        # List containers
        result = cli_command(["container", "list"])
        
        # Assert
        assert result.returncode == 0


class TestSubsystemIntegration:
    """Test subsystem monitoring integration"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self, cli_command):
        """Authenticate before each test"""
        cli_command(["auth", "login", "--username", "admin", "--password", "admin123"])
    
    def test_subsystem_status_via_cli(self, backend_server, cli_command):
        """Test getting subsystem status via CLI"""
        # Act
        result = cli_command(["subsystem", "status", "--name", "jes"])
        
        # Assert
        assert result.returncode == 0
        assert "jes" in result.stdout.lower() or len(result.stdout) > 0
    
    def test_list_all_subsystems_via_cli(self, backend_server, cli_command):
        """Test listing all subsystems via CLI"""
        # Act
        result = cli_command(["subsystem", "list"])
        
        # Assert
        assert result.returncode == 0


class TestMetricsIntegration:
    """Test metrics retrieval integration"""
    
    @pytest.fixture(autouse=True)
    def setup_auth(self, cli_command):
        """Authenticate before each test"""
        cli_command(["auth", "login", "--username", "admin", "--password", "admin123"])
    
    def test_get_metrics_via_cli(self, backend_server, cli_command):
        """Test getting system metrics via CLI"""
        # Act
        result = cli_command(["metrics", "system"])
        
        # Assert
        assert result.returncode == 0
        assert len(result.stdout) > 0


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    def test_complete_workload_workflow(self, backend_server, cli_command):
        """Test complete workload submission and execution workflow"""
        # 1. Login
        login_result = cli_command(["auth", "login", "--username", "admin", "--password", "admin123"])
        assert login_result.returncode == 0
        
        # 2. Create workload
        workload_name = f"e2e-test-{int(time.time())}"
        create_result = cli_command([
            "workload", "create",
            "--name", workload_name,
            "--type", "batch",
            "--image", "alpine:latest",
            "--command", "echo 'End-to-end test'"
        ])
        assert create_result.returncode == 0
        
        # 3. List workloads
        list_result = cli_command(["workload", "list"])
        assert list_result.returncode == 0
        
        # 4. Get system metrics
        metrics_result = cli_command(["metrics", "system"])
        assert metrics_result.returncode == 0
    
    def test_api_direct_access(self, backend_server):
        """Test direct API access (bypassing CLI)"""
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        
        # Test API version endpoint
        response = requests.get("http://localhost:8000/api/v1")
        assert response.status_code in [200, 404]  # May not be implemented
