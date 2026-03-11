"""
Integration tests: Mission Planning role rules and complete flow.
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
    registration.clear()
    crew_module.clear()
    inventory.clear()
    race_module.clear()
    results.clear()
    mission.clear()


class TestMissionRoleRules:

    def setup_method(self):
        clear_all()

    def test_mission_requires_correct_role(self):
        """A driver cannot be assigned to a mechanic mission."""
        registration.register("Dom", "driver")
        with pytest.raises(ValueError, match="requires 'mechanic'"):
            mission.create_mission("repair", "mechanic", "Dom")

    def test_unregistered_member_cannot_get_mission(self):
        """Cannot assign a mission to someone not in registration."""
        with pytest.raises(ValueError, match="not registered"):
            mission.create_mission("delivery", "driver", "Ghost")

    def test_member_cannot_have_two_active_missions(self):
        """A crew member already on a mission cannot take another."""
        registration.register("Dom", "driver")
        mission.create_mission("delivery", "driver", "Dom")
        with pytest.raises(ValueError, match="already on an active mission"):
            mission.create_mission("escort", "driver", "Dom")

    def test_completed_mission_allows_new_one(self):
        """After completing a mission, the member can be assigned again."""
        registration.register("Dom", "driver")
        m = mission.create_mission("delivery", "driver", "Dom")
        mission.complete_mission(m["id"])
        m2 = mission.create_mission("escort", "driver", "Dom")
        assert m2["status"] == "active"

    def test_mission_cannot_start_if_role_unavailable(self):
        """Mission requiring strategist role fails when assignee is a driver."""
        registration.register("Dom", "driver")
        with pytest.raises(ValueError, match="requires 'strategist'"):
            mission.create_mission("escort", "strategist", "Dom")


class TestFullEndToEnd:

    def setup_method(self):
        clear_all()

    def test_full_workflow(self):
        """
        register crew → add car → assign skills → create race → enter race → start race 
        → record result → verify cash and ranking → assign post-race mission.
        """
        # Step 1: Register crew
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        registration.register("Brian", "strategist")

        # Step 2: Assign skills
        crew_module.assign_skill("Dom", 9)
        crew_module.assign_skill("Letty", 8)

        # Step 3: Add car and set starting cash
        inventory.add_car("Skyline")
        inventory.set_cash(1000)

        # Step 4: Create race and enter Dom
        r = race_module.create_race("Grand Prix", "Tokyo")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        race_module.start_race(r["id"])

        # Step 5: Record result — Dom wins $5000
        results.record_result(r["id"], "Dom", 5000)

        # Step 6: Verify cash updated and ranking recorded
        assert inventory.get_cash() == 6000   # 1000 starting + 5000 prize
        assert results.get_ranking("Dom") == 1
        assert race_module.get_race(r["id"])["status"] == "finished"

        # Step 7: Assign a post-race delivery mission to Dom
        m = mission.create_mission("delivery", "driver", "Dom")
        assert m["status"] == "active"
        assert m["assignee"] == "Dom"
