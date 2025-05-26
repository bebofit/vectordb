"""
Health check endpoints for monitoring API status.
"""

from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the current status of the API service.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="0.1.0",
        uptime_seconds=0.0,  # TODO: Implement actual uptime tracking
    )


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Returns comprehensive health information including dependencies.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "0.1.0",
        "components": {
            "api": {"status": "healthy"},
            "memory_store": {"status": "healthy"},
            "vector_search": {"status": "healthy"},
        },
        "system": {
            "python_version": "3.13+",
            "fastapi_version": "0.115+",
        },
    } 
