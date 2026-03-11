"""
White-box tests for player.py.
Covers all branches in add_money, deduct_money, is_bankrupt, and move.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moneypoly"))

from moneypoly.player import Player
from moneypoly.config import STARTING_BALANCE, GO_SALARY


class TestAddMoney:
    """Branch coverage for Player.add_money()."""

    def test_add_positive_amount_increases_balance(self):
        """Normal positive amount increases balance correctly."""
        p = Player("Alice")
        p.add_money(100)
        assert p.balance == STARTING_BALANCE + 100

    def test_add_zero_does_not_change_balance(self):
        """Adding zero is valid and balance stays the same."""
        p = Player("Alice")
        p.add_money(0)
        assert p.balance == STARTING_BALANCE

    def test_add_negative_raises_value_error(self):
        """Branch: amount < 0 must raise ValueError."""
        p = Player("Alice")
        try:
            p.add_money(-50)
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestDeductMoney:
    """Branch coverage for Player.deduct_money()."""

    def test_deduct_positive_amount_decreases_balance(self):
        """Normal positive deduction decreases balance correctly."""
        p = Player("Alice")
        p.deduct_money(100)
        assert p.balance == STARTING_BALANCE - 100

    def test_deduct_zero_does_not_change_balance(self):
        """Deducting zero is valid and balance stays the same."""
        p = Player("Alice")
        p.deduct_money(0)
        assert p.balance == STARTING_BALANCE

    def test_deduct_negative_raises_value_error(self):
        """Branch: amount < 0 must raise ValueError."""
        p = Player("Alice")
        try:
            p.deduct_money(-50)
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestIsBankrupt:
    """Branch coverage for Player.is_bankrupt()."""

    def test_positive_balance_not_bankrupt(self):
        """Player with positive balance is not bankrupt."""
        p = Player("Alice")
        assert not p.is_bankrupt()

    def test_zero_balance_is_bankrupt(self):
        """Edge case: zero balance triggers bankruptcy."""
        p = Player("Alice")
        p.balance = 0
        assert p.is_bankrupt()

    def test_negative_balance_is_bankrupt(self):
        """Negative balance also triggers bankruptcy."""
        p = Player("Alice")
        p.balance = -1
        assert p.is_bankrupt()


class TestMove:
    """Branch coverage for Player.move()."""

    def test_move_normal_updates_position(self):
        """Normal move updates position correctly."""
        p = Player("Alice")
        result = p.move(5)
        assert result == 5
        assert p.position == 5

    def test_move_wraps_around_board(self):
        """Moving past board size wraps position back correctly."""
        p = Player("Alice")
        p.position = 38
        result = p.move(4)  # 38 + 4 = 42 % 40 = 2
        assert result == 2

    def test_move_lands_on_go_collects_salary(self):
        """Branch: position == 0 after move awards GO_SALARY."""
        p = Player("Alice")
        p.position = 38
        p.move(2)  # 38 + 2 = 40 % 40 = 0
        assert p.position == 0
        assert p.balance == STARTING_BALANCE + GO_SALARY

    def test_move_passing_go_does_not_collect_salary(self):
        """
        BUG EXPOSED: Player passing Go (position > 0 after wrapping) should
        collect GO_SALARY, but the code only checks position == 0.
        Moving from 38 by 5 steps lands on position 3 (passed Go),
        but no salary is awarded.
        """
        p = Player("Alice")
        p.position = 38
        p.move(5)  # 38 + 5 = 43 % 40 = 3 — passed Go
        assert p.position == 3
        # BUG: balance stays the same instead of increasing by GO_SALARY
        assert p.balance == STARTING_BALANCE
