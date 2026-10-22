"""Audit logging middleware."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.app.crud import create_audit_log
from backend.app.database import get_session_factory
from backend.app.logging_config import get_logger

logger = get_logger("app.middleware.audit")


class AuditMiddleware(BaseHTTPMiddleware):
    SKIP_PATHS = {"/health", "/ready", "/", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        response = await call_next(request)
        path = request.url.path
        if path in self.SKIP_PATHS or path.startswith("/static"):
            return response
        try:
            db = get_session_factory()()
            user_id = getattr(request.state, "user_id", None)
            create_audit_log(
                db,
                user_id=user_id,
                action=f"{request.method} {path}",
                resource=path.split("/")[1] if path.startswith("/") else None,
                details={"status_code": response.status_code, "duration_ms": round((time.time() - start) * 1000, 2)},
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
            db.close()
        except Exception as exc:
            logger.warning("Audit log failed", extra={"error": str(exc)})
        return response
