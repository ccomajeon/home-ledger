from fastapi.testclient import TestClient

from app.config import get_settings
from app.utils.security import create_password_hash


def test_me_requires_authentication(test_client: TestClient) -> None:
    response = test_client.get("/api/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_me_returns_allowlisted_account(owner_client: TestClient) -> None:
    response = owner_client.get("/api/me")

    assert response.status_code == 200
    assert response.json()["email"] == "owner@example.com"
    assert response.json()["role"] == "OWNER"


def test_login_requires_oauth_configuration(test_client: TestClient) -> None:
    response = test_client.get("/auth/login")

    assert response.status_code == 503
    assert response.json()["detail"] == "Google OAuth is not configured"


def test_invalid_session_is_rejected(test_client: TestClient) -> None:
    test_client.cookies.set("home_ledger_session", "tampered")

    response = test_client.get("/api/me")

    assert response.status_code == 401


def test_local_admin_login_creates_owner_session(test_client: TestClient) -> None:
    settings = get_settings()
    previous = (
        settings.local_admin_enabled,
        settings.local_admin_username,
        settings.local_admin_password_hash,
        settings.local_admin_identity,
    )
    settings.local_admin_enabled = True
    settings.local_admin_username = "SYSTEM"
    settings.local_admin_password_hash = create_password_hash("test-password")
    settings.local_admin_identity = "system@local"
    try:
        response = test_client.post(
            "/auth/local-login",
            json={"username": "SYSTEM", "password": "test-password"},
        )

        assert response.status_code == 200
        assert response.json()["email"] == "system@local"
        assert response.json()["role"] == "OWNER"
        assert test_client.get("/api/me").status_code == 200
    finally:
        (
            settings.local_admin_enabled,
            settings.local_admin_username,
            settings.local_admin_password_hash,
            settings.local_admin_identity,
        ) = previous


def test_local_admin_login_rejects_invalid_password(test_client: TestClient) -> None:
    settings = get_settings()
    previous = (
        settings.local_admin_enabled,
        settings.local_admin_password_hash,
    )
    settings.local_admin_enabled = True
    settings.local_admin_password_hash = create_password_hash("test-password")
    try:
        response = test_client.post(
            "/auth/local-login",
            json={"username": "SYSTEM", "password": "wrong-password"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"
    finally:
        settings.local_admin_enabled, settings.local_admin_password_hash = previous
