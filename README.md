# From "works on my machine" to a reliable, parallel-safe test pipeline

A Python test framework and CI pipeline for **Toolshop**, an open-source practice e-commerce app. The aim wasn't the number of tests but
whether they can be **trusted**: each test is isolated, every result is backed by data, and every failure is traced to its root cause.

**Key results**
- **23 test cases** (19 distinct tests; the concurrency test runs 5 times) covering API, concurrency and UI, run on every pull request against Toolshop built from a pinned commit in Docker Compose.
- **0 flaky tests in 1,380 test executions** (three 20-run baselines: sequential twice, parallel once).
- **2 product bugs found** ([#11](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/11), [#14](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/14), a race condition), plus several mismatches between the API and its Swagger docs.
- **A Linux-only CI failure traced to its root cause** (a uid mismatch between containers), fixed at the cause instead of with `chmod 777`.
- **Parallel execution proven safe** (0 failures in 460 parallel executions), then **kept out of CI on purpose**, based on measurements.

## The problem

Toolshop is a realistic web shop: an **Angular** UI, a **Laravel REST API** and a **MariaDB** database, run with Docker Compose. Testing it
automatically is easy to start and hard to trust:
- tests that share users or carts break each other, especially once they run in parallel;
- UI tests with fixed sleeps fail randomly;
- a pipeline that passes on one machine can fail on another;
- a known bug can hide new failures if it's silenced too broadly.

The goal: tests that give the **same answer every time**, locally and in CI, and that fail only when the product is wrong.

## What I built

- **Framework:** Python 3.12 + pytest, with a small `ApiClient` (requests) that never stores auth state. A token is passed per request, so one
  test's login can't leak into another.
- **Test data isolation:** every test that needs a user registers its own (unique `uuid4` email), and every cart test gets a new cart. Products
  are chosen by criteria from the API (in stock, not a rental), never hard-coded.
- **API tests:** products, registration/login/auth, and carts (create, add, add twice, remove, unknown cart).
- **Concurrency test:** 10 threads, each with its own HTTP session, released at the same moment by a `threading.Barrier`, add the same product to
  one cart.
- **UI tests:** Playwright (headless Chromium) with the app's `data-test` locators and no fixed sleeps. Setup goes through the API, and only the
  behaviour under test goes through the UI.
- **CI:** GitHub Actions starts Toolshop with Docker Compose at a pinned commit, seeds it, waits until API and UI really respond, and runs the
  suite. It uploads the JUnit report on every run, and container logs plus API diagnostics on failure.
- **Reliability tooling:** a manual workflow runs the suite N times (sequential or parallel), and a standard-library script turns the JUnit reports
  into per-test outcome counts, durations, flaky tests and known-bug xfails.

```
.github/
  actions/start-toolshop/      # composite action: checkout, start, seed, readiness checks
  actions/save-toolshop-logs/  # composite action: container logs + API diagnostics on failure
  workflows/tests.yml          # every PR and push to main
  workflows/reliability.yml    # manual: run the suite N times, summarise
docs/metrics/                  # baseline.md, parallel.md
scripts/junit_summary.py       # JUnit reports → reliability summary
tests/
  conftest.py                  # shared fixtures: api_client, registered_user, cart_id, product_id
  api/                         # products, users, carts, concurrency
  ui/                          # Playwright tests + UI base_url
toolshop/api_client.py         # stateless API client
```

## Key findings and decisions

**Race condition in the cart API, reported with a narrow xfail** ([#14](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/14), [PR #15](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/15))
Ten simultaneous "add 1" requests never lost quantity, but in 4 of 10 probe runs the cart held **two lines for the same product** (e.g. 9 + 1): a
check-then-insert race on the server. The test keeps status codes and the total quantity as normal assertions, and only calls `pytest.xfail("Bug #14 …")`
when duplicate lines appear. A known bug can't hide a new failure, and the test passes by itself once the bug is fixed.

**CI failed only on Linux: a uid mismatch between containers** ([PR #19](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/19))
The API returned HTTP 500 with an empty body in CI but worked on macOS. Added diagnostics showed that PHP-FPM runs as uid 1000, while the
composer container had given `storage/` to uid 82, so Laravel couldn't write logs or cache, not even the error itself. The fix gives `storage/` to the
right user after composer finishes and checks it with `test -w`. `chmod 777` was rejected because it hides the mismatch.

**Parallel execution: safe, but CI stays sequential** ([PR #25](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/25), [parallel.md](docs/metrics/parallel.md))
With pytest-xdist the suite ran 460 times in parallel without a single failure, which shows the tests really are independent. But the CI speedup (0.16 s)
was within the variation between two sequential baselines (0.18 s), and the concurrency test caught Bug #14 far less often (6% vs 27–39%). So CI stays
sequential, with parallel mode kept for measurements.

**Account lockout: why every test gets its own user** ([PR #9](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/9))
Toolshop locks an account after 3 failed logins (checked manually in Swagger), and tokens expire after 300 seconds. A shared test account would let one
wrong-password test lock out every other test, so each test registers a fresh user. An automated lockout test is still open ([#8](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/8)).

**Bugs and API/docs mismatches** ([#11](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/11), [#14](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/14), [PR #9](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/9), [PR #12](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/12))
- **Out-of-stock products can be added to a cart** (#11), and **concurrent adds create duplicate cart lines** (#14).
- **Duplicates and validation:** a duplicate email returns 422, while Swagger documents 409, and email format isn't validated on registration.
- **Inconsistent error bodies:** `{"error": …}` for a bad login, `{"message": …}` for a missing token, and three different 404 messages for an unknown cart.
- **Docs vs reality:** Swagger lists a 401 on cart deletes, but no auth is required.

## Results

**Reliability: 20 runs each, Toolshop `ae7caecb`** ([baseline.md](docs/metrics/baseline.md), [parallel.md](docs/metrics/parallel.md))

| | Baseline (`main`) | Sequential | Parallel (`-n 4`) |
|---|---|---|---|
| Test executions | 460 | 460 | 460 |
| Failures / errors / flaky | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Bug #14 caught (xfailed / 100) | 27 | 39 | 6 |
| Suite time per run, median | 3.37 s | 3.19 s | 3.03 s |
| Suite time per run, min–max | 3.25–7.33 s | 3.09–4.39 s | 2.76–7.21 s |

**Slowest tests:** the 4 UI tests, mean 0.30–0.91 s each in the sequential runs. In the baseline, every API test averages under 0.2 s.

**CI time is dominated by setup, not tests:** across the last 6 green Tests runs, "Start Toolshop" (build, start, seed, readiness) took
**166–262 s (2 min 46 s – 4 min 22 s)**, and "Run tests" took **5–9 s**. Speeding up CI means caching the environment, not parallelising the tests.

## How to run it

**Locally**: requires Python 3.12, pip 25.1 or newer, and Toolshop running ([practice-software-testing](https://github.com/testsmith-io/practice-software-testing), API on :8091, UI on :4200).
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install --group test
playwright install chromium        # once, for the UI tests
pytest -v -rxX                     # all tests; or: pytest tests/api, pytest tests/ui
pytest -n 4                        # optional: in parallel
```
Other environments: set `API_BASE_URL` and `UI_BASE_URL` (defaults `http://localhost:8091` and `http://localhost:4200`).

**In CI**
- **Tests** (`tests.yml`) runs automatically on every pull request and push to `main`.
- **Reliability baseline** (`reliability.yml`) is started by hand, from the Actions tab or with
  `gh workflow run reliability.yml -f runs=20 -f mode=sequential` (or `mode=parallel`). The summary appears on the run page, and all reports are
  uploaded as an artifact.
- Reports summarised locally: `python scripts/junit_summary.py reports/*.xml`.

## How I used Claude Code

Claude Code wrote the code from my prompts. My part was the engineering judgement: I set the design rules (no auth state on the shared client,
unique test data, no fixed sleeps, nothing I can't explain in an interview), reviewed every plan and change before committing, verified results
myself, and made the decisions. Commits and pushes are mine. Three examples:
- **Evidence before assertions** ([PR #15](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/15)): before writing the concurrency
  assertion, I required a throwaway probe and a stop if quantities were lost. The probe found duplicate lines instead, which became Bug #14. I then chose
  how to report it, narrowing the xfail so it can't hide other failures.
- **Root cause before fix** ([PR #19](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/19)): the first analysis of the
  Linux-only 500 was a hypothesis, not a proof. I had diagnostics added and checked in CI before any fix was written.
- **Data over the ticket** ([PR #25](https://github.com/ginatoriachambe/toolshop-python-test-automation/pull/25)): the ticket asked for parallel
  CI. After comparing three 20-run baselines, I decided to keep CI sequential and documented why.

## Possible improvements

- **Flaky-test quarantine:** detection already exists (`junit_summary.py`), and there have been 0 flaky tests so far. Quarantine only becomes useful once one appears.
- **Docker build caching:** setup takes minutes and tests take seconds, so this is the main lever on CI time.
- **Single source for the pinned Toolshop commit:** it's currently in both workflows ([#22](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/22)).
- **A lock file for transitive dependencies:** direct dependencies are pinned, transitive ones aren't.
- **Automated account-lockout test** ([#8](https://github.com/ginatoriachambe/toolshop-python-test-automation/issues/8)).
- **Page objects** once the UI tests grow beyond a few tests per page.
