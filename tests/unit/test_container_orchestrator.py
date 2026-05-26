"""
ZenithOne Explorer - Container Orchestrator Unit Tests
Tests for container management functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid


class TestContainerOrchestrator:
    """Test suite for ContainerOrchestrator class"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create ContainerOrchestrator instance for testing"""
        with patch('core.container_orchestrator.subprocess'):
            from core.container_orchestrator import ContainerOrchestrator
            return ContainerOrchestrator()
    
    def test_create_container_success(self, orchestrator, sample_container):
        """Test successful container creation"""
        # Arrange
        mock_result = Mock()
        mock_result.stdout = "container123\n"
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.create_container(sample_container)
            
            # Assert
            assert result is not None
            assert 'id' in result
            assert result['name'] == sample_container['name']
            assert result['status'] == 'created'
    
    def test_create_container_missing_image(self, orchestrator):
        """Test container creation with missing image"""
        # Arrange
        invalid_container = {"name": "test"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Image is required"):
            orchestrator.create_container(invalid_container)
    
    def test_start_container_success(self, orchestrator):
        """Test successful container start"""
        # Arrange
        container_id = "container123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.start_container(container_id)
            
            # Assert
            assert result is True
    
    def test_start_container_failure(self, orchestrator):
        """Test container start failure"""
        # Arrange
        container_id = "container123"
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error starting container"
        
        with patch('subprocess.run', return_value=mock_result):
            # Act & Assert
            with pytest.raises(RuntimeError, match="Failed to start container"):
                orchestrator.start_container(container_id)
    
    def test_stop_container_success(self, orchestrator):
        """Test successful container stop"""
        # Arrange
        container_id = "container123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.stop_container(container_id)
            
            # Assert
            assert result is True
    
    def test_restart_container_success(self, orchestrator):
        """Test successful container restart"""
        # Arrange
        container_id = "container123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.restart_container(container_id)
            
            # Assert
            assert result is True
    
    def test_pause_container_success(self, orchestrator):
        """Test successful container pause"""
        # Arrange
        container_id = "container123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.pause_container(container_id)
            
            # Assert
            assert result is True
    
    def test_unpause_container_success(self, orchestrator):
        """Test successful container unpause"""
        # Arrange
        container_id = "container123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.unpause_container(container_id)
            
            # Assert
            assert result is True
    
    def test_list_containers_all(self, orchestrator):
        """Test listing all containers"""
        # Arrange
        mock_output = """[
            {"Id": "abc123", "Names": ["test1"], "State": "running", "Image": "alpine"},
            {"Id": "def456", "Names": ["test2"], "State": "stopped", "Image": "ubuntu"}
        ]"""
        mock_result = Mock()
        mock_result.stdout = mock_output
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.list_containers()
            
            # Assert
            assert len(result) == 2
            assert result[0]['id'] == 'abc123'
            assert result[1]['id'] == 'def456'
    
    def test_list_containers_running_only(self, orchestrator):
        """Test listing only running containers"""
        # Arrange
        mock_output = """[
            {"Id": "abc123", "Names": ["test1"], "State": "running", "Image": "alpine"}
        ]"""
        mock_result = Mock()
        mock_result.stdout = mock_output
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.list_containers(status='running')
            
            # Assert
            assert len(result) == 1
            assert result[0]['status'] == 'running'
    
    def test_get_container_success(self, orchestrator):
        """Test successful container retrieval"""
        # Arrange
        container_id = "abc123"
        mock_output = """[{
            "Id": "abc123",
            "Name": "test-container",
            "State": {"Status": "running"},
            "Config": {"Image": "alpine"}
        }]"""
        mock_result = Mock()
        mock_result.stdout = mock_output
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.get_container(container_id)
            
            # Assert
            assert result is not None
            assert result['id'] == container_id
    
    def test_get_container_not_found(self, orchestrator):
        """Test container retrieval when container doesn't exist"""
        # Arrange
        container_id = "nonexistent"
        mock_result = Mock()
        mock_result.stdout = "[]"
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act & Assert
            with pytest.raises(ValueError, match="Container not found"):
                orchestrator.get_container(container_id)
    
    def test_delete_container_success(self, orchestrator):
        """Test successful container deletion"""
        # Arrange
        container_id = "abc123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.delete_container(container_id)
            
            # Assert
            assert result is True
    
    def test_delete_container_force(self, orchestrator):
        """Test forced container deletion"""
        # Arrange
        container_id = "abc123"
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.delete_container(container_id, force=True)
            
            # Assert
            assert result is True
    
    def test_get_container_logs(self, orchestrator):
        """Test retrieving container logs"""
        # Arrange
        container_id = "abc123"
        mock_logs = "Log line 1\nLog line 2\nLog line 3"
        mock_result = Mock()
        mock_result.stdout = mock_logs
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.get_container_logs(container_id)
            
            # Assert
            assert result == mock_logs
    
    def test_get_container_logs_with_tail(self, orchestrator):
        """Test retrieving container logs with tail limit"""
        # Arrange
        container_id = "abc123"
        mock_logs = "Log line 1\nLog line 2"
        mock_result = Mock()
        mock_result.stdout = mock_logs
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            # Act
            result = orchestrator.get_container_logs(container_id, tail=100)
            
            # Assert
            assert result == mock_logs
            # Verify tail parameter was passed
            call_args = mock_run.call_args[0][0]
            assert '--tail' in call_args
            assert '100' in call_args
    
    def test_inspect_container(self, orchestrator):
        """Test container inspection"""
        # Arrange
        container_id = "abc123"
        mock_inspect = {
            "Id": "abc123",
            "State": {"Status": "running"},
            "Config": {"Image": "alpine"}
        }
        mock_result = Mock()
        mock_result.stdout = str(mock_inspect)
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.inspect_container(container_id)
            
            # Assert
            assert result is not None
    
    def test_get_container_stats(self, orchestrator):
        """Test retrieving container statistics"""
        # Arrange
        container_id = "abc123"
        mock_stats = {
            "cpu_percent": 25.5,
            "memory_usage": 512000000,
            "memory_limit": 1024000000
        }
        mock_result = Mock()
        mock_result.stdout = str(mock_stats)
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            # Act
            result = orchestrator.get_container_stats(container_id)
            
            # Assert
            assert result is not None
