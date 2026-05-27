"""
ZenithOne Explorer - Workload Management Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database.connection import get_db
from database.models import User, Workload, WorkloadLog
from api.routes.auth import get_current_user
from core.workload_manager import workload_manager
from core.security import check_permission
from utils.logger import get_logger

logger = get_logger("workloads_routes")
router = APIRouter()


# Request/Response models
class WorkloadCreate(BaseModel):
    name: str
    type: str  # batch, transaction, interactive
    priority: str = "medium"  # low, medium, high, critical
    subsystem: str  # JES, CICS, TSO
    command: str
    parameters: Optional[dict] = None
    resources: Optional[dict] = None


class WorkloadResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    priority: str
    subsystem: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration: Optional[int]
    owner: str


class WorkloadListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    workloads: List[WorkloadResponse]


@router.post("", response_model=WorkloadResponse, status_code=201)
async def create_workload(
    request: WorkloadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new workload for execution.
    """
    try:
        # Check permission
        if not check_permission(current_user.role, "workload:create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create workload
        import json
        workload = Workload(
            name=request.name,
            type=request.type,
            priority=request.priority,
            subsystem=request.subsystem,
            command=request.command,
            parameters=json.dumps(request.parameters) if request.parameters else None,
            resources=json.dumps(request.resources) if request.resources else None,
            owner_id=current_user.id
        )
        
        # Submit to workload manager
        workload = await workload_manager.submit_workload(db, workload)
        
        return WorkloadResponse(
            id=workload.id,
            name=workload.name,
            type=workload.type,
            status=workload.status,
            priority=workload.priority,
            subsystem=workload.subsystem,
            created_at=workload.created_at,
            started_at=workload.started_at,
            completed_at=workload.completed_at,
            duration=workload.duration,
            owner=current_user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workload: {e}")
        raise HTTPException(status_code=500, detail="Failed to create workload")


@router.get("", response_model=WorkloadListResponse)
async def list_workloads(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List workloads with filtering and pagination.
    """
    try:
        # Check permission
        if not check_permission(current_user.role, "workload:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query
        query = db.query(Workload)
        
        # Apply filters
        if status:
            query = query.filter(Workload.status == status)
        if priority:
            query = query.filter(Workload.priority == priority)
        
        # Non-admin users can only see their own workloads
        if current_user.role != "admin":
            query = query.filter(Workload.owner_id == current_user.id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        workloads = query.order_by(Workload.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response
        workload_list = []
        for w in workloads:
            owner = db.query(User).filter(User.id == w.owner_id).first()
            workload_list.append(WorkloadResponse(
                id=w.id,
                name=w.name,
                type=w.type,
                status=w.status,
                priority=w.priority,
                subsystem=w.subsystem,
                created_at=w.created_at,
                started_at=w.started_at,
                completed_at=w.completed_at,
                duration=w.duration,
                owner=owner.username if owner else "unknown"
            ))
        
        return WorkloadListResponse(
            total=total,
            limit=limit,
            offset=offset,
            workloads=workload_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing workloads: {e}")
        raise HTTPException(status_code=500, detail="Failed to list workloads")


@router.get("/{workload_id}")
async def get_workload(
    workload_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed workload information.
    """
    try:
        # Check permission
        if not check_permission(current_user.role, "workload:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get workload
        workload = db.query(Workload).filter(Workload.id == workload_id).first()
        if not workload:
            raise HTTPException(status_code=404, detail="Workload not found")
        
        # Check ownership
        if current_user.role != "admin" and workload.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get owner
        owner = db.query(User).filter(User.id == workload.owner_id).first()
        
        # Get logs
        logs = db.query(WorkloadLog).filter(
            WorkloadLog.workload_id == workload_id
        ).order_by(WorkloadLog.timestamp.desc()).limit(100).all()
        
        import json
        return {
            "id": workload.id,
            "name": workload.name,
            "type": workload.type,
            "status": workload.status,
            "priority": workload.priority,
            "subsystem": workload.subsystem,
            "command": workload.command,
            "parameters": json.loads(workload.parameters) if workload.parameters else {},
            "resources": json.loads(workload.resources) if workload.resources else {},
            "created_at": workload.created_at.isoformat(),
            "started_at": workload.started_at.isoformat() if workload.started_at else None,
            "completed_at": workload.completed_at.isoformat() if workload.completed_at else None,
            "duration": workload.duration,
            "cpu_usage": workload.cpu_usage,
            "memory_usage": workload.memory_usage,
            "owner": owner.username if owner else "unknown",
            "exit_code": workload.exit_code,
            "error_message": workload.error_message,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message
                }
                for log in logs
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workload: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workload")


@router.delete("/{workload_id}", status_code=204)
async def cancel_workload(
    workload_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a workload.
    """
    try:
        # Check permission
        if not check_permission(current_user.role, "workload:delete"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get workload
        workload = db.query(Workload).filter(Workload.id == workload_id).first()
        if not workload:
            raise HTTPException(status_code=404, detail="Workload not found")
        
        # Check ownership
        if current_user.role != "admin" and workload.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Cancel workload
        success = await workload_manager.cancel_workload(db, workload_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel workload")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling workload: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel workload")


@router.get("/{workload_id}/logs")
async def get_workload_logs(
    workload_id: str,
    tail: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get workload logs.
    """
    try:
        # Check permission
        if not check_permission(current_user.role, "workload:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get workload
        workload = db.query(Workload).filter(Workload.id == workload_id).first()
        if not workload:
            raise HTTPException(status_code=404, detail="Workload not found")
        
        # Check ownership
        if current_user.role != "admin" and workload.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get logs
        logs = db.query(WorkloadLog).filter(
            WorkloadLog.workload_id == workload_id
        ).order_by(WorkloadLog.timestamp.desc()).limit(tail).all()
        
        return {
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "source": log.source
                }
                for log in reversed(logs)
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workload logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workload logs")
