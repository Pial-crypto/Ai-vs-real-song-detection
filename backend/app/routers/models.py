"""Model metadata routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app import schemas
from backend.app.crud import list_model_metadata, register_model_metadata
from backend.app.database import get_db
from backend.app.deps import require_role

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[schemas.ModelMetadataOut])
def list_models(
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    return list_model_metadata(db)


@router.post("", response_model=schemas.ModelMetadataOut, status_code=201)
def register(
    name: str,
    version: str,
    accuracy: str = None,
    path: str = None,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    return register_model_metadata(db, name, version, accuracy, path)
