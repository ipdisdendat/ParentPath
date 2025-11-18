"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from qdrant_client import QdrantClient
import redis
from datetime import datetime

from api.database import get_db
from api.config import settings
from api.services.qdrant_service import client as qdrant_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with dependency status"""
    checks = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "qdrant": "unknown",
        "timestamp": datetime.utcnow().isoformat()
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"

    # Check Qdrant
    try:
        collections = qdrant_client.get_collections()
        checks["qdrant"] = "healthy"
        checks["qdrant_collections"] = len(collections.collections)
    except Exception as e:
        checks["qdrant"] = f"unhealthy: {str(e)}"

    return checks


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement proper metrics
    return {
        "metrics": "not_implemented"
    }
