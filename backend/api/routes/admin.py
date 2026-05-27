"""
ZenithOne Explorer - Administration Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime

from database.connection import get_db
from database.models import User, AuditLog, Configuration
from api.routes.auth import get_current_user
from core.security import get_password_hash, validate_password_strength, check_permission
from utils.logger import get_logger

logger = get_logger("admin_routes")
router = APIRouter()


# Request/Response models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # admin, user, viewer


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    active: bool
    created_at: datetime
    last_login: Optional[datetime]


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users."""
    try:
        if not check_permission(current_user.role, "admin:users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        total = query.count()
        users = query.offset(offset).limit(limit).all()
        
        return [
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                role=u.role,
                active=u.active,
                created_at=u.created_at,
                last_login=u.last_login
            )
            for u in users
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user."""
    try:
        if not check_permission(current_user.role, "admin:users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Validate password
        is_valid, error_msg = validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check if username exists
        if db.query(User).filter(User.username == request.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email exists
        if db.query(User).filter(User.email == request.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create user
        user = User(
            username=request.username,
            email=request.email,
            password_hash=get_password_hash(request.password),
            role=request.role,
            active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log action
        audit_log = AuditLog(
            user_id=current_user.id,
            action="admin:user_create",
            resource_type="user",
            resource_id=user.id,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {user.username} created by {current_user.username}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user details."""
    try:
        if not check_permission(current_user.role, "admin:users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user properties."""
    try:
        if not check_permission(current_user.role, "admin:users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        if request.email is not None:
            user.email = request.email
        if request.role is not None:
            user.role = request.role
        if request.active is not None:
            user.active = request.active
        
        db.commit()
        db.refresh(user)
        
        # Log action
        audit_log = AuditLog(
            user_id=current_user.id,
            action="admin:user_update",
            resource_type="user",
            resource_id=user.id,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {user.username} updated by {current_user.username}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            active=user.active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    try:
        if not check_permission(current_user.role, "admin:users"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Log action before deletion
        audit_log = AuditLog(
            user_id=current_user.id,
            action="admin:user_delete",
            resource_type="user",
            resource_id=user.id,
            status="success"
        )
        db.add(audit_log)
        
        db.delete(user)
        db.commit()
        
        logger.info(f"User {user.username} deleted by {current_user.username}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")


@router.get("/config")
async def get_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system configuration."""
    try:
        if not check_permission(current_user.role, "admin:config"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        configs = db.query(Configuration).all()
        
        # Group by category
        config_dict = {}
        for config in configs:
            if config.category not in config_dict:
                config_dict[config.category] = {}
            config_dict[config.category][config.key] = config.value
        
        return config_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


@router.get("/audit")
async def get_audit_logs(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit logs."""
    try:
        if not check_permission(current_user.role, "admin:audit"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        
        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "status": log.status,
                    "details": log.details
                }
                for log in logs
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get audit logs")
