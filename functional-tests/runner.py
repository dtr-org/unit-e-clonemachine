# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.

import subprocess
from pathlib import Path
import os
import datetime
import yaml

import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))
from fork import ForkConfig
from processor import Processor

class Runner:
    def __init__(self, git_dir):
        self.base_path = Path(os.path.dirname(__file__))
        self.tmp_path = self.base_path / "tmp"
        self.tmp_path.mkdir(exist_ok=True)
        self.git_dir = self.tmp_path / git_dir
        self.test_data_path = self.base_path / "test_data"
        self.clonemachine = (self.base_path / "../clonemachine.py").resolve()
        self.bitcoin_branch = "0.17"
        self.bitcoin_git_revision = "1e49fe450dbb0c258776526dba3ee583461d42ff"
        self.unite_git_revision_known = "cc3bb51638a2e3dc756412f055aae92ae305a467"

    def run_git(self, arguments, cwd=None):
        if not cwd:
            cwd = self.git_dir
        result = subprocess.run(["git"] + arguments, cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        output = result.stdout.rstrip().decode("utf-8")
        return output

    def run_git_clone(self, remote, shallow=False, branch=None):
        args = ["clone"]
        if shallow:
            args += ["--depth", "1"]
        if branch:
            args += ["--branch", branch]
        args.append(remote)
        self.run_git(args, cwd=self.tmp_path)

    def checkout_unit_e_clone(self, label=None):
        if not os.path.exists(self.git_dir):
            self.run_git_clone("git@github.com:dtr-org/unit-e")
        if label:
            meta_file = self.test_data_path / f"clonemachine-{label}-expected.diff.meta"
            with meta_file.open() as file:
                meta_data = yaml.safe_load(file)
            unit_e_revision = meta_data["unit_e_git_revision"]
        else:
            unit_e_revision = self.unite_git_revision_known
        self.run_git(["checkout", "master"])
        self.run_git(["reset", "--hard", unit_e_revision])

    def checkout_shallow_bitcoin_clone(self):
        bitcoin_revision_file = self.tmp_path / "bitcoin-revision"

        if os.path.exists(self.git_dir):
            with open(bitcoin_revision_file, "r") as file:
                self.bitcoin_git_revision = file.read()
        else:
            self.run_git_clone("https://github.com/bitcoin/bitcoin",
                    shallow=True, branch=self.bitcoin_branch)
            self.bitcoin_git_revision = self.get_git_revision()
            with open(bitcoin_revision_file, "w") as file:
                file.write(self.bitcoin_git_revision)
        self.run_git(["checkout", self.bitcoin_git_revision])
        git_revision = self.get_git_revision()
        if git_revision != self.bitcoin_git_revision:
            raise RuntimeError(f"Expected git revision '{self.bitcoin_git_revision}', got '{git_revision}'")

    def add_clonemachine_config(self, config):
        with Path(self.git_dir, ".clonemachine").open("w") as file:
            file.write(config)
        self.run_git(["add", ".clonemachine"])
        self.run_git(["commit", "-m", "Add clonemachine configuration"])

    def fetch_bitcoin(self):
        remotes = self.run_git(["remote"])
        if remotes == "origin":
            self.run_git(["remote", "add", "upstream", "https://github.com/bitcoin/bitcoin"])
            self.run_git(["fetch", "upstream"])
        self.checkout_bitcoin()

    def checkout_bitcoin(self):
        self.run_git(["checkout", self.bitcoin_git_revision])
        git_revision = self.get_git_revision()
        if git_revision != self.bitcoin_git_revision:
            raise RuntimeError(f"Expected git revision '{self.bitcoin_git_revision}', got '{git_revision}'")

    def run_clonemachine(self, cmd="fork", cwd=None):
        if cwd is None:
            cwd = self.git_dir
        cmd = [self.clonemachine, cmd]
        return subprocess.run(cmd, cwd = cwd, stdout=subprocess.PIPE, check=True)

    def get_commit_date(self, git_revision, git_dir=None):
        if git_dir is None:
            git_dir = self.git_dir
        if git_revision.endswith("+changes"):
            return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
        else:
            return self.run_git(["show", "--no-patch", "--no-notes", "--pretty=%cI", git_revision], git_dir)

    def get_git_revision(self, rev="HEAD", cwd=None):
        if cwd is None:
            cwd = self.git_dir
        return self.run_git(["rev-parse", rev], cwd=cwd)

    def write_diff(self, label, expected=False, verbose=False):
        config = ForkConfig()
        config.read_from_branch("master", self.git_dir)
        exclude_files = config.appropriated_files + config.removed_files

        if verbose:
            print(f"Writing diff '{label}' ...")

        if expected:
            suffix = "expected"
        else:
            suffix = "actual"
        clonemachine_filename = f"clonemachine-{label}-{suffix}.diff"
        diff_file = self.test_data_path / clonemachine_filename

        exclude_options = [f":(exclude){filename}" for filename in exclude_files]
        diff = self.run_git(["diff", self.bitcoin_git_revision] + exclude_options)

        with diff_file.open("w") as file:
            file.write(diff)
            file.write("\n")

        clonemachine_git_revision = self.get_git_revision(cwd=".")
        if self.run_git(["diff-index", "HEAD"], "."):
            clonemachine_git_revision += "+changes"

        unite_git_revision_master = self.get_git_revision("master")

        meta_data = {
            "bitcoin_branch": self.bitcoin_branch,
            "bitcoin_commit_date": self.get_commit_date(self.bitcoin_git_revision),
            "bitcoin_git_revision": self.bitcoin_git_revision,
            "clonemachine_commit_date": self.get_commit_date(clonemachine_git_revision, "."),
            "clonemachine_git_revision": clonemachine_git_revision,
            "unit_e_commit_date": self.get_commit_date(unite_git_revision_master),
            "unit_e_git_revision": unite_git_revision_master,
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
        self.run_git(["apply", self.test_data_path / f"clonemachine-{label}-expected.diff"])
        self.commit(f"Apply diff {label}")

    def commit(self, message):
        self.run_git(["add", "."])
        self.run_git(["commit", "-m", message])

    def compare_latest_diffs(self, label):
        expected_file = self.test_data_path / f"clonemachine-{label}-expected.diff"
        actual_file = self.test_data_path / f"clonemachine-{label}-actual.diff"
        result = subprocess.run(["diff", "-u", expected_file, actual_file], stdout=subprocess.PIPE)
        diff = result.stdout.decode("utf-8")
        if diff:
            with Path(self.base_path / "tmp" / "diff.diff").open("w") as file:
                file.write(diff)
        return diff
