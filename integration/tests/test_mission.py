"""Unit tests for mission.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import crew as crew_module
import inventory
import mission
import pytest


class TestCreateMission:

    def setup_method(self):
        registration.clear()
        crew_module.clear()
        inventory.clear()
        mission.clear()
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        inventory.add_car("Skyline")

    def test_create_mission_valid_driver_delivery(self):
        m = mission.create_mission("delivery", "driver", "Dom")
        assert m["assignee"] == "Dom"
        assert m["type"] == "delivery"
        assert m["status"] == "active"

    def test_create_mission_valid_mechanic_repair(self):
        m = mission.create_mission("repair", "mechanic", "Letty")
        assert m["assignee"] == "Letty"

    def test_create_mission_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid mission type"):
            mission.create_mission("heist", "driver", "Dom")

    def test_create_mission_unregistered_assignee_raises(self):
        with pytest.raises(ValueError, match="not registered"):
            mission.create_mission("delivery", "driver", "Ghost")

    def test_create_mission_role_mismatch_raises(self):
        with pytest.raises(ValueError, match="requires 'mechanic'"):
            mission.create_mission("repair", "mechanic", "Dom")

    def test_create_mission_already_active_raises(self):
        mission.create_mission("delivery", "driver", "Dom")
        with pytest.raises(ValueError, match="already on an active mission"):
            mission.create_mission("escort", "driver", "Dom")

    def test_create_mission_damaged_car_no_mechanic_raises(self):
        inventory.mark_car_damaged("Skyline")
        mission.create_mission("repair", "mechanic", "Letty")
        with pytest.raises(ValueError, match="damaged"):
            mission.create_mission("delivery", "driver", "Dom", car_name="Skyline")

    def test_create_mission_damaged_car_mechanic_available(self):
        inventory.mark_car_damaged("Skyline")
        m = mission.create_mission("delivery", "driver", "Dom", car_name="Skyline")
        assert m["status"] == "active"

    def test_create_mission_undamaged_car_no_mechanic_needed(self):
        m = mission.create_mission("delivery", "driver", "Dom", car_name="Skyline")
        assert m["status"] == "active"


class TestCompleteMission:

    def setup_method(self):
        registration.clear()
        crew_module.clear()
        inventory.clear()
        mission.clear()
        registration.register("Dom", "driver")

    def test_complete_mission_valid(self):
        m = mission.create_mission("delivery", "driver", "Dom")
        completed = mission.complete_mission(m["id"])
        assert completed["status"] == "completed"

    def test_complete_mission_nonexistent_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            mission.complete_mission(999)

    def test_complete_mission_already_completed_raises(self):
        m = mission.create_mission("delivery", "driver", "Dom")
        mission.complete_mission(m["id"])
        with pytest.raises(ValueError, match="already completed"):
            mission.complete_mission(m["id"])

    def test_complete_mission_frees_member_for_new_mission(self):
        m = mission.create_mission("delivery", "driver", "Dom")
        mission.complete_mission(m["id"])
        m2 = mission.create_mission("escort", "driver", "Dom")
        assert m2["status"] == "active"
