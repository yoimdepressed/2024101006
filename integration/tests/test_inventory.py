"""Unit tests for inventory.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import inventory
import pytest


class TestCash:

    def setup_method(self):
        inventory.clear()

    def test_initial_cash_is_zero(self):
        assert inventory.get_cash() == 0

    def test_set_cash_valid(self):
        inventory.set_cash(1000)
        assert inventory.get_cash() == 1000

    def test_set_cash_zero_valid(self):
        inventory.set_cash(0)
        assert inventory.get_cash() == 0

    def test_set_cash_negative_raises(self):
        with pytest.raises(ValueError, match="negative"):
            inventory.set_cash(-1)

    def test_add_cash_increases_balance(self):
        inventory.set_cash(500)
        inventory.add_cash(200)
        assert inventory.get_cash() == 700

    def test_add_cash_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            inventory.add_cash(0)

    def test_add_cash_negative_raises(self):
        with pytest.raises(ValueError, match="positive"):
            inventory.add_cash(-100)

    def test_deduct_cash_decreases_balance(self):
        inventory.set_cash(500)
        inventory.deduct_cash(200)
        assert inventory.get_cash() == 300

    def test_deduct_cash_exact_balance(self):
        inventory.set_cash(500)
        inventory.deduct_cash(500)
        assert inventory.get_cash() == 0

    def test_deduct_cash_exceeds_balance_raises(self):
        inventory.set_cash(100)
        with pytest.raises(ValueError, match="Insufficient"):
            inventory.deduct_cash(200)

    def test_deduct_cash_zero_raises(self):
        inventory.set_cash(100)
        with pytest.raises(ValueError, match="positive"):
            inventory.deduct_cash(0)


class TestCars:

    def setup_method(self):
        inventory.clear()

    def test_add_car_valid(self):
        car = inventory.add_car("Skyline")
        assert car["name"] == "Skyline"
        assert car["damaged"] is False

    def test_add_car_empty_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            inventory.add_car("")

    def test_add_car_duplicate_raises(self):
        inventory.add_car("Skyline")
        with pytest.raises(ValueError, match="already exists"):
            inventory.add_car("Skyline")

    def test_get_car_exists(self):
        inventory.add_car("Skyline")
        assert inventory.get_car("Skyline") is not None

    def test_get_car_not_found_returns_none(self):
        assert inventory.get_car("Ghost") is None

    def test_mark_car_damaged(self):
        inventory.add_car("Skyline")
        inventory.mark_car_damaged("Skyline")
        assert inventory.get_car("Skyline")["damaged"] is True

    def test_repair_car(self):
        inventory.add_car("Skyline")
        inventory.mark_car_damaged("Skyline")
        inventory.repair_car("Skyline")
        assert inventory.get_car("Skyline")["damaged"] is False

    def test_mark_nonexistent_car_raises(self):
        with pytest.raises(ValueError, match="not found"):
            inventory.mark_car_damaged("Ghost")


class TestParts:

    def setup_method(self):
        inventory.clear()

    def test_add_parts_valid(self):
        inventory.add_parts("tire", 4)
        assert inventory.get_parts("tire") == 4

    def test_add_parts_accumulates(self):
        inventory.add_parts("tire", 4)
        inventory.add_parts("tire", 2)
        assert inventory.get_parts("tire") == 6

    def test_add_parts_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            inventory.add_parts("tire", 0)

    def test_get_parts_not_stocked_returns_zero(self):
        assert inventory.get_parts("engine") == 0
