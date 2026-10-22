"""Export job routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import complete_export_job, create_export_job
from backend.app.database import get_db
from backend.app.deps import get_current_user

router = APIRouter(prefix="/export", tags=["export"])


@router.post("", response_model=schemas.ExportJobOut, status_code=201)
def create_job(
    fmt: str = "json",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if fmt not in {"json", "csv"}:
        from backend.app.errors import ValidationError

        raise ValidationError("Unsupported export format")
    return create_export_job(db, current_user.id, fmt)


@router.post("/{job_id}/complete")
def complete_job(
    job_id: int,
    file_path: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return complete_export_job(db, job_id, file_path)
