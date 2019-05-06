#!/usr/bin/env python3
# Copyright (c) 2018-2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.
"""Usage:
  clonemachine.py fork [--unit-e-branch=<name>]
  clonemachine.py file <filename>
  clonemachine.py substitute-unit-e-naming
  clonemachine.py substitute-unit-e-urls
  clonemachine.py substitute-unit-e-executables
  clonemachine.py show-upstream-diff --bitcoin-branch=<name>
  clonemachine.py -h | --help

Commands:
  fork                        Substitute all occurrences of bitcoin specific
                              identifiers by corresponding unit-e identifiers on
                              a fork. Processes files recursively and creates
                              git commits with the changes.
  file                        Do subsitutions on one file. Don't traverse the
                              file tree and don't create git commits.
  substitute-unit-e-naming    Substitute the old unit-e naming scheme by the new
                              one. To be used on the unit-e master branch before
                              merging with a bitcoin version processed through
                              clonemachine using the new naming scheme. Doesn't
                              do git commits. Replaces "UnitE Core" by "unit-e"
                              and "UnitE" by "Unit-e".
  substitute-unit-e-urls      Substitute wrongly subsituted URLs such as to the
                              bitcoin repo or the bips.
  substitute-unit-e-executables  Rename `united` to `unit-e`
  show-upstream-diff          Show how upstream has changed appropriated and
                              removed files since last merge. Requires a
                              `--bitcoin-branch`.

Examples:
  `clonemachine.py --show-upstream-diff --bitcoin-branch upstream/0.17` will
  show the diff from the last merge up to 0.17, provided you have fetched a
  bitcoin remote under the name `upstream`.

Options:
  -h --help                   Show this help
  --unit-e-branch=<name>      Name of unit-e branch [default: master]
  --bitcoin-branch=<name>     Name of bitcoin branch (e.g. bitcoin/master), when
                              this option is set, the diff of appropriated files
                              is shown
"""
from docopt import docopt
import sys

from processor import Processor
from fork import Fork
from fork import ForkConfig
from unit_e_substituter import UnitESubstituter

if __name__ == "__main__":
    arguments = docopt(__doc__)
    processor = Processor(ForkConfig())
    unit_e_branch = arguments["--unit-e-branch"]
    bitcoin_branch = arguments["--bitcoin-branch"]
    if arguments["fork"]:
        Fork(unit_e_branch, bitcoin_branch).run()
    elif arguments["file"]:
        filename = arguments["<filename>"]
        print(f"Substituting strings in file {filename}")
        processor.substitute_bitcoin_core_identifier_in_file(filename)
        processor.substitute_bitcoin_identifier_in_file(filename)
        processor.replace_in_file(filename, "BTC", "UTE", match_before="$|[^a-bd-ln-tv-zA-Z]")
    elif arguments["substitute-unit-e-naming"]:
        UnitESubstituter().substitute_naming(processor)
    elif arguments["substitute-unit-e-urls"]:
        UnitESubstituter().substitute_urls(processor)
    elif arguments["substitute-unit-e-executables"]:
        UnitESubstituter().substitute_executables(processor)
    elif arguments["show-upstream-diff"]:
        Fork(unit_e_branch, bitcoin_branch).show_upstream_diff()
    else:
        sys.exit("Unable to process command")
