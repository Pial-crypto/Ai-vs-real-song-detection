"""Metrics endpoint (Prometheus format)."""

from __future__ import annotations

from fastapi import APIRouter, Response

from backend.app.services.metrics_service import get_metrics_registry

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics() -> Response:
    registry = get_metrics_registry()
    return Response(content=registry.render_all(), media_type="text/plain; version=0.0.4")
