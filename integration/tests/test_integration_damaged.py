"""
Integration tests: Inventory (damaged car) → Race and Mission
Tests that a damaged car blocks race entry and triggers mechanic availability
checks before a mission can proceed.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import crew as crew_module
import inventory
import race as race_module
import mission
import pytest


def clear_all():
    registration.clear()
    crew_module.clear()
    inventory.clear()
    race_module.clear()
    mission.clear()


class TestDamagedCarInteractions:

    def setup_method(self):
        clear_all()

    def test_damaged_car_cannot_enter_race(self):
        """A car marked as damaged is rejected at race entry."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.mark_car_damaged("Skyline")
        r = race_module.create_race("Night Race", "LA")
        with pytest.raises(ValueError, match="damaged"):
            race_module.enter_race(r["id"], "Dom", "Skyline")

    def test_repaired_car_can_enter_race(self):
        """After repairing a damaged car, it can race again."""
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.mark_car_damaged("Skyline")
        inventory.repair_car("Skyline")
        r = race_module.create_race("Night Race", "LA")
        entry = race_module.enter_race(r["id"], "Dom", "Skyline")
        assert entry["car"] == "Skyline"

    def test_damaged_car_mission_blocked_no_free_mechanic(self):
        """Mission with damaged car is blocked when no mechanic is available."""
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        inventory.add_car("Skyline")
        inventory.mark_car_damaged("Skyline")
        # Letty is already busy on another mission
        mission.create_mission("repair", "mechanic", "Letty")
        with pytest.raises(ValueError, match="damaged"):
            mission.create_mission("delivery", "driver", "Dom", car_name="Skyline")

    def test_damaged_car_mission_allowed_mechanic_is_free(self):
        """Mission with damaged car is allowed when a mechanic is free."""
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        inventory.add_car("Skyline")
        inventory.mark_car_damaged("Skyline")
        # Letty is free — mission proceeds
        m = mission.create_mission("delivery", "driver", "Dom", car_name="Skyline")
        assert m["status"] == "active"

    def test_mechanic_freed_after_mission_unblocks_next_mission(self):
        """Completing a mechanic's mission frees them for the next damaged-car mission."""
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        inventory.add_car("Skyline")
        inventory.add_car("Supra")
        inventory.mark_car_damaged("Skyline")
        inventory.mark_car_damaged("Supra")
        # Letty takes a repair mission
        m1 = mission.create_mission("repair", "mechanic", "Letty")
        # Dom's delivery with Skyline is blocked — Letty is busy
        with pytest.raises(ValueError, match="damaged"):
            mission.create_mission("delivery", "driver", "Dom", car_name="Skyline")
        # Letty finishes — now Dom's mission can proceed
        mission.complete_mission(m1["id"])
        m2 = mission.create_mission("delivery", "driver", "Dom", car_name="Supra")
        assert m2["status"] == "active"
