"""
ZenithOne Explorer - Monitoring Service
System metrics collection and performance monitoring
"""
import asyncio
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database.models import SystemMetric
from config import settings
from utils.logger import get_logger

logger = get_logger("monitoring_service")


class MonitoringService:
    """
    Collects and stores system metrics for monitoring and analytics.
    Provides real-time and historical performance data.
    """
    
    def __init__(self):
        self.running = False
        self.collection_task: Optional[asyncio.Task] = None
        self.interval = settings.metrics_interval
        self.retention_days = settings.metrics_retention_days
        
        logger.info(f"Monitoring Service initialized (interval: {self.interval}s)")
    
    async def start(self, db: Session):
        """
        Start metrics collection.
        
        Args:
            db: Database session
        """
        if self.running:
            logger.warning("Monitoring service already running")
            return
        
        self.running = True
        self.collection_task = asyncio.create_task(self._collect_metrics_loop(db))
        logger.info("Monitoring service started")
    
    async def stop(self):
        """Stop metrics collection."""
        if not self.running:
            return
        
        self.running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring service stopped")
    
    async def _collect_metrics_loop(self, db: Session):
        """
        Main metrics collection loop.
        
        Args:
            db: Database session
        """
        while self.running:
            try:
                # Collect metrics
                metrics = await self.collect_system_metrics()
                
                # Store in database
                await self._store_metrics(db, metrics)
                
                # Cleanup old metrics
                await self._cleanup_old_metrics(db)
                
                # Wait for next interval
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(self.interval)
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect current system metrics.
        
        Returns:
            Dictionary of system metrics
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            metrics = {
                "timestamp": datetime.utcnow(),
                "cpu": {
                    "usage": cpu_percent,
                    "cores": cpu_count,
                    "load_1": load_avg[0],
                    "load_5": load_avg[1],
                    "load_15": load_avg[2]
                },
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    async def _store_metrics(self, db: Session, metrics: Dict[str, Any]):
        """
        Store metrics in database.
        
        Args:
            db: Database session
            metrics: Metrics to store
        """
        try:
            if not metrics:
                return
            
            # Count active workloads and containers
            from database.models import Workload, Container
            
            active_workloads = db.query(Workload).filter(
                Workload.status.in_(["pending", "running"])
            ).count()
            
            active_containers = db.query(Container).filter(
                Container.status == "running"
            ).count()
            
            # Create metric record
            metric = SystemMetric(
                timestamp=metrics["timestamp"],
                cpu_usage=metrics["cpu"]["usage"],
                cpu_load_1=metrics["cpu"]["load_1"],
                cpu_load_5=metrics["cpu"]["load_5"],
                cpu_load_15=metrics["cpu"]["load_15"],
                memory_total=metrics["memory"]["total"],
                memory_used=metrics["memory"]["used"],
                memory_available=metrics["memory"]["available"],
                disk_total=metrics["disk"]["total"],
                disk_used=metrics["disk"]["used"],
                network_rx=metrics["network"]["bytes_recv"],
                network_tx=metrics["network"]["bytes_sent"],
                active_workloads=active_workloads,
                active_containers=active_containers
            )
            
            db.add(metric)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
            db.rollback()
    
    async def _cleanup_old_metrics(self, db: Session):
        """
        Remove metrics older than retention period.
        
        Args:
            db: Database session
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            deleted = db.query(SystemMetric).filter(
                SystemMetric.timestamp < cutoff_date
            ).delete()
            
            if deleted > 0:
                db.commit()
                logger.info(f"Cleaned up {deleted} old metric records")
                
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
            db.rollback()
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics without storing.
        
        Returns:
            Current metrics
        """
        return await self.collect_system_metrics()
    
    async def get_historical_metrics(
        self,
        db: Session,
        metric_type: str,
        start_time: datetime,
        end_time: datetime,
        interval: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get historical metrics for a specific type.
        
        Args:
            db: Database session
            metric_type: Type of metric (cpu, memory, disk, network)
            start_time: Start time
            end_time: End time
            interval: Aggregation interval in seconds
            
        Returns:
            List of historical metrics
        """
        try:
            # Query metrics in time range
            metrics = db.query(SystemMetric).filter(
                SystemMetric.timestamp >= start_time,
                SystemMetric.timestamp <= end_time
            ).order_by(SystemMetric.timestamp).all()
            
            # Format based on metric type
            result = []
            for metric in metrics:
                data_point = {
                    "timestamp": metric.timestamp.isoformat()
                }
                
                if metric_type == "cpu":
                    data_point["value"] = metric.cpu_usage
                elif metric_type == "memory":
                    data_point["value"] = (metric.memory_used / metric.memory_total * 100) if metric.memory_total > 0 else 0
                elif metric_type == "disk":
                    data_point["value"] = (metric.disk_used / metric.disk_total * 100) if metric.disk_total > 0 else 0
                elif metric_type == "network":
                    data_point["rx"] = metric.network_rx
                    data_point["tx"] = metric.network_tx
                
                result.append(data_point)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting historical metrics: {e}")
            return []
    
    async def get_system_health(self, db: Session) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Args:
            db: Database session
            
        Returns:
            System health information
        """
        try:
            metrics = await self.collect_system_metrics()
            
            # Determine health status
            cpu_status = "healthy" if metrics["cpu"]["usage"] < 80 else "warning" if metrics["cpu"]["usage"] < 90 else "critical"
            memory_status = "healthy" if metrics["memory"]["percent"] < 80 else "warning" if metrics["memory"]["percent"] < 90 else "critical"
            disk_status = "healthy" if metrics["disk"]["percent"] < 80 else "warning" if metrics["disk"]["percent"] < 90 else "critical"
            
            # Overall status
            if any(s == "critical" for s in [cpu_status, memory_status, disk_status]):
                overall_status = "critical"
            elif any(s == "warning" for s in [cpu_status, memory_status, disk_status]):
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            return {
                "status": overall_status,
                "timestamp": metrics["timestamp"].isoformat(),
                "components": {
                    "cpu": {
                        "status": cpu_status,
                        "usage": metrics["cpu"]["usage"],
                        "load": metrics["cpu"]["load_1"]
                    },
                    "memory": {
                        "status": memory_status,
                        "usage": metrics["memory"]["percent"],
                        "available": metrics["memory"]["available"]
                    },
                    "disk": {
                        "status": disk_status,
                        "usage": metrics["disk"]["percent"],
                        "free": metrics["disk"]["free"]
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    async def generate_alert(
        self,
        db: Session,
        alert_type: str,
        message: str,
        severity: str = "warning"
    ):
        """
        Generate a system alert.
        
        Args:
            db: Database session
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (info, warning, critical)
        """
        try:
            # Log alert
            logger.warning(f"ALERT [{severity.upper()}] {alert_type}: {message}")
            
            # In production, this would:
            # - Send email notifications
            # - Trigger webhooks
            # - Store in alerts table
            # - Push to UI via WebSocket
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")


# Global monitoring service instance
monitoring_service = MonitoringService()
