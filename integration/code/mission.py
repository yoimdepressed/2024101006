"""Mission Planning module for StreetRace Manager."""

import registration
import crew as crew_module
import inventory

# In-memory store
_missions = {}
_next_id = 1

VALID_MISSION_TYPES = {"delivery", "rescue", "repair", "escort"}


def create_mission(mission_type: str, required_role: str, assignee_name: str, car_name: str = None) -> dict:
    """Create and assign a mission. Enforces role and mechanic availability rules."""
    global _next_id
    if mission_type not in VALID_MISSION_TYPES:
        raise ValueError(f"Invalid mission type '{mission_type}'. Must be one of: {VALID_MISSION_TYPES}")
    if not registration.is_registered(assignee_name):
        raise ValueError(f"'{assignee_name}' is not registered.")
    actual_role = crew_module.get_role(assignee_name)
    if actual_role != required_role:
        raise ValueError(
            f"Mission requires '{required_role}' but '{assignee_name}' has role '{actual_role}'."
        )
    for m in _missions.values():
        if m["assignee"] == assignee_name and m["status"] == "active":
            raise ValueError(f"'{assignee_name}' is already on an active mission.")
    if car_name is not None:
        car = inventory.get_car(car_name)
        if car is not None and car["damaged"]:
            mechanics = crew_module.list_by_role("mechanic")
            active_assignees = {m["assignee"] for m in _missions.values() if m["status"] == "active"}
            available_mechanics = [mech for mech in mechanics if mech["name"] not in active_assignees]
            if not available_mechanics:
                raise ValueError(
                    f"Car '{car_name}' is damaged — mission cannot proceed without an available mechanic."
                )
    mission = {
        "id": _next_id,
        "type": mission_type,
        "required_role": required_role,
        "assignee": assignee_name,
        "car": car_name,
        "status": "active",
    }
    _missions[_next_id] = mission
    _next_id += 1
    return mission


def complete_mission(mission_id: int) -> dict:
    """Mark a mission as completed."""
    mission = _missions.get(mission_id)
    if mission is None:
        raise ValueError(f"Mission {mission_id} does not exist.")
    if mission["status"] != "active":
        raise ValueError(f"Mission {mission_id} is already completed.")
    mission["status"] = "completed"
    return mission


def get_mission(mission_id: int) -> dict:
    """Return a mission by id, or None if not found."""
    return _missions.get(mission_id)


def list_active_missions() -> list:
    """Return all currently active missions."""
    return [m for m in _missions.values() if m["status"] == "active"]


def clear() -> None:
    """Clear all missions. Used in tests."""
    global _next_id
    _missions.clear()
    _next_id = 1
