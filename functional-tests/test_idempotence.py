# Copyright (c) 2018 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Functional test for clonemachine
#
# Run it with `python3 -m unittest -v test_idempotence.py`

import unittest

import tempfile
import os
import subprocess
from pathlib import Path

class TestIdempotence(unittest.TestCase):
    def run_git(self, arguments, cwd):
        result = subprocess.run(["git"] + arguments, cwd = cwd, capture_output=True)
        return result.stdout.rstrip().decode("utf-8")

    def setUp(self):
        self.bitcoin_git_dir = os.path.dirname(__file__) / Path("tmp/bitcoin")

        self.bitcoin_branch = "0.17"
        self.bitcoin_git_revision = "9e87d82e7f0696a40d08c6e4cff3f040a447ece5"

        if not os.path.exists(self.bitcoin_git_dir):
            subprocess.run(["git", "clone", "--depth", "1", "--branch",
                    self.bitcoin_branch, "https://github.com/bitcoin/bitcoin",
                    self.bitcoin_git_dir])
        self.run_git(["checkout", self.bitcoin_git_revision], self.bitcoin_git_dir)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.bitcoin_git_dir)
        if git_revision != self.bitcoin_git_revision:
            raise RuntimeError("Expected git revision '{}', got '{}'".format(
                    self.bitcoin_git_revision, git_revision))

    def test_run_clonemachine_twice(self):
        clonemachine = (Path(os.path.dirname(__file__)) / "../fork.py").resolve()
        subprocess.run([clonemachine], cwd = self.bitcoin_git_dir, capture_output=True)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.bitcoin_git_dir)
        # Check that some substitution was done and new commits where added
        self.assertNotEqual(git_revision, self.bitcoin_git_revision)
        subprocess.run([clonemachine], cwd = self.bitcoin_git_dir, capture_output=True)
        new_git_revision = self.run_git(["rev-parse", "HEAD"], self.bitcoin_git_dir)
        # Check that no new commits where added
        self.assertEqual(git_revision, new_git_revision)

if __name__ == '__main__':
    unittest.main()
