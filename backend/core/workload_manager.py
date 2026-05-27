"""
ZenithOne Explorer - Workload Manager
AI-enhanced job scheduling and resource management using Qwen2.5
"""
import asyncio
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from queue import PriorityQueue
from sqlalchemy.orm import Session

from database.models import Workload, WorkloadLog, WorkloadMetric
from config import settings
from utils.logger import get_logger

logger = get_logger("workload_manager")


class WorkloadManager:
    """
    Manages workload scheduling, execution, and monitoring.
    Uses AI-enhanced scheduling with Qwen2.5 for optimization.
    """
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.running_workloads: Dict[str, asyncio.Task] = {}
        self.max_concurrent = settings.workload_max_concurrent
        self.ai_enabled = settings.ai_enabled
        
        # Priority mapping
        self.priority_map = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }
        
        logger.info(f"Workload Manager initialized (max concurrent: {self.max_concurrent})")
    
    async def submit_workload(
        self,
        db: Session,
        workload: Workload
    ) -> Workload:
        """
        Submit a new workload for execution.
        
        Args:
            db: Database session
            workload: Workload object
            
        Returns:
            Created workload
        """
        try:
            # Set initial status
            workload.status = "pending"
            
            # AI-enhanced priority optimization
            if self.ai_enabled:
                workload.priority = await self._optimize_priority(workload)
            
            # Add to database
            db.add(workload)
            db.commit()
            db.refresh(workload)
            
            # Add to queue
            priority = self.priority_map.get(workload.priority, 2)
            self.queue.put((priority, workload.id, workload))
            
            # Log submission
            self._log_workload(db, workload.id, "INFO", f"Workload submitted: {workload.name}")
            
            logger.info(f"Workload {workload.id} submitted (priority: {workload.priority})")
            
            # Start processing if capacity available
            await self._process_queue(db)
            
            return workload
            
        except Exception as e:
            logger.error(f"Error submitting workload: {e}")
            raise
    
    async def _optimize_priority(self, workload: Workload) -> str:
        """
        Use Qwen2.5 to optimize workload priority based on context.
        
        Args:
            workload: Workload to optimize
            
        Returns:
            Optimized priority level
        """
        try:
            # In production, this would call Ollama with Qwen2.5
            # For now, use rule-based optimization
            
            # Critical workloads
            if workload.type == "transaction" and "urgent" in workload.name.lower():
                return "critical"
            
            # High priority for interactive workloads
            if workload.type == "interactive":
                return "high"
            
            # Default to specified priority
            return workload.priority
            
        except Exception as e:
            logger.warning(f"AI optimization failed, using default priority: {e}")
            return workload.priority
    
    async def _process_queue(self, db: Session):
        """
        Process workloads from the queue.
        
        Args:
            db: Database session
        """
        while len(self.running_workloads) < self.max_concurrent and not self.queue.empty():
            try:
                priority, workload_id, workload = self.queue.get_nowait()
                
                # Update status
                workload.status = "running"
                workload.started_at = datetime.utcnow()
                db.commit()
                
                # Create execution task
                task = asyncio.create_task(self._execute_workload(db, workload))
                self.running_workloads[workload_id] = task
                
                logger.info(f"Started workload {workload_id}")
                
            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                break
    
    async def _execute_workload(self, db: Session, workload: Workload):
        """
        Execute a workload.
        
        Args:
            db: Database session
            workload: Workload to execute
        """
        start_time = datetime.utcnow()
        
        try:
            self._log_workload(db, workload.id, "INFO", "Execution started")
            
            # Parse parameters
            params = json.loads(workload.parameters) if workload.parameters else {}
            resources = json.loads(workload.resources) if workload.resources else {}
            
            # Get timeout
            timeout = resources.get("timeout", settings.workload_default_timeout)
            
            # Execute based on subsystem
            if workload.subsystem == "JES":
                await self._execute_jes_job(db, workload, params, timeout)
            elif workload.subsystem == "CICS":
                await self._execute_cics_transaction(db, workload, params, timeout)
            elif workload.subsystem == "TSO":
                await self._execute_tso_command(db, workload, params, timeout)
            else:
                raise ValueError(f"Unknown subsystem: {workload.subsystem}")
            
            # Update completion status
            workload.status = "completed"
            workload.completed_at = datetime.utcnow()
            workload.duration = int((workload.completed_at - workload.started_at).total_seconds())
            workload.exit_code = 0
            
            self._log_workload(db, workload.id, "INFO", f"Execution completed (duration: {workload.duration}s)")
            
        except asyncio.TimeoutError:
            workload.status = "failed"
            workload.error_message = "Execution timeout"
            workload.exit_code = 124
            self._log_workload(db, workload.id, "ERROR", "Execution timeout")
            
        except Exception as e:
            workload.status = "failed"
            workload.error_message = str(e)
            workload.exit_code = 1
            self._log_workload(db, workload.id, "ERROR", f"Execution failed: {e}")
            logger.error(f"Workload {workload.id} failed: {e}")
            
        finally:
            # Update database
            workload.completed_at = datetime.utcnow()
            if workload.started_at:
                workload.duration = int((workload.completed_at - workload.started_at).total_seconds())
            db.commit()
            
            # Remove from running workloads
            if workload.id in self.running_workloads:
                del self.running_workloads[workload.id]
            
            # Process next workload
            await self._process_queue(db)
    
    async def _execute_jes_job(
        self,
        db: Session,
        workload: Workload,
        params: Dict[str, Any],
        timeout: int
    ):
        """Execute JES job."""
        self._log_workload(db, workload.id, "INFO", "JES job processing started")
        
        # Simulate job execution
        await asyncio.sleep(2)  # Simulate processing time
        
        # Collect metrics
        self._record_metric(db, workload.id, cpu_usage=25.5, memory_usage=256)
        
        self._log_workload(db, workload.id, "INFO", "JES job processing completed")
    
    async def _execute_cics_transaction(
        self,
        db: Session,
        workload: Workload,
        params: Dict[str, Any],
        timeout: int
    ):
        """Execute CICS transaction."""
        self._log_workload(db, workload.id, "INFO", "CICS transaction started")
        
        # Simulate transaction processing
        await asyncio.sleep(1)
        
        # Collect metrics
        self._record_metric(db, workload.id, cpu_usage=15.2, memory_usage=128)
        
        self._log_workload(db, workload.id, "INFO", "CICS transaction completed")
    
    async def _execute_tso_command(
        self,
        db: Session,
        workload: Workload,
        params: Dict[str, Any],
        timeout: int
    ):
        """Execute TSO command."""
        self._log_workload(db, workload.id, "INFO", f"TSO command: {workload.command}")
        
        # Simulate command execution
        await asyncio.sleep(0.5)
        
        # Collect metrics
        self._record_metric(db, workload.id, cpu_usage=10.0, memory_usage=64)
        
        self._log_workload(db, workload.id, "INFO", "TSO command completed")
    
    def _log_workload(
        self,
        db: Session,
        workload_id: str,
        level: str,
        message: str
    ):
        """Add log entry for workload."""
        log = WorkloadLog(
            workload_id=workload_id,
            level=level,
            message=message,
            source="workload_manager"
        )
        db.add(log)
        db.commit()
    
    def _record_metric(
        self,
        db: Session,
        workload_id: str,
        cpu_usage: float = 0.0,
        memory_usage: int = 0
    ):
        """Record workload metrics."""
        metric = WorkloadMetric(
            workload_id=workload_id,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage
        )
        db.add(metric)
        db.commit()
    
    async def cancel_workload(self, db: Session, workload_id: str) -> bool:
        """
        Cancel a running workload.
        
        Args:
            db: Database session
            workload_id: Workload ID to cancel
            
        Returns:
            True if cancelled, False otherwise
        """
        try:
            # Check if running
            if workload_id in self.running_workloads:
                task = self.running_workloads[workload_id]
                task.cancel()
                
                # Update status
                workload = db.query(Workload).filter(Workload.id == workload_id).first()
                if workload:
                    workload.status = "cancelled"
                    workload.completed_at = datetime.utcnow()
                    db.commit()
                    
                    self._log_workload(db, workload_id, "WARNING", "Workload cancelled by user")
                
                logger.info(f"Workload {workload_id} cancelled")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling workload: {e}")
            return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status.
        
        Returns:
            Queue status information
        """
        return {
            "queued": self.queue.qsize(),
            "running": len(self.running_workloads),
            "capacity": self.max_concurrent,
            "available": self.max_concurrent - len(self.running_workloads)
        }


# Global workload manager instance
workload_manager = WorkloadManager()
