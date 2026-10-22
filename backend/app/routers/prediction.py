"""Prediction (file upload) routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.app import models, schemas
from backend.app.database import get_db
from backend.app.deps import get_optional_user
from backend.app.errors import FileValidationError
from backend.app.logging_config import get_logger
from backend.app.services.prediction_service import (
    cleanup_temp,
    run_prediction,
    save_upload_to_temp,
)

logger = get_logger("app.routers.prediction")

router = APIRouter(tags=["prediction"])


@router.post("/prediction")
async def predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_optional_user),
):
    temp_path = None
    try:
        temp_path = await save_upload_to_temp(file)
        chunk_preds, model_preds, final_prediction, final_model_vote = run_prediction(temp_path)

        # Persist prediction if user authenticated
        if current_user is not None:
            from backend.app.crud import create_prediction_history

            payload = schemas.PredictionCreate(
                chunkWisePrediction=chunk_preds,
                modelWiseMajorityPrediction=model_preds,
                fileName=file.filename or "unknown",
                finalPrediction={
                    "chunk_majority": final_prediction,
                    "model_majority": final_model_vote,
                },
                user_id=current_user.id,
            )
            try:
                create_prediction_history(db, payload)
            except Exception as exc:  # pragma: no cover - best effort
                logger.warning("Failed to persist prediction", extra={"error": str(exc)})

        return {
            "status": "success",
            "final_decision": {
                "chunk_majority": final_prediction,
                "model_majority": final_model_vote,
            },
            "chunk_predictions": chunk_preds,
            "model_predictions": model_preds,
        }
    except FileValidationError:
        raise
    except Exception as exc:
        logger.exception("Prediction failed", extra={"error": str(exc)})
        from backend.app.errors import AppError

        raise AppError(str(exc), status_code=500, code="PREDICTION_FAILED")
    finally:
        if temp_path:
            cleanup_temp(temp_path)
