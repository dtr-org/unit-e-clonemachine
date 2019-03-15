# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Regression tests for clonemachine, checks against known good substitutions
#
# Run it with `python3 -m unittest -v test_regressions.py`

import unittest

import tempfile
import os
import subprocess
from pathlib import Path

from runner import Runner

class TestRegressions(unittest.TestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.checkout_unit_e()
        self.runner.reset_unit_e("naming")
        self.runner.fetch_bitcoin()

    def test_naming(self):
        self.runner.run_clonemachine()
        self.runner.write_diff("naming")
        self.assertEqual(self.runner.compare_latest_diffs("naming"), "")

if __name__ == '__main__':
    unittest.main()
