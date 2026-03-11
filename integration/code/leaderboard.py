"""Leaderboard module for StreetRace Manager."""
import results as results_module


def get_leaderboard() -> list:
    """Return drivers sorted by wins descending. Each entry is (name, wins)."""
    rankings = results_module.get_all_rankings()
    sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    return sorted_rankings


def get_top_driver() -> str:
    """Return the name of the driver with the most wins, or None if no races recorded."""
    board = get_leaderboard()
    if not board:
        return None
    return board[0][0]


def get_position(driver_name: str) -> int:
    """Return the leaderboard position (1-based) of a driver, or -1 if not ranked."""
    board = get_leaderboard()
    for position, (name, _) in enumerate(board, start=1):
        if name == driver_name:
            return position
    return -1
