import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_and_read_product():
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 9.99,
        "quantity": 5
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["price"] == product_data["price"]
    assert data["quantity"] == product_data["quantity"]
    product_id = data["id"]

    # Retrieve the product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == product_data["name"] 