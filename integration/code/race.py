"""Race Management module for StreetRace Manager."""

import registration
import inventory

_races = {}
_next_id = 1


def create_race(name: str, location: str) -> dict:
    """Create a new race with a name and location."""
    global _next_id
    if not name or not name.strip():
        raise ValueError("Race name cannot be empty.")
    if not location or not location.strip():
        raise ValueError("Race location cannot be empty.")
    race = {
        "id": _next_id,
        "name": name.strip(),
        "location": location.strip(),
        "entries": [],
        "status": "open",
    }
    _races[_next_id] = race
    _next_id += 1
    return race


def get_race(race_id: int) -> dict:
    """Return a race by id, or None if not found."""
    return _races.get(race_id)


def list_races() -> list:
    """Return all races."""
    return list(_races.values())


def enter_race(race_id: int, driver_name: str, car_name: str) -> dict:
    """Enter a driver and car into a race. Enforces all business rules."""
    race = _races.get(race_id)
    if race is None:
        raise ValueError(f"Race with id {race_id} does not exist.")
    if race["status"] != "open":
        raise ValueError(f"Race '{race['name']}' is not open for entries.")
    if not registration.is_registered(driver_name):
        raise ValueError(f"'{driver_name}' is not a registered crew member.")
    member = registration.get_member(driver_name)
    if member["role"] != "driver":
        raise ValueError(
            f"'{driver_name}' has role '{member['role']}' — only drivers may enter a race."
        )
    car = inventory.get_car(car_name)
    if car is None:
        raise ValueError(f"Car '{car_name}' is not in the inventory.")
    if car["damaged"]:
        raise ValueError(f"Car '{car_name}' is damaged and cannot race.")
    for entry in race["entries"]:
        if entry["driver"] == driver_name:
            raise ValueError(f"'{driver_name}' is already entered in this race.")
    entry = {"driver": driver_name, "car": car_name}
    race["entries"].append(entry)
    return entry


def start_race(race_id: int) -> dict:
    """Mark a race as started. Requires at least one entry."""
    race = _races.get(race_id)
    if race is None:
        raise ValueError(f"Race with id {race_id} does not exist.")
    if race["status"] != "open":
        raise ValueError(f"Race is already {race['status']}.")
    if not race["entries"]:
        raise ValueError("Cannot start a race with no entries.")
    race["status"] = "in_progress"
    return race


def clear() -> None:
    """Clear all races. Used in tests."""
    global _next_id
    _races.clear()
    _next_id = 1
