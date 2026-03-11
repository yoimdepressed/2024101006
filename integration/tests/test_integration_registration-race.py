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
