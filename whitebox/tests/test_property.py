"""
White-box tests for property.py.
Covers all branches in Property.mortgage(), unmortgage(), get_rent(),
and PropertyGroup.all_owned_by().
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "moneypoly"))

from moneypoly.property import Property, PropertyGroup
from moneypoly.player import Player


class TestPropertyMortgage:
    """Branch coverage for Property.mortgage()."""

    def _make_prop(self):
        return Property("Park Lane", 37, 350, 35)

    def test_mortgage_returns_half_price(self):
        """Mortgaging returns price // 2 as payout."""
        prop = self._make_prop()
        payout = prop.mortgage()
        assert payout == 175  # 350 // 2

    def test_mortgage_sets_is_mortgaged_true(self):
        """After mortgaging, is_mortgaged flag is True."""
        prop = self._make_prop()
        prop.mortgage()
        assert prop.is_mortgaged

    def test_mortgage_already_mortgaged_returns_zero(self):
        """Branch: already mortgaged returns 0 without changing state."""
        prop = self._make_prop()
        prop.mortgage()
        second_payout = prop.mortgage()
        assert second_payout == 0


class TestPropertyUnmortgage:
    """Branch coverage for Property.unmortgage()."""

    def _make_prop(self):
        return Property("Park Lane", 37, 350, 35)

    def test_unmortgage_returns_110_percent_of_mortgage_value(self):
        """Unmortgaging costs 110% of mortgage value."""
        prop = self._make_prop()
        prop.mortgage()
        cost = prop.unmortgage()
        assert cost == int(175 * 1.1)

    def test_unmortgage_clears_flag(self):
        """After unmortgaging, is_mortgaged flag is False."""
        prop = self._make_prop()
        prop.mortgage()
        prop.unmortgage()
        assert not prop.is_mortgaged

    def test_unmortgage_not_mortgaged_returns_zero(self):
        """Branch: unmortgaging a property that is not mortgaged returns 0."""
        prop = self._make_prop()
        cost = prop.unmortgage()
        assert cost == 0


class TestPropertyGetRent:
    """Branch coverage for Property.get_rent()."""

    def test_get_rent_mortgaged_returns_zero(self):
        """Branch: mortgaged property returns 0 rent."""
        prop = self._make_prop()
        prop.mortgage()
        assert prop.get_rent() == 0

    def test_get_rent_no_group_returns_base_rent(self):
        """Property with no group returns base_rent."""
        prop = self._make_prop()
        assert prop.get_rent() == 35

    def test_get_rent_full_group_doubles_rent(self):
        """Branch: owner holds full group, rent is doubled."""
        group = PropertyGroup("Blue", "blue")
        prop = Property("Park Lane", 37, 350, 35, group)
        player = Player("Alice")
        prop.owner = player
        group.properties = [prop]  # only one property in group for simplicity
        assert prop.get_rent() == 70  # 35 * 2

    def _make_prop(self):
        return Property("Park Lane", 37, 350, 35)


class TestPropertyGroupAllOwnedBy:
    """Branch coverage for PropertyGroup.all_owned_by() — exposes any() vs all() bug."""

    def _make_group(self):
        group = PropertyGroup("Blue", "blue")
        p1 = Property("Mayfair", 39, 400, 50, group)
        p2 = Property("Park Lane", 37, 350, 35, group)
        return group, p1, p2

    def test_all_owned_returns_true_when_all_owned(self):
        """Returns True when every property in group is owned by the same player."""
        group, p1, p2 = self._make_group()
        player = Player("Alice")
        p1.owner = player
        p2.owner = player
        assert group.all_owned_by(player)

    def test_all_owned_returns_false_when_none_owned(self):
        """Returns False when no properties are owned."""
        group, p1, p2 = self._make_group()
        player = Player("Alice")
        assert not group.all_owned_by(player)

    def test_all_owned_returns_false_when_only_one_owned(self):
        """
        BUG EXPOSED: all_owned_by uses any() instead of all().
        With only one of two properties owned, any() wrongly returns True.
        The correct behaviour is to return False.
        """
        group, p1, p2 = self._make_group()
        player = Player("Alice")
        p1.owner = player  # only one of two owned
        # BUG: any() returns True — should be False
        assert not group.all_owned_by(player)

    def test_all_owned_none_player_returns_false(self):
        """Branch: passing None as player always returns False."""
        group, p1, p2 = self._make_group()
        assert not group.all_owned_by(None)
