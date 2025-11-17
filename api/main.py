"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from api.config import settings
from api.database import init_db
from api.routers import health, intake, admin, family, webhooks
from api.services.qdrant_service import init_qdrant_collections

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting ParentPath API...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Initialize Qdrant collections
        await init_qdrant_collections()
        logger.info("Qdrant collections initialized")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down ParentPath API...")


# Create FastAPI app
app = FastAPI(
    title="ParentPath API",
    description="AI-Powered Educational Equity Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else ["https://parentpath.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(intake.router, prefix="/api/v1/intake", tags=["Intake"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(family.router, prefix="/api/v1/family", tags=["Family"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ParentPath API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
