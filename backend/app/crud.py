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


# ---------------- Audit Logs ----------------
def create_audit_log(db: Session, user_id, action, resource=None, resource_id=None, details=None, ip_address=None, user_agent=None):
    entry = models.AuditLog(
        user_id=user_id, action=action, resource=resource, resource_id=resource_id,
        details=details, ip_address=ip_address, user_agent=user_agent,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_audit_logs(db: Session, skip=0, limit=100, user_id=None, action=None):
    q = db.query(models.AuditLog)
    if user_id is not None:
        q = q.filter(models.AuditLog.user_id == user_id)
    if action is not None:
        q = q.filter(models.AuditLog.action == action)
    total = q.count()
    items = q.order_by(models.AuditLog.id.desc()).offset(skip).limit(limit).all()
    return items, total


# ---------------- Notifications ----------------
def create_notification(db: Session, user_id, title, message, level="info"):
    n = models.Notification(user_id=user_id, title=title, message=message, level=level)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def list_notifications(db: Session, user_id, skip=0, limit=50, unread_only=False):
    q = db.query(models.Notification).filter(models.Notification.user_id == user_id)
    if unread_only:
        q = q.filter(models.Notification.read.is_(False))
    total = q.count()
    items = q.order_by(models.Notification.id.desc()).offset(skip).limit(limit).all()
    return items, total


def mark_notification_read(db: Session, notification_id, user_id):
    n = db.query(models.Notification).filter(models.Notification.id == notification_id, models.Notification.user_id == user_id).first()
    if not n:
        raise NotFoundError("Notification", notification_id)
    n.read = True
    db.commit()
    db.refresh(n)
    return n


def mark_all_notifications_read(db: Session, user_id):
    db.query(models.Notification).filter(models.Notification.user_id == user_id, models.Notification.read.is_(False)).update({"read": True})
    db.commit()


# ---------------- Feature Flags ----------------
def get_feature_flag(db: Session, key):
    return db.query(models.FeatureFlag).filter(models.FeatureFlag.key == key).first()


def list_feature_flags(db: Session):
    return db.query(models.FeatureFlag).order_by(models.FeatureFlag.key).all()


def upsert_feature_flag(db: Session, key, enabled=None, description=None, rollout_percent=None):
    flag = get_feature_flag(db, key)
    if flag is None:
        flag = models.FeatureFlag(key=key, enabled=enabled or False, description=description, rollout_percent=rollout_percent if rollout_percent is not None else 100)
        db.add(flag)
    else:
        if enabled is not None:
            flag.enabled = enabled
        if description is not None:
            flag.description = description
        if rollout_percent is not None:
            flag.rollout_percent = rollout_percent
    db.commit()
    db.refresh(flag)
    return flag


def is_feature_enabled(db: Session, key, user_id=None):
    flag = get_feature_flag(db, key)
    if flag is None or not flag.enabled:
        return False
    if flag.rollout_percent >= 100:
        return True
    if user_id is None:
        return True
    # deterministic rollout based on user_id
    return (user_id * 31 + len(key)) % 100 < flag.rollout_percent


# ---------------- Model Metadata ----------------
def list_model_metadata(db: Session, active_only=True):
    q = db.query(models.ModelMetadata)
    if active_only:
        q = q.filter(models.ModelMetadata.is_active.is_(True))
    return q.order_by(models.ModelMetadata.name).all()


def register_model_metadata(db: Session, name, version, accuracy=None, path=None):
    m = models.ModelMetadata(name=name, version=version, accuracy=accuracy, path=path, is_active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


# ---------------- User Profiles ----------------
def get_user_profile(db: Session, user_id):
    return db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()


def upsert_user_profile(db: Session, user_id, display_name=None, avatar_url=None, preferences=None, bio=None):
    profile = get_user_profile(db, user_id)
    if profile is None:
        profile = models.UserProfile(user_id=user_id, display_name=display_name, avatar_url=avatar_url, preferences=preferences, bio=bio)
        db.add(profile)
    else:
        if display_name is not None:
            profile.display_name = display_name
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if preferences is not None:
            profile.preferences = preferences
        if bio is not None:
            profile.bio = bio
    db.commit()
    db.refresh(profile)
    return profile


# ---------------- Batch Jobs ----------------
def create_batch_job(db: Session, user_id, total_files):
    job = models.BatchJob(user_id=user_id, total_files=total_files, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_batch_job(db: Session, job_id, status=None, processed_files=None, results=None, error=None, completed=False):
    job = db.query(models.BatchJob).filter(models.BatchJob.id == job_id).first()
    if not job:
        raise NotFoundError("BatchJob", job_id)
    if status is not None:
        job.status = status
    if processed_files is not None:
        job.processed_files = processed_files
    if results is not None:
        job.results = results
    if error is not None:
        job.error = error
    if completed:
        from datetime import datetime, timezone
        job.completed_at = datetime.now(timezone.utc)
        job.status = "completed"
    db.commit()
    db.refresh(job)
    return job


def get_batch_job(db: Session, job_id, user_id=None):
    q = db.query(models.BatchJob).filter(models.BatchJob.id == job_id)
    if user_id is not None:
        q = q.filter(models.BatchJob.user_id == user_id)
    job = q.first()
    if not job:
        raise NotFoundError("BatchJob", job_id)
    return job


def list_batch_jobs(db: Session, user_id, skip=0, limit=50):
    q = db.query(models.BatchJob).filter(models.BatchJob.user_id == user_id)
    total = q.count()
    items = q.order_by(models.BatchJob.id.desc()).offset(skip).limit(limit).all()
    return items, total


# ---------------- Export Jobs ----------------
def create_export_job(db: Session, user_id, fmt="json"):
    job = models.ExportJob(user_id=user_id, format=fmt, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def complete_export_job(db: Session, job_id, file_path):
    job = db.query(models.ExportJob).filter(models.ExportJob.id == job_id).first()
    if not job:
        raise NotFoundError("ExportJob", job_id)
    job.status = "completed"
    job.file_path = file_path
    from datetime import datetime, timezone
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
