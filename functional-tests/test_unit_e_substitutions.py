# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Regression tests for clonemachine, checks against known good substitutions
#
# Run it with `pytest -v test_unit_e_substitutions.py`

import pytest

from runner import Runner

@pytest.fixture
def runner():
    """Set up git checkout for test and return a runner to run operations
    on it.
    """
    runner = Runner("unit-e")
    runner.checkout_unit_e_clone()
    runner.fetch_bitcoin()
    return runner

def test_naming(runner):
    runner.apply_diff("old-naming")
    runner.run_clonemachine("--substitute-unit-e-naming")
    runner.commit("Ran clonemachine.py --substitute-unit-e-naming")
    runner.write_diff("naming")
    assert runner.compare_latest_diffs("naming") == ""
