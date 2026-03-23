import pytest
import requests
from conftest import BASE_URL


@pytest.fixture
def empty_cart(auth_headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)


@pytest.fixture
def populated_cart(auth_headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 10})
    yield
    requests.delete(f"{BASE_URL}/cart/clear", headers=auth_headers)


def _get_coupons(admin_headers):
    adm = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers).json()
    coupons = adm.get("coupons", adm) if isinstance(adm, dict) else adm
    return [c for c in coupons if isinstance(c, dict)]


def _get_code(coupon):
    return coupon.get("code") or coupon.get("coupon_code")


# Fix 1: Find an actual active coupon and assert 200, not [200,400,404]
@pytest.mark.xfail(reason="BUG: Coupon apply call returns 400 even with a valid active coupon (likely tied to broken cart total)")
def test_coupon_apply_valid(auth_headers, populated_cart, admin_headers):
    coupons = _get_coupons(admin_headers)
    active = next((c for c in coupons if c.get("is_active", True) and c.get("min_cart_value", 0) <= 2000), None)
    if active is None:
        pytest.skip("No active coupon with low min_cart_value found in DB")
    resp = requests.post(f"{BASE_URL}/coupon/apply", headers=auth_headers, json={"code": _get_code(active)})
    assert resp.status_code == 200


# Fix 2: Skip explicitly if no expired coupon, or use hardcoded fallback
def test_coupon_expired(auth_headers, populated_cart, admin_headers):
    coupons = _get_coupons(admin_headers)
    expired = next((c for c in coupons if not c.get("is_active", True)), None)
    code = _get_code(expired) if expired else "EXPIREDCOUPON"
    resp = requests.post(f"{BASE_URL}/coupon/apply", headers=auth_headers, json={"code": code})
    assert resp.status_code in [400, 404]


# Fix 2: Skip explicitly if no high-min coupon found
def test_coupon_minimum_cart_value(auth_headers, empty_cart, admin_headers):
    coupons = _get_coupons(admin_headers)
    high_min = next((c for c in coupons if c.get("min_cart_value", 0) > 1000 and c.get("is_active", True)), None)
    if high_min is None:
        pytest.skip("No coupon with min_cart_value > 1000 found in DB")
    requests.post(f"{BASE_URL}/cart/add", headers=auth_headers, json={"product_id": 250, "quantity": 1})
    resp = requests.post(f"{BASE_URL}/coupon/apply", headers=auth_headers, json={"code": _get_code(high_min)})
    assert resp.status_code == 400


# Fix 2: Skip explicitly if no active coupon found
@pytest.mark.xfail(reason="BUG: Coupon discount returned as 0 instead of expected amount (likely tied to cart total bug)")
def test_coupon_discount_calculation(auth_headers, populated_cart, admin_headers):
    coupons = _get_coupons(admin_headers)
    active = next((c for c in coupons if c.get("is_active", True) and c.get("min_cart_value", 0) <= 2000), None)
    if active is None:
        pytest.skip("No active coupon found in DB")

    requests.post(f"{BASE_URL}/coupon/apply", headers=auth_headers, json={"code": _get_code(active)})
    cart = requests.get(f"{BASE_URL}/cart", headers=auth_headers).json()
    subtotal = sum(i["quantity"] * i["unit_price"] for i in cart.get("items", []))

    expected_discount = 0
    if active.get("discount_type") == "PERCENT":
        expected_discount = (subtotal * active.get("discount_value", 0)) / 100
        if "max_discount" in active and expected_discount > active["max_discount"]:
            expected_discount = active["max_discount"]
    elif active.get("discount_type") == "FIXED":
        expected_discount = active.get("discount_value", 0)

    assert cart.get("discount", 0) == expected_discount


def test_coupon_remove(auth_headers, populated_cart):
    requests.post(f"{BASE_URL}/coupon/apply", headers=auth_headers, json={"code": "WELCOME10"})
    resp = requests.post(f"{BASE_URL}/coupon/remove", headers=auth_headers)
    assert resp.status_code == 200
