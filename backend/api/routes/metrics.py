"""
ZenithOne Explorer - Metrics Routes
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.api.routes.auth import get_current_user
from backend.core.monitoring_service import monitoring_service
from backend.core.security import check_permission
from backend.utils.logger import get_logger

logger = get_logger("metrics_routes")
router = APIRouter()


@router.get("")
async def get_current_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current system metrics."""
    try:
        if not check_permission(current_user.role, "metrics:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        metrics = await monitoring_service.get_current_metrics()
        
        return {
            "timestamp": metrics["timestamp"].isoformat(),
            "system": {
                "cpu": {
                    "usage": metrics["cpu"]["usage"],
                    "cores": metrics["cpu"]["cores"],
                    "load_average": [
                        metrics["cpu"]["load_1"],
                        metrics["cpu"]["load_5"],
                        metrics["cpu"]["load_15"]
                    ]
                },
                "memory": {
                    "total": metrics["memory"]["total"],
                    "used": metrics["memory"]["used"],
                    "available": metrics["memory"]["available"],
                    "usage_percent": metrics["memory"]["percent"]
                },
                "disk": {
                    "total": metrics["disk"]["total"],
                    "used": metrics["disk"]["used"],
                    "free": metrics["disk"]["free"],
                    "usage_percent": metrics["disk"]["percent"]
                },
                "network": {
                    "bytes_sent": metrics["network"]["bytes_sent"],
                    "bytes_recv": metrics["network"]["bytes_recv"],
                    "packets_sent": metrics["network"]["packets_sent"],
                    "packets_recv": metrics["network"]["packets_recv"]
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/history")
async def get_historical_metrics(
    metric: str = Query(..., regex="^(cpu|memory|disk|network)$"),
    from_time: Optional[datetime] = Query(None),
    to_time: Optional[datetime] = Query(None),
    interval: int = Query(60, ge=1, le=3600),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical metrics data."""
    try:
        if not check_permission(current_user.role, "metrics:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Default time range: last hour
        if not to_time:
            to_time = datetime.utcnow()
        if not from_time:
            from_time = to_time - timedelta(hours=1)
        
        metrics = await monitoring_service.get_historical_metrics(
            db, metric, from_time, to_time, interval
        )
        
        return {
            "metric": metric,
            "from": from_time.isoformat(),
            "to": to_time.isoformat(),
            "interval": interval,
            "data": metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get historical metrics")


@router.get("/health")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall system health status."""
    try:
        if not check_permission(current_user.role, "metrics:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        health = await monitoring_service.get_system_health(db)
        
        return health
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")
