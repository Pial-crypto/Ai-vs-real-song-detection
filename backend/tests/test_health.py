"""Tests for health endpoints."""

from __future__ import annotations


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "running" in r.json()["message"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in {"ok", "degraded"}
    assert data["database"] is True


def test_ready(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["ready"] is True
