# 2024101006 — Software Testing Assignment

Git Repository: https://github.com/yoimdepressed/2024101006
OneDrive Link: <INSERT_ONEDRIVE_LINK_HERE> (includes .git zip if >20MB)

---

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pylint pytest
```

---

## Task 1: White-Box Testing (MoneyPoly)

### How to run the MoneyPoly game

```bash
cd whitebox/code
python main.py
```

### How to run pylint

```bash
cd /path/to/2024101006
.venv/bin/pylint whitebox/code/moneypoly/
```

### How to run the white-box tests

```bash
cd /path/to/2024101006
.venv/bin/pytest whitebox/tests/ -v
```

Test files are located in `whitebox/tests/`:
- `test_player.py` — tests for player.py
- `test_dice.py` — tests for dice.py
- `test_property.py` — tests for property.py
- `test_bank.py` — tests for bank.py
- `test_game.py` — tests for game.py

The report for Task 1 is at `whitebox/report.md`.

---

## Task 2: Integration Testing (StreetRace Manager)

### How to run the integration tests

```bash
cd /path/to/2024101006
.venv/bin/pytest integration/tests/ -v
```

The report for Task 2 is at `integration/report.md`.

---

## Task 3: Black-Box API Testing (QuickCart)

### How to run the QuickCart API server

```bash
docker load -i quickcart_image.tar
docker run -p 8080:8080 quickcart
```

### How to run the black-box tests

```bash
cd /path/to/2024101006
.venv/bin/pytest blackbox/tests/ -v
```

Test files are located in `blackbox/tests/`:
- `test_auth.py` — header validation tests
- `test_admin.py` — admin endpoint tests
- `test_profile.py` — profile tests
- `test_addresses.py` — address tests
- `test_products.py` — product tests
- `test_cart.py` — cart tests
- `test_coupons.py` — coupon tests
- `test_checkout.py` — checkout tests
- `test_wallet.py` — wallet tests
- `test_loyalty_orders.py` — loyalty and order tests
- `test_reviews_tickets.py` — reviews and support ticket tests

The report for Task 3 is at `blackbox/report.md`.
