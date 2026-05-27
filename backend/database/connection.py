"""
ZenithOne Explorer - Database Connection Management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from pathlib import Path

from config import settings
from database.models import Base
from utils.logger import get_logger

logger = get_logger("database")


# Create database engine
def get_engine():
    """Create and configure database engine."""
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
    
    return engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_database():
    """Seed database with initial data."""
    from core.security import get_password_hash
    from database.models import User, Subsystem, Configuration
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(User).first():
            logger.info("Database already seeded")
            return
        
        logger.info("Seeding database with initial data...")
        
        # Create default users
        users = [
            User(
                id="00000000-0000-0000-0000-000000000001",
                username="admin",
                email="admin@zenitone.local",
                password_hash=get_password_hash("Admin@123"),
                role="admin",
                active=True
            ),
            User(
                id="00000000-0000-0000-0000-000000000002",
                username="demo",
                email="demo@zenitone.local",
                password_hash=get_password_hash("Demo@123"),
                role="user",
                active=True
            ),
            User(
                id="00000000-0000-0000-0000-000000000003",
                username="viewer",
                email="viewer@zenitone.local",
                password_hash=get_password_hash("Viewer@123"),
                role="viewer",
                active=True
            ),
        ]
        
        for user in users:
            db.add(user)
        
        # Create subsystems
        subsystems = [
            Subsystem(
                name="JES",
                status="inactive",
                version="1.0.0",
                configuration='{"max_jobs": 1000, "spool_size": 10737418240}',
                statistics='{}'
            ),
            Subsystem(
                name="CICS",
                status="inactive",
                version="1.0.0",
                configuration='{"max_transactions": 10000, "timeout": 30}',
                statistics='{}'
            ),
            Subsystem(
                name="DB2",
                status="inactive",
                version="1.0.0",
                configuration='{"max_connections": 100, "cache_size": 536870912}',
                statistics='{}'
            ),
            Subsystem(
                name="TSO",
                status="inactive",
                version="1.0.0",
                configuration='{"max_sessions": 50, "timeout": 1800}',
                statistics='{}'
            ),
        ]
        
        for subsystem in subsystems:
            db.add(subsystem)
        
        # Create default configurations
        configurations = [
            Configuration(key="security.jwt_expiration", value="3600", category="security", description="JWT token expiration in seconds"),
            Configuration(key="security.rate_limit", value="100", category="security", description="API rate limit per minute"),
            Configuration(key="security.password_min_length", value="8", category="security", description="Minimum password length"),
            Configuration(key="resources.max_workloads", value="1000", category="resources", description="Maximum concurrent workloads"),
            Configuration(key="resources.max_containers", value="100", category="resources", description="Maximum concurrent containers"),
            Configuration(key="resources.default_cpu_limit", value="2", category="resources", description="Default CPU limit per workload"),
            Configuration(key="resources.default_memory_limit", value="1024", category="resources", description="Default memory limit in MB"),
            Configuration(key="ui.theme", value="dark", category="ui", description="Default UI theme"),
            Configuration(key="ui.refresh_interval", value="5", category="ui", description="Metrics refresh interval in seconds"),
        ]
        
        for config in configurations:
            db.add(config)
        
        db.commit()
        logger.info("Database seeded successfully")
        logger.info("Default users created:")
        logger.info("  - admin / Admin@123 (admin role)")
        logger.info("  - demo / Demo@123 (user role)")
        logger.info("  - viewer / Viewer@123 (viewer role)")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()
