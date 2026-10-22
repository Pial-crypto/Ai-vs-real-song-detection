"""Backup and recovery routes (admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.deps import require_role
from backend.app.services.backup_service import (
    create_backup,
    list_backups,
    prune_old_backups,
)

router = APIRouter(prefix="/backups", tags=["backups"])


@router.post("/create")
def create(_admin=Depends(require_role("admin"))):
    path = create_backup()
    return {"status": "ok", "path": str(path) if path else None}


@router.get("")
def list_all(_admin=Depends(require_role("admin"))):
    return {"backups": [str(p) for p in list_backups()]}


@router.post("/prune")
def prune(_admin=Depends(require_role("admin"))):
    removed = prune_old_backups()
    return {"removed": removed}
