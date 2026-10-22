"""User profile routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import get_user_profile, upsert_user_profile
from backend.app.database import get_db
from backend.app.deps import get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=schemas.UserProfileOut)
def get_mine(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    profile = get_user_profile(db, current_user.id)
    if profile is None:
        profile = upsert_user_profile(db, current_user.id)
    return profile


@router.put("/me", response_model=schemas.UserProfileOut)
def update_mine(
    payload: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return upsert_user_profile(
        db,
        current_user.id,
        display_name=payload.display_name,
        avatar_url=payload.avatar_url,
        preferences=payload.preferences,
        bio=payload.bio,
    )
