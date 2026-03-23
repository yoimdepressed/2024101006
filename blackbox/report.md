# Part 3: Black Box API Testing Report — QuickCart REST API

---

## Test Case Design

All test cases below are based on the [QuickCart API documentation](../QuickCart%20System.md). Tests are implemented using `pytest` and `requests`, located in `blackbox/tests/`. Each test validates correct HTTP status codes, proper JSON response structures, and correctness of returned data.

---

### 1. Authentication & Header Validation (`test_auth.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_missing_roll_number` | GET /profile without X-Roll-Number | 401 Unauthorized | Doc states missing roll number returns 401 |
| `test_invalid_roll_number` | X-Roll-Number: "abc" | 400 Bad Request | Doc states non-integer roll number returns 400 |
| `test_missing_user_id` | GET /profile without X-User-ID | 400 Bad Request | User-scoped endpoints require X-User-ID |
| `test_invalid_user_id` | X-User-ID: "abc" | 400 Bad Request | Invalid (non-integer) user ID must fail |
| `test_symbol_roll_number` | X-Roll-Number: "12@34" | 400 Bad Request | Symbols in roll number are not valid integers |
| `test_nonexistent_user_id` | X-User-ID: "999999" | 400 Bad Request | Non-existent user ID must be rejected |

---

### 2. Admin / Data Inspection Endpoints (`test_admin.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_admin_get_all_users` | GET /admin/users | 200 OK | Verifies admin can see all users |
| `test_admin_get_specific_user` | GET /admin/users/1 | 200 OK | Verifies fetching a known user works |
| `test_admin_get_nonexistent_user` | GET /admin/users/999999 | 404 Not Found | Non-existent user must return 404 |
| `test_admin_get_all_carts` | GET /admin/carts | 200 OK | Returns all carts across users |
| `test_admin_get_all_orders` | GET /admin/orders | 200 OK | Returns all orders across users |
| `test_admin_get_all_products` | GET /admin/products | 200 OK | Returns ALL products including inactive |
| `test_admin_get_all_coupons` | GET /admin/coupons | 200 OK | Returns all coupons including expired |
| `test_admin_get_all_tickets` | GET /admin/tickets | 200 OK | Returns all support tickets |
| `test_admin_get_all_addresses` | GET /admin/addresses | 200 OK | Returns all addresses across users |

---

### 3. Profile (`test_profile.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_get_profile` | GET /profile | 200 OK with name, phone | Basic valid retrieval |
| `test_update_profile_valid` | PUT name="Test User", phone="1234567890" | 200 OK | Normal valid update |
| `test_update_profile_boundary_valid` | name=2 chars, name=50 chars | 200 OK | Boundary min/max for name length |
| `test_update_profile_invalid_name_length` | name=1 char, name=51 chars | 400 Bad Request | Below/above allowed name range |
| `test_update_profile_invalid_phone_format` | phone=9 digits, 11 digits, "123abc4567" | 400 Bad Request | Phone must be exactly 10 digits |
| `test_update_profile_wrong_type` | name=12345 (int instead of string) | 400 Bad Request | Wrong data type validation |

---

### 4. Addresses (`test_addresses.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_add_address_valid_labels` | label=HOME/OFFICE/OTHER, valid street/city/pincode | 200 OK with full address object | All three valid labels accepted |
| `test_add_address_invalid_label` | label="INVALID" | 400 Bad Request | Only HOME/OFFICE/OTHER allowed |
| `test_add_address_invalid_street_length` | street=4 chars, street=101 chars | 400 Bad Request | Street must be 5-100 chars |
| `test_add_address_invalid_pincode` | pincode=5 digits, 7 digits, "abcdef" | 400 Bad Request | Pincode must be exactly 6 digits |
| `test_add_address_invalid_city_length` | city=1 char, city=51 chars | 400 Bad Request | City must be 2-50 chars |
| `test_default_address_logic` | Add two addresses, set second as default | First.is_default=False, Second=True | Only one default at a time |
| `test_update_address_street` | PUT new street on existing address | 200 OK, response shows new street | Update must return new data |
| `test_update_address_ignored_fields` | PUT label/city/pincode changes | Original values unchanged | Only street and is_default can change |
| `test_delete_non_existent_address` | DELETE /addresses/99999 | 404 Not Found | Non-existent address returns 404 |
| `test_add_address_response_includes_all_fields` | POST valid address | Response has address_id, label, street, city, pincode, is_default | Validates complete JSON structure |
| `test_delete_existing_address` | DELETE a real address | 200/204 | Verifies successful deletion |

---

### 5. Products (`test_products.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_get_products_active_only` | GET /products | All products have is_active=True | Inactive products must be hidden |
| `test_get_single_product_valid` | GET /products/250 | 200 OK with product_id, price, category, etc. | Basic valid retrieval |
| `test_get_single_product_not_found` | GET /products/999999 | 404 Not Found | Non-existent product returns 404 |
| `test_products_filter_category` | GET /products?category=Fruits | All results have category="Fruits" | Category filter works correctly |
| `test_products_search_name` | GET /products?search=Apple | 200 OK | Name search returns results |
| `test_products_sort_price` | GET /products?sort=price_asc, price_desc | Prices sorted correctly | Sort functionality works both ways |
| `test_products_price_matches_admin` | Compare user GET prices to admin GET prices | Prices must match exactly | Price must be the real DB price |

---

### 6. Cart (`test_cart.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_cart_add_valid` | product_id=250, qty=2 | 200 OK | Normal add-to-cart |
| `test_cart_add_invalid_quantity_zero` | qty=0 | 400 Bad Request | Quantity must be at least 1 |
| `test_cart_add_invalid_quantity_negative` | qty=-1 | 400 Bad Request | Negative quantities are invalid |
| `test_cart_add_wrong_data_type` | qty="two" | 400 Bad Request | Wrong data type for quantity |
| `test_cart_add_missing_product_id` | No product_id in body | 400 Bad Request | Missing required field |
| `test_cart_add_stock_exceeded` | qty=9999 | 400 Bad Request | Cannot exceed stock |
| `test_cart_add_non_existent` | product_id=99999 | 404 Not Found | Non-existent product |
| `test_cart_duplicate_add_accumulates` | Add qty=1, then qty=2 for same product | Total qty=3 | Quantities accumulate, not replace |
| `test_cart_update_quantity` | Update to qty=5, then try qty=0 | 200 then 400 | Valid update works, zero rejected |
| `test_cart_remove` | Remove existing, then non-existent | 200 then 404 | Remove works, non-existent returns 404 |
| `test_cart_totals_calculation` | Add 2 products, check total | total = sum of subtotals | Validates total calculation correctness |
| `test_cart_clear` | Add item then clear | Cart has 0 items | Clear empties the cart |
| `test_cart_item_subtotal_per_item` | Add qty=3 | subtotal = qty * unit_price | Per-item subtotal verification |

---

### 7. Coupons (`test_coupons.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_coupon_apply_valid` | Active coupon with low min_cart_value | 200 OK | Valid coupon should be accepted |
| `test_coupon_expired` | Expired/non-existent coupon code | 400/404 | Expired coupons rejected |
| `test_coupon_minimum_cart_value` | Coupon with min > cart total | 400 Bad Request | Cart must meet minimum value |
| `test_coupon_discount_calculation` | Apply PERCENT coupon, check discount amount | discount = (subtotal×pct/100), capped at max | Discount calculated correctly |
| `test_coupon_remove` | Remove applied coupon | 200 OK | Coupon removal works |

---

### 8. Checkout (`test_checkout.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_checkout_empty_cart` | Checkout with empty cart | 400 Bad Request | Cannot checkout empty cart |
| `test_checkout_invalid_method` | payment_method="CASH" | 400 Bad Request | Only COD/WALLET/CARD allowed |
| `test_checkout_missing_payment_method` | Empty JSON body | 400 Bad Request | Missing required field |
| `test_checkout_cod_limit` | COD with total > 5000 | 400 Bad Request | COD not allowed > 5000 |
| `test_checkout_valid_cod` | COD with low total | 200 OK, payment_status=PENDING | COD starts as PENDING |
| `test_checkout_valid_wallet` | WALLET payment | 200 OK, payment_status=PENDING | WALLET starts as PENDING |
| `test_checkout_valid_card` | CARD payment | 200 OK, payment_status=PAID | CARD starts as PAID |
| `test_checkout_gst_and_stock_reduction` | CARD checkout, verify GST and stock | GST = 5% of subtotal, stock reduces by 1 | Validates GST calculation and stock management |

---

### 9. Wallet (`test_wallet.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_wallet_get` | GET /wallet | 200 OK with wallet_balance | Basic retrieval |
| `test_wallet_add_boundary_100000` | amount=100000 | 200 OK | Boundary max: exactly 100000 accepted |
| `test_wallet_add_valid_and_verify` | Add 50, check balance increases by 50 | after = before + 50 | Verifies exact addition |
| `test_wallet_add_invalid_amount` | amount=100001, amount=0 | 400 Bad Request | Over limit and zero rejected |
| `test_wallet_add_wrong_type` | amount="hundred" | 400 Bad Request | Wrong data type |
| `test_wallet_add_negative_amount` | amount=-50 | 400 Bad Request | Negative amounts rejected |
| `test_wallet_pay_exact_deduction` | Pay 100, check balance decreases by exactly 100 | after = before - 100 | No extra amount should be deducted |
| `test_wallet_pay_insufficient` | Pay amount > balance | 400 Bad Request | Insufficient funds rejected |
| `test_wallet_pay_invalid_amount` | amount=0, amount=-100 | 400 Bad Request | Zero and negative pay rejected |

---

### 10. Loyalty Points & Orders (`test_loyalty_orders.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_loyalty_get` | GET /loyalty | 200 OK with loyalty_points | Basic retrieval |
| `test_loyalty_redeem` | Redeem 0, -1, valid, over-balance | 400/200/400 accordingly | Validates all redeem edge cases |
| `test_orders_get_all` | GET /orders | 200 OK | Basic order listing |
| `test_orders_get_single_and_non_existent` | GET existing order, GET /orders/99999 | 200, then 404 | Valid retrieval and 404 for missing |
| `test_orders_invoice` | GET /orders/{id}/invoice | Has subtotal, gst_amount, total | Invoice structure validation |
| `test_orders_cancel_restores_stock` | Cancel order, check product stock | Stock restored to pre-order level | Cancellation must restore inventory |
| `test_orders_cancel_non_existent` | POST /orders/99999/cancel | 404 Not Found | Non-existent order can't be cancelled |
| `test_orders_cancel_delivered` | Cancel DELIVERED order | 400 Bad Request | Delivered orders cannot be cancelled |

---

### 11. Reviews & Support Tickets (`test_reviews_tickets.py`)

| Test | Input | Expected Output | Justification |
|------|-------|-----------------|---------------|
| `test_review_get_and_average` | POST rating=3 and rating=4, check average | average_rating is float (3.5) | Average must be decimal, not integer-divided |
| `test_review_valid_and_boundaries` | rating=1, rating=5 | 200 OK | Boundary min/max for rating |
| `test_review_invalid_rating` | rating=0, rating=6 | 400 Bad Request | Outside 1-5 range rejected |
| `test_review_comment_boundaries` | comment="" (empty), comment=201 chars | 400 Bad Request | Comment must be 1-200 chars |
| `test_review_wrong_data_type` | rating="five" | 400 Bad Request | Wrong data type validation |
| `test_review_missing_fields` | Missing comment, missing rating | 400 Bad Request | Required fields must be present |
| `test_support_ticket_get_all` | GET /support/tickets | 200 OK | Basic retrieval |
| `test_support_ticket_missing_fields` | Missing message, missing subject | 400 Bad Request | Required fields must be present |
| `test_support_ticket_create_valid` | subject=valid, message=valid | 200 OK, status=OPEN | New ticket starts OPEN |
| `test_support_ticket_create_boundaries` | subject=4 chars, 101 chars, message=501 chars | 400 Bad Request | Subject 5-100, message 1-500 |
| `test_support_ticket_valid_transitions` | OPEN→IN_PROGRESS→CLOSED | 200 OK each step | Valid forward transitions |
| `test_support_ticket_closed_to_open_invalid` | CLOSED→OPEN | 400 Bad Request | Reverse transitions not allowed |
| `test_support_ticket_invalid_transition` | OPEN→CLOSED (skip IN_PROGRESS) | 400 Bad Request | Must go through IN_PROGRESS |
| `test_support_ticket_message_saved_exactly` | POST with specific message text | Message in response matches exactly | Doc says "full message must be saved exactly" |

---

## Bug Reports

### Bug 1: Address Update Returns Old Data
**Endpoint Tested:** `PUT /api/v1/addresses/{address_id}`
**Request payload:**
- **Method:** PUT
- **URL:** `http://localhost:8080/api/v1/addresses/<address_id>`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"street": "New Street Name"}`
**Expected result:** The API should return the address with the new updated data (`"street": "New Street Name"`).
**Actual result observed:** The API returned the old address data (`"street": "Valid St"`), completely ignoring the rule to return updated data.

### Bug 2: Cart Allows Zero Quantity
**Endpoint Tested:** `POST /api/v1/cart/add`
**Request payload:**
- **Method:** POST
- **URL:** `http://localhost:8080/api/v1/cart/add`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"product_id": 250, "quantity": 0}`
**Expected result:** The API should return `400 Bad Request` because quantity must be at least 1.
**Actual result observed:** The API returned `200 OK` and added an invalid quantity to the cart.

### Bug 3: Cart Total and Subtotal Calculation is Incorrect
**Endpoint Tested:** `GET /api/v1/cart`
**Request payload:**
- **Method:** GET
- **URL:** `http://localhost:8080/api/v1/cart`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
**Expected result:** Adding 5 × "Apple - Red" (price 120 each) should give subtotal=600 and total=600.
**Actual result observed:** The API returned `"subtotal": 88` and `"total": 0`. The subtotal is wildly incorrect (should be 600, got 88), and the cart total is always 0. Similarly, adding 2 × Apple Red gives subtotal=-16. This is a fundamental calculation logic error.

### Bug 4: Checkout allows empty cart
**Endpoint Tested:** `POST /api/v1/checkout`
**Request payload:**
- **Method:** POST
- **URL:** `http://localhost:8080/api/v1/checkout`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"payment_method": "COD"}`
**Expected result:** The API should return `400 Bad Request` because the cart is empty.
**Actual result observed:** The API returned `200 OK` and processed a checkout for 0 items.

### Bug 5: Support Ticket allows jumping statuses
**Endpoint Tested:** `PUT /api/v1/support/tickets/{ticket_id}`
**Request payload:**
- **Method:** PUT
- **URL:** `http://localhost:8080/api/v1/support/tickets/<ticket_id>`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"status": "CLOSED"}`
**Expected result:** The API should return `400 Bad Request` because a ticket must go OPEN → IN_PROGRESS → CLOSED.
**Actual result observed:** The API returned `200 OK` and allowed an OPEN ticket to immediately become CLOSED.

### Bug 6: Addresses allow non-digit pincodes
**Endpoint Tested:** `POST /api/v1/addresses`
**Request payload:**
- **Method:** POST
- **URL:** `http://localhost:8080/api/v1/addresses`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"label": "HOME", "street": "Valid St", "city": "City", "pincode": "abcdef"}`
**Expected result:** The API should return `400 Bad Request` when pincode is "abcdef".
**Actual result observed:** The API returned `200 OK` and saved the invalid pincode.

### Bug 7: Profile allows non-digit phone numbers
**Endpoint Tested:** `PUT /api/v1/profile`
**Request payload:**
- **Method:** PUT
- **URL:** `http://localhost:8080/api/v1/profile`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"name": "Test User", "phone": "123abc4567"}`
**Expected result:** The API should return `400 Bad Request` when phone is "123abc4567".
**Actual result observed:** The API returned `200 OK` and saved the invalid phone string.

### Bug 8: Review average rating is integer-divided
**Endpoint Tested:** `GET /api/v1/products/{product_id}/reviews`
**Request payload:**
- **Method:** GET
- **URL:** `http://localhost:8080/api/v1/products/250/reviews`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
**Expected result:** The API should return a proper decimal average (e.g. 3.5 for 3 and 4).
**Actual result observed:** The API rounded down to `3` (integer division).

### Bug 9: Support Ticket allows reopening closed tickets
**Endpoint Tested:** `PUT /api/v1/support/tickets/{ticket_id}`
**Request payload:**
- **Method:** PUT
- **URL:** `http://localhost:8080/api/v1/support/tickets/<ticket_id>`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"status": "OPEN"}`
**Expected result:** The API should return `400 Bad Request` when trying to change a CLOSED ticket back to OPEN.
**Actual result observed:** The API returned `200 OK` and allowed the transition.

### Bug 10: Wallet pay deducts extra hidden amount
**Endpoint Tested:** `POST /api/v1/wallet/pay`
**Request payload:**
- **Method:** POST
- **URL:** `http://localhost:8080/api/v1/wallet/pay`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"amount": 50}`
**Expected result:** The API should deduct exactly 50. Balance was 584.79, should become 534.79.
**Actual result observed:** The API deducted 50.80 instead of 50—balance became 533.99 instead of 534.79. The doc states "no extra amount is taken" but 0.80 extra was subtracted.

### Bug 11: Standard product API returns wrong price
**Endpoint Tested:** `GET /api/v1/products/{product_id}`
**Request payload:**
- **Method:** GET
- **URL:** `http://localhost:8080/api/v1/products/250`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
**Expected result:** The API should return the exact real price stored in the database. Admin endpoint shows product 250 price as **284.61**.
**Actual result observed:** The user-facing endpoint returned `"price": 280` instead of `284.61`. The doc states "the price shown for every product must be the exact real price stored in the database."

### Bug 12: Coupon Discount Calculated as Zero
**Endpoint Tested:** `POST /api/v1/coupon/apply` + `GET /api/v1/cart`
**Request payload:**
- **Method:** POST then GET
- **URL:** `http://localhost:8080/api/v1/coupon/apply`
- **Headers:** `{"X-Roll-Number": "2024101006", "X-User-ID": "1"}`
- **Body:** `{"coupon_code": "WELCOME50"}`
**Expected result:** After applying the WELCOME50 coupon (FIXED, discount_value=50, min_cart_value=100), `GET /api/v1/cart` should show a discount of 50 and reduce the total accordingly.
**Actual result observed:** The coupon was applied (200 OK), but `GET /api/v1/cart` showed `"total": 0` with no discount field, because the cart total calculation is fundamentally broken (see Bug 3). The coupon system likely uses the broken total for its computation.
