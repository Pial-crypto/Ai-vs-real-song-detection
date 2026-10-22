"""Prediction orchestration service with file validation."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from backend.app.config import get_settings
from backend.app.errors import FileValidationError
from backend.app.logging_config import get_logger
from backend.app.ml.inference import ensemble_predict

logger = get_logger("app.services.prediction")

_ALLOWED_MIMES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3",
    "audio/flac", "audio/ogg", "audio/mp4", "audio/x-m4a",
    "application/octet-stream",
}


def validate_upload(file: UploadFile) -> None:
    settings = get_settings()
    if file.filename is None or not file.filename.strip():
        raise FileValidationError("Missing file name")
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_audio_extensions:
        raise FileValidationError(
            f"Unsupported file extension '{ext}'",
            details={"allowed": settings.allowed_audio_extensions},
        )
    if file.content_type and file.content_type not in _ALLOWED_MIMES:
        logger.warning("Unexpected content type", extra={"content_type": file.content_type})


async def save_upload_to_temp(file: UploadFile) -> str:
    settings = get_settings()
    validate_upload(file)
    contents = await file.read()
    if len(contents) == 0:
        raise FileValidationError("Uploaded file is empty")
    if len(contents) > settings.max_upload_size_bytes:
        raise FileValidationError(
            f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
            details={"size_bytes": len(contents), "max_bytes": settings.max_upload_size_bytes},
        )
    suffix = Path(file.filename).suffix if file.filename else ""
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(contents)
    except Exception:
        os.remove(temp_path)
        raise
    logger.info("Upload saved", extra={"temp_path": temp_path, "size_bytes": len(contents)})
    return temp_path


def file_checksum(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_prediction(file_path: str) -> tuple[Any, Any]:
    settings = get_settings()
    chunk_preds, model_preds = ensemble_predict(
        file_path, chunk_sec=settings.chunk_sec, sr=settings.sample_rate
    )
    # Final decision logic
    from collections import Counter

    final_majority_counts = Counter([c["chunk_majority"] for c in chunk_preds])
    final_prediction = final_majority_counts.most_common(1)[0][0] if final_majority_counts else None
    final_model_vote = Counter(model_preds.values()).most_common(1)[0][0] if model_preds else None
    return chunk_preds, model_preds, final_prediction, final_model_vote


def cleanup_temp(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError as exc:
        logger.warning("Failed to remove temp file", extra={"path": path, "error": str(exc)})
