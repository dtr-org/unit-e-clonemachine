# Copyright (c) 2018 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Functional test for clonemachine
#
# Run it with `python3 -m unittest -v test_clonemachine.py`

import unittest

import tempfile
import os
import subprocess
from pathlib import Path

class TestClonemachine(unittest.TestCase):
    def run_cmd(self, command_and_arguments, cwd = None):
        result = subprocess.run(command_and_arguments, cwd = cwd, stdout=subprocess.PIPE)
        return result.stdout.rstrip().decode("utf-8")

    def run_git(self, arguments, cwd):
        result = subprocess.run(["git"] + arguments, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.rstrip().decode("utf-8")

    def find_files_with_trailing_whitespace(self, file_pattern):
        return self.run_cmd(["find",
            self.bitcoin_git_dir, "-type", "f", "-name", file_pattern,
            "-exec", "egrep", "-l", " +$", "{}", ";"])

    def setUp(self):
        self.clonemachine = (Path(os.path.dirname(__file__)) / "../fork.py").resolve()
        self.bitcoin_git_dir = os.path.dirname(__file__) / Path("tmp/bitcoin")
        self.bitcoin_branch = "0.17"
        self.bitcoin_git_revision = "1e49fe450dbb0c258776526dba3ee583461d42ff"

        if not os.path.exists(self.bitcoin_git_dir):
            subprocess.run(["git", "clone", "--depth", "1", "--branch",
                    self.bitcoin_branch, "https://github.com/bitcoin/bitcoin",
                    self.bitcoin_git_dir])
        self.run_git(["checkout", self.bitcoin_git_revision], self.bitcoin_git_dir)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.bitcoin_git_dir)
        if git_revision != self.bitcoin_git_revision:
            raise RuntimeError("Expected git revision '{}', got '{}'".format(
                    self.bitcoin_git_revision, git_revision))

    def test_idempotence(self):
        subprocess.run([self.clonemachine], cwd = self.bitcoin_git_dir, stdout=subprocess.PIPE)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.bitcoin_git_dir)
        # Check that some substitution was done and new commits where added
        self.assertNotEqual(git_revision, self.bitcoin_git_revision)
        subprocess.run([self.clonemachine], cwd = self.bitcoin_git_dir, stdout=subprocess.PIPE)
        new_git_revision = self.run_git(["rev-parse", "HEAD"], self.bitcoin_git_dir)
        # Check that no new commits where added
        self.assertEqual(git_revision, new_git_revision)

    def test_remove_trailing_whitespace(self):
        subprocess.run([self.clonemachine], cwd = self.bitcoin_git_dir, stdout=subprocess.PIPE)

        files_with_trailing_whitespace = self.find_files_with_trailing_whitespace("*.md")
        self.assertEqual(files_with_trailing_whitespace, "")
        files_with_trailing_whitespace = self.find_files_with_trailing_whitespace("*.py")
        self.assertEqual(files_with_trailing_whitespace, "")

if __name__ == '__main__':
    unittest.main()
