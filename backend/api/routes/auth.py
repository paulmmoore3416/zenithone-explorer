"""
ZenithOne Explorer - Authentication Routes
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User, AuditLog
from backend.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
    get_password_hash,
    validate_password_strength
)
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("auth")
router = APIRouter()
security = HTTPBearer()


# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    active: bool


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    Args:
        request: Login credentials
        db: Database session
        
    Returns:
        Access token and user information
    """
    try:
        # Find user
        user = db.query(User).filter(User.username == request.username).first()
        
        if not user or not verify_password(request.password, user.password_hash):
            # Log failed attempt
            audit_log = AuditLog(
                user_id=user.id if user else None,
                action="auth:login",
                resource_type="user",
                resource_id=user.id if user else None,
                status="failure",
                details='{"reason": "invalid_credentials"}'
            )
            db.add(audit_log)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username, "role": user.role}
        )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        
        # Log successful login
        audit_log = AuditLog(
            user_id=user.id,
            action="auth:login",
            resource_type="user",
            resource_id=user.id,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {user.username} logged in successfully")
        
        return LoginResponse(
            access_token=access_token,
            expires_in=settings.jwt_expiration,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh access token.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        New access token
    """
    try:
        # Create new access token
        access_token = create_access_token(
            data={"sub": current_user.id, "username": current_user.username, "role": current_user.role}
        )
        
        return {
            "access_token": access_token,
            "expires_in": settings.jwt_expiration
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during token refresh"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user (invalidate token).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        # Log logout
        audit_log = AuditLog(
            user_id=current_user.id,
            action="auth:logout",
            resource_type="user",
            resource_id=current_user.id,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {current_user.username} logged out")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        active=current_user.active
    )
