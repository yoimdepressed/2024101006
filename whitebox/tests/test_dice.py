"""
White-box tests for dice.py.
Covers all branches in roll(), is_doubles(), and doubles_streak tracking.
"""
import sys
import os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moneypoly"))

from moneypoly.dice import Dice


class TestDiceInit:
    """Verify initial state of a new Dice object."""

    def test_doubles_streak_initialized_to_zero(self):
        """doubles_streak must be 0 on a fresh Dice object."""
        d = Dice()
        assert d.doubles_streak == 0

    def test_die_values_initialized_to_zero(self):
        """die1 and die2 start at 0 before any roll."""
        d = Dice()
        assert d.die1 == 0
        assert d.die2 == 0


class TestDiceRoll:
    """Branch coverage for Dice.roll()."""

    def test_roll_minimum_total_is_two(self):
        """Each die minimum is 1 so minimum total is 2."""
        d = Dice()
        original = random.randint
        random.randint = lambda a, b: a  # always return lower bound (1)
        total = d.roll()
        random.randint = original
        assert total == 2

    def test_roll_max_total_exposes_dice_bug(self):
        """
        BUG EXPOSED: roll() uses randint(1, 5) instead of randint(1, 6).
        Forcing upper bound: should give 6+6=12 but gives 5+5=10.
        """
        d = Dice()
        original = random.randint
        random.randint = lambda a, b: b  # always return upper bound
        total = d.roll()
        random.randint = original
        # BUG: upper bound is 5, total is 10 instead of the correct 12
        assert total == 12

    def test_roll_doubles_increments_streak(self):
        """Branch: doubles roll increments doubles_streak."""
        d = Dice()
        original = random.randint
        random.randint = lambda a, b: 3  # both dice = 3, doubles
        d.roll()
        random.randint = original
        assert d.doubles_streak == 1

    def test_roll_non_doubles_resets_streak(self):
        """Branch: non-doubles roll resets doubles_streak to 0."""
        d = Dice()
        original = random.randint
        random.randint = lambda a, b: 3
        d.roll()  # doubles, streak = 1
        counter = [0]
        def alternating(a, b):
            counter[0] += 1
            return 3 if counter[0] % 2 == 1 else 4  # die1=3, die2=4
        random.randint = alternating
        d.roll()  # not doubles
        random.randint = original
        assert d.doubles_streak == 0

    def test_roll_consecutive_doubles_increments_streak(self):
        """Streak increments correctly across multiple consecutive doubles."""
        d = Dice()
        original = random.randint
        random.randint = lambda a, b: 3
        d.roll()
        d.roll()
        random.randint = original
        assert d.doubles_streak == 2


class TestIsDoubles:
    """Tests for Dice.is_doubles()."""

    def test_is_doubles_true_when_equal(self):
        """is_doubles returns True when both dice show same value."""
        d = Dice()
        original = random.randint
        random.randint = lambda a, b: 4
        d.roll()
        random.randint = original
        assert d.is_doubles()

    def test_is_doubles_false_when_not_equal(self):
        """is_doubles returns False when dice show different values."""
        d = Dice()
        counter = [0]
        original = random.randint
        def alternating(a, b):
            counter[0] += 1
            return 2 if counter[0] % 2 == 1 else 5
        random.randint = alternating
        d.roll()
        random.randint = original
        assert not d.is_doubles()
