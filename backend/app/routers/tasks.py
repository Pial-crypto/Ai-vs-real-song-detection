"""Task queue routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.deps import require_role
from backend.app.services.task_queue import get_task_queue

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/stats")
def stats(_admin=Depends(require_role("admin"))):
    return get_task_queue().stats()


@router.get("")
def list_tasks(_admin=Depends(require_role("admin"))):
    tasks = get_task_queue().list_tasks()
    return [{"id": t.id, "name": t.name, "status": t.status, "created_at": t.created_at} for t in tasks]
