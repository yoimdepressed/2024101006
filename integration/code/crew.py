"""Crew Management module for StreetRace Manager."""

import registration

_skills = {}


def assign_skill(name: str, skill_level: int) -> None:
    """Assign a skill level (1-10) to a registered crew member."""
    if not registration.is_registered(name):
        raise ValueError(f"Cannot assign skill: '{name}' is not registered.")
    if not isinstance(skill_level, int) or skill_level < 1 or skill_level > 10:
        raise ValueError("Skill level must be an integer between 1 and 10.")
    _skills[name] = skill_level


def get_skill(name: str) -> int:
    """Return skill level for a member (0 if not yet assigned)."""
    if not registration.is_registered(name):
        raise ValueError(f"'{name}' is not a registered crew member.")
    return _skills.get(name, 0)


def get_role(name: str) -> str:
    """Return the role of a crew member, or None if not registered."""
    member = registration.get_member(name)
    if member is None:
        return None
    return member["role"]


def list_by_role(role: str) -> list:
    """Return all registered members with the given role."""
    return [m for m in registration.list_members() if m["role"] == role]


def clear() -> None:
    """Clear all skill data. Used in tests."""
    _skills.clear()
