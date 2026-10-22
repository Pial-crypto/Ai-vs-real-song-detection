from __future__ import annotations


def _token(client, email="nf@example.com"):
    client.post("/api/v1/auth/register", json={"username": "nfuser", "email": email, "password": "Secret123"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret123"})
    return r.json()["access_token"]


def test_notifications_flow(client):
    token = _token(client)
    h = {"Authorization": f"Bearer {token}"}
    r = client.post("/api/v1/notifications", json={"title": "hi", "message": "msg"}, headers=h)
    assert r.status_code == 201
    nid = r.json()["id"]
    r = client.get("/api/v1/notifications", headers=h)
    assert r.status_code == 200 and len(r.json()) == 1
    r = client.post(f"/api/v1/notifications/{nid}/read", headers=h)
    assert r.status_code == 200 and r.json()["read"] is True
    r = client.post("/api/v1/notifications/read-all", headers=h)
    assert r.status_code == 200


def test_profile_flow(client):
    token = _token(client, "pf@example.com")
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/profiles/me", headers=h)
    assert r.status_code == 200
    r = client.put("/api/v1/profiles/me", json={"display_name": "P", "bio": "hi"}, headers=h)
    assert r.status_code == 200
    assert r.json()["display_name"] == "P"


def test_feature_flags_admin(client):
    token = _token(client, "ff@example.com")
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/feature-flags", headers=h)
    assert r.status_code == 403


def test_batch_flow(client):
    token = _token(client, "bf@example.com")
    h = {"Authorization": f"Bearer {token}"}
    r = client.post("/api/v1/batch?total_files=3", headers=h)
    assert r.status_code == 201
    jid = r.json()["id"]
    r = client.get(f"/api/v1/batch/{jid}", headers=h)
    assert r.status_code == 200
    r = client.post(f"/api/v1/batch/{jid}/progress?processed_files=2&status=running", headers=h)
    assert r.status_code == 200
    r = client.post(f"/api/v1/batch/{jid}/complete", json={"a": 1}, headers=h)
    assert r.status_code == 200


def test_export_flow(client):
    token = _token(client, "ef@example.com")
    h = {"Authorization": f"Bearer {token}"}
    r = client.post("/api/v1/export?fmt=json", headers=h)
    assert r.status_code == 201
    jid = r.json()["id"]
    r = client.post(f"/api/v1/export/{jid}/complete?file_path=/tmp/x.json", headers=h)
    assert r.status_code == 200


def test_audit_admin_forbidden(client):
    token = _token(client, "af@example.com")
    h = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/audit", headers=h)
    assert r.status_code == 403
