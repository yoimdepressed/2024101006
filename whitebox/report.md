# White-Box Testing Report: MoneyPoly

---

## 1.2 Code Quality Analysis (Pylint Iterations)

Pylint was run on `whitebox/moneypoly/moneypoly/` after each fix. The initial score was **8.17/10**. The final score after all iterations is **10.00/10**.

All E0401 import errors in earlier runs were false positives caused by running pylint without the package root in `sys.path`. This was resolved in Iteration 19 (see below).

---

### Iteration 1: Added missing module docstrings to all files

**Warning fixed:** C0114 (missing-module-docstring) in all 9 files.

**Why:** Every Python module should have a top-level docstring explaining what it does. Without it, tools like pylint and documentation generators cannot describe the module.

**Files changed:** `game.py`, `player.py`, `board.py`, `bank.py`, `property.py`, `cards.py`, `dice.py`, `config.py`, `ui.py`

---

### Iteration 2: Added missing class docstrings to Bank and PropertyGroup

**Warning fixed:** C0115 (missing-class-docstring) in `bank.py` and `property.py`.

**Why:** Class docstrings explain the purpose of a class. `Bank` and `PropertyGroup` were missing them.

**Files changed:** `bank.py`, `property.py`

---

### Iteration 3: Removed unused imports from game.py, bank.py, dice.py, player.py

**Warning fixed:** W0611 (unused-import) in four files.

- `game.py`: `GO_TO_JAIL_POSITION` imported but never used in the file
- `bank.py`: `import math` imported but never used
- `dice.py`: `BOARD_SIZE` imported but never used
- `player.py`: `import sys` imported but never used

**Why:** Unused imports add clutter, slow down loading, and can confuse readers into thinking those names are needed.

**Files changed:** `game.py`, `bank.py`, `dice.py`, `player.py`

---

### Iteration 4: Fixed bare except to except ValueError in ui.py

**Warning fixed:** W0702 (bare-except) in `ui.py`.

**Why:** A bare `except:` catches every possible exception including system exits and keyboard interrupts. Specifying `except ValueError:` makes it only catch the expected error from bad integer input, which is the correct intent.

**Files changed:** `ui.py`

---

### Iteration 5: Fixed singleton comparison == True in board.py

**Warning fixed:** C0121 (singleton-comparison) in `board.py`.

**Why:** Writing `if prop.is_mortgaged == True:` is redundant. The Pythonic way is `if prop.is_mortgaged:` which reads more clearly and avoids subtle bugs with objects that override `__eq__`.

**Files changed:** `board.py`

---

### Iteration 6: Fixed f-string, no-else-break, superfluous parens, missing newline in game.py

**Warnings fixed:** W1309, R1723, C0325 (x2), C0304 in `game.py`.

- `f"GAME OVER"` had no interpolation so the `f` prefix was unnecessary
- `elif` after `break` in `interactive_menu` was removed (unreachable branch)
- Two `if not (condition):` expressions had unnecessary parentheses
- Missing newline added at end of file

**Files changed:** `game.py`

---

### Iteration 7: Fixed no-else-return in property.py, removed unused variable and missing newline in player.py

**Warnings fixed:** R1705 in `property.py`, W0612 and C0304 in `player.py`.

- `unmortgage()` had an unnecessary `else` block after a `return` statement
- `old_position` variable in `move()` was assigned but never used
- Missing newline added at end of `player.py`

**Files changed:** `property.py`, `player.py`

---

### Iteration 8: Removed unused variable and added missing newline in player.py

**Warning fixed:** W0612, C0304 in `player.py`.

**Files changed:** `player.py`

---

### Iteration 9: Fixed doubles_streak attribute defined outside __init__ in dice.py

**Warning fixed:** W0201 (attribute-defined-outside-init) in `dice.py`.

**Why:** `doubles_streak` was only assigned inside `reset()`, not in `__init__`. Pylint cannot guarantee the attribute exists if `reset()` is never called. Adding it to `__init__` ensures it is always defined on construction.

**Files changed:** `dice.py`

---

### Iteration 10: Fixed no-else-return in property.py

**Warning fixed:** R1705 in `property.py`.

**Why:** After a `return` statement, an `else` block is unnecessary. Removing it de-indents the code and makes the flow cleaner.

**Files changed:** `property.py`

---

### Iteration 11: Fixed long lines in cards.py by splitting card dicts across two lines

**Warning fixed:** C0301 (line-too-long) — 27 lines in `cards.py` exceeded 100 characters.

**Why:** Long lines reduce readability and make code harder to review. Each card dictionary was split so the `description` key sits on one line and `action`/`value` on the next.

**Files changed:** `cards.py`

---

### Iteration 12: Fixed trailing whitespace in cards.py

**Warning fixed:** C0303 (trailing-whitespace) — introduced when splitting long lines in Iteration 11.

**Why:** Trailing spaces are invisible noise that clutter diffs and version control output.

**Files changed:** `cards.py`

---

### Iteration 13: Fixed missing final newline in player.py

**Warning fixed:** C0304 (missing-final-newline) in `player.py`.

**Why:** POSIX standard requires text files to end with a newline. Many tools behave incorrectly without it.

**Files changed:** `player.py`

---

### Iteration 14: Added pylint disable comments for too-many-instance-attributes and too-many-arguments

**Warnings suppressed:** R0902 (too-many-instance-attributes) in `game.py`, `player.py`, `property.py` and R0913/R0917 (too-many-arguments) in `property.py`.

**Why these are justified:**
- `Game` genuinely needs 9 attributes: board, bank, dice, players, two indexes, running flag, and two card decks
- `Player` genuinely needs 8 attributes: name, balance, position, properties, jail state, jail turns, card count, and elimination flag
- `Property` genuinely needs 9 attributes: name, position, price, rent, mortgage value, owner, mortgaged flag, houses, and group
- `Property.__init__` needs 6 arguments because all are required to define a property

A `# pylint: disable` comment with a justification comment is the correct approach when refactoring would make the code worse.

**Files changed:** `game.py`, `player.py`, `property.py`

---

### Iteration 15: Refactored _move_and_resolve to fix too-many-branches by extracting _resolve_tile

**Warning fixed:** R0912 (too-many-branches, 15/12) in `game.py`.

**Why:** The `_move_and_resolve` method had 15 decision branches handling every tile type. This exceeds pylint's limit of 12 and makes the method hard to read. The tile-handling logic was extracted into a new `_resolve_tile` method. The two separate `elif tile == "railroad"` and `elif tile == "property"` branches were also combined into `elif tile in ("railroad", "property")`, reducing the count further.

**Files changed:** `game.py`

---

### Iteration 16: Fixed remaining trailing whitespace in cards.py

**Warning fixed:** C0303 (trailing-whitespace) — 3 remaining lines after Iteration 12.

**Files changed:** `cards.py`

---

### Iteration 17: Fixed too-many-positional-arguments disable comment in property.py

**Warning fixed:** R0917 (too-many-positional-arguments) in `property.py`.

**Why:** The existing disable comment only covered R0913 (too-many-arguments). R0917 is a separate but related warning in newer pylint versions and required being added to the same comment.

**Files changed:** `property.py`

---

### Iteration 18: Refactored _apply_card to fix too-many-branches by extracting _distribute_payment

**Warning fixed:** R0912 (too-many-branches, 15/12) in `game.py` — `_apply_card` method.

**Why:** `_apply_card` handled 7 different card action types with separate branches. The `birthday` and `collect_from_all` actions share identical logic (collect money from all other players), so they were merged into one `elif` and the shared logic extracted into `_distribute_payment`.

**Files changed:** `game.py`

---

### Iteration 19: Added __init__.py and .pylintrc to fix E0401 false-positive import errors

**Warning fixed:** E0401 (import-error) — 12 occurrences across `board.py`, `game.py`, `bank.py`, `player.py`.

**Why:** The `moneypoly` package had no `__init__.py` file, and the `whitebox/code` directory was not in pylint's module search path. This caused pylint to report that all `from moneypoly.xxx import ...` statements were broken, even though the code runs perfectly. The fix was to:
1. Add an empty `whitebox/code/moneypoly/__init__.py` to properly mark `moneypoly` as a Python package.
2. Add a `.pylintrc` at the project root with `init-hook='import sys; sys.path.insert(0, "whitebox/code")'` so pylint can find the package regardless of where it is invoked from.

**Files changed:** `moneypoly/__init__.py` (created), `.pylintrc` (created)

---

### Final pylint score: 10.00/10

---

## 1.3 White-Box Test Cases

Tests are located in `whitebox/tests/` and split into one file per module:

- `test_player.py` — tests for `player.py`
- `test_dice.py` — tests for `dice.py`
- `test_property.py` — tests for `property.py`
- `test_bank.py` — tests for `bank.py`
- `test_game.py` — tests for `game.py`

Test results after all bug fixes: **52 tests, 52 passed, 0 failed**.

---

### How the tests were designed

White-box testing means reading the source code structure and writing a test for every decision path. For each function, the approach was:

1. Identify every `if/elif/else` branch
2. Write one test per branch to ensure it is exercised
3. Test edge cases: zero values, exact boundary values, None inputs
4. Look for any logical errors visible from reading the code and write a test that proves the bug

---

### Test file: test_player.py

**TestAddMoney**

| Test | Why it is needed |
|------|-----------------|
| test_add_positive_amount_increases_balance | Normal path: positive amount should increase balance |
| test_add_zero_does_not_change_balance | Edge case: zero is a valid amount and should not change balance |
| test_add_negative_raises_value_error | Branch: amount < 0 triggers the ValueError branch |

**TestDeductMoney**

| Test | Why it is needed |
|------|-----------------|
| test_deduct_positive_amount_decreases_balance | Normal path: positive amount should decrease balance |
| test_deduct_zero_does_not_change_balance | Edge case: zero deduction leaves balance unchanged |
| test_deduct_negative_raises_value_error | Branch: amount < 0 triggers the ValueError branch |

**TestIsBankrupt**

| Test | Why it is needed |
|------|-----------------|
| test_positive_balance_not_bankrupt | Branch: balance > 0 returns False |
| test_zero_balance_is_bankrupt | Edge case: exactly zero triggers bankruptcy |
| test_negative_balance_is_bankrupt | Branch: balance < 0 also triggers bankruptcy |

**TestMove**

| Test | Why it is needed |
|------|-----------------|
| test_move_normal_updates_position | Normal path: position advances correctly |
| test_move_wraps_around_board | Edge case: position wraps using modulo when exceeding BOARD_SIZE |
| test_move_lands_on_go_collects_salary | Branch: position == 0 after move awards GO_SALARY |
| test_move_passing_go_collects_salary | Bug exposure → after fix: player passing Go without landing on it now correctly collects GO_SALARY |

---

### Test file: test_dice.py

**TestDiceInit**

| Test | Why it is needed |
|------|-----------------|
| test_doubles_streak_initialized_to_zero | Verifies attribute is set in __init__ after Iteration 9 fix |
| test_die_values_initialized_to_zero | Verifies initial state before any roll |

**TestDiceRoll**

| Test | Why it is needed |
|------|-----------------|
| test_roll_minimum_total_is_two | Edge case: minimum possible roll is 1+1=2 |
| test_roll_max_total_is_twelve | Bug exposure → after fix: max total is correctly 12 (6+6) |
| test_roll_doubles_increments_streak | Branch: doubles roll increments doubles_streak |
| test_roll_non_doubles_resets_streak | Branch: non-doubles roll resets doubles_streak to 0 |
| test_roll_consecutive_doubles_increments_streak | Key variable state: streak accumulates across consecutive doubles |

**TestIsDoubles**

| Test | Why it is needed |
|------|-----------------|
| test_is_doubles_true_when_equal | Branch: equal dice returns True |
| test_is_doubles_false_when_not_equal | Branch: unequal dice returns False |

---

### Test file: test_property.py

**TestPropertyMortgage**

| Test | Why it is needed |
|------|-----------------|
| test_mortgage_returns_half_price | Normal path: payout is price divided by 2 |
| test_mortgage_sets_is_mortgaged_true | Key variable state: flag must be set after mortgaging |
| test_mortgage_already_mortgaged_returns_zero | Branch: already mortgaged returns 0 |

**TestPropertyUnmortgage**

| Test | Why it is needed |
|------|-----------------|
| test_unmortgage_returns_110_percent_of_mortgage_value | Normal path: cost is 110% of mortgage value |
| test_unmortgage_clears_flag | Key variable state: flag must be cleared after unmortgaging |
| test_unmortgage_not_mortgaged_returns_zero | Branch: not mortgaged returns 0 |

**TestPropertyGetRent**

| Test | Why it is needed |
|------|-----------------|
| test_get_rent_mortgaged_returns_zero | Branch: mortgaged property has no rent |
| test_get_rent_no_group_returns_base_rent | Branch: no group means base rent only |
| test_get_rent_full_group_doubles_rent | Branch: full group ownership doubles the rent |

**TestPropertyGroupAllOwnedBy**

| Test | Why it is needed |
|------|-----------------|
| test_all_owned_returns_true_when_all_owned | Normal path: all properties owned returns True |
| test_all_owned_returns_false_when_none_owned | Branch: no properties owned returns False |
| test_all_owned_returns_false_when_only_one_owned | Bug exposure: any() wrongly returns True when only one of two is owned |
| test_all_owned_none_player_returns_false | Edge case: None player always returns False |

---

### Test file: test_bank.py

**TestBankCollect**

| Test | Why it is needed |
|------|-----------------|
| test_collect_increases_funds | Normal path: collecting increases reserves |
| test_collect_zero_does_not_change_balance | Edge case: zero collection does nothing |

**TestBankPayOut**

| Test | Why it is needed |
|------|-----------------|
| test_pay_out_decreases_funds | Normal path: valid payout reduces reserves |
| test_pay_out_zero_returns_zero_and_no_change | Branch: amount <= 0 returns 0 |
| test_pay_out_negative_returns_zero | Branch: negative amount also returns 0 |
| test_pay_out_more_than_funds_raises_value_error | Branch: insufficient funds raises ValueError |
| test_pay_out_exact_funds_succeeds | Edge case: paying exactly the available balance should succeed |

**TestBankGiveLoan**

| Test | Why it is needed |
|------|-----------------|
| test_give_loan_credits_player | Normal path: loan increases player balance |
| test_give_loan_zero_does_nothing | Branch: zero amount is ignored |

---

### Test file: test_game.py

**TestBuyProperty**

| Test | Why it is needed |
|------|-----------------|
| test_buy_property_sufficient_funds_succeeds | Normal path: player with enough money buys property |
| test_buy_property_insufficient_funds_fails | Branch: balance less than price returns False |
| test_buy_property_exact_balance_equals_price | Bug exposure: balance exactly equal to price should succeed but does not |
| test_buy_property_zero_balance_fails | Edge case: zero balance cannot buy anything |

**TestFindWinner**

| Test | Why it is needed |
|------|-----------------|
| test_find_winner_returns_richest_player | Bug exposure: min() returns the poorest player instead of the richest |
| test_find_winner_empty_returns_none | Branch: no players returns None |
| test_find_winner_single_player_returns_that_player | Edge case: only one player always wins |
| test_find_winner_equal_balances | Edge case: all equal balances, any player is a valid result |

---

## Errors Found and Fixes

### Error 1: PropertyGroup.all_owned_by uses any() instead of all()

**File:** `property.py`

**Bug:** The method `all_owned_by` is supposed to return True only when every property in the group is owned by the given player. However, it uses `any()` which returns True as soon as even one property is owned by that player.

**Effect:** Players get doubled rent on a property the moment they own any one property in a group, even when the opponent owns the other properties in the same group. This breaks the core rent-doubling mechanic.

**Test that caught it:** `test_all_owned_returns_false_when_only_one_owned`

**Fix:** Change `any(p.owner == player for p in self.properties)` to `all(p.owner == player for p in self.properties)` in `property.py`.

**Commit:** `Error 1: Fixed any() to all() in PropertyGroup.all_owned_by in property.py`

---

### Error 2: Game.buy_property uses <= instead of <

**File:** `game.py`

**Bug:** The condition `if player.balance <= prop.price:` blocks the purchase when the player's balance is exactly equal to the property price. A player who has exactly the right amount of money should be able to afford the property.

**Effect:** A player with exactly $400 trying to buy a $400 property is told they cannot afford it and the purchase fails, even though they have the exact required funds.

**Test that caught it:** `test_buy_property_exact_balance_equals_price`

**Fix:** Change `if player.balance <= prop.price:` to `if player.balance < prop.price:` in `game.py`.

**Commit:** `Error 2: Fixed <= to < in buy_property in game.py`

---

### Error 3: Game.find_winner uses min() instead of max()

**File:** `game.py`

**Bug:** The method `find_winner` is supposed to return the player with the highest net worth. However, it uses `min()` which returns the player with the lowest net worth.

**Effect:** At the end of the game, the wrong player is declared the winner. The poorest remaining player wins instead of the richest.

**Test that caught it:** `test_find_winner_returns_richest_player`

**Fix:** Change `return min(self.players, key=lambda p: p.net_worth())` to `return max(self.players, key=lambda p: p.net_worth())` in `game.py`.

**Commit:** `Error 3: Fixed min() to max() in find_winner in game.py`

---

### Error 4: Dice.roll() uses randint(1, 5) instead of randint(1, 6)

**File:** `dice.py`

**Bug:** Both dice in `roll()` use `random.randint(1, 5)` which means neither die can ever show a 6. A standard six-sided die should produce values 1 through 6.

**Effect:** The maximum total roll is 10 (5+5) instead of 12 (6+6). All high-roll probabilities are distorted, making the game statistically incorrect.

**Test that caught it:** `test_roll_max_total_is_twelve`

**Fix:** Change both `random.randint(1, 5)` calls to `random.randint(1, 6)` in `dice.py`.

**Commit:** `Error 4: Fixed randint(1,5) to randint(1,6) in Dice.roll in dice.py`

---

### Error 5: Player.move() only awards GO salary when landing on Go, not when passing it

**File:** `player.py`

**Bug:** The `move()` method checks `if self.position == 0:` to decide whether to award the GO salary. This only triggers when the player lands exactly on position 0. If a player moves from position 38 by 5 steps, they land on position 3 (having passed Go), but receive no salary.

**Effect:** Players who pass Go without landing on it receive no salary. In standard Monopoly rules, passing Go always awards the salary regardless of whether the player lands on it exactly.

**Test that caught it:** `test_move_passing_go_collects_salary`

**Fix:** Track the old position before moving and check if the new position is less than the old position (which means the board wrapped around, i.e., passed Go). Change the salary logic in `move()` in `player.py`.

**Commit:** `Error 5: Fixed move() to award GO salary when passing Go, not only when landing on it`
