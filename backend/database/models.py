"""
ZenithOne Explorer - Database Models
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, 
    String, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(32), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, index=True)  # admin, user, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    metadata = Column(Text, nullable=True)  # JSON
    
    # Relationships
    workloads = relationship("Workload", back_populates="owner", cascade="all, delete-orphan")
    containers = relationship("Container", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    api_tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")


class Workload(Base):
    """Workload/job model."""
    __tablename__ = "workloads"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # batch, transaction, interactive
    status = Column(String(50), nullable=False, index=True)  # pending, running, completed, failed, cancelled
    priority = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    subsystem = Column(String(20), nullable=False, index=True)  # JES, CICS, TSO, DB2
    command = Column(Text, nullable=False)
    parameters = Column(Text, nullable=True)  # JSON
    resources = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    cpu_usage = Column(Float, nullable=True)  # percentage
    memory_usage = Column(Integer, nullable=True)  # MB
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exit_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="workloads")
    logs = relationship("WorkloadLog", back_populates="workload", cascade="all, delete-orphan")
    metrics = relationship("WorkloadMetric", back_populates="workload", cascade="all, delete-orphan")


class WorkloadLog(Base):
    """Workload execution logs."""
    __tablename__ = "workload_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workload_id = Column(String, ForeignKey("workloads.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    
    # Relationships
    workload = relationship("Workload", back_populates="logs")


class WorkloadMetric(Base):
    """Time-series metrics for workloads."""
    __tablename__ = "workload_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workload_id = Column(String, ForeignKey("workloads.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Integer, nullable=True)
    disk_read = Column(Integer, nullable=True)
    disk_write = Column(Integer, nullable=True)
    network_rx = Column(Integer, nullable=True)
    network_tx = Column(Integer, nullable=True)
    
    # Relationships
    workload = relationship("Workload", back_populates="metrics")


class Container(Base):
    """Container model."""
    __tablename__ = "containers"
    
    id = Column(String, primary_key=True)  # Container ID from Podman
    name = Column(String(255), unique=True, nullable=False, index=True)
    image = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, index=True)  # running, stopped, paused, error
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ports = Column(Text, nullable=True)  # JSON
    environment = Column(Text, nullable=True)  # JSON
    volumes = Column(Text, nullable=True)  # JSON
    cpu_limit = Column(Float, nullable=True)
    memory_limit = Column(Integer, nullable=True)
    command = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relationships
    owner = relationship("User", back_populates="containers")


class Subsystem(Base):
    """z/OS subsystem model."""
    __tablename__ = "subsystems"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False, index=True)  # JES, CICS, DB2, TSO
    status = Column(String(50), nullable=False, index=True)  # active, inactive, error
    uptime = Column(Integer, default=0)  # seconds
    version = Column(String(50), nullable=True)
    configuration = Column(Text, nullable=True)  # JSON
    statistics = Column(Text, nullable=True)  # JSON
    last_started = Column(DateTime, nullable=True)
    last_stopped = Column(DateTime, nullable=True)


class SystemMetric(Base):
    """System-wide metrics."""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cpu_usage = Column(Float, nullable=True)
    cpu_load_1 = Column(Float, nullable=True)
    cpu_load_5 = Column(Float, nullable=True)
    cpu_load_15 = Column(Float, nullable=True)
    memory_total = Column(Integer, nullable=True)
    memory_used = Column(Integer, nullable=True)
    memory_available = Column(Integer, nullable=True)
    disk_total = Column(Integer, nullable=True)
    disk_used = Column(Integer, nullable=True)
    network_rx = Column(Integer, nullable=True)
    network_tx = Column(Integer, nullable=True)
    active_workloads = Column(Integer, nullable=True)
    active_containers = Column(Integer, nullable=True)


class AuditLog(Base):
    """Audit log for security and compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    status = Column(String(20), nullable=False)  # success, failure
    details = Column(Text, nullable=True)  # JSON
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class APIToken(Base):
    """API authentication tokens."""
    __tablename__ = "api_tokens"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_tokens")


class Configuration(Base):
    """System configuration key-value store."""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    category = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
