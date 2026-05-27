"""
ZenithOne Explorer - CICS (Customer Information Control System) Simulator
Simulates mainframe CICS transaction processing
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database.models import Subsystem, Workload
from config import settings
from utils.logger import get_logger

logger = get_logger("cics")


class CICSSimulator:
    """
    Simulates IBM z/OS CICS (Customer Information Control System).
    Handles transaction processing and session management.
    """
    
    def __init__(self):
        self.name = "CICS"
        self.version = "1.0.0"
        self.status = "inactive"
        self.max_transactions = settings.cics_max_transactions
        self.timeout = settings.cics_timeout
        
        # Active sessions
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            "transactions_processed": 0,
            "transactions_failed": 0,
            "active_transactions": 0,
            "active_sessions": 0,
            "avg_response_time": 0.0,
            "throughput": 0.0  # transactions per second
        }
        
        logger.info(f"CICS Simulator initialized (max transactions: {self.max_transactions})")
    
    async def start(self, db: Session) -> bool:
        """
        Start CICS subsystem.
        
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
            
            logger.info("CICS subsystem started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting CICS: {e}")
            self.status = "error"
            return False
    
    async def stop(self, db: Session) -> bool:
        """
        Stop CICS subsystem.
        
        Args:
            db: Database session
            
        Returns:
            True if stopped successfully
        """
        try:
            self.status = "inactive"
            
            # Close all sessions
            self.sessions.clear()
            
            # Update database
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            if subsystem:
                subsystem.status = "inactive"
                subsystem.last_stopped = datetime.utcnow()
                db.commit()
            
            logger.info("CICS subsystem stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping CICS: {e}")
            return False
    
    async def create_session(self, user_id: str) -> Optional[str]:
        """
        Create a new CICS session.
        
        Args:
            user_id: User ID
            
        Returns:
            Session ID if created successfully
        """
        try:
            if self.status != "active":
                logger.error("CICS is not active")
                return None
            
            session_id = str(uuid.uuid4())
            
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "transactions": 0
            }
            
            self.stats["active_sessions"] = len(self.sessions)
            
            logger.info(f"CICS session {session_id} created for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close a CICS session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if closed successfully
        """
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                self.stats["active_sessions"] = len(self.sessions)
                logger.info(f"CICS session {session_id} closed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error closing session: {e}")
            return False
    
    async def process_transaction(
        self,
        db: Session,
        session_id: str,
        transaction_type: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process a CICS transaction.
        
        Args:
            db: Database session
            session_id: Session ID
            transaction_type: Type of transaction (READ, WRITE, UPDATE, DELETE)
            data: Transaction data
            
        Returns:
            Transaction result
        """
        try:
            if self.status != "active":
                logger.error("CICS is not active")
                return None
            
            if session_id not in self.sessions:
                logger.error(f"Invalid session: {session_id}")
                return None
            
            # Check transaction limit
            if self.stats["active_transactions"] >= self.max_transactions:
                logger.warning(f"CICS transaction limit reached ({self.max_transactions})")
                return None
            
            # Start transaction
            transaction_id = str(uuid.uuid4())
            start_time = datetime.utcnow()
            
            self.stats["active_transactions"] += 1
            
            # Process based on type
            result = await self._execute_transaction(transaction_type, data)
            
            # Calculate response time
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            # Update statistics
            self.stats["transactions_processed"] += 1
            self.stats["active_transactions"] -= 1
            
            # Update average response time
            total_transactions = self.stats["transactions_processed"]
            current_avg = self.stats["avg_response_time"]
            self.stats["avg_response_time"] = (
                (current_avg * (total_transactions - 1) + response_time) / total_transactions
            )
            
            # Update session
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            self.sessions[session_id]["transactions"] += 1
            
            await self._update_statistics(db)
            
            logger.info(f"CICS transaction {transaction_id} processed ({transaction_type}, {response_time:.2f}ms)")
            
            return {
                "transaction_id": transaction_id,
                "type": transaction_type,
                "status": "success",
                "response_time": response_time,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            self.stats["transactions_failed"] += 1
            self.stats["active_transactions"] -= 1
            return None
    
    async def _execute_transaction(
        self,
        transaction_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute transaction logic.
        
        Args:
            transaction_type: Transaction type
            data: Transaction data
            
        Returns:
            Transaction result
        """
        # Simulate transaction processing
        import asyncio
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if transaction_type == "READ":
            return {"data": data, "records": 1}
        elif transaction_type == "WRITE":
            return {"status": "written", "id": str(uuid.uuid4())}
        elif transaction_type == "UPDATE":
            return {"status": "updated", "records": 1}
        elif transaction_type == "DELETE":
            return {"status": "deleted", "records": 1}
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")
    
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
            
            return {
                "session_id": session_id,
                "user_id": session["user_id"],
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat(),
                "transactions": session["transactions"],
                "active": True
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None
    
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
                logger.info(f"Closed idle session {session_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up idle sessions: {e}")
    
    async def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get CICS statistics.
        
        Args:
            db: Database session
            
        Returns:
            CICS statistics
        """
        try:
            # Calculate throughput (simplified)
            subsystem = db.query(Subsystem).filter(Subsystem.name == self.name).first()
            if subsystem and subsystem.last_started:
                uptime = (datetime.utcnow() - subsystem.last_started).total_seconds()
                if uptime > 0:
                    self.stats["throughput"] = self.stats["transactions_processed"] / uptime
            
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
        Get CICS status.
        
        Args:
            db: Database session
            
        Returns:
            CICS status information
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
                    "max_transactions": self.max_transactions,
                    "timeout": self.timeout
                },
                "statistics": stats,
                "sessions": {
                    "active": len(self.sessions),
                    "total": len(self.sessions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "name": self.name,
                "status": "error",
                "error": str(e)
            }


# Global CICS simulator instance
cics_simulator = CICSSimulator()
