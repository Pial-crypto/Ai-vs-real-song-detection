"""Application-wide error handling and exception definitions."""

from __future__ import annotations

import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.logging_config import get_logger

logger = get_logger("app.errors")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any | None = None


class AppError(Exception):
    """Base application exception with HTTP status."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "APP_ERROR",
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: Any = None) -> None:
        msg = f"{resource} not found"
        if identifier is not None:
            msg = f"{resource} with id '{identifier}' not found"
        super().__init__(msg, status_code=404, code="NOT_FOUND")


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, status_code=409, code="CONFLICT")


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, status_code=401, code="UNAUTHORIZED")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status_code=403, code="FORBIDDEN")


class ValidationError(AppError):
    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message, status_code=422, code="VALIDATION_ERROR", details=details)


class FileValidationError(AppError):
    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message, status_code=415, code="FILE_VALIDATION_ERROR", details=details)


class RateLimitError(AppError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60) -> None:
        super().__init__(message, status_code=429, code="RATE_LIMITED", details={"retry_after": retry_after})
        self.retry_after = retry_after


def _error_response(status_code: int, code: str, message: str, details: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "Application error",
            extra={"path": str(request.url), "code": exc.code, "status": exc.status_code},
        )
        return _error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info("Request validation failed", extra={"path": str(request.url), "errors": exc.errors()})
        safe_errors = []
        for err in exc.errors():
            item = {k: v for k, v in err.items() if k != "ctx"}
            if "ctx" in err:
                item["ctx"] = {kk: str(vv) for kk, vv in err["ctx"].items()}
            safe_errors.append(item)
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "REQUEST_VALIDATION_ERROR",
            "Invalid request payload",
            safe_errors,
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            extra={"path": str(request.url), "exception": repr(exc)},
            exc_info=True,
        )
        if get_settings_debug():
            return _error_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "INTERNAL_ERROR",
                str(exc),
                traceback.format_exc().splitlines(),
            )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred",
            None,
        )


def get_settings_debug() -> bool:
    from backend.app.config import get_settings

    return get_settings().debug
