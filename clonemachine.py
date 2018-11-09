#!/usr/bin/env python3
# Copyright (c) 2018 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Usage:
  clonemachine.py [--unite-branch=<branch-name>] [--bitcoin-branch=<branch-name>]
  clonemachine.py -h | --help

Options:
  -h --help                Show this help
  --unite-branch=<name>    Name of unit-e branch [default: master]
  --bitcoin-branch=<name>  Name of bitcoin branch (e.g. bitcoin/master), when
                           this option is set, the diff of appropriated files is
                           shown
"""
from docopt import docopt
from fork import main

if __name__ == "__main__":
    arguments = docopt(__doc__)
    unite_branch = arguments["--unite-branch"]
    bitcoin_branch = arguments["--bitcoin-branch"]
    main(unite_branch, bitcoin_branch)
