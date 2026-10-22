"""User management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.crud import get_user_by_id, list_users
from backend.app.database import get_db
from backend.app.deps import require_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    items, _ = list_users(db, skip=skip, limit=limit)
    return items


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _admin=Depends(require_role("admin"))):
    user = get_user_by_id(db, user_id)
    if user is None:
        from backend.app.errors import NotFoundError

        raise NotFoundError("User", user_id)
    return user
