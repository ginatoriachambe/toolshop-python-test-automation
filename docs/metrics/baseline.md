# Test suite reliability baseline

| | |
|---|---|
| Date | 2026-11-16 |
| Runs (N) | 20 |
| Toolshop commit | [`ae7caecb811dd8952c09d997e69be7cb946ecd44`](https://github.com/testsmith-io/practice-software-testing/commit/ae7caecb811dd8952c09d997e69be7cb946ecd44) |
| Test repo commit | `57470f47d5cce32858cd786f42554aa6ee128f4b` (`main`) |
| Workflow run | [Reliability baseline #43957364623](https://github.com/ginatoriachambe/toolshop-python-test-automation/actions/runs/43957364623) |
| How | `reliability.yml`: Toolshop started once, then `pytest tests` run 20 times in a row on one `ubuntu-24.04` runner; summary by `scripts/junit_summary.py` |

## Interpretation

- **0 flaky tests across 20 runs = 460 test executions**, with 0 failures and 0 errors. This shows the suite is stable *in this setup*: one runner,
  one Toolshop instance, runs one after another. It doesn't prove the suite can't flake. Each test ran only 20 times, so a rare flake could
  simply not have shown up, and conditions not covered here (parallel runs, a slower or loaded environment) weren't tested.
- **Bug #14 reproduces in 27% of concurrency executions** (27 xfailed / 100). Each of the 5 parametrized runs xfailed 4–8 times out of 20, and
  every full suite run had 0–3 of them. These are the test catching the real race in the API, not flakiness, which is why they're reported
  separately and don't count as failures.
- **Slowest tests are the UI tests** (mean 0.906 s cart, 0.664 s login, 0.410 s search, 0.325 s home), followed by the API user tests (~0.17–0.18 s,
  which register a user through the API in their fixtures; durations include fixture setup). The cart test's max of 4.332 s comes from run 1 only, where it
  was the first UI test. In runs 2–20 its max is 0.781 s. The reports don't show the cause of that one-off.
- **One full suite run takes about 3.4 s** (pytest-reported: median 3.37 s, range 3.25–3.48 s in runs 2–20; run 1 took 7.33 s). All 20 runs together
  took 71 s of pytest time.
- **CI time is dominated by environment setup, not by the tests.** In the Tests workflow, "Start Toolshop" takes ~2.5 min versus ~5 s for the tests,
  so speeding up CI means speeding up the setup (e.g. image caching), not the suite.

## Summary (output of `scripts/junit_summary.py`, unchanged)

23 tests · 0 flaky · 0 always failing · 5 with known-bug xfails

### Flaky (passed and failed across runs)

None.

### Always failing

None.

### Known bugs (xfail, not counted as flaky)

| Test | Passed | Xfailed | Bug |
|---|---|---|---|
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[0] | 12 | 8 | Bug #14 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[1] | 16 | 4 | Bug #14 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[2] | 15 | 5 | Bug #14 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[3] | 14 | 6 | Bug #14 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[4] | 16 | 4 | Bug #14 |

### All tests

| Test | Runs | Passed | Failed | Error | Xfailed | Skipped | Mean (s) | Max (s) |
|---|---|---|---|---|---|---|---|---|
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[0] | 20 | 12 | 0 | 0 | 8 | 0 | 0.084 | 0.126 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[1] | 20 | 16 | 0 | 0 | 4 | 0 | 0.075 | 0.084 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[2] | 20 | 15 | 0 | 0 | 5 | 0 | 0.074 | 0.085 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[3] | 20 | 14 | 0 | 0 | 6 | 0 | 0.073 | 0.079 |
| tests.api.test_cart_concurrency::test_parallel_adds_to_same_cart_keep_every_quantity[4] | 20 | 16 | 0 | 0 | 4 | 0 | 0.072 | 0.075 |
| tests.api.test_carts::test_add_product_shows_it_in_cart_with_quantity | 20 | 20 | 0 | 0 | 0 | 0 | 0.033 | 0.034 |
| tests.api.test_carts::test_adding_same_product_twice_increases_quantity | 20 | 20 | 0 | 0 | 0 | 0 | 0.042 | 0.045 |
| tests.api.test_carts::test_create_cart_returns_cart_id | 20 | 20 | 0 | 0 | 0 | 0 | 0.007 | 0.008 |
| tests.api.test_carts::test_get_unknown_cart_returns_404 | 20 | 20 | 0 | 0 | 0 | 0 | 0.007 | 0.007 |
| tests.api.test_carts::test_removing_product_removes_it_from_cart | 20 | 20 | 0 | 0 | 0 | 0 | 0.039 | 0.041 |
| tests.api.test_products::test_get_product_by_id_returns_that_product | 20 | 20 | 0 | 0 | 0 | 0 | 0.015 | 0.019 |
| tests.api.test_products::test_get_product_with_unknown_id_returns_404 | 20 | 20 | 0 | 0 | 0 | 0 | 0.007 | 0.007 |
| tests.api.test_products::test_get_products_returns_paginated_list | 20 | 20 | 0 | 0 | 0 | 0 | 0.008 | 0.009 |
| tests.api.test_products::test_search_returns_only_matching_products | 20 | 20 | 0 | 0 | 0 | 0 | 0.016 | 0.019 |
| tests.api.test_users::test_get_current_user_with_token_returns_that_user | 20 | 20 | 0 | 0 | 0 | 0 | 0.179 | 0.194 |
| tests.api.test_users::test_get_current_user_without_token_is_rejected | 20 | 20 | 0 | 0 | 0 | 0 | 0.007 | 0.008 |
| tests.api.test_users::test_login_with_valid_credentials_returns_token | 20 | 20 | 0 | 0 | 0 | 0 | 0.170 | 0.190 |
| tests.api.test_users::test_login_with_wrong_password_is_rejected | 20 | 20 | 0 | 0 | 0 | 0 | 0.169 | 0.181 |
| tests.api.test_users::test_register_returns_created_user | 20 | 20 | 0 | 0 | 0 | 0 | 0.120 | 0.232 |
| tests.ui.test_cart::test_add_to_cart_updates_cart_indicator[chromium] | 20 | 20 | 0 | 0 | 0 | 0 | 0.906 | 4.332 |
| tests.ui.test_home::test_home_page_shows_products[chromium] | 20 | 20 | 0 | 0 | 0 | 0 | 0.325 | 0.373 |
| tests.ui.test_home::test_search_shows_only_matching_products[chromium] | 20 | 20 | 0 | 0 | 0 | 0 | 0.410 | 0.443 |
| tests.ui.test_login::test_registered_user_can_log_in[chromium] | 20 | 20 | 0 | 0 | 0 | 0 | 0.664 | 0.710 |
