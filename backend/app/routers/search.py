"""Search routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app import models
from backend.app.database import get_db
from backend.app.deps import get_current_user, require_role
from backend.app.services.search_service import search_predictions, search_users

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/predictions")
def search_preds(
    q: str = Query(""),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = search_predictions(db, current_user.id, q, limit=limit)
    return {"results": items, "count": len(items)}


@router.get("/users")
def search_users_route(
    q: str = Query(""),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    items = search_users(db, q, limit=limit)
    return {"results": items, "count": len(items)}
