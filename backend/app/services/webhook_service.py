"""Webhook delivery service."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from backend.app.logging_config import get_logger

logger = get_logger("app.services.webhook")


@dataclass
class WebhookEndpoint:
    id: str
    url: str
    secret: Optional[str] = None
    events: List[str] = field(default_factory=list)
    active: bool = True
    failure_count: int = 0


@dataclass
class DeliveryResult:
    success: bool
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class WebhookService:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        self._endpoints: Dict[str, WebhookEndpoint] = {}

    def register(self, endpoint: WebhookEndpoint) -> None:
        self._endpoints[endpoint.id] = endpoint

    def unregister(self, endpoint_id: str) -> bool:
        return self._endpoints.pop(endpoint_id, None) is not None

    def list_endpoints(self) -> List[WebhookEndpoint]:
        return list(self._endpoints.values())

    def _sign(self, payload: bytes, secret: str) -> str:
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    def deliver(self, endpoint: WebhookEndpoint, event: str, data: Any) -> DeliveryResult:
        if not endpoint.active:
            return DeliveryResult(success=False, error="endpoint inactive")
        if endpoint.events and event not in endpoint.events:
            return DeliveryResult(success=False, error="event not subscribed")

        payload = {"event": event, "data": data, "timestamp": time.time()}
        body = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json", "X-Webhook-Event": event}
        if endpoint.secret:
            headers["X-Webhook-Signature"] = self._sign(body, endpoint.secret)

        start = time.time()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(endpoint.url, content=body, headers=headers)
            duration = (time.time() - start) * 1000
            success = 200 <= resp.status_code < 300
            if not success:
                endpoint.failure_count += 1
            return DeliveryResult(
                success=success,
                status_code=resp.status_code,
                response_body=resp.text[:500],
                duration_ms=round(duration, 2),
            )
        except Exception as exc:
            endpoint.failure_count += 1
            return DeliveryResult(success=False, error=str(exc), duration_ms=round((time.time() - start) * 1000, 2))

    def broadcast(self, event: str, data: Any) -> List[DeliveryResult]:
        results = []
        for ep in self._endpoints.values():
            if ep.active:
                results.append(self.deliver(ep, event, data))
        return results

    def retry_failed(self, max_failures: int = 5) -> int:
        # Re-enable endpoints that have recovered
        reactivated = 0
        for ep in self._endpoints.values():
            if not ep.active and ep.failure_count < max_failures:
                ep.active = True
                reactivated += 1
        return reactivated


_service = WebhookService()


def get_webhook_service() -> WebhookService:
    return _service
