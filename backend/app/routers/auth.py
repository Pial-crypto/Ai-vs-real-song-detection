"""Authentication routes: register, login, refresh, me."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.config import get_settings
from backend.app.crud import authenticate_user, create_user
from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.errors import UnauthorizedError
from backend.app.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
    return create_user(db, payload)


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)) -> schemas.TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise UnauthorizedError("Invalid email or password")
    settings = get_settings()
    access = create_access_token(str(user.id), extra={"role": user.role, "email": user.email})
    refresh = create_refresh_token(str(user.id))
    return schemas.TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=schemas.TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> schemas.TokenResponse:
    payload = decode_token(refresh_token, expected_type="refresh")
    user_id = int(payload["sub"])
    from backend.app.crud import get_user_by_id

    user = get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("User not found")
    settings = get_settings()
    access = create_access_token(str(user.id), extra={"role": user.role, "email": user.email})
    new_refresh = create_refresh_token(str(user.id))
    return schemas.TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)) -> models.User:
    return current_user
