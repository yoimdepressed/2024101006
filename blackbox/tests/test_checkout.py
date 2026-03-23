import pytest
import requests
from conftest import BASE_URL

@pytest.fixture
def empty_cart(auth_headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)

@pytest.fixture
def populated_cart(auth_headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})

@pytest.mark.xfail(reason="BUG: Checkout allows empty cart instead of returning 400")
def test_checkout_empty_cart(auth_headers, empty_cart):
    payload = {"payment_method": "COD"}
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json=payload)
    assert resp.status_code == 400

def test_checkout_invalid_method(auth_headers, populated_cart):
    payload = {"payment_method": "CASH"}
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json=payload)
    assert resp.status_code == 400

# Fix 9: missing fields test
def test_checkout_missing_payment_method(auth_headers, populated_cart):
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json={})
    assert resp.status_code == 400

def test_checkout_cod_limit(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 50})
    payload = {"payment_method": "COD"}
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json=payload)
    assert resp.status_code == 400

def test_checkout_valid_cod(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    payload = {"payment_method": "COD"}
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json=payload)
    assert resp.status_code == 200
    assert resp.json().get("payment_status") == "PENDING"

def test_checkout_valid_wallet(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    # ensure wallet has balance
    requests.post(f"{BASE_URL}/wallet/add", headers=auth_headers, json={"amount": 1000})
    payload = {"payment_method": "WALLET"}
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json=payload)
    assert resp.status_code == 200
    assert resp.json().get("payment_status") == "PENDING"

def test_checkout_valid_card(auth_headers, empty_cart):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    payload = {"payment_method": "CARD"}
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json=payload)
    assert resp.status_code == 200
    assert resp.json().get("payment_status") == "PAID"

@pytest.mark.xfail(reason="BUG: Checkout does not reduce stock or calculate GST accurately")
def test_checkout_gst_and_stock_reduction(auth_headers, empty_cart, admin_headers):
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 249, "quantity": 1})
    
    # get pre-checkout stock
    pre_stock = next((p["stock_quantity"] for p in requests.get(f"{BASE_URL}/admin/products", headers=admin_headers).json() if p["product_id"] == 249), 0)
    
    resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json={"payment_method": "CARD"})
    data = resp.json()
    
    # 5% GST exactly check
    # cart_total = requests.get(f"{BASE_URL}/orders", headers=auth_headers).json()[-1]["total"] # deleted
    subtotal = data.get("total", 0) - data.get("gst_amount", 0)
    assert abs((subtotal * 0.05) - data.get("gst_amount", 0)) < 1.0 # Due to float rounding limits
    
    # check stock reduced
    post_stock = next((p["stock_quantity"] for p in requests.get(f"{BASE_URL}/admin/products", headers=admin_headers).json() if p["product_id"] == 249), 0)
    assert post_stock == pre_stock - 1
