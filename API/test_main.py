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

def test_create_product_missing_fields():
    # Test missing required fields
    incomplete_data = {
        "name": "Incomplete Product"
        # Missing description, price, quantity
    }
    response = client.post("/products/", json=incomplete_data)
    assert response.status_code == 422  # Validation error

def test_create_product_invalid_price():
    # Test negative price
    product_data = {
        "name": "Invalid Price Product",
        "description": "Product with invalid price",
        "price": -10.99,
        "quantity": 5
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422

def test_create_product_invalid_quantity():
    # Test negative quantity
    product_data = {
        "name": "Invalid Quantity Product",
        "description": "Product with invalid quantity",
        "price": 19.99,
        "quantity": -1
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422

def test_create_product_zero_price():
    # Test zero price (might be valid for free products)
    product_data = {
        "name": "Free Product",
        "description": "A free product",
        "price": 0.0,
        "quantity": 10
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 0.0

def test_create_product_zero_quantity():
    # Test zero quantity (out of stock)
    product_data = {
        "name": "Out of Stock Product",
        "description": "Product with zero quantity",
        "price": 29.99,
        "quantity": 0
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 0

def test_create_product_unicode_characters():
    # Test with unicode characters in name and description
    product_data = {
        "name": "测试产品 🚀",
        "description": "Продукт для тестирования with émojis 🎉",
        "price": 15.50,
        "quantity": 3
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]

def test_create_product_empty_strings():
    # Test with empty strings
    product_data = {
        "name": "",
        "description": "",
        "price": 10.99,
        "quantity": 5
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200

def test_create_product_special_characters():
    # Test with special characters
    product_data = {
        "name": "Product with \"quotes\" & symbols!@#$%^&*()",
        "description": "Description with <html> tags & other symbols: <>?/\\|",
        "price": 12.34,
        "quantity": 7
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]

def test_read_nonexistent_product():
    # Test reading a product that doesn't exist
    response = client.get("/products/99999")
    assert response.status_code == 404

def test_read_invalid_product_id():
    # Test with invalid product ID format
    response = client.get("/products/invalid-id")
    assert response.status_code == 422

def test_get_all_products():
    # Test getting all products with default pagination
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_products_with_pagination():
    # Create multiple products first
    for i in range(15):
        product_data = {
            "name": f"Pagination Product {i}",
            "description": f"Product for pagination test {i}",
            "price": 10.0 + i,
            "quantity": i + 1
        }
        client.post("/products/", json=product_data)
    
    # Test pagination with skip and limit
    response = client.get("/products/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5

def test_get_products_invalid_pagination():
    # Test with negative skip/limit values
    response = client.get("/products/?skip=-1&limit=-1")
    assert response.status_code == 422

def test_update_product():
    # Create a product first
    product_data = {
        "name": "Original Product",
        "description": "Original description",
        "price": 20.00,
        "quantity": 5
    }
    create_response = client.post("/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Update the product
    updated_data = {
        "name": "Updated Product",
        "description": "Updated description",
        "price": 25.00,
        "quantity": 10
    }
    response = client.put(f"/products/{product_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_data["name"]
    assert data["description"] == updated_data["description"]
    assert data["price"] == updated_data["price"]
    assert data["quantity"] == updated_data["quantity"]
    assert data["id"] == product_id

def test_update_nonexistent_product():
    # Test updating a product that doesn't exist
    product_data = {
        "name": "Nonexistent Product",
        "description": "This shouldn't work",
        "price": 15.00,
        "quantity": 3
    }
    response = client.put("/products/99999", json=product_data)
    assert response.status_code == 404

def test_update_product_invalid_data():
    # Create a product first
    product_data = {
        "name": "Test Product",
        "description": "Test description",
        "price": 20.00,
        "quantity": 5
    }
    create_response = client.post("/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Try to update with invalid data
    invalid_data = {
        "name": "Updated Product",
        "description": "Updated description",
        "price": -10.00,  # Invalid negative price
        "quantity": 10
    }
    response = client.put(f"/products/{product_id}", json=invalid_data)
    assert response.status_code == 422

def test_delete_product():
    # Create a product first
    product_data = {
        "name": "Product to Delete",
        "description": "This product will be deleted",
        "price": 15.00,
        "quantity": 3
    }
    create_response = client.post("/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Delete the product
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"]
    
    # Verify the product is deleted
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_product():
    # Test deleting a product that doesn't exist
    response = client.delete("/products/99999")
    assert response.status_code == 404

def test_delete_invalid_product_id():
    # Test deleting with invalid product ID format
    response = client.delete("/products/invalid-id")
    assert response.status_code == 422

def test_create_multiple_products():
    # Test creating multiple products and ensure they have unique IDs
    products = []
    for i in range(5):
        product_data = {
            "name": f"Multiple Product {i}",
            "description": f"Description for product {i}",
            "price": 10.0 + i,
            "quantity": 5 + i
        }
        response = client.post("/products/", json=product_data)
        assert response.status_code == 200
        data = response.json()
        products.append(data)
        assert "id" in data
    
    # Ensure all products have unique IDs
    ids = [p["id"] for p in products]
    assert len(ids) == len(set(ids))

def test_malformed_json():
    # Test with malformed JSON
    response = client.post("/products/", data="invalid json")
    assert response.status_code == 422

def test_empty_request_body():
    # Test with empty request body
    response = client.post("/products/")
    assert response.status_code == 422

def test_extra_fields_ignored():
    # Test with extra fields that should be ignored
    product_data = {
        "name": "Extra Fields Product",
        "description": "Testing extra fields",
        "price": 15.99,
        "quantity": 4,
        "extra_field": "should be ignored",
        "another_extra": 123
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    # Extra fields should not be in the response
    assert "extra_field" not in data
    assert "another_extra" not in data

@pytest.mark.parametrize("price,quantity,expected_status", [
    (10.99, 5, 200),
    (0.01, 1, 200),
    (999.99, 100, 200),
    (-1.00, 5, 422),
    (10.99, -1, 422),
    (0, 0, 200),
])
def test_create_product_parametrized(price, quantity, expected_status):
    # Parametrized test for various price/quantity combinations
    product_data = {
        "name": f"Param Test Product {price}_{quantity}",
        "description": f"Testing price {price} and quantity {quantity}",
        "price": price,
        "quantity": quantity
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == expected_status

def test_api_response_structure():
    # Test that API responses have the expected structure
    product_data = {
        "name": "Structure Test Product",
        "description": "Testing response structure",
        "price": 20.00,
        "quantity": 3
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields are present
    required_fields = ["id", "name", "description", "price", "quantity"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check data types
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["description"], str)
    assert isinstance(data["price"], (int, float))
    assert isinstance(data["quantity"], int)

def test_crud_workflow():
    # Test complete CRUD workflow
    # Create
    product_data = {
        "name": "CRUD Test Product",
        "description": "Testing complete CRUD workflow",
        "price": 30.00,
        "quantity": 8
    }
    create_response = client.post("/products/", json=product_data)
    assert create_response.status_code == 200
    created_product = create_response.json()
    product_id = created_product["id"]
    
    # Read
    read_response = client.get(f"/products/{product_id}")
    assert read_response.status_code == 200
    read_product = read_response.json()
    assert read_product["name"] == product_data["name"]
    
    # Update
    updated_data = {
        "name": "Updated CRUD Product",
        "description": "Updated description",
        "price": 35.00,
        "quantity": 12
    }
    update_response = client.put(f"/products/{product_id}", json=updated_data)
    assert update_response.status_code == 200
    updated_product = update_response.json()
    assert updated_product["name"] == updated_data["name"]
    assert updated_product["price"] == updated_data["price"]
    
    # Delete
    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    final_read_response = client.get(f"/products/{product_id}")
    assert final_read_response.status_code == 404

def test_database_persistence():
    # Test that data persists across multiple requests
    product_data = {
        "name": "Persistence Test Product",
        "description": "Testing database persistence",
        "price": 40.00,
        "quantity": 15
    }
    
    # Create product
    create_response = client.post("/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Read multiple times to ensure persistence
    for _ in range(3):
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == product_data["name"]
        assert data["price"] == product_data["price"]

def test_concurrent_operations():
    # Test concurrent create and read operations
    import concurrent.futures

    results = []

    def create_and_read_product(index):
        product_data = {
            "name": f"Concurrent Product {index}",
            "description": f"Product created concurrently {index}",
            "price": 10.0 + index,
            "quantity": index + 1
        }
        # Create
        create_response = client.post("/products/", json=product_data)
        if create_response.status_code == 200:
            product_id = create_response.json()["id"]
            # Read
            read_response = client.get(f"/products/{product_id}")
            return read_response.status_code == 200
        return False

    # Run concurrent operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_and_read_product, i) for i in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # All operations should succeed
    assert all(results)

def test_data_type_coercion():
    # Test that API handles different numeric formats correctly
    product_data = {
        "name": "Type Coercion Test",
        "description": "Testing data type handling",
        "price": "19.99",  # String that should be converted to float
        "quantity": "5"    # String that should be converted to int
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["price"], (int, float))
    assert isinstance(data["quantity"], int)

def test_large_dataset_operations():
    # Test operations with larger datasets
    # Create multiple products
    product_ids = []
    for i in range(20):
        product_data = {
            "name": f"Large Dataset Product {i}",
            "description": f"Product {i} for large dataset test",
            "price": 10.0 + (i * 0.5),
            "quantity": i + 1
        }
        response = client.post("/products/", json=product_data)
        assert response.status_code == 200
        product_ids.append(response.json()["id"])
    
    # Test reading all products
    response = client.get("/products/?limit=25")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 20

def test_edge_case_values():
    # Test with edge case values
    edge_cases = [
        {"price": 0.01, "quantity": 1},      # Minimum positive values
        {"price": 999999.99, "quantity": 999999},  # Very large values
        {"price": 0.001, "quantity": 1},     # Very small price
    ]
    
    for i, case in enumerate(edge_cases):
        product_data = {
            "name": f"Edge Case Product {i}",
            "description": f"Testing edge case {i}",
            "price": case["price"],
            "quantity": case["quantity"]
        }
        response = client.post("/products/", json=product_data)
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == case["price"]
        assert data["quantity"] == case["quantity"]

def test_update_partial_fields():
    # Create a product
    product_data = {
        "name": "Partial Update Test",
        "description": "Original description",
        "price": 25.00,
        "quantity": 5
    }
    create_response = client.post("/products/", json=product_data)
    product_id = create_response.json()["id"]
    
    # Update with all fields (FastAPI PUT requires all fields)
    updated_data = {
        "name": "Updated Name Only",
        "description": "Original description",  # Keep original
        "price": 25.00,  # Keep original
        "quantity": 5     # Keep original
    }
    response = client.put(f"/products/{product_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name Only"
    assert data["description"] == "Original description"

def test_error_response_format():
    # Test that error responses have consistent format
    response = client.get("/products/99999")
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data
    assert error_data["detail"] == "Product not found"