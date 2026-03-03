from fastapi.testclient import TestClient


def test_me_requires_authentication(test_client: TestClient) -> None:
    response = test_client.get("/api/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"

