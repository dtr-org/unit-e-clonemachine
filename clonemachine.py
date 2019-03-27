#!/usr/bin/env python3
# Copyright (c) 2018 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Usage:
  clonemachine.py [options]
  clonemachine.py -h | --help

Options:
  -h --help                   Show this help
  --unit-e-branch=<name>      Name of unit-e branch [default: master]
  --bitcoin-branch=<name>     Name of bitcoin branch (e.g. bitcoin/master), when
                              this option is set, the diff of appropriated files
                              is shown
  --file=<filename>           If this option is set don't traverse the file tree
                              but just substitute in this file and don't create
                              git commits
  --substitute-unit-e-naming  Substitute the old unit-e naming scheme by the new
                              one. To be used on the unit-e master branch before
                              merging with a bitcoin version processed through
                              clonemachine using the new naming scheme. Doesn't
                              do git commits. Replaces "UnitE Core" by "unit-e"
                              and "UnitE" by "Unit-e".
  --substitute-unit-e-urls    Substitute wrongly subsituted URLs such as to the
                              bitcoin repo or the bips.
"""
from docopt import docopt

from processor import Processor
from fork import Fork
from fork import ForkConfig
from unit_e_substituter import UnitESubstituter

if __name__ == "__main__":
    arguments = docopt(__doc__)
    processor = Processor(ForkConfig())
    unit_e_branch = arguments["--unit-e-branch"]
    bitcoin_branch = arguments["--bitcoin-branch"]
    if arguments["--file"]:
        filename = arguments["--file"]
        print(f"Substituting strings in file {filename}")
        processor.substitute_bitcoin_core_identifier_in_file(filename)
        processor.substitute_bitcoin_identifier_in_file(filename)
        processor.replace_in_file(filename, "BTC", "UTE", match_before="$|[^a-bd-ln-tv-zA-Z]")
    elif arguments["--substitute-unit-e-naming"]:
        UnitESubstituter().substitute_naming(processor)
    elif arguments["--substitute-unit-e-urls"]:
        UnitESubstituter().substitute_urls(processor)
    else:
        Fork().run(unit_e_branch, bitcoin_branch)
