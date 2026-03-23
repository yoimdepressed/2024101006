"""Unit tests for the finance module."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))
import inventory
import finance


def setup_function():
    inventory.clear()
    finance.clear()
    inventory.set_cash(0)


# income 

def test_record_income_adds_to_log():
    finance.record_income(500, "race prize")
    log = finance.get_log()
    assert len(log) == 1
    assert log[0] == {"type": "income", "amount": 500, "reason": "race prize"}


def test_record_income_increases_cash():
    finance.record_income(300, "sponsorship")
    assert inventory.get_cash() == 300


def test_total_income_sums_correctly():
    finance.record_income(200, "a")
    finance.record_income(400, "b")
    assert finance.get_total_income() == 600


def test_record_income_zero_raises():
    with pytest.raises(ValueError):
        finance.record_income(0, "nothing")


def test_record_income_negative_raises():
    with pytest.raises(ValueError):
        finance.record_income(-50, "negative")


# expense 

def test_record_expense_adds_to_log():
    inventory.set_cash(500)
    finance.record_expense(100, "fuel")
    log = finance.get_log()
    assert len(log) == 1
    assert log[0] == {"type": "expense", "amount": 100, "reason": "fuel"}


def test_record_expense_decreases_cash():
    inventory.set_cash(500)
    finance.record_expense(200, "parts")
    assert inventory.get_cash() == 300


def test_total_expenses_sums_correctly():
    inventory.set_cash(1000)
    finance.record_expense(100, "a")
    finance.record_expense(250, "b")
    assert finance.get_total_expenses() == 350


def test_record_expense_zero_raises():
    with pytest.raises(ValueError):
        finance.record_expense(0, "nothing")


def test_record_expense_insufficient_funds_raises():
    inventory.set_cash(50)
    with pytest.raises(ValueError):
        finance.record_expense(200, "too expensive")


# mixed 

def test_log_preserves_order():
    inventory.set_cash(1000)
    finance.record_income(500, "a")
    finance.record_expense(100, "b")
    finance.record_income(200, "c")
    types = [e["type"] for e in finance.get_log()]
    assert types == ["income", "expense", "income"]


def test_clear_resets_log():
    inventory.set_cash(1000)
    finance.record_income(100, "x")
    finance.clear()
    assert finance.get_log() == []
    assert finance.get_total_income() == 0
    assert finance.get_total_expenses() == 0
