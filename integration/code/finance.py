"""Finance module for StreetRace Manager."""
import inventory

_log = []  # list of {"type": "income"/"expense", "amount": int, "reason": str}


def record_income(amount: int, reason: str) -> None:
    """Add money to inventory and log it as income."""
    if amount <= 0:
        raise ValueError("Income amount must be positive.")
    inventory.add_cash(amount)
    _log.append({"type": "income", "amount": amount, "reason": reason})


def record_expense(amount: int, reason: str) -> None:
    """Deduct money from inventory and log it as an expense."""
    if amount <= 0:
        raise ValueError("Expense amount must be positive.")
    inventory.deduct_cash(amount)  # raises if insufficient funds
    _log.append({"type": "expense", "amount": amount, "reason": reason})


def get_log() -> list:
    """Return the full transaction log."""
    return list(_log)


def get_total_income() -> int:
    """Return the sum of all recorded income."""
    return sum(e["amount"] for e in _log if e["type"] == "income")


def get_total_expenses() -> int:
    """Return the sum of all recorded expenses."""
    return sum(e["amount"] for e in _log if e["type"] == "expense")


def clear() -> None:
    """Clear the transaction log. Used in tests."""
    _log.clear()
