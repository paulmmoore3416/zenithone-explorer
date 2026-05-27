"""
ZenithOne Explorer - TSO (Time Sharing Option) Simulator
Simulates mainframe TSO interactive command processing
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database.models import Subsystem
from config import settings
from utils.logger import get_logger

logger = get_logger("tso")


class TSOSimulator:
    """
    Simulates IBM z/OS TSO (Time Sharing Option).
    Provides interactive command processing and session management.
    """
    
    def __init__(self):
        self.name = "TSO"
        self.version = "1.0.0"
        self.status = "inactive"
        self.max_sessions = settings.tso_max_sessions
        self.timeout = settings.tso_timeout
        
        # Active sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Command history
        self.command_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Statistics
        self.stats = {
            "sessions_created": 0,
            "sessions_closed": 0,
            "active_sessions": 0,
            "commands_executed": 0,
            "commands_failed": 0,
            "avg_command_time": 0.0
        }
        
        # Available commands
        self.commands = {
            "LISTCAT": self._cmd_listcat,
            "LISTDS": self._cmd_listds,
            "SUBMIT": self._cmd_submit,
            "STATUS": self._cmd_status,
            "CANCEL": self._cmd_cancel,
            "ALLOCATE": self._cmd_allocate,
            "DELETE": self._cmd_delete,
            "RENAME": self._cmd_rename,
            "HELP": self._cmd_help,
            "TIME": self._cmd_time,
            "LOGOFF": self._cmd_logoff
        }
        
        logger.info(f"TSO Simulator initialized (max sessions: {self.max_sessions})")
    
    async def start(self, db: Session) -> bool:
        """
        Start TSO subsystem.
        
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
            
            logger.info("TSO subsystem started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting TSO: {e}")
            self.status = "error"
            return False
    
    async def stop(self, db: Session) -> bool:
        """
        Stop TSO subsystem.
        
        Args:
            db: Database session
            
        Returns:
            True if stopped successfully
        """
        try:
            self.status = "inactive"
            
            # Close all sessions
            self.sessions.clear()
            self.command_history.clear()
            
            # Update database
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            if subsystem:
                subsystem.status = "inactive"
                subsystem.last_stopped = datetime.utcnow()
                db.commit()
            
            logger.info("TSO subsystem stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping TSO: {e}")
            return False
    
    async def create_session(self, user_id: str) -> Optional[str]:
        """
        Create a new TSO session.
        
        Args:
            user_id: User ID
            
        Returns:
            Session ID if created successfully
        """
        try:
            if self.status != "active":
                logger.error("TSO is not active")
                return None
            
            # Check session limit
            if len(self.sessions) >= self.max_sessions:
                logger.warning(f"TSO session limit reached ({self.max_sessions})")
                return None
            
            session_id = str(uuid.uuid4())
            
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "commands_executed": 0,
                "current_dataset": None
            }
            
            self.command_history[session_id] = []
            
            self.stats["sessions_created"] += 1
            self.stats["active_sessions"] = len(self.sessions)
            
            logger.info(f"TSO session {session_id} created for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close a TSO session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if closed successfully
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                if session_id in self.command_history:
                    del self.command_history[session_id]
                
                self.stats["sessions_closed"] += 1
                self.stats["active_sessions"] = len(self.sessions)
                
                logger.info(f"TSO session {session_id} closed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing session: {e}")
            return False
    
    async def execute_command(
        self,
        db: Session,
        session_id: str,
        command: str
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a TSO command.
        
        Args:
            db: Database session
            session_id: Session ID
            command: Command to execute
            
        Returns:
            Command result
        """
        try:
            if self.status != "active":
                logger.error("TSO is not active")
                return None
            
            if session_id not in self.sessions:
                logger.error(f"Invalid session: {session_id}")
                return None
            
            start_time = datetime.utcnow()
            
            # Parse command
            parts = command.strip().upper().split()
            if not parts:
                return {"status": "error", "message": "Empty command"}
            
            cmd_name = parts[0]
            cmd_args = parts[1:] if len(parts) > 1 else []
            
            # Execute command
            if cmd_name in self.commands:
                result = await self.commands[cmd_name](session_id, cmd_args)
            else:
                result = {
                    "status": "error",
                    "message": f"Unknown command: {cmd_name}",
                    "suggestion": "Type HELP for available commands"
                }
                self.stats["commands_failed"] += 1
            
            # Calculate execution time
            end_time = datetime.utcnow()
            exec_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            # Update statistics
            if result.get("status") == "success":
                self.stats["commands_executed"] += 1
                
                # Update average command time
                total_commands = self.stats["commands_executed"]
                current_avg = self.stats["avg_command_time"]
                self.stats["avg_command_time"] = (
                    (current_avg * (total_commands - 1) + exec_time) / total_commands
                )
            
            # Update session
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            self.sessions[session_id]["commands_executed"] += 1
            
            # Add to command history
            self.command_history[session_id].append({
                "command": command,
                "timestamp": datetime.utcnow().isoformat(),
                "result": result.get("status"),
                "exec_time": exec_time
            })
            
            # Keep only last 100 commands
            if len(self.command_history[session_id]) > 100:
                self.command_history[session_id] = self.command_history[session_id][-100:]
            
            await self._update_statistics(db)
            
            logger.info(f"TSO command executed: {cmd_name} ({exec_time:.2f}ms)")
            
            result["exec_time"] = exec_time
            return result
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            self.stats["commands_failed"] += 1
            return {
                "status": "error",
                "message": str(e)
            }
    
    # Command implementations
    
    async def _cmd_listcat(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """List catalog entries."""
        return {
            "status": "success",
            "message": "Catalog listing",
            "output": [
                "DATASET.NAME.ONE",
                "DATASET.NAME.TWO",
                "DATASET.NAME.THREE"
            ]
        }
    
    async def _cmd_listds(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """List dataset information."""
        if not args:
            return {"status": "error", "message": "Dataset name required"}
        
        dataset = args[0]
        return {
            "status": "success",
            "message": f"Dataset information for {dataset}",
            "output": {
                "name": dataset,
                "type": "PS",
                "records": 1000,
                "size": "100KB",
                "created": "2026-05-26"
            }
        }
    
    async def _cmd_submit(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Submit a job."""
        if not args:
            return {"status": "error", "message": "Job name required"}
        
        job_name = args[0]
        job_id = f"JOB{str(uuid.uuid4())[:5].upper()}"
        
        return {
            "status": "success",
            "message": f"Job {job_name} submitted",
            "output": {
                "job_id": job_id,
                "job_name": job_name,
                "status": "submitted"
            }
        }
    
    async def _cmd_status(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Check job status."""
        if not args:
            return {"status": "error", "message": "Job ID required"}
        
        job_id = args[0]
        return {
            "status": "success",
            "message": f"Status for job {job_id}",
            "output": {
                "job_id": job_id,
                "status": "running",
                "progress": "50%"
            }
        }
    
    async def _cmd_cancel(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Cancel a job."""
        if not args:
            return {"status": "error", "message": "Job ID required"}
        
        job_id = args[0]
        return {
            "status": "success",
            "message": f"Job {job_id} cancelled"
        }
    
    async def _cmd_allocate(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Allocate a dataset."""
        if not args:
            return {"status": "error", "message": "Dataset name required"}
        
        dataset = args[0]
        return {
            "status": "success",
            "message": f"Dataset {dataset} allocated"
        }
    
    async def _cmd_delete(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Delete a dataset."""
        if not args:
            return {"status": "error", "message": "Dataset name required"}
        
        dataset = args[0]
        return {
            "status": "success",
            "message": f"Dataset {dataset} deleted"
        }
    
    async def _cmd_rename(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Rename a dataset."""
        if len(args) < 2:
            return {"status": "error", "message": "Old and new names required"}
        
        old_name = args[0]
        new_name = args[1]
        return {
            "status": "success",
            "message": f"Dataset {old_name} renamed to {new_name}"
        }
    
    async def _cmd_help(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Display help."""
        return {
            "status": "success",
            "message": "Available TSO commands",
            "output": {
                "commands": list(self.commands.keys()),
                "description": {
                    "LISTCAT": "List catalog entries",
                    "LISTDS": "List dataset information",
                    "SUBMIT": "Submit a job",
                    "STATUS": "Check job status",
                    "CANCEL": "Cancel a job",
                    "ALLOCATE": "Allocate a dataset",
                    "DELETE": "Delete a dataset",
                    "RENAME": "Rename a dataset",
                    "HELP": "Display this help",
                    "TIME": "Display current time",
                    "LOGOFF": "End TSO session"
                }
            }
        }
    
    async def _cmd_time(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Display current time."""
        return {
            "status": "success",
            "message": "Current time",
            "output": {
                "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        }
    
    async def _cmd_logoff(self, session_id: str, args: List[str]) -> Dict[str, Any]:
        """Logoff session."""
        return {
            "status": "success",
            "message": "Session will be closed",
            "action": "close_session"
        }
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session information
        """
        try:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            history = self.command_history.get(session_id, [])
            
            return {
                "session_id": session_id,
                "user_id": session["user_id"],
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "commands_executed": session["commands_executed"],
                "current_dataset": session["current_dataset"],
                "history_count": len(history),
                "active": True
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None
    
    async def get_command_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get command history for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of commands to return
            
        Returns:
            Command history
        """
        try:
            if session_id not in self.command_history:
                return []
            
            history = self.command_history[session_id]
            return history[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting command history: {e}")
            return []
    
    async def cleanup_idle_sessions(self):
        """Clean up idle sessions that have exceeded timeout."""
        try:
            current_time = datetime.utcnow()
            idle_sessions = []
            
            for session_id, session in self.sessions.items():
                idle_time = (current_time - session["last_activity"]).total_seconds()
                if idle_time > self.timeout:
                    idle_sessions.append(session_id)
            
            for session_id in idle_sessions:
                await self.close_session(session_id)
                logger.info(f"Closed idle TSO session {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up idle sessions: {e}")
    
    async def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get TSO statistics.
        
        Args:
            db: Database session
            
        Returns:
            TSO statistics
        """
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
        Get TSO status.
        
        Args:
            db: Database session
            
        Returns:
            TSO status information
        """
        try:
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            
            uptime = 0
            if subsystem and subsystem.last_started:
                uptime = int((datetime.utcnow() - subsystem.last_started).total_seconds())
            
            stats = await self.get_statistics(db)
            
            return {
                "name": self.name,
                "version": self.version,
                "status": self.status,
                "uptime": uptime,
                "configuration": {
                    "max_sessions": self.max_sessions,
                    "timeout": self.timeout
                },
                "statistics": stats,
                "sessions": {
                    "active": len(self.sessions),
                    "total": len(self.sessions)
                },
                "commands": {
                    "available": len(self.commands),
                    "list": list(self.commands.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "name": self.name,
                "status": "error",
                "error": str(e)
            }


# Global TSO simulator instance
tso_simulator = TSOSimulator()
