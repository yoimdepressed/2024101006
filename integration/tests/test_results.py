"""Unit tests for results.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import inventory
import race as race_module
import results
import pytest


def _setup_in_progress_race():
    """Helper: create a race in 'in_progress' state with Dom driving Skyline."""
    registration.register("Dom", "driver")
    inventory.add_car("Skyline")
    inventory.set_cash(0)
    r = race_module.create_race("Night Race", "LA")
    race_module.enter_race(r["id"], "Dom", "Skyline")
    race_module.start_race(r["id"])
    return r["id"]


class TestRecordResult:

    def setup_method(self):
        registration.clear()
        inventory.clear()
        race_module.clear()
        results.clear()

    def test_record_result_valid(self):
        race_id = _setup_in_progress_race()
        result = results.record_result(race_id, "Dom", 5000)
        assert result["winner"] == "Dom"
        assert result["prize"] == 5000
        assert inventory.get_cash() == 5000

    def test_record_result_zero_prize(self):
        race_id = _setup_in_progress_race()
        results.record_result(race_id, "Dom", 0)
        assert inventory.get_cash() == 0

    def test_record_result_negative_prize_raises(self):
        race_id = _setup_in_progress_race()
        with pytest.raises(ValueError, match="negative"):
            results.record_result(race_id, "Dom", -100)

    def test_record_result_nonexistent_race_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            results.record_result(999, "Dom", 1000)

    def test_record_result_race_not_started_raises(self):
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        r = race_module.create_race("Race", "LA")
        race_module.enter_race(r["id"], "Dom", "Skyline")
        with pytest.raises(ValueError, match="not in progress"):
            results.record_result(r["id"], "Dom", 1000)

    def test_record_result_winner_not_entered_raises(self):
        race_id = _setup_in_progress_race()
        registration.register("Brian", "driver")
        with pytest.raises(ValueError, match="not entered"):
            results.record_result(race_id, "Brian", 1000)

    def test_record_result_marks_race_finished(self):
        race_id = _setup_in_progress_race()
        results.record_result(race_id, "Dom", 1000)
        r = race_module.get_race(race_id)
        assert r["status"] == "finished"

    def test_record_result_updates_ranking(self):
        race_id = _setup_in_progress_race()
        results.record_result(race_id, "Dom", 1000)
        assert results.get_ranking("Dom") == 1


class TestRankings:

    def setup_method(self):
        registration.clear()
        inventory.clear()
        race_module.clear()
        results.clear()

    def test_ranking_zero_for_new_driver(self):
        assert results.get_ranking("Dom") == 0

    def test_ranking_increments_across_races(self):
        registration.register("Dom", "driver")
        inventory.add_car("Skyline")
        inventory.add_car("Supra")
        inventory.set_cash(0)
        r1 = race_module.create_race("Race 1", "LA")
        race_module.enter_race(r1["id"], "Dom", "Skyline")
        race_module.start_race(r1["id"])
        results.record_result(r1["id"], "Dom", 1000)
        r2 = race_module.create_race("Race 2", "Miami")
        race_module.enter_race(r2["id"], "Dom", "Supra")
        race_module.start_race(r2["id"])
        results.record_result(r2["id"], "Dom", 2000)
        assert results.get_ranking("Dom") == 2
        assert inventory.get_cash() == 3000
