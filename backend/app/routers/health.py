"""
Health check router — GET /api/v1/health
Returns application status and version.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns 200 if the application is running. Use this for liveness probes.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )
