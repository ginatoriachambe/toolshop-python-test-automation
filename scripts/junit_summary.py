"""Summarise several pytest JUnit XML reports: outcome counts and durations per test.

Usage: python scripts/junit_summary.py reports/run-*.xml > summary.md
"""

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from statistics import mean, median

# Most severe last: when one test has two <testcase> elements in a report
# (failure in the test body + error in teardown), the most severe one wins.
SEVERITY = ["passed", "skipped", "xfailed", "failed", "error"]


def outcome(testcase):
    for child in testcase:
        if child.tag == "failure":
            return "failed"
        if child.tag == "error":
            return "error"
        if child.tag == "skipped":
            return "xfailed" if child.get("type") == "pytest.xfail" else "skipped"
    return "passed"


def bug_id(testcase):
    for child in testcase:
        if child.get("type") == "pytest.xfail":
            match = re.search(r"Bug #\d+", child.get("message", ""))
            return match.group(0) if match else "no bug id"
    return None


def read_report(path):
    """Return {test_id: (outcome, seconds, bug)} for one report."""
    results = {}
    for testcase in ET.parse(path).getroot().iter("testcase"):
        test_id = f"{testcase.get('classname')}::{testcase.get('name')}"
        result = (outcome(testcase), float(testcase.get("time", 0)), bug_id(testcase))
        if test_id in results:
            old_outcome, old_time, old_bug = results[test_id]
            worst = max(old_outcome, result[0], key=SEVERITY.index)
            result = (worst, old_time + result[1], old_bug or result[2])
        results[test_id] = result
    return results


def suite_time(path):
    """Wall time of one pytest run, as pytest reports it (also correct with xdist workers)."""
    return sum(float(suite.get("time", 0)) for suite in ET.parse(path).getroot().iter("testsuite"))


def main(paths):
    if not paths:
        sys.exit("usage: junit_summary.py REPORT.xml [REPORT.xml ...]")

    counts = defaultdict(Counter)
    durations = defaultdict(list)
    bugs = defaultdict(set)
    for path in paths:
        for test_id, (result, seconds, bug) in read_report(path).items():
            counts[test_id][result] += 1
            durations[test_id].append(seconds)
            if bug:
                bugs[test_id].add(bug)

    def failures(test_id):
        return counts[test_id]["failed"] + counts[test_id]["error"]

    tests = sorted(counts)
    flaky = [t for t in tests if counts[t]["passed"] > 0 and failures(t) > 0]
    always_failing = [t for t in tests if failures(t) > 0 and counts[t]["passed"] == 0]
    known_bugs = [t for t in tests if counts[t]["xfailed"] > 0 and failures(t) == 0]

    print(f"## Reliability summary: {len(paths)} runs\n")
    print(f"{len(tests)} tests · {len(flaky)} flaky · {len(always_failing)} always failing"
          f" · {len(known_bugs)} with known-bug xfails\n")
    times = [suite_time(path) for path in paths]
    print(f"Suite time per run: median {median(times):.2f} s (min {min(times):.2f} s, max {max(times):.2f} s)\n")

    for title, group in [("Flaky (passed and failed across runs)", flaky),
                         ("Always failing", always_failing)]:
        print(f"### {title}\n")
        if not group:
            print("None.\n")
            continue
        print("| Test | Passed | Failed | Error |\n|---|---|---|---|")
        for t in group:
            print(f"| {t} | {counts[t]['passed']} | {counts[t]['failed']} | {counts[t]['error']} |")
        print()

    print("### Known bugs (xfail, not counted as flaky)\n")
    if not known_bugs:
        print("None.\n")
    else:
        print("| Test | Passed | Xfailed | Bug |\n|---|---|---|---|")
        for t in known_bugs:
            print(f"| {t} | {counts[t]['passed']} | {counts[t]['xfailed']} | {', '.join(sorted(bugs[t]))} |")
        print()

    print("### All tests\n")
    print("| Test | Runs | Passed | Failed | Error | Xfailed | Skipped | Mean (s) | Max (s) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for t in tests:
        c = counts[t]
        print(f"| {t} | {sum(c.values())} | {c['passed']} | {c['failed']} | {c['error']} | {c['xfailed']}"
              f" | {c['skipped']} | {mean(durations[t]):.3f} | {max(durations[t]):.3f} |")


if __name__ == "__main__":
    main(sys.argv[1:])
