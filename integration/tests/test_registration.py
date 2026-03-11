"""Unit tests for registration.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import pytest


class TestRegister:

    def setup_method(self):
        registration.clear()

    def test_register_valid_driver(self):
        member = registration.register("Dom", "driver")
        assert member["name"] == "Dom"
        assert member["role"] == "driver"

    def test_register_valid_mechanic(self):
        member = registration.register("Letty", "mechanic")
        assert member["role"] == "mechanic"

    def test_register_valid_strategist(self):
        member = registration.register("Brian", "strategist")
        assert member["role"] == "strategist"

    def test_register_empty_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            registration.register("", "driver")

    def test_register_whitespace_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            registration.register("   ", "driver")

    def test_register_invalid_role_raises(self):
        with pytest.raises(ValueError, match="Invalid role"):
            registration.register("Dom", "racer")

    def test_register_duplicate_name_raises(self):
        registration.register("Dom", "driver")
        with pytest.raises(ValueError, match="already registered"):
            registration.register("Dom", "mechanic")


class TestGetMember:

    def setup_method(self):
        registration.clear()

    def test_get_existing_member(self):
        registration.register("Dom", "driver")
        m = registration.get_member("Dom")
        assert m is not None
        assert m["name"] == "Dom"

    def test_get_nonexistent_member_returns_none(self):
        assert registration.get_member("Ghost") is None


class TestIsRegistered:

    def setup_method(self):
        registration.clear()

    def test_is_registered_true(self):
        registration.register("Dom", "driver")
        assert registration.is_registered("Dom") is True

    def test_is_registered_false(self):
        assert registration.is_registered("Nobody") is False


class TestListMembers:

    def setup_method(self):
        registration.clear()

    def test_list_empty(self):
        assert registration.list_members() == []

    def test_list_multiple_members(self):
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        assert len(registration.list_members()) == 2
