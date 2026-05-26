"""
ZenithOne Explorer - Container Management Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User, Container
from backend.api.routes.auth import get_current_user
from backend.core.container_orchestrator import container_orchestrator
from backend.core.security import check_permission
from backend.utils.logger import get_logger

logger = get_logger("containers_routes")
router = APIRouter()


# Request/Response models
class ContainerCreate(BaseModel):
    name: str
    image: str
    command: Optional[str] = None
    environment: Optional[dict] = None
    ports: Optional[List[str]] = None
    volumes: Optional[List[str]] = None
    cpu_limit: Optional[float] = None
    memory_limit: Optional[int] = None


class ContainerResponse(BaseModel):
    id: str
    name: str
    image: str
    status: str
    created_at: str
    owner: str


@router.post("", response_model=ContainerResponse, status_code=201)
async def create_container(
    request: ContainerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and start a new container."""
    try:
        if not check_permission(current_user.role, "container:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = await container_orchestrator.create_container(
            db=db,
            name=request.name,
            image=request.image,
            command=request.command,
            environment=request.environment,
            ports=request.ports,
            volumes=request.volumes,
            cpu_limit=request.cpu_limit,
            memory_limit=request.memory_limit,
            owner_id=current_user.id
        )
        
        return ContainerResponse(
            id=container.id,
            name=container.name,
            image=container.image,
            status=container.status,
            created_at=container.created_at.isoformat(),
            owner=current_user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating container: {e}")
        raise HTTPException(status_code=500, detail="Failed to create container")


@router.get("")
async def list_containers(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all containers."""
    try:
        if not check_permission(current_user.role, "container:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        containers = await container_orchestrator.list_containers(db, status)
        
        # Filter by ownership for non-admin users
        if current_user.role != "admin":
            containers = [c for c in containers if c.owner_id == current_user.id]
        
        import json
        return {
            "total": len(containers),
            "containers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "image": c.image,
                    "status": c.status,
                    "created_at": c.created_at.isoformat(),
                    "ports": json.loads(c.ports) if c.ports else [],
                    "cpu_limit": c.cpu_limit,
                    "memory_limit": c.memory_limit
                }
                for c in containers
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing containers: {e}")
        raise HTTPException(status_code=500, detail="Failed to list containers")


@router.get("/{container_id}")
async def get_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get container details."""
    try:
        if not check_permission(current_user.role, "container:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        if current_user.role != "admin" and container.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get stats
        stats = await container_orchestrator.get_container_stats(container_id)
        
        import json
        return {
            "id": container.id,
            "name": container.name,
            "image": container.image,
            "status": container.status,
            "created_at": container.created_at.isoformat(),
            "started_at": container.started_at.isoformat() if container.started_at else None,
            "ports": json.loads(container.ports) if container.ports else [],
            "environment": json.loads(container.environment) if container.environment else {},
            "volumes": json.loads(container.volumes) if container.volumes else [],
            "cpu_limit": container.cpu_limit,
            "memory_limit": container.memory_limit,
            "command": container.command,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting container: {e}")
        raise HTTPException(status_code=500, detail="Failed to get container")


@router.post("/{container_id}/start")
async def start_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a stopped container."""
    try:
        if not check_permission(current_user.role, "container:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        if current_user.role != "admin" and container.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await container_orchestrator.start_container(db, container_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start container")
        
        return {"message": "Container started", "status": "running"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting container: {e}")
        raise HTTPException(status_code=500, detail="Failed to start container")


@router.post("/{container_id}/stop")
async def stop_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop a running container."""
    try:
        if not check_permission(current_user.role, "container:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        if current_user.role != "admin" and container.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await container_orchestrator.stop_container(db, container_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to stop container")
        
        return {"message": "Container stopped", "status": "stopped"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping container: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop container")


@router.post("/{container_id}/restart")
async def restart_container(
    container_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart a container."""
    try:
        if not check_permission(current_user.role, "container:update"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        if current_user.role != "admin" and container.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await container_orchestrator.restart_container(db, container_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to restart container")
        
        return {"message": "Container restarted", "status": "running"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting container: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart container")


@router.delete("/{container_id}", status_code=204)
async def remove_container(
    container_id: str,
    force: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a container."""
    try:
        if not check_permission(current_user.role, "container:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        if current_user.role != "admin" and container.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await container_orchestrator.remove_container(db, container_id, force)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to remove container")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing container: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove container")


@router.get("/{container_id}/logs")
async def get_container_logs(
    container_id: str,
    tail: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get container logs."""
    try:
        if not check_permission(current_user.role, "container:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            raise HTTPException(status_code=404, detail="Container not found")
        
        if current_user.role != "admin" and container.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logs = await container_orchestrator.get_container_logs(container_id, tail)
        
        return {"logs": logs}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting container logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get container logs")
