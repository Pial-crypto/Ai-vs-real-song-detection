"""CRUD operations for database entities."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.errors import ConflictError, NotFoundError
from backend.app.logging_config import get_logger
from backend.app.utils import hash_password, verify_password

logger = get_logger("app.crud")


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_user(db: Session, user_data: schemas.UserCreate) -> models.User:
    if get_user_by_email(db, user_data.email):
        raise ConflictError("Email already registered")
    existing = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing:
        raise ConflictError("Username already taken")
    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
        role="user",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User created", extra={"user_id": db_user.id, "email": db_user.email})
    return db_user


def list_users(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[models.User], int]:
    query = db.query(models.User)
    total = query.count()
    items = query.order_by(models.User.id).offset(skip).limit(limit).all()
    return items, total


def create_prediction_history(db: Session, prediction_data: schemas.PredictionCreate) -> models.PredictionHistory:
    db_prediction = models.PredictionHistory(
        file_name=prediction_data.fileName,
        chunk_wise_prediction=prediction_data.chunkWisePrediction,
        model_wise_majority_prediction=prediction_data.modelWiseMajorityPrediction,
        final_prediction=prediction_data.finalPrediction,
        user_id=prediction_data.user_id,
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    logger.info("Prediction saved", extra={"prediction_id": db_prediction.id, "user_id": prediction_data.user_id})
    return db_prediction


def get_prediction_history_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> tuple[list[models.PredictionHistory], int]:
    query = db.query(models.PredictionHistory).filter(models.PredictionHistory.user_id == user_id)
    total = query.count()
    items = query.order_by(models.PredictionHistory.id.desc()).offset(skip).limit(limit).all()
    return items, total


def get_prediction_by_id(db: Session, prediction_id: int) -> models.PredictionHistory:
    prediction = db.query(models.PredictionHistory).filter(models.PredictionHistory.id == prediction_id).first()
    if not prediction:
        raise NotFoundError("Prediction", prediction_id)
    return prediction


def delete_prediction_by_id(db: Session, prediction_id: int) -> None:
    prediction = get_prediction_by_id(db, prediction_id)
    db.delete(prediction)
    db.commit()
    logger.info("Prediction deleted", extra={"prediction_id": prediction_id})


def add_dashboard(db: Session, prediction_id: int, dashboard_data: schemas.DashBoardCreate) -> models.DashBoard:
    prediction = get_prediction_by_id(db, prediction_id)
    db_dashboard = models.DashBoard(
        created_at=dashboard_data.createdAt,
        chunk_majority_prediction=dashboard_data.chunkMajorityPrediction,
        model_wise_majority_prediction=dashboard_data.modelWiseMajorityPrediction,
        user_id=dashboard_data.user_id,
        prediction_id=prediction.id,
    )
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    logger.info("Dashboard added", extra={"dashboard_id": db_dashboard.id, "prediction_id": prediction_id})
    return db_dashboard


def get_dashboards(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[models.DashBoard], int]:
    query = db.query(models.DashBoard)
    total = query.count()
    items = query.order_by(models.DashBoard.id.desc()).offset(skip).limit(limit).all()
    return items, total


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[models.User], int]:
    return list_users(db, skip=skip, limit=limit)


def count_predictions(db: Session) -> int:
    return db.query(func.count(models.PredictionHistory.id)).scalar() or 0
