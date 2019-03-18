# Copyright (c) 2018-2019 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Functional test for clonemachine using a full checkout of the unit-e repo
# and a full fetched remote of the bitcoin repo
#
# Run it with `python3 -m unittest -v test_full_checkout.py`

import unittest

import tempfile
import os
import subprocess
from pathlib import Path
import yaml

class TestFullCheckout(unittest.TestCase):
    def run_git(self, arguments):
        result = subprocess.run(["git"] + arguments, cwd = self.unite_git_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.rstrip().decode("utf-8")
        return output

    def setUp(self):
        self.clonemachine = (Path(os.path.dirname(__file__)) / "../clonemachine.py").resolve()
        self.bitcoin_branch = "0.17"
        self.bitcoin_git_revision = "1e49fe450dbb0c258776526dba3ee583461d42ff"
        self.unite_git_dir = os.path.dirname(__file__) / Path("tmp/unit-e")
        self.unite_git_revision = "85f9080ce2b287ee09f03bf9f8c5b2a7d84ea4a3"

        if not os.path.exists(self.unite_git_dir):
            subprocess.run(["git", "clone", "git@github.com:dtr-org/unit-e",
                    self.unite_git_dir])
        self.run_git(["checkout", "master"])
        self.run_git(["reset", "--hard", self.unite_git_revision])
        git_revision = self.run_git(["rev-parse", "HEAD"])
        if git_revision != self.unite_git_revision:
            raise RuntimeError(f"Expected git revision '{self.unite_git_revision}', got '{git_revision}'")

        with Path(self.unite_git_dir, ".clonemachine").open("w") as file:
            file.write("appropriated_files:\n- doc/gitian-building.md\n\n"
                       "removed_files:\n- contrib/gitian-descriptors/gitian-osx-signer.yml\n")
        self.run_git(["add", ".clonemachine"])
        self.run_git(["commit", "-m", "Add clonemachine configuration"])

        remotes = self.run_git(["remote"])
        if remotes == "origin":
            self.run_git(["remote", "add", "upstream", "https://github.com/bitcoin/bitcoin"])
            self.run_git(["fetch", "upstream"])
        self.run_git(["checkout", self.bitcoin_git_revision])

    def test_clonemachine_config(self):
        yaml_data = self.run_git(["show", "master:.clonemachine"])
        config = yaml.load(yaml_data)
        self.assertEqual(config, {
            "appropriated_files": ["doc/gitian-building.md"],
            "removed_files": ["contrib/gitian-descriptors/gitian-osx-signer.yml"],
        })

    def test_appropriation(self):
        # Run clonemachine
        result = subprocess.run([self.clonemachine, "--unit-e-branch", "master"], cwd = self.unite_git_dir, stdout=subprocess.PIPE)
        with Path(os.path.dirname(__file__), "tmp", "clonemachine.log").open("w") as file:
            file.write(result.stdout.decode('utf-8'))

        # Check that one of the appropriated files is identical to the unit-e version
        diff = self.run_git(["diff", "master", "--", "CONTRIBUTING.md"])
        self.assertEqual(diff, "")

        # Check file list, assuming the latest commit is the appropriating commit
        appropriated_files = self.run_git(["diff-tree", "--name-only", "--no-commit-id", "-r", "HEAD"])
        expected_files = """CONTRIBUTING.md
README.md
contrib/devtools/copyright_header.py
doc/developer-notes.md
doc/gitian-building.md"""
        self.assertEqual(appropriated_files, expected_files)

        # Check that commit message contains the revision of the appropriated files
        unite_master_git_revision = self.run_git(["rev-parse", "master"])
        commit_msg = self.run_git(["log", "-1", "--pretty=%B"])
        self.assertRegex(commit_msg, "revision: " + unite_master_git_revision)

    def test_remove_files(self):
        files_to_be_removed = [".github/ISSUE_TEMPLATE.md", "contrib/gitian-descriptors/gitian-osx-signer.yml"]
        for file in files_to_be_removed:
            self.assertTrue(os.path.isfile(self.unite_git_dir / file))

        result = subprocess.run([self.clonemachine, "--unit-e-branch", "master"], cwd = self.unite_git_dir, stdout=subprocess.PIPE)
        with Path(os.path.dirname(__file__), "tmp", "clonemachine.log").open("w") as file:
            file.write(result.stdout.decode('utf-8'))

        for file in files_to_be_removed:
            self.assertFalse(os.path.isfile(self.unite_git_dir / file))

if __name__ == '__main__':
    unittest.main()
