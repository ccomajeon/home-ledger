from fastapi.testclient import TestClient

from app.config import get_settings
from app.db.models import AllowedAccount
from app.db.session import SessionLocal
from app.utils.security import create_session_token


def test_owner_manages_accounts(owner_client: TestClient) -> None:
    create_response = owner_client.post(
        "/api/admin/accounts",
        json={"email": "family@example.com", "role": "USER"},
    )
    assert create_response.status_code == 201
    account_id = create_response.json()["id"]

    update_response = owner_client.patch(
        f"/api/admin/accounts/{account_id}",
        json={"enabled": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["enabled"] is False

    logs = owner_client.get("/api/admin/audit-logs").json()
    assert {log["action"] for log in logs} >= {"account.create", "account.update"}


def test_regular_user_cannot_access_admin(owner_client: TestClient) -> None:
    with SessionLocal() as db:
        db.add(AllowedAccount(email="family@example.com", role="USER", enabled=True))
        db.commit()
    owner_client.cookies.set(
        get_settings().session_cookie_name,
        create_session_token("family@example.com"),
    )

    response = owner_client.get("/api/admin/accounts")

    assert response.status_code == 403
    assert response.json()["detail"] == "Owner role required"


def test_owner_cannot_disable_self(owner_client: TestClient) -> None:
    owner_id = owner_client.get("/api/me").json()["id"]

    response = owner_client.patch(
        f"/api/admin/accounts/{owner_id}",
        json={"enabled": False},
    )

    assert response.status_code == 400
