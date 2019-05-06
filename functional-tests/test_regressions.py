# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.

# Regression tests for clonemachine, checks against known good substitutions
#
# Run it with `pytest -v test_regressions.py`

import pytest

from runner import Runner

@pytest.fixture
def runner():
    """Set up git checkout for test and return a runner to run operations
    on it.
    """
    runner = Runner("unit-e")
    runner.checkout_unit_e_clone(label="urls")
    return runner

def test_latest(runner):
    runner.fetch_bitcoin()
    runner.run_clonemachine()
    runner.write_diff("latest")
    assert runner.compare_latest_diffs("latest") == ""

def test_bitcoin_0_18(runner):
    runner.fetch_bitcoin(branch="0.18")
    runner.run_clonemachine()
    runner.write_diff("0.18")
    assert runner.compare_latest_diffs("0.18") == ""
