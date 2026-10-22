"""Tests for prediction history endpoints."""

from __future__ import annotations


def _register_login(client, email="p@example.com"):
    client.post("/api/v1/auth/register", json={"username": "ptest", "email": email, "password": "Secret123"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret123"})
    return r.json()["access_token"]


def test_save_and_list_predictions(client):
    token = _register_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "chunkWisePrediction": [{"chunk_majority": "real"}],
        "modelWiseMajorityPrediction": {"cnn": "real"},
        "fileName": "song.wav",
        "finalPrediction": {"chunk_majority": "real", "model_majority": "real"},
        "user_id": 1,
    }
    r = client.post("/api/v1/predictions", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    r = client.get("/api/v1/predictions/me", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get(f"/api/v1/predictions/{pid}", headers=headers)
    assert r.status_code == 200

    r = client.delete(f"/api/v1/predictions/{pid}", headers=headers)
    assert r.status_code == 204


def test_prediction_forbidden_other_user(client):
    t1 = _register_login(client, "a@example.com")
    # second user
    client.post("/api/v1/auth/register", json={"username": "other", "email": "b@example.com", "password": "Secret123"})
    r = client.post("/api/v1/auth/login", json={"email": "b@example.com", "password": "Secret123"})
    t2 = r.json()["access_token"]

    payload = {
        "chunkWisePrediction": [],
        "modelWiseMajorityPrediction": {},
        "fileName": "x.wav",
        "finalPrediction": {},
        "user_id": 1,
    }
    r = client.post("/api/v1/predictions", json=payload, headers={"Authorization": f"Bearer {t2}"})
    assert r.status_code == 403
