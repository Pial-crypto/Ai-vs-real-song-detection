"""Dashboard routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import add_dashboard, get_dashboards
from backend.app.database import get_db
from backend.app.deps import get_current_user

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post("/{prediction_id}", response_model=schemas.DashBoardOut, status_code=201)
def create_dashboard(
    prediction_id: int,
    payload: schemas.DashBoardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return add_dashboard(db, prediction_id, payload)


@router.get("", response_model=list[schemas.DashBoardOut])
def list_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items, _ = get_dashboards(db, skip=skip, limit=limit)
    return items
