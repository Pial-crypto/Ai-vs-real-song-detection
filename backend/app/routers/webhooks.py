"""Webhook management routes (admin)."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.deps import require_role
from backend.app.services.webhook_service import WebhookEndpoint, get_webhook_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class WebhookCreate(BaseModel):
    url: str
    secret: Optional[str] = None
    events: List[str] = []


@router.get("")
def list_hooks(_admin=Depends(require_role("admin"))):
    svc = get_webhook_service()
    return [{"id": e.id, "url": e.url, "events": e.events, "active": e.active, "failure_count": e.failure_count} for e in svc.list_endpoints()]


@router.post("", status_code=201)
def register_hook(payload: WebhookCreate, _admin=Depends(require_role("admin"))):
    import uuid
    svc = get_webhook_service()
    ep = WebhookEndpoint(id=str(uuid.uuid4()), url=payload.url, secret=payload.secret, events=payload.events)
    svc.register(ep)
    return {"id": ep.id, "url": ep.url}


@router.post("/{endpoint_id}/test")
def test_hook(endpoint_id: str, _admin=Depends(require_role("admin"))):
    svc = get_webhook_service()
    ep = next((e for e in svc.list_endpoints() if e.id == endpoint_id), None)
    if ep is None:
        from backend.app.errors import NotFoundError

        raise NotFoundError("Webhook", endpoint_id)
    result = svc.deliver(ep, "test", {"message": "ping"})
    return {"success": result.success, "status_code": result.status_code, "error": result.error}
