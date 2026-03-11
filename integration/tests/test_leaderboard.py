"""Unit tests for leaderboard.py."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import registration
import inventory
import race as race_module
import results
import leaderboard


def clear_all():
    registration.clear()
    inventory.clear()
    race_module.clear()
    results.clear()


def _run_race(driver, car, prize):
    """Helper: run a complete race and record result."""
    inventory.add_car(car)
    r = race_module.create_race(f"Race-{car}", "LA")
    race_module.enter_race(r["id"], driver, car)
    race_module.start_race(r["id"])
    results.record_result(r["id"], driver, prize)


class TestLeaderboard:

    def setup_method(self):
        clear_all()

    def test_empty_leaderboard(self):
        """No races recorded — leaderboard is empty."""
        assert leaderboard.get_leaderboard() == []

    def test_single_winner_on_leaderboard(self):
        """One win — driver appears with 1 win."""
        registration.register("Dom", "driver")
        inventory.set_cash(0)
        _run_race("Dom", "Skyline", 1000)
        board = leaderboard.get_leaderboard()
        assert board[0] == ("Dom", 1)

    def test_leaderboard_sorted_by_wins(self):
        """Driver with more wins is ranked higher."""
        registration.register("Dom", "driver")
        registration.register("Brian", "driver")
        inventory.set_cash(0)
        _run_race("Dom", "Skyline", 1000)
        _run_race("Dom", "Supra", 1000)
        _run_race("Brian", "GTR", 500)
        board = leaderboard.get_leaderboard()
        assert board[0][0] == "Dom"
        assert board[1][0] == "Brian"

    def test_get_top_driver(self):
        """Top driver is the one with the most wins."""
        registration.register("Dom", "driver")
        registration.register("Brian", "driver")
        inventory.set_cash(0)
        _run_race("Dom", "Skyline", 1000)
        _run_race("Dom", "Supra", 1000)
        _run_race("Brian", "GTR", 500)
        assert leaderboard.get_top_driver() == "Dom"

    def test_get_top_driver_no_races_returns_none(self):
        """No races — top driver is None."""
        assert leaderboard.get_top_driver() is None

    def test_get_position_ranked_driver(self):
        """Returns correct 1-based position for a ranked driver."""
        registration.register("Dom", "driver")
        registration.register("Brian", "driver")
        inventory.set_cash(0)
        _run_race("Dom", "Skyline", 1000)
        _run_race("Dom", "Supra", 1000)
        _run_race("Brian", "GTR", 500)
        assert leaderboard.get_position("Dom") == 1
        assert leaderboard.get_position("Brian") == 2

    def test_get_position_unranked_driver_returns_minus_one(self):
        """Driver who has never won returns -1."""
        assert leaderboard.get_position("Nobody") == -1
