"""Security helpers: password hashing and JWT token management."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.config import get_settings
from backend.app.errors import UnauthorizedError
from backend.app.logging_config import get_logger

logger = get_logger("app.security")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    settings = get_settings()
    return pwd_context.hash(password, rounds=settings.bcrypt_rounds)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Password verification failed", extra={"error": str(exc)})
        return False


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        logger.info("Token decode failed", extra={"error": str(exc)})
        raise UnauthorizedError("Invalid or expired token")
    if payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid token type")
    if "sub" not in payload:
        raise UnauthorizedError("Token missing subject")
    return payload


def get_subject_from_token(token: str, expected_type: str = "access") -> str:
    payload = decode_token(token, expected_type=expected_type)
    return str(payload["sub"])
