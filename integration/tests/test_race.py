"""Unit tests for race.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import inventory
import race
import pytest


class TestCreateRace:

    def setup_method(self):
        race.clear()

    def test_create_race_valid(self):
        r = race.create_race("Night Race", "Los Angeles")
        assert r["name"] == "Night Race"
        assert r["location"] == "Los Angeles"
        assert r["status"] == "open"
        assert r["entries"] == []

    def test_create_race_empty_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            race.create_race("", "LA")

    def test_create_race_empty_location_raises(self):
        with pytest.raises(ValueError, match="empty"):
            race.create_race("Night Race", "")

    def test_create_race_ids_increment(self):
        r1 = race.create_race("Race 1", "LA")
        r2 = race.create_race("Race 2", "Miami")
        assert r2["id"] == r1["id"] + 1


class TestEnterRace:

    def setup_method(self):
        registration.clear()
        inventory.clear()
        race.clear()
        registration.register("Dom", "driver")
        registration.register("Letty", "mechanic")
        inventory.add_car("Skyline")
        self.race_id = race.create_race("Night Race", "LA")["id"]

    def test_enter_race_valid(self):
        entry = race.enter_race(self.race_id, "Dom", "Skyline")
        assert entry["driver"] == "Dom"
        assert entry["car"] == "Skyline"

    def test_enter_race_nonexistent_race_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            race.enter_race(999, "Dom", "Skyline")

    def test_enter_race_unregistered_driver_raises(self):
        with pytest.raises(ValueError, match="not a registered"):
            race.enter_race(self.race_id, "Ghost", "Skyline")

    def test_enter_race_non_driver_role_raises(self):
        with pytest.raises(ValueError, match="only drivers"):
            race.enter_race(self.race_id, "Letty", "Skyline")

    def test_enter_race_car_not_in_inventory_raises(self):
        with pytest.raises(ValueError, match="not in the inventory"):
            race.enter_race(self.race_id, "Dom", "UnknownCar")

    def test_enter_race_damaged_car_raises(self):
        inventory.mark_car_damaged("Skyline")
        with pytest.raises(ValueError, match="damaged"):
            race.enter_race(self.race_id, "Dom", "Skyline")

    def test_enter_race_duplicate_driver_raises(self):
        race.enter_race(self.race_id, "Dom", "Skyline")
        inventory.add_car("Supra")
        with pytest.raises(ValueError, match="already entered"):
            race.enter_race(self.race_id, "Dom", "Supra")


class TestStartRace:

    def setup_method(self):
        registration.clear()
        inventory.clear()
        race.clear()
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        self.race_id = race.create_race("Night Race", "LA")["id"]

    def test_start_race_valid(self):
        race.enter_race(self.race_id, "Dom", "Skyline")
        r = race.start_race(self.race_id)
        assert r["status"] == "in_progress"

    def test_start_race_no_entries_raises(self):
        with pytest.raises(ValueError, match="no entries"):
            race.start_race(self.race_id)

    def test_start_race_already_started_raises(self):
        race.enter_race(self.race_id, "Dom", "Skyline")
        race.start_race(self.race_id)
        with pytest.raises(ValueError, match="already"):
            race.start_race(self.race_id)

    def test_start_race_nonexistent_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            race.start_race(999)
