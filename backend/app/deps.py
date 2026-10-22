"""FastAPI dependency helpers."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app import models
from backend.app.crud import get_user_by_email, get_user_by_id
from backend.app.database import get_db
from backend.app.errors import ForbiddenError, UnauthorizedError
from backend.app.security import get_subject_from_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Missing authentication token")
    subject = get_subject_from_token(credentials.credentials, expected_type="access")
    try:
        user_id = int(subject)
        user = get_user_by_id(db, user_id)
    except ValueError:
        user = get_user_by_email(db, subject)
    if user is None:
        raise UnauthorizedError("User not found")
    return user


def require_role(*roles: str):
    allowed = set(roles) | {"admin"}

    def _guard(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in allowed:
            raise ForbiddenError("Insufficient permissions")
        return user

    return _guard


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User | None:
    if credentials is None or not credentials.credentials:
        return None
    try:
        subject = get_subject_from_token(credentials.credentials, expected_type="access")
    except Exception:
        return None
    try:
        user_id = int(subject)
        return get_user_by_id(db, user_id)
    except ValueError:
        return get_user_by_email(db, subject)
