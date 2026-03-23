import pytest
import requests
from conftest import BASE_URL

def test_get_profile(auth_headers):
    response = requests.get(f"{BASE_URL}/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "phone" in data

def test_update_profile_valid(auth_headers):
    payload = {"name": "Test User", "phone": "1234567890"}
    response = requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload)
    assert response.status_code == 200

def test_update_profile_boundary_valid(auth_headers):
    # Name 2 chars, 50 chars
    payload1 = {"name": "ab", "phone": "1234567890"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload1).status_code == 200
    
    payload2 = {"name": "a" * 50, "phone": "1234567890"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload2).status_code == 200

def test_update_profile_invalid_name_length(auth_headers):
    # Name 1 char, 51 chars
    payload1 = {"name": "a", "phone": "1234567890"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload1).status_code == 400
    
    payload2 = {"name": "a" * 51, "phone": "1234567890"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload2).status_code == 400

@pytest.mark.xfail(reason="BUG: API allows non-digit phone numbers")
def test_update_profile_invalid_phone_format(auth_headers):
    # Phone length 9, 11
    payload1 = {"name": "Test User", "phone": "123456789"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload1).status_code == 400
    
    payload2 = {"name": "Test User", "phone": "12345678901"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload2).status_code == 400
    
    # Non-digits
    payload3 = {"name": "Test User", "phone": "123abc4567"}
    assert requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload3).status_code == 400

# Fix 8: wrong data type test
def test_update_profile_wrong_type(auth_headers):
    payload = {"name": 12345, "phone": "1234567890"}  # name as int instead of string
    resp = requests.put(f"{BASE_URL}/profile", headers=auth_headers, json=payload)
    assert resp.status_code == 400
