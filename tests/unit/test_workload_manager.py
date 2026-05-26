"""
ZenithOne Explorer - Workload Manager Unit Tests
Tests for core workload management functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid


class TestWorkloadManager:
    """Test suite for WorkloadManager class"""
    
    @pytest.fixture
    def workload_manager(self):
        """Create WorkloadManager instance for testing"""
        with patch('core.workload_manager.get_db'):
            from core.workload_manager import WorkloadManager
            return WorkloadManager()
    
    def test_create_workload_success(self, workload_manager, sample_workload):
        """Test successful workload creation"""
        # Arrange
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(lastrowid=1))
        
        # Act
        result = workload_manager.create_workload(sample_workload)
        
        # Assert
        assert result is not None
        assert 'id' in result
        assert result['name'] == sample_workload['name']
        assert result['status'] == 'pending'
        workload_manager.db.execute.assert_called_once()
    
    def test_create_workload_missing_required_fields(self, workload_manager):
        """Test workload creation with missing required fields"""
        # Arrange
        invalid_workload = {"name": "test"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required field"):
            workload_manager.create_workload(invalid_workload)
    
    def test_create_workload_invalid_type(self, workload_manager, sample_workload):
        """Test workload creation with invalid type"""
        # Arrange
        sample_workload['type'] = 'invalid_type'
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid workload type"):
            workload_manager.create_workload(sample_workload)
    
    def test_get_workload_success(self, workload_manager):
        """Test successful workload retrieval"""
        # Arrange
        workload_id = str(uuid.uuid4())
        mock_workload = {
            'id': workload_id,
            'name': 'test-workload',
            'status': 'running'
        }
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(fetchone=Mock(return_value=mock_workload)))
        
        # Act
        result = workload_manager.get_workload(workload_id)
        
        # Assert
        assert result is not None
        assert result['id'] == workload_id
        assert result['name'] == 'test-workload'
    
    def test_get_workload_not_found(self, workload_manager):
        """Test workload retrieval when workload doesn't exist"""
        # Arrange
        workload_id = str(uuid.uuid4())
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(fetchone=Mock(return_value=None)))
        
        # Act & Assert
        with pytest.raises(ValueError, match="Workload not found"):
            workload_manager.get_workload(workload_id)
    
    def test_list_workloads_no_filters(self, workload_manager):
        """Test listing all workloads without filters"""
        # Arrange
        mock_workloads = [
            {'id': '1', 'name': 'workload1', 'status': 'running'},
            {'id': '2', 'name': 'workload2', 'status': 'pending'}
        ]
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(fetchall=Mock(return_value=mock_workloads)))
        
        # Act
        result = workload_manager.list_workloads()
        
        # Assert
        assert len(result) == 2
        assert result[0]['name'] == 'workload1'
        assert result[1]['name'] == 'workload2'
    
    def test_list_workloads_with_status_filter(self, workload_manager):
        """Test listing workloads with status filter"""
        # Arrange
        mock_workloads = [
            {'id': '1', 'name': 'workload1', 'status': 'running'}
        ]
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(fetchall=Mock(return_value=mock_workloads)))
        
        # Act
        result = workload_manager.list_workloads(status='running')
        
        # Assert
        assert len(result) == 1
        assert result[0]['status'] == 'running'
    
    def test_update_workload_status(self, workload_manager):
        """Test updating workload status"""
        # Arrange
        workload_id = str(uuid.uuid4())
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock()
        
        # Act
        workload_manager.update_workload_status(workload_id, 'running')
        
        # Assert
        workload_manager.db.execute.assert_called_once()
        call_args = workload_manager.db.execute.call_args[0][0]
        assert 'UPDATE' in call_args
        assert 'status' in call_args
    
    def test_delete_workload_success(self, workload_manager):
        """Test successful workload deletion"""
        # Arrange
        workload_id = str(uuid.uuid4())
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(rowcount=1))
        
        # Act
        result = workload_manager.delete_workload(workload_id)
        
        # Assert
        assert result is True
        workload_manager.db.execute.assert_called_once()
    
    def test_delete_workload_not_found(self, workload_manager):
        """Test workload deletion when workload doesn't exist"""
        # Arrange
        workload_id = str(uuid.uuid4())
        workload_manager.db = Mock()
        workload_manager.db.execute = Mock(return_value=Mock(rowcount=0))
        
        # Act & Assert
        with pytest.raises(ValueError, match="Workload not found"):
            workload_manager.delete_workload(workload_id)
    
    @pytest.mark.slow
    def test_schedule_workload_with_ai(self, workload_manager, mock_ollama):
        """Test AI-enhanced workload scheduling"""
        # Arrange
        workload_id = str(uuid.uuid4())
        workload_manager.ai_service = mock_ollama
        workload_manager.db = Mock()
        
        # Act
        result = workload_manager.schedule_workload(workload_id, use_ai=True)
        
        # Assert
        assert result is not None
        assert 'scheduled_at' in result
    
    def test_get_workload_logs(self, workload_manager):
        """Test retrieving workload logs"""
        # Arrange
        workload_id = str(uuid.uuid4())
        mock_logs = "Test log output\nLine 2\nLine 3"
        workload_manager.db = Mock()
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = mock_logs
            
            # Act
            result = workload_manager.get_workload_logs(workload_id)
            
            # Assert
            assert result == mock_logs
    
    def test_validate_workload_config(self, workload_manager, sample_workload):
        """Test workload configuration validation"""
        # Act
        result = workload_manager.validate_workload_config(sample_workload)
        
        # Assert
        assert result is True
    
    def test_validate_workload_config_invalid_cpu(self, workload_manager, sample_workload):
        """Test workload validation with invalid CPU limit"""
        # Arrange
        sample_workload['cpu_limit'] = -1
        
        # Act & Assert
        with pytest.raises(ValueError, match="CPU limit must be positive"):
            workload_manager.validate_workload_config(sample_workload)
    
    def test_validate_workload_config_invalid_memory(self, workload_manager, sample_workload):
        """Test workload validation with invalid memory limit"""
        # Arrange
        sample_workload['memory_limit'] = 0
        
        # Act & Assert
        with pytest.raises(ValueError, match="Memory limit must be positive"):
            workload_manager.validate_workload_config(sample_workload)
