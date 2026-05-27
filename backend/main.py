"""
ZenithOne Explorer - Main Application
FastAPI backend server with WebSocket support
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time

from config import settings
from database.connection import init_db, seed_database
from core.monitoring_service import monitoring_service
from utils.logger import get_logger

# Import routers
from api.routes import auth, workloads, containers, metrics, subsystems, admin

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting ZenithOne Explorer...")
    
    try:
        # Initialize database
        init_db()
        seed_database()
        
        # Start monitoring service
        from database.connection import SessionLocal
        db = SessionLocal()
        await monitoring_service.start(db)
        db.close()
        
        logger.info("ZenithOne Explorer started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ZenithOne Explorer...")
    
    try:
        # Stop monitoring service
        await monitoring_service.stop()
        
        logger.info("ZenithOne Explorer shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-grade workload management and container orchestration",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": str(exc) if settings.debug else None
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/api/docs" if settings.debug else None
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(workloads.router, prefix="/api/v1/workloads", tags=["Workloads"])
app.include_router(containers.router, prefix="/api/v1/containers", tags=["Containers"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(subsystems.router, prefix="/api/v1/subsystems", tags=["Subsystems"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administration"])


# Mount static files (UI)
if settings.debug:
    try:
        app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
    except:
        logger.warning("UI directory not found, static files not mounted")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
