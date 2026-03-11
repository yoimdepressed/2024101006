"""Registration module for StreetRace Manager."""

VALID_ROLES = {"driver", "mechanic", "strategist"}

# In-memory store: maps name (str) -> {"name": str, "role": str}
_members = {}


def register(name: str, role: str) -> dict:
    """Register a new crew member with a name and role."""
    if not name or not name.strip():
        raise ValueError("Name cannot be empty.")
    name = name.strip()
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {VALID_ROLES}")
    if name in _members:
        raise ValueError(f"Crew member '{name}' is already registered.")
    member = {"name": name, "role": role}
    _members[name] = member
    return member


def get_member(name: str) -> dict:
    """Return the member dict for the given name, or None."""
    return _members.get(name)


def is_registered(name: str) -> bool:
    """Return True if the name is already registered."""
    return name in _members


def list_members() -> list:
    """Return a list of all registered crew members."""
    return list(_members.values())


def clear() -> None:
    """Clear all members. Used in tests."""
    _members.clear()
