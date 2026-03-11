"""
White-box tests for bank.py.
Covers all branches in Bank.collect(), pay_out(), and give_loan().
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moneypoly"))

from moneypoly.bank import Bank
from moneypoly.player import Player
from moneypoly.config import BANK_STARTING_FUNDS


class TestBankCollect:
    """Branch coverage for Bank.collect()."""

    def test_collect_increases_funds(self):
        """Collecting a positive amount increases bank reserves."""
        b = Bank()
        b.collect(500)
        assert b.get_balance() == BANK_STARTING_FUNDS + 500

    def test_collect_zero_does_not_change_balance(self):
        """Collecting zero does not change bank reserves."""
        b = Bank()
        b.collect(0)
        assert b.get_balance() == BANK_STARTING_FUNDS


class TestBankPayOut:
    """Branch coverage for Bank.pay_out()."""

    def test_pay_out_decreases_funds(self):
        """Paying out a valid amount reduces bank reserves."""
        b = Bank()
        b.pay_out(500)
        assert b.get_balance() == BANK_STARTING_FUNDS - 500

    def test_pay_out_zero_returns_zero_and_no_change(self):
        """Branch: amount <= 0 returns 0 without changing balance."""
        b = Bank()
        result = b.pay_out(0)
        assert result == 0
        assert b.get_balance() == BANK_STARTING_FUNDS

    def test_pay_out_negative_returns_zero(self):
        """Branch: negative amount treated the same as zero, returns 0."""
        b = Bank()
        result = b.pay_out(-100)
        assert result == 0

    def test_pay_out_more_than_funds_raises_value_error(self):
        """Branch: amount exceeds bank funds raises ValueError."""
        b = Bank()
        b._funds = 100
        try:
            b.pay_out(200)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_pay_out_exact_funds_succeeds(self):
        """Edge case: paying out exactly the bank balance succeeds."""
        b = Bank()
        b._funds = 500
        result = b.pay_out(500)
        assert result == 500
        assert b.get_balance() == 0


class TestBankGiveLoan:
    """Branch coverage for Bank.give_loan()."""

    def test_give_loan_credits_player(self):
        """A valid loan increases the player balance."""
        b = Bank()
        p = Player("Alice")
        before = p.balance
        b.give_loan(p, 200)
        assert p.balance == before + 200

    def test_give_loan_zero_does_nothing(self):
        """Branch: amount <= 0 is ignored, player balance unchanged."""
        b = Bank()
        p = Player("Alice")
        before = p.balance
        b.give_loan(p, 0)
        assert p.balance == before
