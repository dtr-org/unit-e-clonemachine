#!/usr/bin/env python3
# Copyright (c) 2018 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Usage:
  clonemachine.py [options]
  clonemachine.py -h | --help

Options:
  -h --help                Show this help
  --unite-branch=<name>    Name of unit-e branch [default: master]
  --bitcoin-branch=<name>  Name of bitcoin branch (e.g. bitcoin/master), when
                           this option is set, the diff of appropriated files is
                           shown
  --file=<filename>        If this option is set don't traverse the file tree
                           but just substitute in this file and don't create
                           git commits
"""
from docopt import docopt
from fork import main
from fork import substitute_bitcoin_identifier_in_file
from fork import replace_in_file

if __name__ == "__main__":
    arguments = docopt(__doc__)
    unite_branch = arguments["--unite-branch"]
    bitcoin_branch = arguments["--bitcoin-branch"]
    if arguments["--file"]:
        filename = arguments["--file"]
        print("Substituting strings in file {}".format(filename))
        substitute_bitcoin_identifier_in_file(filename)
        replace_in_file(filename, "BTC", "UTE", match_before="$|[^a-bd-ln-tv-zA-Z]")
    else:
        main(unite_branch, bitcoin_branch)
