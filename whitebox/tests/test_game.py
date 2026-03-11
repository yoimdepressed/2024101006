"""
White-box tests for game.py.
Covers buy_property and find_winner branches, exposing two logical bugs.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moneypoly"))

from moneypoly.game import Game
from moneypoly.property import Property


class TestBuyProperty:
    """Branch coverage for Game.buy_property()."""

    def _setup(self):
        game = Game(["Alice"])
        player = game.players[0]
        prop = Property("Mayfair", 39, 400, 50)
        return game, player, prop

    def test_buy_property_sufficient_funds_succeeds(self):
        """Player with more than enough money buys the property."""
        game, player, prop = self._setup()
        player.balance = 1000
        result = game.buy_property(player, prop)
        assert result is True
        assert prop.owner == player
        assert player.balance == 600

    def test_buy_property_insufficient_funds_fails(self):
        """Branch: player balance less than price returns False."""
        game, player, prop = self._setup()
        player.balance = 300
        result = game.buy_property(player, prop)
        assert result is False
        assert prop.owner is None

    def test_buy_property_exact_balance_equals_price(self):
        """
        BUG EXPOSED: buy_property uses `balance <= price` instead of `< price`.
        When balance exactly equals the price the player can afford it,
        but the bug incorrectly blocks the purchase and returns False.
        """
        game, player, prop = self._setup()
        player.balance = 400  # exactly equal to price
        result = game.buy_property(player, prop)
        # BUG: condition is <= so this returns False instead of True
        assert result is True

    def test_buy_property_zero_balance_fails(self):
        """Edge case: zero balance cannot buy any property."""
        game, player, prop = self._setup()
        player.balance = 0
        result = game.buy_property(player, prop)
        assert result is False


class TestFindWinner:
    """Branch coverage for Game.find_winner()."""

    def test_find_winner_returns_richest_player(self):
        """
        BUG EXPOSED: find_winner uses min() instead of max().
        It should return the player with the highest net worth,
        but currently returns the player with the lowest.
        """
        game = Game(["Alice", "Bob"])
        alice = game.players[0]
        bob = game.players[1]
        alice.balance = 5000
        bob.balance = 1000
        winner = game.find_winner()
        # BUG: min() picks Bob (lowest), should pick Alice (highest)
        assert winner == alice

    def test_find_winner_empty_returns_none(self):
        """Branch: no players remaining returns None."""
        game = Game(["Alice"])
        game.players = []
        assert game.find_winner() is None

    def test_find_winner_single_player_returns_that_player(self):
        """Edge case: only one player always wins."""
        game = Game(["Alice"])
        assert game.find_winner() == game.players[0]

    def test_find_winner_equal_balances(self):
        """Edge case: all players have same balance, any one can be returned."""
        game = Game(["Alice", "Bob"])
        game.players[0].balance = 1000
        game.players[1].balance = 1000
        winner = game.find_winner()
        assert winner in game.players
