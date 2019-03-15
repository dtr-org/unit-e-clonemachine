# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Regression tests for clonemachine, checks against known good substitutions
#
# Run it with `python3 test_unit_e_substitutions.py -v`

import unittest

import tempfile
import os
import subprocess
from pathlib import Path

from runner import Runner

class TestUnitESubstitutions(unittest.TestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.checkout_unit_e()
        self.runner.fetch_bitcoin()

    def test_naming(self):
        self.runner.apply_diff("old-naming")
        self.runner.run_clonemachine("--substitute-unit-e-naming")
        self.runner.commit("Ran clonemachine.py --substitute-unit-e-naming")
        self.runner.write_diff("naming")
        self.assertEqual(self.runner.compare_latest_diffs("naming"), "")

if __name__ == '__main__':
    unittest.main()
