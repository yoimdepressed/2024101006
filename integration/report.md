# Part 2: Integration Testing Report

## 1. Additional Modules Designed
As part of the system requirements, two additional modules were designed to extend the core functionality of the StreetRace Manager:
1. **Finance Module**: Manages the team's income and expenses. It records race prize money as income and handles any expenses. It ensures all financial transactions are logged and tracks the total balance.
2. **Leaderboard Module**: Tracks the total wins of drivers and ranks them accordingly. It updates automatically when race results are recorded and allows retrieving the top drivers or a specific driver's position.

## 2.1 Call Graph
*(Attach your hand-drawn Call Graph here)*

## 2.2 Integration Test Design

Below is the design of integration test cases validating how different modules interact with one another:

### Scenarios Tested in `test_integration_registration-race.py`
* **Test Case**: `test_registered_driver_can_enter_race`
  * **Modules Involved**: Registration, Crew Management, Race Management
  * **Expected Result**: A successfully registered driver can be added to a race.
  * **Actual Result**: Pass
  * **Why it is needed**: Verifies the core flow of registering a crew member, assigning a driver role, and successfully entering them in a race.

* **Test Case**: `test_unregistered_person_cannot_enter_race`, `test_mechanic_cannot_enter_race`, `test_strategist_cannot_enter_race`
  * **Modules Involved**: Registration, Crew Management, Race Management
  * **Expected Result**: System rejects unregistered users or non-drivers (mechanics/strategists) from entering races.
  * **Actual Result**: Pass
  * **Why it is needed**: Enforces the business rule that *only* registered members with the "driver" role can enter a race.

### Scenarios Tested in `test_integration_damaged.py`
* **Test Case**: `test_damaged_car_cannot_enter_race`, `test_repaired_car_can_enter_race`
  * **Modules Involved**: Inventory, Race Management
  * **Expected Result**: A race cannot start with a damaged car, but it can if the car is repaired.
  * **Actual Result**: Pass
  * **Why it is needed**: Verifies the interaction between car condition (Inventory) and race entry (Race Management).

* **Test Case**: `test_damaged_car_mission_blocked_no_free_mechanic`, `test_damaged_car_mission_allowed_mechanic_is_free`
  * **Modules Involved**: Inventory, Crew Management, Mission Planning
  * **Expected Result**: A damaged car triggers a repair mission only if a mechanic is available.
  * **Actual Result**: Pass
  * **Why it is needed**: Enforces the rule that missions requiring a mechanic must check for role availability.

### Scenarios Tested in `test_integration_results.py`
* **Test Cases**: `test_completing_race_updates_cash`, `test_completing_race_updates_driver_ranking`
  * **Modules Involved**: Results, Inventory, Crew Management
  * **Expected Result**: Completing a race appropriately updates the cash balance and increases the driver's win count.
  * **Actual Result**: Pass
  * **Why it is needed**: Ensures that race outcomes propagate correctly to financial tracking and driver statistics.

### Scenarios Tested in `test_integration_mission.py`
* **Test Cases**: `test_mission_requires_correct_role`, `test_mission_cannot_start_if_role_unavailable`, `test_unregistered_member_cannot_get_mission`
  * **Modules Involved**: Mission Planning, Crew Management
  * **Expected Result**: Missions are only assigned to registered crew members with the correct and available role.
  * **Actual Result**: Pass
  * **Why it is needed**: Validates role verification and availability checks before assigning tasks.

### Scenarios Tested in `test_integration_finance.py`
* **Test Cases**: `test_race_prize_logged_as_income`, `test_expense_reduces_inventory_cash`
  * **Modules Involved**: Finance, Results, Inventory
  * **Expected Result**: Race prizes increase cash and log as income, while expenses decrease cash and log correctly.
  * **Actual Result**: Pass
  * **Why it is needed**: Validates the end-to-end flow of money from racing rewards to inventory balance.

### Scenarios Tested in `test_integration_leaderboard.py`
* **Test Cases**: `test_leaderboard_updates_after_single_race`, `test_leaderboard_sorted_most_wins_first`
  * **Modules Involved**: Leaderboard, Results, Crew Management
  * **Expected Result**: The leaderboard accurately reflects and sorts driver rankings based on updated race results.
  * **Actual Result**: Pass
  * **Why it is needed**: Ensures the new Leaderboard extra module properly consumes result data to maintain a global ranking.

---
*Note: Any logical issues found during development, such as incorrectly tracking state across tests or incorrect role assignments, were actively resolved in code. All tests currently pass successfully.*
