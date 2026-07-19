from fastapi.testclient import TestClient


def _defaults(client: TestClient) -> tuple[int, int]:
    categories = client.get("/api/categories").json()
    payment_methods = client.get("/api/payment-methods").json()
    return categories[0]["id"], payment_methods[0]["id"]


def test_transaction_crud_and_summary(owner_client: TestClient) -> None:
    category_id, payment_method_id = _defaults(owner_client)
    create_response = owner_client.post(
        "/api/transactions",
        json={
            "tx_date": "2026-07-19",
            "amount": "12500.50",
            "tx_type": "EXPENSE",
            "description": "주말 장보기",
            "category_id": category_id,
            "payment_method_id": payment_method_id,
        },
    )
    assert create_response.status_code == 201
    transaction = create_response.json()
    assert transaction["description"] == "주말 장보기"
    assert transaction["amount"] == "12500.50"

    list_response = owner_client.get("/api/transactions", params={"search": "장보기"})
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [transaction["id"]]

    update_response = owner_client.patch(
        f"/api/transactions/{transaction['id']}",
        json={"amount": "10000.00"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["amount"] == "10000.00"

    summary_response = owner_client.get("/api/transactions/summary")
    assert summary_response.status_code == 200
    assert summary_response.json() == {
        "income": "0.00",
        "expense": "10000.00",
        "balance": "-10000.00",
    }

    delete_response = owner_client.delete(f"/api/transactions/{transaction['id']}")
    assert delete_response.status_code == 200
    assert owner_client.get("/api/transactions").json() == []


def test_transaction_rejects_disabled_reference(owner_client: TestClient) -> None:
    category_id, payment_method_id = _defaults(owner_client)
    owner_client.patch(f"/api/categories/{category_id}", json={"enabled": False})

    response = owner_client.post(
        "/api/transactions",
        json={
            "tx_date": "2026-07-19",
            "amount": "1000",
            "tx_type": "EXPENSE",
            "category_id": category_id,
            "payment_method_id": payment_method_id,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Category is not available"


def test_transactions_require_authentication(test_client: TestClient) -> None:
    assert test_client.get("/api/transactions").status_code == 401
