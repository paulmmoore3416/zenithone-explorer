"""
ZenithOne Explorer - JES (Job Entry Subsystem) Simulator
Simulates mainframe JES functionality for job management
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database.models import Subsystem, Workload
from config import settings
from utils.logger import get_logger

logger = get_logger("jes")


class JESSimulator:
    """
    Simulates IBM z/OS Job Entry Subsystem (JES).
    Handles job submission, scheduling, and spool management.
    """
    
    def __init__(self):
        self.name = "JES"
        self.version = "1.0.0"
        self.status = "inactive"
        self.max_jobs = settings.jes_max_jobs
        self.spool_size = settings.jes_spool_size
        self.spool_used = 0
        
        # Statistics
        self.stats = {
            "jobs_submitted": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_cancelled": 0,
            "spool_usage_percent": 0.0,
            "avg_job_duration": 0.0
        }
        
        logger.info(f"JES Simulator initialized (max jobs: {self.max_jobs})")
    
    async def start(self, db: Session) -> bool:
        """
        Start JES subsystem.
        
        Args:
            db: Database session
            
        Returns:
            True if started successfully
        """
        try:
            self.status = "active"
            
            # Update database
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            if subsystem:
                subsystem.status = "active"
                subsystem.last_started = datetime.utcnow()
                subsystem.uptime = 0
                db.commit()
            
            logger.info("JES subsystem started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting JES: {e}")
            self.status = "error"
            return False
    
    async def stop(self, db: Session) -> bool:
        """
        Stop JES subsystem.
        
        Args:
            db: Database session
            
        Returns:
            True if stopped successfully
        """
        try:
            self.status = "inactive"
            
            # Update database
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            if subsystem:
                subsystem.status = "inactive"
                subsystem.last_stopped = datetime.utcnow()
                db.commit()
            
            logger.info("JES subsystem stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping JES: {e}")
            return False
    
    async def submit_job(
        self,
        db: Session,
        job_name: str,
        jcl: str,
        priority: str = "medium"
    ) -> Optional[str]:
        """
        Submit a job to JES.
        
        Args:
            db: Database session
            job_name: Job name
            jcl: Job Control Language (simplified)
            priority: Job priority
            
        Returns:
            Job ID if submitted successfully
        """
        try:
            if self.status != "active":
                logger.error("JES is not active")
                return None
            
            # Check job limit
            active_jobs = db.query(Workload).filter(
                Workload.subsystem == "JES",
                Workload.status.in_(["pending", "running"])
            ).count()
            
            if active_jobs >= self.max_jobs:
                logger.warning(f"JES job limit reached ({self.max_jobs})")
                return None
            
            # Parse JCL (simplified)
            job_info = self._parse_jcl(jcl)
            
            # Update statistics
            self.stats["jobs_submitted"] += 1
            await self._update_statistics(db)
            
            logger.info(f"Job {job_name} submitted to JES")
            return job_info.get("job_id")
            
        except Exception as e:
            logger.error(f"Error submitting job: {e}")
            return None
    
    def _parse_jcl(self, jcl: str) -> Dict[str, Any]:
        """
        Parse JCL (simplified).
        
        Args:
            jcl: Job Control Language
            
        Returns:
            Parsed job information
        """
        # Simplified JCL parsing
        # In real JES, this would be much more complex
        
        import uuid
        job_id = f"JOB{str(uuid.uuid4())[:8].upper()}"
        
        return {
            "job_id": job_id,
            "jcl": jcl,
            "steps": [],
            "estimated_time": 60  # seconds
        }
    
    async def get_job_status(
        self,
        db: Session,
        job_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get job status.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            Job status information
        """
        try:
            workload = db.query(Workload).filter(
                Workload.id == job_id,
                Workload.subsystem == "JES"
            ).first()
            
            if not workload:
                return None
            
            return {
                "job_id": workload.id,
                "name": workload.name,
                "status": workload.status,
                "priority": workload.priority,
                "submitted": workload.created_at.isoformat(),
                "started": workload.started_at.isoformat() if workload.started_at else None,
                "completed": workload.completed_at.isoformat() if workload.completed_at else None,
                "duration": workload.duration,
                "exit_code": workload.exit_code
            }
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return None
    
    async def cancel_job(self, db: Session, job_id: str) -> bool:
        """
        Cancel a job.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            workload = db.query(Workload).filter(
                Workload.id == job_id,
                Workload.subsystem == "JES"
            ).first()
            
            if not workload:
                return False
            
            if workload.status in ["completed", "failed", "cancelled"]:
                logger.warning(f"Job {job_id} already finished")
                return False
            
            workload.status = "cancelled"
            workload.completed_at = datetime.utcnow()
            db.commit()
            
            # Update statistics
            self.stats["jobs_cancelled"] += 1
            await self._update_statistics(db)
            
            logger.info(f"Job {job_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling job: {e}")
            return False
    
    async def get_spool_info(self, db: Session) -> Dict[str, Any]:
        """
        Get spool information.
        
        Args:
            db: Database session
            
        Returns:
            Spool information
        """
        try:
            # Calculate spool usage (simplified)
            active_jobs = db.query(Workload).filter(
                Workload.subsystem == "JES",
                Workload.status.in_(["pending", "running", "completed"])
            ).count()
            
            # Estimate spool usage
            self.spool_used = active_jobs * 1024 * 1024  # 1MB per job (simplified)
            spool_percent = (self.spool_used / self.spool_size) * 100
            
            return {
                "total": self.spool_size,
                "used": self.spool_used,
                "free": self.spool_size - self.spool_used,
                "percent": round(spool_percent, 2),
                "active_jobs": active_jobs
            }
            
        except Exception as e:
            logger.error(f"Error getting spool info: {e}")
            return {}
    
    async def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get JES statistics.
        
        Args:
            db: Database session
            
        Returns:
            JES statistics
        """
        try:
            # Update statistics from database
            completed_jobs = db.query(Workload).filter(
                Workload.subsystem == "JES",
                Workload.status == "completed"
            ).all()
            
            if completed_jobs:
                total_duration = sum(job.duration or 0 for job in completed_jobs)
                self.stats["avg_job_duration"] = total_duration / len(completed_jobs)
            
            self.stats["jobs_completed"] = len(completed_jobs)
            
            failed_jobs = db.query(Workload).filter(
                Workload.subsystem == "JES",
                Workload.status == "failed"
            ).count()
            
            self.stats["jobs_failed"] = failed_jobs
            
            # Spool usage
            spool_info = await self.get_spool_info(db)
            self.stats["spool_usage_percent"] = spool_info.get("percent", 0.0)
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return self.stats
    
    async def _update_statistics(self, db: Session):
        """
        Update statistics in database.
        
        Args:
            db: Database session
        """
        try:
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            if subsystem:
                subsystem.statistics = json.dumps(self.stats)
                db.commit()
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    async def get_status(self, db: Session) -> Dict[str, Any]:
        """
        Get JES status.
        
        Args:
            db: Database session
            
        Returns:
            JES status information
        """
        try:
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            
            uptime = 0
            if subsystem and subsystem.last_started:
                uptime = int((datetime.utcnow() - subsystem.last_started).total_seconds())
            
            stats = await self.get_statistics(db)
            spool = await self.get_spool_info(db)
            
            return {
                "name": self.name,
                "version": self.version,
                "status": self.status,
                "uptime": uptime,
                "configuration": {
                    "max_jobs": self.max_jobs,
                    "spool_size": self.spool_size
                },
                "statistics": stats,
                "spool": spool
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "name": self.name,
                "status": "error",
                "error": str(e)
            }


# Global JES simulator instance
jes_simulator = JESSimulator()
