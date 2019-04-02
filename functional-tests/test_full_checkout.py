# Copyright (c) 2018-2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.

# Functional test for clonemachine using a full checkout of the unit-e repo
# and a full fetched remote of the bitcoin repo
#
# Run it with `pytest -v test_full_checkout.py`

import pytest
import tempfile
import os
import subprocess
from pathlib import Path
import yaml

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

def test_appropriation(runner):
    runner.run_clonemachine()

    # Check that one of the appropriated files is identical to the unit-e version
    diff = runner.run_git(["diff", "master", "--", "CONTRIBUTING.md"])
    assert diff == ""

    # Check file list, assuming the latest commit is the appropriating commit
    appropriated_files = runner.run_git(["diff-tree", "--name-only", "--no-commit-id", "-r", "HEAD"])
    expected_files = """CONTRIBUTING.md
README.md
contrib/devtools/copyright_header.py
contrib/gitian-build.py
contrib/gitian-keys/keys.txt
doc/developer-notes.md
doc/gitian-building.md"""
    assert appropriated_files == expected_files

    # Check that commit message contains the revision of the appropriated files
    unite_master_git_revision = runner.get_git_revision("master")
    commit_msg = runner.run_git(["log", "-1", "--pretty=%B"])
    assert "revision: " + unite_master_git_revision in commit_msg

def test_remove_files(runner):
    files_to_be_removed = [".github/ISSUE_TEMPLATE.md", "contrib/gitian-descriptors/gitian-osx-signer.yml"]
    for file in files_to_be_removed:
        assert os.path.isfile(runner.git_dir / file)

    result = runner.run_clonemachine()
    with Path(os.path.dirname(__file__), "tmp", "clonemachine.log").open("w") as file:
        file.write(result.stdout.decode('utf-8'))

    for file in files_to_be_removed:
        assert not os.path.isfile(runner.git_dir / file)
