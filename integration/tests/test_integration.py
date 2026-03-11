"""
Integration tests for StreetRace Manager.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import crew as crew_module
import inventory
import race as race_module
import results
import mission
import pytest

def clear_all():
    """Reset all module state before each test."""
    registration.clear()
    crew_module.clear()
    inventory.clear()
    race_module.clear()
    results.clear()
    mission.clear()

class TestRegistrationToRace:

    def setup_method(self):
        clear_all()

    def test_registered_driver_can_enter_race(self):
        """Full flow: register a driver, add a car, enter the race."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        entry = race_module.enter_race(r["id"], "Dom", "Skyline")
        assert entry["driver"] == "Dom"
        assert entry["car"] == "Skyline"

    def test_unregistered_person_cannot_enter_race(self):
        """must be registered before entering a race."""
        inventory.add_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        with pytest.raises(ValueError, match="not a registered"):
            race_module.enter_race(r["id"], "Ghost", "Skyline")

    def test_mechanic_cannot_enter_race(self):
        """only drivers can race , mechanic must be rejected."""
        registration.register("Letty", "mechanic")
        inventory.add_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        with pytest.raises(ValueError, match="only drivers"):
            race_module.enter_race(r["id"], "Letty", "Skyline")

    def test_strategist_cannot_enter_race(self):
        """strategist also cannot enter a race."""
        registration.register("Brian", "strategist")
        inventory.add_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        with pytest.raises(ValueError, match="only drivers"):
            race_module.enter_race(r["id"], "Brian", "Skyline")


class TestRaceToResultsToInventory:

    def setup_method(self):
        clear_all()

    def test_completing_race_updates_cash(self):
        """Full flow: race finishes, prize money lands in inventory."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.set_cash(0)
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])
        results.record_result(r["id"], "Dom", 5000)
        assert inventory.get_cash() == 5000

    def test_completing_race_updates_driver_ranking(self):
        """Win is recorded in rankings after race finishes."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.set_cash(0)
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])
        results.record_result(r["id"], "Dom", 5000)
        assert results.get_ranking("Dom") == 1

    def test_cannot_record_result_for_unstarted_race(self):
        """result can only be recorded for in_progress race."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        # deliberately skip start_race
        with pytest.raises(ValueError, match="not in progress"):
            results.record_result(r["id"], "Dom", 5000)

    def test_cannot_record_result_for_non_entrant(self):
        """winner must be entered in the race."""
        registration.register("Dom", "driver")
        registration.register("Brian", "driver")
        inventory.add_car("Skyline")
        inventory.set_cash(0)
        r = race_module.create_race("Night Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])
        with pytest.raises(ValueError, match="not entered"):
            results.record_result(r["id"], "Brian", 5000)

    def test_multiple_race_wins_accumulate_cash_and_ranking(self):
        """Two race wins = cash from both prizes added, ranking = 2."""
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
