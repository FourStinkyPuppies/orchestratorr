"""
Main FastAPI application for orchestratorr backend.

Unified *arr API proxy with comprehensive error handling and CORS support.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.routes import proxy_router
from backend.routes import search_router
from backend.routes import activity_router

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup and shutdown.

    Handles any initialization and cleanup needed for the application.
    """
    logger.info("Starting orchestratorr backend")
    yield
    logger.info("Shutting down orchestratorr backend")


# Initialize FastAPI app
app = FastAPI(
    title="Orchestratorr",
    description="Unified front-end for the *arr suite (Radarr, Sonarr, Lidarr, Prowlarr)",
    version="0.1.0",
    lifespan=lifespan,
)

# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for origins: {settings.allowed_origins}")

# ============================================================================
# Route Registration
# ============================================================================

app.include_router(proxy_router)
app.include_router(search_router)
app.include_router(activity_router)

# ============================================================================
# Health Check Endpoint
# ============================================================================


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for load balancers and monitors.

    Returns:
        dict: Status and version information
    """
    return {
        "status": "healthy",
        "service": "orchestratorr",
        "version": "0.1.0",
    }


@app.get("/api/v1/health")
async def api_health_check() -> dict:
    """
    API version-specific health check endpoint.

    Returns:
        dict: Status and version information
    """
    return {
        "status": "healthy",
        "service": "orchestratorr",
        "version": "0.1.0",
        "api_version": "v1",
    }


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/")
async def root() -> dict:
    """
    Root endpoint with service information.

    Returns:
        dict: Service metadata and available endpoints
    """
    return {
        "service": "Orchestratorr",
        "description": "Unified front-end for the *arr suite",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "api_health": "/api/v1/health",
            "proxy": "/api/v1/proxy",
            "radarr": "/api/v1/proxy/radarr",
        },
        "docs": "/docs",
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Global exception handler for unexpected errors.

    Logs the error and returns a generic error response without exposing
    sensitive details.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Orchestratorr backend initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Orchestratorr backend shutdown")


if __name__ == "__main__":
    import uvicorn

    # Run with: python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
