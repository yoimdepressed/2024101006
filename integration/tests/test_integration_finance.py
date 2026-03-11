"""
Integration tests: Results + Inventory → Finance 
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import inventory
import race as race_module
import results
import finance


def clear_all():
    registration.clear()
    inventory.clear()
    race_module.clear()
    results.clear()
    finance.clear()


def _run_race(driver, car, prize):
    """driver must already be registered."""
    inventory.add_car(car)
    r = race_module.create_race(f"Race-{car}", "LA")
    race_module.enter_race(r["id"], driver, car)
    race_module.start_race(r["id"])
    results.record_result(r["id"], driver, prize)


class TestFinanceIntegration:

    def setup_method(self):
        clear_all()
        inventory.set_cash(0)

    def test_race_prize_logged_as_income(self):
        """After a race, manually logging prize matches inventory cash."""
        registration.register("Dom", "driver")
        _run_race("Dom", "Skyline", 5000)
        finance.record_income(5000, "race prize")
        assert finance.get_total_income() == 5000
        assert inventory.get_cash() == 10000

    def test_expense_reduces_inventory_cash(self):
        """Recording an expense correctly reduces inventory cash."""
        inventory.set_cash(3000)
        finance.record_expense(1000, "spare parts")
        assert inventory.get_cash() == 2000
        assert finance.get_total_expenses() == 1000

    def test_income_and_expense_net_balance(self):
        """Net balance after income and expense reflects in inventory."""
        finance.record_income(5000, "prize")
        finance.record_expense(1500, "fuel and parts")
        assert inventory.get_cash() == 3500
        assert finance.get_total_income() == 5000
        assert finance.get_total_expenses() == 1500

    def test_transaction_log_captures_full_race_weekend(self):
        """Finance log records the complete money flow of a race weekend."""
        registration.register("Dom", "driver")
        # Pre-race costs
        finance.record_income(2000, "sponsorship")
        finance.record_expense(500, "entry fee")
        finance.record_expense(300, "fuel")
        _run_race("Dom", "Skyline", 4000)
        finance.record_income(4000, "race prize")
        log = finance.get_log()
        assert len(log) == 4
        types = [e["type"] for e in log]
        assert types.count("income") == 2
        assert types.count("expense") == 2

    def test_expense_blocked_when_funds_insufficient(self):
        """Finance prevents expense that would overdraw inventory."""
        inventory.set_cash(100)
        with pytest.raises(ValueError):
            finance.record_expense(500, "engine rebuild")
        assert inventory.get_cash() == 100
        assert finance.get_total_expenses() == 0

    def test_multiple_races_income_tracked_separately(self):
        """Two race prizes logged as two separate income entries."""
        registration.register("Dom", "driver")
        _run_race("Dom", "Skyline", 3000)
        finance.record_income(3000, "race 1 prize")
        _run_race("Dom", "Supra", 2000)
        finance.record_income(2000, "race 2 prize")
        assert finance.get_total_income() == 5000
        log = finance.get_log()
        assert len(log) == 2
        assert log[0]["reason"] == "race 1 prize"
        assert log[1]["reason"] == "race 2 prize"
