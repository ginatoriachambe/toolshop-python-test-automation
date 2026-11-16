import pytest


def test_ci_failure_path():
    pytest.fail("Deliberate failure to verify the CI failure path")
