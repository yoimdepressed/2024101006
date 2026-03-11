"""Results module for StreetRace Manager."""

import inventory
import race as race_module

_results = {}
_rankings = {}


def record_result(race_id: int, winner_name: str, prize_money: int) -> dict:
    """Record race result, update rankings, and add prize money to inventory."""
    r = race_module.get_race(race_id)
    if r is None:
        raise ValueError(f"Race with id {race_id} does not exist.")
    if r["status"] != "in_progress":
        raise ValueError(f"Race '{r['name']}' is not in progress — cannot record result.")
    if prize_money < 0:
        raise ValueError("Prize money cannot be negative.")
    entered_drivers = [entry["driver"] for entry in r["entries"]]
    if winner_name not in entered_drivers:
        raise ValueError(f"'{winner_name}' is not entered in race '{r['name']}'.")
    r["status"] = "finished"
    if prize_money > 0:
        inventory.add_cash(prize_money)
    _rankings[winner_name] = _rankings.get(winner_name, 0) + 1
    result = {"race_id": race_id, "winner": winner_name, "prize": prize_money}
    _results[race_id] = result
    return result


def get_result(race_id: int) -> dict:
    """Return the result for a race, or None if not recorded."""
    return _results.get(race_id)


def get_ranking(driver_name: str) -> int:
    """Return the number of wins for a driver (0 if none)."""
    return _rankings.get(driver_name, 0)


def get_all_rankings() -> dict:
    """Return the full rankings dict."""
    return dict(_rankings)


def clear() -> None:
    """Clear all results and rankings. Used in tests."""
    _results.clear()
    _rankings.clear()
