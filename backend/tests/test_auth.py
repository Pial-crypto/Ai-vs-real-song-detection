"""Tests for authentication flows."""

from __future__ import annotations


def test_register_and_login(client):
    payload = {"username": "alice", "email": "alice@example.com", "password": "Secret123"}
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"

    r = client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "Secret123"})
    assert r.status_code == 200, r.text
    tok = r.json()
    assert "access_token" in tok
    assert tok["token_type"] == "bearer"

    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tok['access_token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"


def test_login_invalid(client):
    client.post("/api/v1/auth/register", json={"username": "bob", "email": "bob@example.com", "password": "Secret123"})
    r = client.post("/api/v1/auth/login", json={"email": "bob@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_password_policy(client):
    r = client.post("/api/v1/auth/register", json={"username": "weak", "email": "weak@example.com", "password": "password"})
    assert r.status_code == 422


def test_duplicate_email(client):
    p = {"username": "userone", "email": "dup@example.com", "password": "Secret123"}
    client.post("/api/v1/auth/register", json=p)
    r = client.post("/api/v1/auth/register", json={"username": "usertwo", "email": "dup@example.com", "password": "Secret123"})
    assert r.status_code == 409


def test_refresh_token(client):
    client.post("/api/v1/auth/register", json={"username": "ruser", "email": "r@example.com", "password": "Secret123"})
    r = client.post("/api/v1/auth/login", json={"email": "r@example.com", "password": "Secret123"})
    tok = r.json()
    r = client.post("/api/v1/auth/refresh", params={"refresh_token": tok["refresh_token"]})
    assert r.status_code == 200
    assert "access_token" in r.json()
