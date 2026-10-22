"""Prediction history routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.crud import (
    create_prediction_history,
    delete_prediction_by_id,
    get_prediction_by_id,
    get_prediction_history_by_user,
)
from backend.app.database import get_db
from backend.app.deps import get_current_user

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("", response_model=schemas.PredictionOut, status_code=201)
def save_prediction(
    payload: schemas.PredictionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.user_id != current_user.id and current_user.role != "admin":
        from backend.app.errors import ForbiddenError

        raise ForbiddenError("Cannot save prediction for another user")
    return create_prediction_history(db, payload)


@router.get("/me", response_model=list[schemas.PredictionOut])
def my_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items, _ = get_prediction_history_by_user(db, current_user.id, skip=skip, limit=limit)
    return items


@router.get("/user/{user_id}", response_model=list[schemas.PredictionOut])
def predictions_for_user(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id != current_user.id and current_user.role != "admin":
        from backend.app.errors import ForbiddenError

        raise ForbiddenError("Cannot view another user's predictions")
    items, _ = get_prediction_history_by_user(db, user_id, skip=skip, limit=limit)
    return items


@router.get("/{prediction_id}", response_model=schemas.PredictionOut)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    pred = get_prediction_by_id(db, prediction_id)
    if pred.user_id != current_user.id and current_user.role != "admin":
        from backend.app.errors import ForbiddenError

        raise ForbiddenError("Cannot view another user's prediction")
    return pred


@router.delete("/{prediction_id}", status_code=204)
def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    pred = get_prediction_by_id(db, prediction_id)
    if pred.user_id != current_user.id and current_user.role != "admin":
        from backend.app.errors import ForbiddenError

        raise ForbiddenError("Cannot delete another user's prediction")
    delete_prediction_by_id(db, prediction_id)
