"""Tests for security helpers."""

from __future__ import annotations

from backend.app.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("Secret123")
    assert verify_password("Secret123", h) is True
    assert verify_password("wrong", h) is False


def test_token_roundtrip():
    token = create_access_token("42", extra={"role": "user"})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_token_type_mismatch():
    import pytest

    from backend.app.errors import UnauthorizedError

    refresh = __import__("backend.app.security", fromlist=["create_refresh_token"]).create_refresh_token("42")
    with pytest.raises(UnauthorizedError):
        decode_token(refresh, expected_type="access")
