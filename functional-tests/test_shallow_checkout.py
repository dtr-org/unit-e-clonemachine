# Copyright (c) 2018-2019 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Functional test for clonemachine using shallow checkout of bitcoin repo
#
# Run it with `pytest -v test_shallow_checkout.py`

import tempfile
import os
import subprocess
from pathlib import Path
import pytest

from runner import Runner

def find_files_with_trailing_whitespace(target_dir, file_pattern):
    result = subprocess.run(["find",
        target_dir, "-type", "f", "-name", file_pattern,
        "-exec", "egrep", "-l", " +$", "{}", ";"], stdout=subprocess.PIPE)
    return result.stdout.rstrip().decode("utf-8")

@pytest.fixture
def runner():
    """Set up git checkout for test and return a runner to run operations
    on it.
    """
    runner = Runner("bitcoin")
    runner.checkout_shallow_bitcoin_clone()
    return runner

def test_idempotence(runner):
    runner.run_clonemachine()
    git_revision = runner.get_git_revision()
    # Check that some substitution was done and new commits where added
    assert git_revision != runner.bitcoin_git_revision

    runner.run_clonemachine()
    new_git_revision = runner.get_git_revision()
    # Check that no new commits where added
    assert git_revision == new_git_revision

def test_remove_trailing_whitespace(runner):
    runner.run_clonemachine()

    files_with_trailing_whitespace = find_files_with_trailing_whitespace(runner.git_dir, "*.md")
    assert files_with_trailing_whitespace == ""
    files_with_trailing_whitespace = find_files_with_trailing_whitespace(runner.git_dir, "*.py")
    assert files_with_trailing_whitespace == ""

def test_remove_files(runner):
    file_to_be_removed = runner.git_dir / ".github/ISSUE_TEMPLATE.md"
    assert os.path.isfile(file_to_be_removed)

    runner.run_clonemachine()
    assert not os.path.isfile(file_to_be_removed)
    # Check that all changes are committed and checkout is clean
    git_status = runner.run_git(["status", "--porcelain"])
    assert git_status == ""
