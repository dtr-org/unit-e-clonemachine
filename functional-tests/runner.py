# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess
from pathlib import Path
import os
import datetime
import yaml

class Runner:
    def __init__(self):
        self.base_path = Path(os.path.dirname(__file__))
        self.test_data_path = self.base_path / "test_data"
        self.clonemachine = (self.base_path / "../clonemachine.py").resolve()
        self.bitcoin_branch = "0.17"
        self.bitcoin_git_revision = "1e49fe450dbb0c258776526dba3ee583461d42ff"
        self.unite_git_dir = os.path.dirname(__file__) / Path("tmp/unit-e")
        self.unite_git_revision_known = "236db46ced3b2fd5573a2edcb1b3276a6a9004e9"
        self.unite_git_revision_master = self.run_git(["rev-parse", "master"], self.unite_git_dir)
        self.clonemachine_git_revision = self.run_git(["rev-parse", "HEAD"], ".")
        if self.run_git(["diff-index", "HEAD"], "."):
            self.clonemachine_git_revision += "+changes"

    def run_git(self, arguments, cwd=None):
        if not cwd:
            cwd = self.unite_git_dir
        result = subprocess.run(["git"] + arguments, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        output = result.stdout.rstrip().decode("utf-8")
        return output

    def checkout_unit_e(self):
        if not os.path.exists(self.unite_git_dir):
            subprocess.run(["git", "clone", "git@github.com:dtr-org/unit-e",
                    self.unite_git_dir])
        self.run_git(["checkout", self.unite_git_revision_known], self.unite_git_dir)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.unite_git_dir)
        if git_revision != self.unite_git_revision_known:
            raise RuntimeError(f"Expected git revision '{self.unite_git_revision_known}', got '{git_revision}'")

    def reset_unit_e(self, label):
        meta_file = self.test_data_path / ("clonemachine-%s-expected.diff.meta" % label)
        with meta_file.open() as file:
            meta_data = yaml.safe_load(file)
        unit_e_revision = meta_data["unit_e_git_revision"]
        self.run_git(["checkout", "master"])
        self.run_git(["reset", "--hard", unit_e_revision])

    def fetch_bitcoin(self):
        remotes = self.run_git(["remote"], self.unite_git_dir)
        if remotes == "origin":
            self.run_git(["remote", "add", "upstream", "https://github.com/bitcoin/bitcoin"], self.unite_git_dir)
            self.run_git(["fetch", "upstream"], self.unite_git_dir)
        self.checkout_bitcoin()

    def checkout_bitcoin(self):
        self.run_git(["checkout", self.bitcoin_git_revision], self.unite_git_dir)
        git_revision = self.run_git(["rev-parse", "HEAD"], self.unite_git_dir)
        if git_revision != self.bitcoin_git_revision:
            raise RuntimeError(f"Expected git revision '{self.bitcoin_git_revision}', got '{git_revision}'")

    def run_clonemachine(self, option=None):
        cmd = [self.clonemachine, "--unite-branch", "master"]
        if option:
            cmd.append(option)
        subprocess.run(cmd, cwd = self.unite_git_dir, stdout=subprocess.PIPE)

    def get_commit_date(self, git_revision, git_dir):
        if git_revision.endswith("+changes"):
            return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        else:
            return self.run_git(["show", "--no-patch", "--no-notes", "--pretty=%cI", git_revision], git_dir)

    def write_diff(self, label, expected=False, verbose=False):
        if verbose:
            print("Writing diff '%s' ..." % label)

        if expected:
            suffix = "expected"
        else:
            suffix = "actual"
        clonemachine_filename = "clonemachine-%s-%s.diff" % (label, suffix)
        diff_file = self.test_data_path / clonemachine_filename
        diff = self.run_git(["diff", self.bitcoin_git_revision], self.unite_git_dir)
        with diff_file.open("w") as file:
            file.write(diff)
            file.write("\n")

        meta_data = {
            "bitcoin_branch": self.bitcoin_branch,
            "bitcoin_commit_date": self.get_commit_date(self.bitcoin_git_revision, self.unite_git_dir),
            "bitcoin_git_revision": self.bitcoin_git_revision,
            "clonemachine_commit_date": self.get_commit_date(self.clonemachine_git_revision, "."),
            "clonemachine_git_revision": self.clonemachine_git_revision,
            "unit_e_commit_date": self.get_commit_date(self.unite_git_revision_master, self.unite_git_dir),
            "unit_e_git_revision": self.unite_git_revision_master,
        }
        meta_output = ""
        for item in meta_data:
            meta_output += item + ": " + meta_data[item] + "\n"
        meta_filename = clonemachine_filename + ".meta"
        with (self.test_data_path / meta_filename).open("w") as file:
            file.write(meta_output)
        if verbose:
            print(meta_output)

    def apply_diff(self, label):
        self.run_git(["apply", self.test_data_path / ("clonemachine-%s-expected.diff" % label)])
        self.commit("Apply diff %s" % label)

    def commit(self, message):
        self.run_git(["add", "."])
        self.run_git(["commit", "-m", message])

    def compare_latest_diffs(self, label):
        expected_file = self.test_data_path / ("clonemachine-%s-expected.diff" % label)
        actual_file = self.test_data_path / ("clonemachine-%s-actual.diff" % label)
        result = subprocess.run(["diff", "-u", expected_file, actual_file], stdout=subprocess.PIPE)
        diff = result.stdout.decode("utf-8")
        if diff:
            with Path(self.base_path / "tmp" / "diff.diff").open("w") as file:
                file.write(diff)
        return diff
