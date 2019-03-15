# Copyright (c) 2018-2019 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Functional test for clonemachine
#
# Run it with `python3 -m unittest -v test_appropriation.py`

import unittest

import tempfile
import os
import subprocess
from pathlib import Path

class TestAppropriation(unittest.TestCase):
    def run_git(self, arguments, cwd):
        result = subprocess.run(["git"] + arguments, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.rstrip().decode("utf-8")
        return output

    def setUp(self):
        self.clonemachine = (Path(os.path.dirname(__file__)) / "../clonemachine.py").resolve()
        self.bitcoin_branch = "0.17"
        self.bitcoin_git_revision = "1e49fe450dbb0c258776526dba3ee583461d42ff"
        self.unite_git_dir = os.path.dirname(__file__) / Path("tmp/unit-e")
        self.unite_git_revision = "236db46ced3b2fd5573a2edcb1b3276a6a9004e9"

        if not os.path.exists(self.unite_git_dir):
            subprocess.run(["git", "clone", "git@github.com:dtr-org/unit-e",
                    self.unite_git_dir])
        self.run_git(["checkout", self.unite_git_revision], self.unite_git_dir)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.unite_git_dir)
        if git_revision != self.unite_git_revision:
            raise RuntimeError(f"Expected git revision '{self.unite_git_revision}', got '{git_revision}'")

        remotes = self.run_git(["remote"], self.unite_git_dir)
        if remotes == "origin":
            self.run_git(["remote", "add", "upstream", "https://github.com/bitcoin/bitcoin"], self.unite_git_dir)
            self.run_git(["fetch", "upstream"], self.unite_git_dir)
        self.run_git(["checkout", self.bitcoin_git_revision], self.unite_git_dir)

    def test_appropriation(self):
        subprocess.run([self.clonemachine, "--unite-branch", "master"], cwd = self.unite_git_dir, stdout=subprocess.PIPE)
        diff = self.run_git(["diff", "master", "--", "CONTRIBUTING.md"], self.unite_git_dir)
        self.assertEqual(diff, "")
        unite_master_git_revision = self.run_git(["rev-parse", "master"], self.unite_git_dir)
        commit_msg = self.run_git(["log", "-1", "--pretty=%B"], self.unite_git_dir)
        self.assertRegex(commit_msg, "revision: " + unite_master_git_revision)

if __name__ == '__main__':
    unittest.main()
