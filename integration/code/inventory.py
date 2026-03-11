"""Inventory module for StreetRace Manager."""

_cash = 0
_cars = {}
_parts = {}
_tools = {}


def set_cash(amount: int) -> None:
    """Set the cash balance. Must be non-negative."""
    global _cash
    if amount < 0:
        raise ValueError("Cash balance cannot be negative.")
    _cash = amount


def get_cash() -> int:
    """Return the current cash balance."""
    return _cash


def add_cash(amount: int) -> None:
    """Add a positive amount to the cash balance."""
    global _cash
    if amount <= 0:
        raise ValueError("Amount to add must be positive.")
    _cash += amount


def deduct_cash(amount: int) -> None:
    """Deduct a positive amount from cash. Raises if insufficient funds."""
    global _cash
    if amount <= 0:
        raise ValueError("Amount to deduct must be positive.")
    if amount > _cash:
        raise ValueError(f"Insufficient funds: have {_cash}, need {amount}.")
    _cash -= amount


def add_car(name: str) -> dict:
    """Add a car to inventory. Name must be unique and non-empty."""
    if not name or not name.strip():
        raise ValueError("Car name cannot be empty.")
    name = name.strip()
    if name in _cars:
        raise ValueError(f"Car '{name}' already exists in inventory.")
    car = {"name": name, "damaged": False}
    _cars[name] = car
    return car


def get_car(name: str) -> dict:
    """Return car dict or None if not found."""
    return _cars.get(name)


def list_cars() -> list:
    """Return all cars in inventory."""
    return list(_cars.values())


def mark_car_damaged(name: str) -> None:
    """Mark a car as damaged."""
    if name not in _cars:
        raise ValueError(f"Car '{name}' not found in inventory.")
    _cars[name]["damaged"] = True


def repair_car(name: str) -> None:
    """Mark a car as repaired (no longer damaged)."""
    if name not in _cars:
        raise ValueError(f"Car '{name}' not found in inventory.")
    _cars[name]["damaged"] = False


def add_parts(part_name: str, quantity: int) -> None:
    """Add spare parts to inventory. Quantity must be positive."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")
    _parts[part_name] = _parts.get(part_name, 0) + quantity


def get_parts(part_name: str) -> int:
    """Return quantity of a spare part, or 0 if not stocked."""
    return _parts.get(part_name, 0)


def add_tools(tool_name: str, quantity: int) -> None:
    """Add tools to inventory. Quantity must be positive."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")
    _tools[tool_name] = _tools.get(tool_name, 0) + quantity


def get_tools(tool_name: str) -> int:
    """Return quantity of a tool, or 0 if not stocked."""
    return _tools.get(tool_name, 0)


def clear() -> None:
    """Clear all inventory data. Used in tests."""
    global _cash
    _cash = 0
    _cars.clear()
    _parts.clear()
    _tools.clear()
