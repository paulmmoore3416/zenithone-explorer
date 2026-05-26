"""
ZenithOne Explorer - Subsystems Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.api.routes.auth import get_current_user
from backend.subsystems.jes import jes_simulator
from backend.subsystems.cics import cics_simulator
from backend.subsystems.db2 import db2_simulator
from backend.subsystems.tso import tso_simulator
from backend.core.security import check_permission
from backend.utils.logger import get_logger

logger = get_logger("subsystems_routes")
router = APIRouter()


@router.get("")
async def list_subsystems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of all z/OS subsystems."""
    try:
        if not check_permission(current_user.role, "subsystem:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        subsystems = []
        
        # Get status from each subsystem
        for simulator in [jes_simulator, cics_simulator, db2_simulator, tso_simulator]:
            status = await simulator.get_status(db)
            subsystems.append(status)
        
        return {"subsystems": subsystems}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing subsystems: {e}")
        raise HTTPException(status_code=500, detail="Failed to list subsystems")


@router.get("/{name}")
async def get_subsystem(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed subsystem information."""
    try:
        if not check_permission(current_user.role, "subsystem:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get simulator
        simulators = {
            "JES": jes_simulator,
            "CICS": cics_simulator,
            "DB2": db2_simulator,
            "TSO": tso_simulator
        }
        
        simulator = simulators.get(name.upper())
        if not simulator:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        status = await simulator.get_status(db)
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subsystem: {e}")
        raise HTTPException(status_code=500, detail="Failed to get subsystem")


@router.post("/{name}/start")
async def start_subsystem(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a subsystem."""
    try:
        if not check_permission(current_user.role, "subsystem:control"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get simulator
        simulators = {
            "JES": jes_simulator,
            "CICS": cics_simulator,
            "DB2": db2_simulator,
            "TSO": tso_simulator
        }
        
        simulator = simulators.get(name.upper())
        if not simulator:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        success = await simulator.start(db)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start subsystem")
        
        return {
            "name": name.upper(),
            "status": "active",
            "message": f"{name.upper()} subsystem started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting subsystem: {e}")
        raise HTTPException(status_code=500, detail="Failed to start subsystem")


@router.post("/{name}/stop")
async def stop_subsystem(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop a subsystem."""
    try:
        if not check_permission(current_user.role, "subsystem:control"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get simulator
        simulators = {
            "JES": jes_simulator,
            "CICS": cics_simulator,
            "DB2": db2_simulator,
            "TSO": tso_simulator
        }
        
        simulator = simulators.get(name.upper())
        if not simulator:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        success = await simulator.stop(db)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to stop subsystem")
        
        return {
            "name": name.upper(),
            "status": "inactive",
            "message": f"{name.upper()} subsystem stopped successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping subsystem: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop subsystem")


@router.post("/{name}/restart")
async def restart_subsystem(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart a subsystem."""
    try:
        if not check_permission(current_user.role, "subsystem:control"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get simulator
        simulators = {
            "JES": jes_simulator,
            "CICS": cics_simulator,
            "DB2": db2_simulator,
            "TSO": tso_simulator
        }
        
        simulator = simulators.get(name.upper())
        if not simulator:
            raise HTTPException(status_code=404, detail="Subsystem not found")
        
        # Stop then start
        await simulator.stop(db)
        success = await simulator.start(db)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to restart subsystem")
        
        return {
            "name": name.upper(),
            "status": "active",
            "message": f"{name.upper()} subsystem restarted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting subsystem: {e}")
        raise HTTPException(status_code=500, detail="Failed to restart subsystem")
