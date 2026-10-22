"""Tests for configuration."""

from __future__ import annotations


def test_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/x.db")
    monkeypatch.setenv("SECRET_KEY", "abc")
    from backend.app.config import get_settings, reset_settings_cache

    reset_settings_cache()
    s = get_settings()
    assert s.max_upload_size_bytes == s.max_upload_size_mb * 1024 * 1024
    assert s.is_production is False


def test_production_flag(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/x.db")
    monkeypatch.setenv("SECRET_KEY", "abc")
    monkeypatch.setenv("ENVIRONMENT", "production")
    from backend.app.config import get_settings, reset_settings_cache

    reset_settings_cache()
    s = get_settings()
    assert s.is_production is True
    reset_settings_cache()
