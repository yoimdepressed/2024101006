import pytest
import requests
from conftest import BASE_URL


def test_loyalty_get(auth_headers):
    resp = requests.get(f"{BASE_URL}/loyalty", headers=auth_headers)
    assert resp.status_code == 200
    assert "loyalty_points" in resp.json()


def test_loyalty_redeem(auth_headers):
    # Zero points (must fail)
    assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=auth_headers, json={"points": 0}).status_code == 400
    # Negative points (must fail — doc says "at least 1")
    assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=auth_headers, json={"points": -1}).status_code == 400

    pts = requests.get(f"{BASE_URL}/loyalty", headers=auth_headers).json().get("loyalty_points", 0)
    # Valid redeem only if we have points
    if pts > 0:
        assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=auth_headers, json={"points": 1}).status_code == 200

    # More than available
    assert requests.post(f"{BASE_URL}/loyalty/redeem", headers=auth_headers, json={"points": pts + 99999}).status_code == 400


def test_orders_get_all(auth_headers):
    assert requests.get(f"{BASE_URL}/orders", headers=auth_headers).status_code == 200


def test_orders_get_single_and_non_existent(auth_headers):
    orders = requests.get(f"{BASE_URL}/orders", headers=auth_headers).json()
    if orders:
        o_id = orders[0]["order_id"]
        resp = requests.get(f"{BASE_URL}/orders/{o_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["order_id"] == o_id

    assert requests.get(f"{BASE_URL}/orders/99999", headers=auth_headers).status_code == 404


@pytest.mark.xfail(reason="BUG: Invoice API response does not include a 'total' field")
def test_orders_invoice(auth_headers):
    orders = requests.get(f"{BASE_URL}/orders", headers=auth_headers).json()
    if not orders:
        pytest.skip("No orders available to test invoice")
    o_id = orders[0]["order_id"]
    resp = requests.get(f"{BASE_URL}/orders/{o_id}/invoice", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "subtotal" in data
    assert "gst_amount" in data
    assert "total" in data


@pytest.mark.xfail(reason="BUG: Cancelling an order does not restore product stock_quantity")
def test_orders_cancel_restores_stock(auth_headers, admin_headers):
    # Create a fresh order for product 250
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})

    admin_products = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers).json()
    # Fix 6: use None default and assert product was found
    pre_stock = next((p["stock_quantity"] for p in admin_products if p["product_id"] == 250), None)
    assert pre_stock is not None, "Product 250 not found in admin products"

    c_resp = requests.post(f"{BASE_URL}/checkout", headers=auth_headers, json={"payment_method": "COD"})
    if c_resp.status_code != 200:
        pytest.skip("Checkout failed, cannot test stock restore")

    o_id = c_resp.json().get("order_id")
    requests.post(f"{BASE_URL}/orders/{o_id}/cancel", headers=auth_headers)

    admin_products_after = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers).json()
    post_stock = next((p["stock_quantity"] for p in admin_products_after if p["product_id"] == 250), None)
    assert post_stock is not None, "Product 250 not found after cancel"
    assert post_stock == pre_stock  # Must be restored


def test_orders_cancel_non_existent(auth_headers):
    assert requests.post(f"{BASE_URL}/orders/99999/cancel", headers=auth_headers).status_code == 404


def test_orders_cancel_delivered(auth_headers):
    orders = requests.get(f"{BASE_URL}/orders", headers=auth_headers).json()
    delivered = next((o for o in orders if o.get("order_status") == "DELIVERED"), None)
    if delivered is None:
        pytest.skip("No DELIVERED orders in DB to test cancel refusal")
    assert requests.post(f"{BASE_URL}/orders/{delivered['order_id']}/cancel",
                         headers=auth_headers).status_code == 400
