"""Cache management routes (admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.deps import require_role
from backend.app.services.cache_service import get_cache

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats")
def stats(_admin=Depends(require_role("admin"))):
    return get_cache().stats()


@router.post("/clear")
def clear(_admin=Depends(require_role("admin"))):
    get_cache().clear()
    return {"status": "ok"}
