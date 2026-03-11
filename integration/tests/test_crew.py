"""Unit tests for crew.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import crew
import pytest


class TestAssignSkill:

    def setup_method(self):
        registration.clear()
        crew.clear()

    def test_assign_skill_valid(self):
        registration.register("Dom", "driver")
        crew.assign_skill("Dom", 8)
        assert crew.get_skill("Dom") == 8

    def test_assign_skill_updates_existing(self):
        registration.register("Dom", "driver")
        crew.assign_skill("Dom", 5)
        crew.assign_skill("Dom", 9)
        assert crew.get_skill("Dom") == 9

    def test_assign_skill_unregistered_raises(self):
        with pytest.raises(ValueError, match="not registered"):
            crew.assign_skill("Ghost", 7)

    def test_assign_skill_too_low_raises(self):
        registration.register("Dom", "driver")
        with pytest.raises(ValueError, match="between 1 and 10"):
            crew.assign_skill("Dom", 0)

    def test_assign_skill_too_high_raises(self):
        registration.register("Dom", "driver")
        with pytest.raises(ValueError, match="between 1 and 10"):
            crew.assign_skill("Dom", 11)

    def test_assign_skill_boundary_one(self):
        registration.register("Dom", "driver")
        crew.assign_skill("Dom", 1)
        assert crew.get_skill("Dom") == 1

    def test_assign_skill_boundary_ten(self):
        registration.register("Dom", "driver")
        crew.assign_skill("Dom", 10)
        assert crew.get_skill("Dom") == 10


class TestGetSkill:

    def setup_method(self):
        registration.clear()
        crew.clear()

    def test_get_skill_no_assignment_returns_zero(self):
        registration.register("Dom", "driver")
        assert crew.get_skill("Dom") == 0

    def test_get_skill_unregistered_raises(self):
        with pytest.raises(ValueError):
            crew.get_skill("Ghost")


class TestGetRole:

    def setup_method(self):
        registration.clear()
        crew.clear()

    def test_get_role_returns_correct_role(self):
        registration.register("Letty", "mechanic")
        assert crew.get_role("Letty") == "mechanic"

    def test_get_role_unregistered_returns_none(self):
        assert crew.get_role("Ghost") is None


class TestListByRole:

    def setup_method(self):
        registration.clear()
        crew.clear()

    def test_list_drivers_returns_only_drivers(self):
        registration.register("Dom", "driver")
        registration.register("Brian", "driver")
        registration.register("Letty", "mechanic")
        drivers = crew.list_by_role("driver")
        names = [d["name"] for d in drivers]
        assert "Dom" in names
        assert "Brian" in names
        assert "Letty" not in names

    def test_list_role_no_members_returns_empty(self):
        registration.register("Dom", "driver")
        assert crew.list_by_role("strategist") == []
