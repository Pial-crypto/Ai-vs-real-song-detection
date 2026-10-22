"""Health and readiness routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.config import get_settings
from backend.app.database import check_db_health, get_db

router = APIRouter(tags=["health"])


@router.get("/health", response_model=schemas.HealthResponse)
def health(db: Session = Depends(get_db)) -> schemas.HealthResponse:
    settings = get_settings()
    db_ok = check_db_health()
    return schemas.HealthResponse(
        status="ok" if db_ok else "degraded",
        version=settings.app_version,
        database=db_ok,
        environment=settings.environment,
    )


@router.get("/ready")
def ready() -> dict:
    settings = get_settings()
    return {"ready": True, "environment": settings.environment}


@router.get("/")
def root() -> dict:
    settings = get_settings()
    return {"message": f"{settings.app_name} running", "version": settings.app_version}
