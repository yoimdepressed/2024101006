import requests
from conftest import BASE_URL

def test_missing_roll_number():
    resp = requests.get(f"{BASE_URL}/profile", headers={"X-User-ID": "1"})
    assert resp.status_code == 401

def test_invalid_roll_number():
    resp = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "abc", "X-User-ID": "1"})
    assert resp.status_code == 400

def test_missing_user_id():
    resp = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "2024101006"})
    assert resp.status_code == 400

def test_invalid_user_id():
    resp = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "2024101006", "X-User-ID": "abc"})
    assert resp.status_code == 400

def test_symbol_roll_number():
    resp = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "12@34", "X-User-ID": "1"})
    assert resp.status_code == 400

def test_nonexistent_user_id():
    resp = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": "2024101006", "X-User-ID": "999999"})
    assert resp.status_code == 400
