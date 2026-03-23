import pytest
import requests
from conftest import BASE_URL


@pytest.fixture
def empty_cart(auth_headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)


def test_cart_add_valid(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 2})
    assert resp.status_code == 200
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    assert len(cart.get("items", [])) == 1


@pytest.mark.xfail(reason="BUG: API allows adding quantity=0 instead of returning 400")
def test_cart_add_invalid_quantity_zero(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 0})
    assert resp.status_code == 400


# Fix 12: checked above — API correctly returns 400 for -1. No xfail needed.
def test_cart_add_invalid_quantity_negative(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": -1})
    assert resp.status_code == 400


# Fix 8: wrong data type
def test_cart_add_wrong_data_type(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": "two"})
    assert resp.status_code == 400


@pytest.mark.xfail(reason="BUG: Missing product_id returns 404 (product not found) instead of 400 (bad request)")
def test_cart_add_missing_product_id(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"quantity": 1})
    assert resp.status_code == 400  # Should be bad request, not 'not found'


def test_cart_add_stock_exceeded(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 9999})
    assert resp.status_code == 400


def test_cart_add_non_existent(auth_headers, empty_cart):
    resp = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 99999, "quantity": 1})
    assert resp.status_code == 404


def test_cart_duplicate_add_accumulates(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 2})
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    item = next((i for i in cart.get("items", []) if i["product_id"] == 250), None)
    assert item is not None
    assert item["quantity"] == 3


def test_cart_update_quantity(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    requests.post(f"{BASE_URL}/cart/update", headers=auth_headers, json={"product_id": 250, "quantity": 5})
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    assert cart["items"][0]["quantity"] == 5
    # invalid update qty < 1
    resp = requests.post(f"{BASE_URL}/cart/update", headers=auth_headers, json={"product_id": 250, "quantity": 0})
    assert resp.status_code == 400


@pytest.mark.xfail(reason="BUG 13: Inactive products (is_active=false) can be added to cart")
def test_cart_add_inactive_product(auth_headers, empty_cart):
    # known inactive product from DB
    payload = {"product_id": 90, "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json=payload)
    assert response.status_code in (400, 404), "Should not allow adding inactive product"


def test_cart_remove(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    resp = requests.post(f"{BASE_URL}/cart/remove", headers=auth_headers, json={"product_id": 250})
    assert resp.status_code == 200

@pytest.mark.xfail(reason="BUG 17: /cart/update allows quantity beyond stock limit")
def test_update_cart_beyond_stock_rejected(auth_headers, empty_cart):
    """Updating quantity beyond stock via /cart/update must return 400."""
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    # Product 250 generally has under 1000 stock. Trying 99999 should fail.
    resp = requests.post(f"{BASE_URL}/cart/update", headers=auth_headers,
                         json={"product_id": 250, "quantity": 99999})
    assert resp.status_code == 400, "Should reject updating cart quantity beyond available stock"

    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    assert len(cart.get("items", [])) == 0
    # removing non-existent
    resp_nf = requests.post(f"{BASE_URL}/cart/remove", headers=auth_headers, json={"product_id": 99999})
    assert resp_nf.status_code == 404


@pytest.mark.xfail(reason="BUG: Cart total calculation is incorrect (returns -96 instead of real subtotal)")
def test_cart_totals_calculation(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 249, "quantity": 2})
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    items = cart.get("items", [])
    calculated_total = sum(item["quantity"] * item["unit_price"] for item in items)
    assert cart["total"] == calculated_total
    for item in items:
        assert item["subtotal"] == item["quantity"] * item["unit_price"]

def test_cart_clear(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    resp = requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)
    assert resp.status_code in (200, 204)
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    assert len(cart.get("items", [])) == 0

def test_cart_item_subtotal_per_item(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 3})
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    for item in cart.get("items", []):
        expected = item["quantity"] * item["unit_price"]
        assert item["subtotal"] == expected, f"Subtotal mismatch: expected {expected}, got {item['subtotal']}"
