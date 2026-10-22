"""Batch prediction job routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import (
    create_batch_job,
    get_batch_job,
    list_batch_jobs,
    update_batch_job,
)
from backend.app.database import get_db
from backend.app.deps import get_current_user

router = APIRouter(prefix="/batch", tags=["batch"])


@router.post("", response_model=schemas.BatchJobOut, status_code=201)
def create_job(
    total_files: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if total_files < 1 or total_files > 100:
        from backend.app.errors import ValidationError

        raise ValidationError("total_files must be between 1 and 100")
    return create_batch_job(db, current_user.id, total_files)


@router.get("", response_model=list[schemas.BatchJobOut])
def list_jobs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items, _ = list_batch_jobs(db, current_user.id, skip=skip, limit=limit)
    return items


@router.get("/{job_id}", response_model=schemas.BatchJobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return get_batch_job(db, job_id, user_id=current_user.id)


@router.post("/{job_id}/progress")
def progress(
    job_id: int,
    processed_files: int,
    status: str = "running",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    job = update_batch_job(db, job_id, status=status, processed_files=processed_files)
    return job


@router.post("/{job_id}/complete")
def complete(
    job_id: int,
    results: dict = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    job = update_batch_job(db, job_id, results=results or {}, completed=True)
    return job
