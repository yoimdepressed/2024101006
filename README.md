# 2024101006 — Software Testing Assignment

Git Repository: https://github.com/yoimdepressed/2024101006

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
cd whitebox/moneypoly
python main.py
```

### How to run pylint

```bash
cd /path/to/2024101006
.venv/bin/pylint whitebox/moneypoly/moneypoly/
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
