import pytest
import requests
from conftest import BASE_URL

@pytest.fixture
def clean_addresses(auth_headers):
    resp = requests.get(f"{BASE_URL}/addresses", headers=auth_headers)
    if resp.status_code == 200:
        for addr in resp.json():
            requests.delete(f"{BASE_URL}/addresses/{addr['address_id']}", headers=auth_headers)

def test_add_address_valid_labels(auth_headers, clean_addresses):
    for label in ["HOME", "OFFICE", "OTHER"]:
        payload = {"label": label, "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
        resp = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload)
        assert resp.status_code == 200
        data = resp.json().get("address", resp.json())
        assert "address_id" in data
        assert data["label"] == label
        assert "street" in data
        assert "city" in data
        assert "pincode" in data
        assert "is_default" in data

def test_add_address_invalid_label(auth_headers):
    payload = {"label": "INVALID", "street": "123 Main St", "city": "Metropolis", "pincode": "123456"}
    resp = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload)
    assert resp.status_code == 400

def test_add_address_invalid_street_length(auth_headers):
    payload1 = {"label": "HOME", "street": "abcd", "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload1).status_code == 400
    
    payload2 = {"label": "HOME", "street": "a"*101, "city": "Metropolis", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload2).status_code == 400

@pytest.mark.xfail(reason="BUG: API allows non-digit pincodes")
def test_add_address_invalid_pincode(auth_headers):
    payload1 = {"label": "HOME", "street": "Valid St", "city": "City", "pincode": "12345"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload1).status_code == 400
    
    payload2 = {"label": "HOME", "street": "Valid St", "city": "City", "pincode": "1234567"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload2).status_code == 400
    
    payload3 = {"label": "HOME", "street": "Valid St", "city": "City", "pincode": "abcdef"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload3).status_code == 400

def test_add_address_invalid_city_length(auth_headers):
    payload1 = {"label": "HOME", "street": "Valid St", "city": "A", "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload1).status_code == 400
    payload2 = {"label": "HOME", "street": "Valid St", "city": "A"*51, "pincode": "123456"}
    assert requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload2).status_code == 400

def test_default_address_logic(auth_headers, clean_addresses):
    # Rule: newly added default makes others non-default
    # Create address 1
    p1 = {"label": "HOME", "street": "First St", "city": "City", "pincode": "123456"}
    r1 = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=p1)
    id1 = r1.json().get("address", r1.json())["address_id"]
    requests.put(f"{BASE_URL}/addresses/{id1}", headers=auth_headers, json={"street": "First St", "is_default": True})
    
    # Create address 2
    p2 = {"label": "OFFICE", "street": "Second St", "city": "City", "pincode": "123456"}
    r2 = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=p2)
    id2 = r2.json().get("address", r2.json())["address_id"]
    requests.put(f"{BASE_URL}/addresses/{id2}", headers=auth_headers, json={"street": "Second St", "is_default": True})
    
    fetch = requests.get(f"{BASE_URL}/addresses", headers=auth_headers).json()
    a1 = next(a for a in fetch if a["address_id"] == id1)
    a2 = next(a for a in fetch if a["address_id"] == id2)
    assert a1["is_default"] is False
    assert a2["is_default"] is True

@pytest.mark.xfail(reason="BUG: API returns old data instead of new data after update")
def test_update_address_street(auth_headers):
    payload = {"label": "HOME", "street": "Valid St", "city": "City", "pincode": "123456"}
    create_resp = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload)
    data = create_resp.json().get("address", create_resp.json())
    addr_id = data["address_id"]
    
    update_payload = {"street": "New Street Name"}
    update_resp = requests.put(f"{BASE_URL}/addresses/{addr_id}", headers=auth_headers, json=update_payload)
    assert update_resp.status_code == 200
    updated_data = update_resp.json().get("address", update_resp.json())
    assert updated_data["street"] == "New Street Name"

def test_update_address_ignored_fields(auth_headers):
    payload = {"label": "HOME", "street": "Valid St", "city": "City", "pincode": "123456"}
    create_resp = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload)
    data = create_resp.json().get("address", create_resp.json())
    addr_id = data["address_id"]
    
    update_payload = {"label": "OFFICE", "city": "New City", "pincode": "654321"}
    update_resp = requests.put(f"{BASE_URL}/addresses/{addr_id}", headers=auth_headers, json=update_payload)
    
    fetch = requests.get(f"{BASE_URL}/addresses", headers=auth_headers).json()
    cur_addr = next(a for a in fetch if a["address_id"] == addr_id)
    assert cur_addr["label"] == "HOME"
    assert cur_addr["city"] == "City"
    assert cur_addr["pincode"] == "123456"

def test_delete_non_existent_address(auth_headers):
    resp = requests.delete(f"{BASE_URL}/addresses/99999", headers=auth_headers)
    assert resp.status_code == 404

def test_add_address_response_includes_all_fields(auth_headers):
    payload = {"label": "HOME", "street": "Field Verification Road", "city": "Hyderabad", "pincode": "500001"}
    r = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload)
    assert r.status_code == 200
    raw = r.json()
    addr = raw.get("address", raw)
    for field in ("address_id", "label", "street", "city", "pincode", "is_default"):
        assert field in addr, f"Missing field '{field}' in address response"

def test_delete_existing_address(auth_headers):
    payload = {"label": "OTHER", "street": "Temp Street For Delete", "city": "Dummy City", "pincode": "111111"}
    r = requests.post(f"{BASE_URL}/addresses", headers=auth_headers, json=payload)
    data = r.json().get("address", r.json())
    addr_id = data["address_id"]
    resp = requests.delete(f"{BASE_URL}/addresses/{addr_id}", headers=auth_headers)
    assert resp.status_code in (200, 204)
