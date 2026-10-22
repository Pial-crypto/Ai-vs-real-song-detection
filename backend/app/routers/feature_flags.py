"""Feature flag routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import is_feature_enabled, list_feature_flags, upsert_feature_flag
from backend.app.database import get_db
from backend.app.deps import get_current_user, require_role

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


@router.get("", response_model=list[schemas.FeatureFlagOut])
def list_flags(
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    return list_feature_flags(db)


@router.post("/{key}", response_model=schemas.FeatureFlagOut)
def upsert(
    key: str,
    payload: schemas.FeatureFlagUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    return upsert_feature_flag(db, key, payload.enabled, payload.description, payload.rollout_percent)


@router.get("/{key}/enabled")
def check_enabled(
    key: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return {"key": key, "enabled": is_feature_enabled(db, key, current_user.id)}
