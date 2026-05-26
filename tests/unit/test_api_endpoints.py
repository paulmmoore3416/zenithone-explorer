"""
ZenithOne Explorer - API Endpoints Unit Tests
Tests for FastAPI REST API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import uuid


@pytest.fixture
def client():
    """Create test client for API testing"""
    with patch('main.get_db'):
        from main import app
        return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    return {"Authorization": "Bearer test_token"}


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    def test_login_success(self, client, sample_user):
        """Test successful login"""
        # Arrange
        with patch('api.routes.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "id": "user123",
                "username": sample_user['username'],
                "role": "user"
            }
            
            # Act
            response = client.post("/api/v1/auth/login", json={
                "username": sample_user['username'],
                "password": sample_user['password']
            })
            
            # Assert
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        # Arrange
        with patch('api.routes.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            # Act
            response = client.post("/api/v1/auth/login", json={
                "username": "invalid",
                "password": "wrong"
            })
            
            # Assert
            assert response.status_code == 401
            assert "detail" in response.json()
    
    def test_register_success(self, client, sample_user):
        """Test successful user registration"""
        # Arrange
        with patch('api.routes.auth.create_user') as mock_create:
            mock_create.return_value = {
                "id": "user123",
                "username": sample_user['username'],
                "email": sample_user['email']
            }
            
            # Act
            response = client.post("/api/v1/auth/register", json=sample_user)
            
            # Assert
            assert response.status_code == 201
            assert response.json()["username"] == sample_user['username']
    
    def test_register_duplicate_username(self, client, sample_user):
        """Test registration with duplicate username"""
        # Arrange
        with patch('api.routes.auth.create_user') as mock_create:
            mock_create.side_effect = ValueError("Username already exists")
            
            # Act
            response = client.post("/api/v1/auth/register", json=sample_user)
            
            # Assert
            assert response.status_code == 400


class TestWorkloadEndpoints:
    """Test suite for workload management endpoints"""
    
    def test_create_workload_success(self, client, auth_headers, sample_workload):
        """Test successful workload creation"""
        # Arrange
        with patch('api.routes.workloads.WorkloadManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.create_workload.return_value = {
                "id": str(uuid.uuid4()),
                **sample_workload,
                "status": "pending"
            }
            mock_manager.return_value = mock_instance
            
            # Act
            response = client.post(
                "/api/v1/workloads",
                json=sample_workload,
                headers=auth_headers
            )
            
            # Assert
            assert response.status_code == 201
            assert response.json()["name"] == sample_workload["name"]
    
    def test_create_workload_unauthorized(self, client, sample_workload):
        """Test workload creation without authentication"""
        # Act
        response = client.post("/api/v1/workloads", json=sample_workload)
        
        # Assert
        assert response.status_code == 401
    
    def test_list_workloads_success(self, client, auth_headers):
        """Test successful workload listing"""
        # Arrange
        mock_workloads = [
            {"id": "1", "name": "workload1", "status": "running"},
            {"id": "2", "name": "workload2", "status": "pending"}
        ]
        
        with patch('api.routes.workloads.WorkloadManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.list_workloads.return_value = mock_workloads
            mock_manager.return_value = mock_instance
            
            # Act
            response = client.get("/api/v1/workloads", headers=auth_headers)
            
            # Assert
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_get_workload_success(self, client, auth_headers):
        """Test successful workload retrieval"""
        # Arrange
        workload_id = str(uuid.uuid4())
        mock_workload = {"id": workload_id, "name": "test", "status": "running"}
        
        with patch('api.routes.workloads.WorkloadManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_workload.return_value = mock_workload
            mock_manager.return_value = mock_instance
            
            # Act
            response = client.get(f"/api/v1/workloads/{workload_id}", headers=auth_headers)
            
            # Assert
            assert response.status_code == 200
            assert response.json()["id"] == workload_id
    
    def test_get_workload_not_found(self, client, auth_headers):
        """Test workload retrieval when not found"""
        # Arrange
        workload_id = str(uuid.uuid4())
        
        with patch('api.routes.workloads.WorkloadManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.get_workload.side_effect = ValueError("Workload not found")
            mock_manager.return_value = mock_instance
            
            # Act
            response = client.get(f"/api/v1/workloads/{workload_id}", headers=auth_headers)
            
            # Assert
            assert response.status_code == 404
    
    def test_delete_workload_success(self, client, auth_headers):
        """Test successful workload deletion"""
        # Arrange
        workload_id = str(uuid.uuid4())
        
        with patch('api.routes.workloads.WorkloadManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.delete_workload.return_value = True
            mock_manager.return_value = mock_instance
            
            # Act
            response = client.delete(f"/api/v1/workloads/{workload_id}", headers=auth_headers)
            
            # Assert
            assert response.status_code == 204
    
    def test_schedule_workload_success(self, client, auth_headers):
        """Test successful workload scheduling"""
        # Arrange
        workload_id = str(uuid.uuid4())
        
        with patch('api.routes.workloads.WorkloadManager') as mock_manager:
            mock_instance = Mock()
            mock_instance.schedule_workload.return_value = {"scheduled": True}
            mock_manager.return_value = mock_instance
            
            # Act
            response = client.post(
                f"/api/v1/workloads/{workload_id}/schedule",
                headers=auth_headers
            )
            
            # Assert
            assert response.status_code == 200


class TestContainerEndpoints:
    """Test suite for container management endpoints"""
    
    def test_list_containers_success(self, client, auth_headers):
        """Test successful container listing"""
        # Arrange
        mock_containers = [
            {"id": "abc123", "name": "container1", "status": "running"},
            {"id": "def456", "name": "container2", "status": "stopped"}
        ]
        
        with patch('api.routes.containers.ContainerOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.list_containers.return_value = mock_containers
            mock_orch.return_value = mock_instance
            
            # Act
            response = client.get("/api/v1/containers", headers=auth_headers)
            
            # Assert
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_start_container_success(self, client, auth_headers):
        """Test successful container start"""
        # Arrange
        container_id = "abc123"
        
        with patch('api.routes.containers.ContainerOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.start_container.return_value = True
            mock_orch.return_value = mock_instance
            
            # Act
            response = client.post(
                f"/api/v1/containers/{container_id}/start",
                headers=auth_headers
            )
            
            # Assert
            assert response.status_code == 200
    
    def test_stop_container_success(self, client, auth_headers):
        """Test successful container stop"""
        # Arrange
        container_id = "abc123"
        
        with patch('api.routes.containers.ContainerOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.stop_container.return_value = True
            mock_orch.return_value = mock_instance
            
            # Act
            response = client.post(
                f"/api/v1/containers/{container_id}/stop",
                headers=auth_headers
            )
            
            # Assert
            assert response.status_code == 200


class TestSubsystemEndpoints:
    """Test suite for subsystem monitoring endpoints"""
    
    def test_get_subsystem_status_success(self, client, auth_headers):
        """Test successful subsystem status retrieval"""
        # Arrange
        subsystem = "jes"
        mock_status = {
            "subsystem": "jes",
            "status": "active",
            "uptime": 3600,
            "active_jobs": 5
        }
        
        with patch('api.routes.subsystems.get_subsystem_status') as mock_status_func:
            mock_status_func.return_value = mock_status
            
            # Act
            response = client.get(f"/api/v1/subsystems/{subsystem}", headers=auth_headers)
            
            # Assert
            assert response.status_code == 200
            assert response.json()["subsystem"] == subsystem
    
    def test_get_subsystem_status_invalid(self, client, auth_headers):
        """Test subsystem status with invalid subsystem"""
        # Act
        response = client.get("/api/v1/subsystems/invalid", headers=auth_headers)
        
        # Assert
        assert response.status_code == 404


class TestMetricsEndpoints:
    """Test suite for metrics endpoints"""
    
    def test_get_system_metrics_success(self, client, auth_headers):
        """Test successful system metrics retrieval"""
        # Arrange
        mock_metrics = {
            "cpu": {"current": 45.5, "average": 42.0},
            "memory": {"current": 60.0, "average": 58.5},
            "disk": {"usage": 70.0},
            "network": {"throughput": 125.5}
        }
        
        with patch('api.routes.metrics.get_system_metrics') as mock_metrics_func:
            mock_metrics_func.return_value = mock_metrics
            
            # Act
            response = client.get("/api/v1/metrics", headers=auth_headers)
            
            # Assert
            assert response.status_code == 200
            assert "cpu" in response.json()
            assert "memory" in response.json()
