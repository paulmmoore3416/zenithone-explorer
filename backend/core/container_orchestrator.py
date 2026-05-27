"""
ZenithOne Explorer - Container Orchestrator
Podman integration for container lifecycle management
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

try:
    from podman import PodmanClient
    PODMAN_AVAILABLE = True
except ImportError:
    PODMAN_AVAILABLE = False
    PodmanClient = None

from database.models import Container
from config import settings
from utils.logger import get_logger

logger = get_logger("container_orchestrator")


class ContainerOrchestrator:
    """
    Manages container lifecycle using Podman.
    Provides abstraction layer for container operations.
    """
    
    def __init__(self):
        self.client: Optional[PodmanClient] = None
        self.connected = False
        
        if PODMAN_AVAILABLE:
            try:
                self.client = PodmanClient()
                self.connected = True
                logger.info("Connected to Podman")
            except Exception as e:
                logger.warning(f"Failed to connect to Podman: {e}")
                logger.warning("Container operations will be simulated")
        else:
            logger.warning("Podman Python SDK not available, operations will be simulated")
    
    async def create_container(
        self,
        db: Session,
        name: str,
        image: str,
        command: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        ports: Optional[List[str]] = None,
        volumes: Optional[List[str]] = None,
        cpu_limit: Optional[float] = None,
        memory_limit: Optional[int] = None,
        owner_id: str = None
    ) -> Container:
        """
        Create and start a new container.
        
        Args:
            db: Database session
            name: Container name
            image: Container image
            command: Command to run
            environment: Environment variables
            ports: Port mappings (e.g., ["8080:80"])
            volumes: Volume mounts (e.g., ["/host:/container"])
            cpu_limit: CPU limit in cores
            memory_limit: Memory limit in MB
            owner_id: User ID who owns the container
            
        Returns:
            Created container object
        """
        try:
            container_id = None
            
            if self.connected and self.client:
                # Create container using Podman
                container_config = {
                    "name": name,
                    "image": image,
                    "detach": True,
                }
                
                if command:
                    container_config["command"] = command
                
                if environment:
                    container_config["environment"] = environment
                
                if ports:
                    # Parse port mappings
                    port_bindings = {}
                    for port_map in ports:
                        host_port, container_port = port_map.split(":")
                        port_bindings[f"{container_port}/tcp"] = host_port
                    container_config["ports"] = port_bindings
                
                if volumes:
                    container_config["volumes"] = volumes
                
                # Resource limits
                if cpu_limit or memory_limit:
                    container_config["resources"] = {}
                    if cpu_limit:
                        container_config["resources"]["cpu_quota"] = int(cpu_limit * 100000)
                    if memory_limit:
                        container_config["resources"]["memory"] = memory_limit * 1024 * 1024
                
                # Create container
                podman_container = self.client.containers.create(**container_config)
                container_id = podman_container.id
                
                # Start container
                podman_container.start()
                
                logger.info(f"Container {name} created and started (ID: {container_id})")
            else:
                # Simulate container creation
                import uuid
                container_id = str(uuid.uuid4())[:12]
                logger.info(f"Simulated container {name} created (ID: {container_id})")
            
            # Create database record
            container = Container(
                id=container_id,
                name=name,
                image=image,
                status="running",
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                ports=json.dumps(ports) if ports else None,
                environment=json.dumps(environment) if environment else None,
                volumes=json.dumps(volumes) if volumes else None,
                cpu_limit=cpu_limit or settings.container_max_cpu,
                memory_limit=memory_limit or settings.container_max_memory,
                command=command,
                owner_id=owner_id
            )
            
            db.add(container)
            db.commit()
            db.refresh(container)
            
            return container
            
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            raise
    
    async def start_container(self, db: Session, container_id: str) -> bool:
        """
        Start a stopped container.
        
        Args:
            db: Database session
            container_id: Container ID
            
        Returns:
            True if started successfully
        """
        try:
            if self.connected and self.client:
                container = self.client.containers.get(container_id)
                container.start()
                logger.info(f"Container {container_id} started")
            else:
                logger.info(f"Simulated start of container {container_id}")
            
            # Update database
            db_container = db.query(Container).filter(Container.id == container_id).first()
            if db_container:
                db_container.status = "running"
                db_container.started_at = datetime.utcnow()
                db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting container: {e}")
            return False
    
    async def stop_container(self, db: Session, container_id: str) -> bool:
        """
        Stop a running container.
        
        Args:
            db: Database session
            container_id: Container ID
            
        Returns:
            True if stopped successfully
        """
        try:
            if self.connected and self.client:
                container = self.client.containers.get(container_id)
                container.stop()
                logger.info(f"Container {container_id} stopped")
            else:
                logger.info(f"Simulated stop of container {container_id}")
            
            # Update database
            db_container = db.query(Container).filter(Container.id == container_id).first()
            if db_container:
                db_container.status = "stopped"
                db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False
    
    async def restart_container(self, db: Session, container_id: str) -> bool:
        """
        Restart a container.
        
        Args:
            db: Database session
            container_id: Container ID
            
        Returns:
            True if restarted successfully
        """
        try:
            if self.connected and self.client:
                container = self.client.containers.get(container_id)
                container.restart()
                logger.info(f"Container {container_id} restarted")
            else:
                logger.info(f"Simulated restart of container {container_id}")
            
            # Update database
            db_container = db.query(Container).filter(Container.id == container_id).first()
            if db_container:
                db_container.status = "running"
                db_container.started_at = datetime.utcnow()
                db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error restarting container: {e}")
            return False
    
    async def remove_container(
        self,
        db: Session,
        container_id: str,
        force: bool = False
    ) -> bool:
        """
        Remove a container.
        
        Args:
            db: Database session
            container_id: Container ID
            force: Force removal even if running
            
        Returns:
            True if removed successfully
        """
        try:
            if self.connected and self.client:
                container = self.client.containers.get(container_id)
                container.remove(force=force)
                logger.info(f"Container {container_id} removed")
            else:
                logger.info(f"Simulated removal of container {container_id}")
            
            # Remove from database
            db_container = db.query(Container).filter(Container.id == container_id).first()
            if db_container:
                db.delete(db_container)
                db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing container: {e}")
            return False
    
    async def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        """
        Get container resource usage statistics.
        
        Args:
            container_id: Container ID
            
        Returns:
            Container statistics or None
        """
        try:
            if self.connected and self.client:
                container = self.client.containers.get(container_id)
                stats = container.stats(stream=False)
                
                # Parse stats
                cpu_usage = 0.0
                memory_usage = 0
                
                if stats:
                    # CPU usage calculation
                    cpu_delta = stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
                    system_delta = stats.get("cpu_stats", {}).get("system_cpu_usage", 0)
                    num_cpus = len(stats.get("cpu_stats", {}).get("cpu_usage", {}).get("percpu_usage", []))
                    
                    if system_delta > 0 and num_cpus > 0:
                        cpu_usage = (cpu_delta / system_delta) * num_cpus * 100.0
                    
                    # Memory usage
                    memory_usage = stats.get("memory_stats", {}).get("usage", 0) // (1024 * 1024)  # Convert to MB
                
                return {
                    "cpu_usage": round(cpu_usage, 2),
                    "memory_usage": memory_usage,
                    "network_rx": stats.get("networks", {}).get("eth0", {}).get("rx_bytes", 0),
                    "network_tx": stats.get("networks", {}).get("eth0", {}).get("tx_bytes", 0),
                    "block_read": stats.get("blkio_stats", {}).get("io_service_bytes_recursive", [{}])[0].get("value", 0),
                    "block_write": 0  # Simplified
                }
            else:
                # Simulate stats
                import random
                return {
                    "cpu_usage": round(random.uniform(5.0, 30.0), 2),
                    "memory_usage": random.randint(64, 512),
                    "network_rx": random.randint(1000000, 10000000),
                    "network_tx": random.randint(500000, 5000000),
                    "block_read": random.randint(1000000, 10000000),
                    "block_write": random.randint(500000, 5000000)
                }
                
        except Exception as e:
            logger.error(f"Error getting container stats: {e}")
            return None
    
    async def get_container_logs(
        self,
        container_id: str,
        tail: int = 100,
        follow: bool = False
    ) -> Optional[str]:
        """
        Get container logs.
        
        Args:
            container_id: Container ID
            tail: Number of lines to return
            follow: Stream logs
            
        Returns:
            Container logs or None
        """
        try:
            if self.connected and self.client:
                container = self.client.containers.get(container_id)
                logs = container.logs(tail=tail, stream=follow)
                
                if follow:
                    return logs  # Return generator for streaming
                else:
                    return logs.decode("utf-8") if isinstance(logs, bytes) else logs
            else:
                # Simulate logs
                return f"[Simulated logs for container {container_id}]\nContainer is running...\n"
                
        except Exception as e:
            logger.error(f"Error getting container logs: {e}")
            return None
    
    async def list_containers(
        self,
        db: Session,
        status_filter: Optional[str] = None
    ) -> List[Container]:
        """
        List all containers.
        
        Args:
            db: Database session
            status_filter: Optional status filter
            
        Returns:
            List of containers
        """
        try:
            query = db.query(Container)
            
            if status_filter:
                query = query.filter(Container.status == status_filter)
            
            containers = query.all()
            
            # Update status from Podman if connected
            if self.connected and self.client:
                for container in containers:
                    try:
                        podman_container = self.client.containers.get(container.id)
                        container.status = podman_container.status
                    except:
                        container.status = "error"
                
                db.commit()
            
            return containers
            
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check orchestrator health.
        
        Returns:
            Health status
        """
        return {
            "connected": self.connected,
            "podman_available": PODMAN_AVAILABLE,
            "status": "healthy" if self.connected else "degraded"
        }


# Global container orchestrator instance
container_orchestrator = ContainerOrchestrator()
