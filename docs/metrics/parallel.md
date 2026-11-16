# Parallel vs sequential: reliability baseline comparison

Two 20-run baselines from the same branch and commit, one sequential and one in parallel with pytest-xdist (4 workers). The earlier
sequential baseline from `main` ([baseline.md](baseline.md)) is shown as a reference.

| | Reference: `main` | Sequential | Parallel |
|---|---|---|---|
| Workflow run | [43957364623](https://github.com/ginatoriachambe/toolshop-python-test-automation/actions/runs/43957364623) | [43975219975](https://github.com/ginatoriachambe/toolshop-python-test-automation/actions/runs/43975219975) | [43975302465](https://github.com/ginatoriachambe/toolshop-python-test-automation/actions/runs/43975302465) |
| Test repo commit | `57470f4` (`main`) | `69083c3` (`feat/24-parallel-execution`) | `69083c3` (`feat/24-parallel-execution`) |
| Toolshop commit | `ae7caecb` | `ae7caecb` | `ae7caecb` |
| Mode | sequential | sequential (`-n 0`) | parallel (`-n 4`) |
| Date | 2026-11-16 | 2026-11-16 | 2026-11-16 |

## Results

| | Reference: `main` | Sequential | Parallel |
|---|---|---|---|
| Runs / test executions | 20 / 460 | 20 / 460 | 20 / 460 |
| Failures / errors | 0 / 0 | 0 / 0 | 0 / 0 |
| Flaky tests | 0 | 0 | 0 |
| Always failing | 0 | 0 | 0 |
| Bug #14 xfailed / concurrency executions | 27 / 100 (27%) | 39 / 100 (39%) | 6 / 100 (6%) |
| Bug #14 xfails per run | 0–3 | 1–4 | 0–2 |
| Suite time per run, median | 3.37 s | 3.19 s | 3.03 s |
| Suite time per run, min–max | 3.25–7.33 s | 3.09–4.39 s | 2.76–7.21 s |
| Run 1 | 7.33 s | 4.12 s | 7.21 s |
| Runs 2–20, median (range) | 3.36 s (3.25–3.48) | 3.18 s (3.09–4.39) | 3.02 s (2.76–3.24) |
| Total pytest time, 20 runs | 71.0 s | 67.4 s | 64.7 s |

Suite time is pytest's own `testsuite@time` (the wall time of the run, also with xdist workers).

Mean duration per test of the slowest tests (the 4 UI tests; durations include fixture setup):

| Test | Reference: `main` | Sequential | Parallel |
|---|---|---|---|
| `tests.ui.test_cart::test_add_to_cart_updates_cart_indicator[chromium]` | 0.906 s | 0.748 s | 1.706 s |
| `tests.ui.test_login::test_registered_user_can_log_in[chromium]` | 0.664 s | 0.667 s | 1.723 s |
| `tests.ui.test_home::test_search_shows_only_matching_products[chromium]` | 0.410 s | 0.378 s | 1.418 s |
| `tests.ui.test_home::test_home_page_shows_products[chromium]` | 0.325 s | 0.304 s | 1.413 s |

## Interpretation

- **Parallel execution is correct:** 0 failures, 0 errors and 0 flaky tests in 460 parallel executions. No test broke from shared state or
  ordering, so the isolation choices hold (a unique `uuid4` user per test, a new cart per test, a stateless shared client). The same limit as in
  [baseline.md](baseline.md) applies: 20 runs per test can only rule out flakiness that happens often.
- **No meaningful speedup in CI.** The parallel median (3.03 s) is 0.16 s below the sequential one from the same branch (3.19 s), but the two
  sequential baselines already differ by 0.18 s from each other (3.37 s vs 3.19 s). So the gain is within the run-to-run variation. Per-test
  durations are much higher in parallel (UI tests 1.41–1.72 s mean vs 0.30–0.91 s): tests now share the runner's CPUs and Toolshop's PHP-FPM pool,
  and, likely, each worker that gets a UI test starts its own Chromium (not visible in the reports). For parallel runs, only the suite's wall time
  is a meaningful speed measure. Run 1 is slow in both the parallel run (7.21 s) and the `main` reference (7.33 s), but not in the sequential run
  from this branch (4.12 s).
- **Bug #14 shows up much less often in parallel:** 6/100, vs 39/100 sequentially on the same branch. Two sequential baselines under the same
  conditions already gave 27% and 39%, so the rate is noisy at 100 executions. Still, 6% is below both. That's consistent with the expected effect
  (the 10 concurrent adds now compete for PHP-FPM workers with other tests' requests, and the 5 concurrency runs can overlap each other), but the reports
  can't show the mechanism. In practice, **sequential runs are the better way to reproduce Bug #14**. A drop in parallel mode doesn't mean the
  bug got better.
- **CI duration is unchanged in practice:** all 20 runs together took 64.7 s of pytest time in parallel vs 67.4 s sequentially.

## Decision

The Tests workflow stays **sequential**. Parallel execution showed no meaningful speedup, and it made the concurrency test catch Bug #14
less often (6% vs 27–39% sequentially). pytest-xdist and the `parallel` mode of the Reliability baseline workflow stay available.
Revisit when the suite is large enough for speed to matter, and then run the concurrency tests separately and sequentially.
