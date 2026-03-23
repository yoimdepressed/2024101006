import pytest
import requests
from conftest import BASE_URL


def test_admin_get_all_users(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_specific_user(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/users/1", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_nonexistent_user(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/users/999999", headers=admin_headers)
    assert resp.status_code == 404

def test_admin_get_all_carts(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/carts", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_all_orders(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_all_products(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_all_coupons(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/coupons", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_all_tickets(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/tickets", headers=admin_headers)
    assert resp.status_code == 200

def test_admin_get_all_addresses(admin_headers):
    resp = requests.get(f"{BASE_URL}/admin/addresses", headers=admin_headers)
    assert resp.status_code == 200
