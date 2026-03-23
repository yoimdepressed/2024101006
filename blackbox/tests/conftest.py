import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"
# We need an X-Roll-Number for all requests, and X-User-ID for user-scoped endpoints
VALID_ROLL_NUMBER = "2024101006"
VALID_USER_ID = "1"

@pytest.fixture
def auth_headers():
    return {
        "X-Roll-Number": VALID_ROLL_NUMBER,
        "X-User-ID": VALID_USER_ID
    }

@pytest.fixture
def admin_headers():
    return {
        "X-Roll-Number": VALID_ROLL_NUMBER
    }
