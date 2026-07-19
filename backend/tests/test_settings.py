from fastapi.testclient import TestClient


def test_category_and_payment_method_management(owner_client: TestClient) -> None:
    category_response = owner_client.post("/api/categories", json={"name": "반려동물"})
    assert category_response.status_code == 201
    assert category_response.json()["name"] == "반려동물"

    duplicate_response = owner_client.post("/api/categories", json={"name": "반려동물"})
    assert duplicate_response.status_code == 409

    payment_response = owner_client.post(
        "/api/payment-methods", json={"name": "가족카드"}
    )
    assert payment_response.status_code == 201
    payment_id = payment_response.json()["id"]

    disable_response = owner_client.patch(
        f"/api/payment-methods/{payment_id}",
        json={"enabled": False},
    )
    assert disable_response.status_code == 200
    assert disable_response.json()["enabled"] is False
    enabled_names = {
        item["name"] for item in owner_client.get("/api/payment-methods").json()
    }
    assert "가족카드" not in enabled_names
