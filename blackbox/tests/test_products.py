import pytest
import pytest
import requests
from conftest import BASE_URL

def test_get_products_active_only(auth_headers):
    resp = requests.get(f"{BASE_URL}/products", headers=auth_headers)
    assert resp.status_code == 200
    products = resp.json()
    for product in products:
        assert product.get("is_active", True) is True

def test_get_single_product_valid(auth_headers):
    resp = requests.get(f"{BASE_URL}/products/250", headers=auth_headers)
    assert resp.status_code == 200
    p = resp.json()
    assert p["product_id"] == 250
    assert "price" in p
    assert "category" in p
    assert "is_active" in p
    assert "stock_quantity" in p

def test_get_single_product_not_found(auth_headers):
    resp = requests.get(f"{BASE_URL}/products/999999", headers=auth_headers)
    assert resp.status_code == 404

def test_products_filter_category(auth_headers):
    resp = requests.get(f"{BASE_URL}/products?category=Fruits", headers=auth_headers)
    assert resp.status_code == 200
    products = resp.json()
    for product in products:
        assert product.get("category") == "Fruits"

def test_products_search_name(auth_headers):
    resp = requests.get(f"{BASE_URL}/products?search=Apple", headers=auth_headers)
    assert resp.status_code == 200

def test_products_sort_price(auth_headers):
    resp = requests.get(f"{BASE_URL}/products?sort=price_asc", headers=auth_headers)
    assert resp.status_code == 200
    products = resp.json()
    prices = [p["price"] for p in products]
    assert prices == sorted(prices)
    
    resp_desc = requests.get(f"{BASE_URL}/products?sort=price_desc", headers=auth_headers)
    products_desc = resp_desc.json()
    prices_desc = [p["price"] for p in products_desc]
    assert prices_desc == sorted(prices_desc, reverse=True)

@pytest.mark.xfail(reason="BUG: Standard product GET returns wrong price compared to real DB price")
def test_products_price_matches_admin(auth_headers, admin_headers):
    # Test that the price returned in normal GET equals actual DB price from admin GET
    admin_resp = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
    assert admin_resp.status_code == 200
    admin_prods = {p["product_id"]: p["price"] for p in admin_resp.json()}
    
    user_resp = requests.get(f"{BASE_URL}/products", headers=auth_headers)
    user_prods = user_resp.json()
    for p in user_prods:
        assert p["price"] == admin_prods[p["product_id"]]
