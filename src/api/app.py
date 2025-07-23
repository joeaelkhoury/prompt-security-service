# src/api/app.py
"""FastAPI application setup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.api.endpoints import health, analysis, metrics
from src.core.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(settings: Settings) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Prompt Security Service",
        description="Microservice for analyzing prompt similarity and security with graph-based intelligence",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts.split(','),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(analysis.router, tags=["analysis"])
    app.include_router(metrics.router, tags=["metrics"])
    
    # Try to import auth router if it exists
    try:
        from src.api.endpoints import auth
        app.include_router(auth.router, prefix="/auth", tags=["authentication"])
        logger.info("Authentication endpoints loaded")
    except ImportError:
        logger.warning("Authentication module not found, running without auth")
    
    # Error handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        """Handle validation errors."""
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        logger.info("Starting Prompt Security Service...")
        logger.info("Service started successfully")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info("Shutting down Prompt Security Service...")
        logger.info("Service stopped")
    
    return app