"""
Integration tests: Results → Leaderboard
"""
import sys
import os
import pytest

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


def _setup_and_run_race(driver, car, prize):
    """register driver, add car, run race, record result."""
    if not registration.is_registered(driver):
        registration.register(driver, "driver")
    inventory.add_car(car)
    r = race_module.create_race(f"Race-{car}", "LA")
    race_module.enter_race(r["id"], driver, car)
    race_module.start_race(r["id"])
    results.record_result(r["id"], driver, prize)


class TestLeaderboardIntegration:

    def setup_method(self):
        clear_all()

    def test_leaderboard_empty_before_any_race(self):
        """Leaderboard has no entries when no races have been run."""
        assert leaderboard.get_leaderboard() == []
        assert leaderboard.get_top_driver() is None

    def test_leaderboard_updates_after_single_race(self):
        """After one race, the winner appears on the leaderboard with 1 win."""
        inventory.set_cash(0)
        _setup_and_run_race("Dom", "Skyline", 3000)
        board = leaderboard.get_leaderboard()
        assert len(board) == 1
        assert board[0] == ("Dom", 1)

    def test_leaderboard_reflects_multiple_drivers(self):
        """Two drivers race once each — both appear with 1 win."""
        inventory.set_cash(0)
        _setup_and_run_race("Dom", "Skyline", 3000)
        _setup_and_run_race("Brian", "Supra", 2000)
        board = leaderboard.get_leaderboard()
        names = [entry[0] for entry in board]
        assert "Dom" in names
        assert "Brian" in names

    def test_leaderboard_sorted_most_wins_first(self):
        """Driver with 2 wins ranks above driver with 1 win."""
        inventory.set_cash(0)
        _setup_and_run_race("Dom", "Skyline", 3000)
        _setup_and_run_race("Dom", "Supra", 3000)
        _setup_and_run_race("Brian", "GTR", 2000)
        board = leaderboard.get_leaderboard()
        assert board[0][0] == "Dom"
        assert board[0][1] == 2
        assert board[1][0] == "Brian"
        assert board[1][1] == 1

    def test_get_top_driver_changes_as_wins_accumulate(self):
        """Top driver is updated live as more race results are recorded."""
        inventory.set_cash(0)
        _setup_and_run_race("Brian", "GTR", 2000)
        assert leaderboard.get_top_driver() == "Brian"
        _setup_and_run_race("Dom", "Skyline", 3000)
        _setup_and_run_race("Dom", "Supra", 3000)
        assert leaderboard.get_top_driver() == "Dom"

    def test_position_reflects_live_rankings(self):
        """get_position() correctly returns 1-based rank tied to results data."""
        inventory.set_cash(0)
        _setup_and_run_race("Dom", "Skyline", 3000)
        _setup_and_run_race("Dom", "Supra", 3000)
        _setup_and_run_race("Brian", "GTR", 2000)
        assert leaderboard.get_position("Dom") == 1
        assert leaderboard.get_position("Brian") == 2
        assert leaderboard.get_position("Letty") == -1

    def test_cash_and_leaderboard_both_update_from_same_race(self):
        """Winning a race updates inventory cash and the leaderboard."""
        inventory.set_cash(0)
        _setup_and_run_race("Dom", "Skyline", 5000)
        assert inventory.get_cash() == 5000
        assert leaderboard.get_top_driver() == "Dom"
        assert leaderboard.get_position("Dom") == 1
