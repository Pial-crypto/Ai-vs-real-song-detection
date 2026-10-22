"""Audit log routes (admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.crud import list_audit_logs
from backend.app.database import get_db
from backend.app.deps import require_role

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[schemas.AuditLogOut])
def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: int = Query(None),
    action: str = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    items, _ = list_audit_logs(db, skip=skip, limit=limit, user_id=user_id, action=action)
    return items
