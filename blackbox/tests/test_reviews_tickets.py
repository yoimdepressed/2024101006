import pytest
import requests
from conftest import BASE_URL

# ---------- REVIEWS ----------

@pytest.mark.xfail(reason="BUG: Average rating uses integer division instead of returning a decimal")
def test_review_get_and_average(auth_headers):
    resp = requests.get(f"{BASE_URL}/products/250/reviews", headers=auth_headers)
    assert resp.status_code == 200
    # Post two reviews to force a non-integer average
    requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers, json={"rating": 3, "comment": "Okay"})
    requests.post(f"{BASE_URL}/products/250/reviews", headers={"X-Roll-Number": "2024101006", "X-User-ID": "2"}, json={"rating": 4, "comment": "Good"})
    revs = requests.get(f"{BASE_URL}/products/250/reviews", headers=auth_headers).json()
    avg_rating = revs.get("average_rating", 0)
    assert isinstance(avg_rating, float)  # 3.5 is a float, not 3 (int)


# Fix 4: use product 250 consistently
def test_review_valid_and_boundaries(auth_headers):
    # Boundary rating=1 with min comment
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 1, "comment": "B"}).status_code == 200
    # Boundary rating=5 with max comment (200 chars)
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 5, "comment": "A" * 200}).status_code == 200


def test_review_invalid_rating(auth_headers):
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 6, "comment": "Great"}).status_code == 400
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 0, "comment": "Bad"}).status_code == 400


def test_review_comment_boundaries(auth_headers):
    # Empty comment
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 5, "comment": ""}).status_code == 400
    # 201 chars (over max)
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 5, "comment": "A" * 201}).status_code == 400


# Fix 8: wrong data type tests
def test_review_wrong_data_type(auth_headers):
    # rating as a string
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": "five", "comment": "Good"}).status_code == 400


# ---------- SUPPORT TICKETS ----------

def test_support_ticket_get_all(auth_headers):
    assert requests.get(f"{BASE_URL}/support/tickets", headers=auth_headers).status_code == 200


# Fix 9: missing fields test
def test_support_ticket_missing_fields(auth_headers):
    # No message field
    assert requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Valid Subject"}).status_code == 400
    # No subject field
    assert requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"message": "Valid message body"}).status_code == 400


def test_support_ticket_create_valid(auth_headers):
    subject = "Valid Subject"
    msg = "This is a strictly exact message."
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": subject, "message": msg})
    assert resp.status_code == 200
    ticket = resp.json().get("ticket", resp.json())
    assert ticket.get("status") == "OPEN"
    assert ticket.get("subject") == subject
    assert ticket.get("message") == msg


def test_support_ticket_create_boundaries(auth_headers):
    # Subject too short (4 chars)
    assert requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "abcd", "message": "msg"}).status_code == 400
    # Subject too long (101 chars)
    assert requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "A" * 101, "message": "msg"}).status_code == 400
    # Message too long (>500 chars)
    assert requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Valid Subject", "message": "A" * 501}).status_code == 400


# Fix 5: split into two separate tests
def test_support_ticket_valid_transitions(auth_headers):
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Help Login", "message": "Forgot pass"})
    t_id = resp.json().get("ticket", resp.json()).get("ticket_id")

    # OPEN -> IN_PROGRESS (must succeed)
    assert requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers,
                        json={"status": "IN_PROGRESS"}).status_code == 200
    # IN_PROGRESS -> CLOSED (must succeed)
    assert requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers,
                        json={"status": "CLOSED"}).status_code == 200


@pytest.mark.xfail(reason="BUG: API allows transitioning a CLOSED ticket back to OPEN (invalid reverse transition)")
def test_support_ticket_closed_to_open_invalid(auth_headers):
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Help Again", "message": "Need more help please"})
    t_id = resp.json().get("ticket", resp.json()).get("ticket_id")
    requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers, json={"status": "IN_PROGRESS"})
    requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers, json={"status": "CLOSED"})
    # CLOSED -> OPEN should be 400
    assert requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers,
                        json={"status": "OPEN"}).status_code == 400


@pytest.mark.xfail(reason="BUG 5: API allows invalid status transitions for tickets (OPEN directly to CLOSED)")
def test_support_ticket_invalid_transition(auth_headers):
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Help Login", "message": "Forgot pass"})
    t_id = resp.json().get("ticket", resp.json()).get("ticket_id")
    assert requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers,
                        json={"status": "CLOSED"}).status_code == 400

@pytest.mark.xfail(reason="BUG 15: Support ticket accepts completely invalid status strings")
def test_support_ticket_invalid_status_string(auth_headers):
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Help Login", "message": "Testing status string"})
    t_id = resp.json().get("ticket", resp.json()).get("ticket_id")
    r_put = requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers,
                         json={"status": "INVALID_STATUS"})
    assert r_put.status_code == 400, "Should reject non-enum status string"


def test_support_ticket_message_saved_exactly(auth_headers):
    msg = "My specific order #12345 is missing item: Widget Pro X"
    payload = {"subject": "Missing item report", "message": msg}
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers, json=payload)
    assert resp.status_code == 200
    ticket = resp.json().get("ticket", resp.json())
    saved_msg = ticket.get("message", "")
    assert saved_msg == msg, f"Message mismatch. Expected: {msg}, Got: {saved_msg}"

def test_review_missing_fields(auth_headers):
    # Missing comment
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"rating": 3}).status_code == 400
    # Missing rating
    assert requests.post(f"{BASE_URL}/products/250/reviews", headers=auth_headers,
                         json={"comment": "No rating given"}).status_code == 400

@pytest.mark.xfail(reason="BUG 16: Duplicate reviews allowed on same product by same user")
def test_review_duplicate_submission(auth_headers):
    payload = {"rating": 5, "comment": "First Review"}
    r1 = requests.post(f"{BASE_URL}/products/3/reviews", headers=auth_headers, json=payload)
    assert r1.status_code == 200
    payload2 = {"rating": 3, "comment": "Second Review"}
    r2 = requests.post(f"{BASE_URL}/products/3/reviews", headers=auth_headers, json=payload2)
    assert r2.status_code == 400, "Should not allow multiple reviews per user per product"

@pytest.mark.xfail(reason="BUG 18: Posting review for non-existent product returns 200")
def test_review_nonexistent_product_returns_404(auth_headers):
    resp = requests.post(f"{BASE_URL}/products/999999/reviews",
                         headers=auth_headers,
                         json={"rating": 5, "comment": "Ghost review"})
    assert resp.status_code == 404, "Should return 404 when reviewing a non-existent product"

@pytest.mark.xfail(reason="BUG 19: IN_PROGRESS → OPEN reverse transition allowed")
def test_in_progress_to_open_is_invalid(auth_headers):
    resp = requests.post(f"{BASE_URL}/support/ticket", headers=auth_headers,
                         json={"subject": "Reverse Test Ticket", "message": "Testing reverse transition"})
    t_id = resp.json().get("ticket", resp.json()).get("ticket_id")
    requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers, json={"status": "IN_PROGRESS"})
    r = requests.put(f"{BASE_URL}/support/tickets/{t_id}", headers=auth_headers, json={"status": "OPEN"})
    assert r.status_code == 400, "IN_PROGRESS → OPEN should be rejected (spec: no reverse transitions)"



