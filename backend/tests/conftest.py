"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.config import reset_settings_cache
from backend.app.database import reset_engine
from backend.app.main import create_app
from backend.app.ml.inference import reset_models


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-1234567890")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("MODEL_DIR", str(tmp_path / "models"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    reset_settings_cache()
    reset_engine()
    reset_models()
    yield
    reset_settings_cache()
    reset_engine()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c
