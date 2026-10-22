"""Notification routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import (
    create_notification,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)
from backend.app.database import get_db
from backend.app.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationOut])
def list_mine(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items, _ = list_notifications(db, current_user.id, skip=skip, limit=limit, unread_only=unread_only)
    return items


@router.post("", response_model=schemas.NotificationOut, status_code=201)
def create(
    payload: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return create_notification(db, current_user.id, payload.title, payload.message, payload.level)


@router.post("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return mark_notification_read(db, notification_id, current_user.id)


@router.post("/read-all")
def read_all(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    mark_all_notifications_read(db, current_user.id)
    return {"status": "ok"}
