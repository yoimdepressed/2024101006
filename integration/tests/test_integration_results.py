"""
Integration tests: Race → Results → Inventory
Tests that finishing a race correctly updates cash balance and driver rankings.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import inventory
import race as race_module
import results
import pytest


def clear_all():
    registration.clear()
    inventory.clear()
    race_module.clear()
    results.clear()


class TestRaceToResultsToInventory:

    def setup_method(self):
        clear_all()

    def test_completing_race_updates_cash(self):
        """Prize money from a finished race is added to inventory cash."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.set_cash(0)
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])
        results.record_result(r["id"], "Dom", 5000)
        assert inventory.get_cash() == 5000

    def test_completing_race_updates_driver_ranking(self):
        """Driver ranking increments after winning a race."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.set_cash(0)
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])
        results.record_result(r["id"], "Dom", 5000)
        assert results.get_ranking("Dom") == 1

    def test_cannot_record_result_for_unstarted_race(self):
        """Result cannot be recorded for a race that hasn't started yet."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        with pytest.raises(ValueError, match="not in progress"):
            results.record_result(r["id"], "Dom", 5000)

    def test_cannot_record_result_for_non_entrant(self):
        """Only a driver who entered the race can be declared winner."""
        registration.register("Dom", "driver")
        registration.register("Brian", "driver")
        inventory.add_car("Skyline")
        inventory.set_cash(0)
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])
        with pytest.raises(ValueError, match="not entered"):
            results.record_result(r["id"], "Brian", 5000)

    def test_multiple_wins_accumulate_cash_and_ranking(self):
        """Winning two races adds both prizes to cash and ranking becomes 2."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.add_car("Supra")
        inventory.set_cash(0)
        r1 = race_module.create_race("Race 1", "LA")
        race_module.enter_race(r1["id"], "Dom", "Skyline")
        race_module.start_race(r1["id"])
        results.record_result(r1["id"], "Dom", 3000)
        r2 = race_module.create_race("Race 2", "Miami")
        race_module.enter_race(r2["id"], "Dom", "Supra")
        race_module.start_race(r2["id"])
        results.record_result(r2["id"], "Dom", 2000)
        assert inventory.get_cash() == 5000
        assert results.get_ranking("Dom") == 2
