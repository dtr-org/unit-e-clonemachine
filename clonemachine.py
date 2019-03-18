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
"""
from docopt import docopt
from fork import main
from fork import substitute_bitcoin_core_identifier_in_file
from fork import substitute_bitcoin_identifier_in_file
from fork import replace_in_file
from fork import replace_recursively

if __name__ == "__main__":
    arguments = docopt(__doc__)
    unit_e_branch = arguments["--unit-e-branch"]
    bitcoin_branch = arguments["--bitcoin-branch"]
    if arguments["--file"]:
        filename = arguments["--file"]
        print(f"Substituting strings in file {filename}")
        substitute_bitcoin_core_identifier_in_file(filename)
        substitute_bitcoin_identifier_in_file(filename)
        replace_in_file(filename, "BTC", "UTE", match_before="$|[^a-bd-ln-tv-zA-Z]")
    elif arguments["--substitute-unit-e-naming"]:
        replace_recursively("unite core", "unit-e")
        replace_recursively("UnitE Core", "unit-e")
        replace_in_file("src/init.h", "UnitE core", "unit-e")

        replace_recursively("UnitE", "Unit-e")

        replace_recursively("unite address", "Unit-e address")
        replace_recursively("unite addresses", "Unit-e addresses")
        replace_recursively("unite transaction", "Unit-e transaction")

        # Follow convention "BITCOIN" -> "UNIT-E" where dashes are allowed
        replace_in_file("doc/man/unite-cli.1", "UNITE-CLI", "UNIT-E-CLI")
        replace_in_file("doc/man/unite-qt.1", "UNITE-QT", "UNIT-E-QT")
        replace_in_file("doc/man/unite-cli.1", "UNITE-CLI", "UNIT-E-CLI")
        replace_in_file("doc/man/unite-tx.1", "UNITE-TX", "UNIT-E-TX")
        replace_in_file("doc/tor.md", "UNITE", "UNIT-E")

        # Handle special cases
        replace_in_file("doc/zmq.md", "UnitEd", "The unit-e daemon")
        replace_in_file("test/functional/wallet_labels.py", "UnitEs", "UTEs")
        replace_in_file("test/functional/rpc_signmessage.py",
            "expected_signature = 'HzSnrVR/sJC1Rg4SQqeecq9GAmIFtlj1u87aIh5i6Mi1bEkm7b+bsI7pIKWJsRZkjAQRkKhcTTYuVJAl0bmdWvY='",
            "expected_signature = 'IBn0HqnF0UhqTgGOiEaQouMyisWG4AOVQS+OJwVXGF2eK+11/YswSl3poGNeDLqYcNIIfTxMMy7o3XfEnxozgIM='")

        # Has already been removed. It's only here to satisfy the tests
        replace_in_file("doc/shared-libraries.md", "NUnitE", "NUnit-e")
        # Has already been fixed. It's only here to satisfy the tests
        replace_in_file("src/util.cpp", '.find("unit-e")', '.find("Unit-e")')
        replace_in_file("src/util.cpp", 'strPrefix + "The Bitcoin Core developers";',
                                        'strPrefix + "The Unit-e developers";')
        replace_in_file('configure.ac', 'COPYRIGHT_HOLDERS_SUBSTITUTION,[[unit-e]])',
                                        'COPYRIGHT_HOLDERS_SUBSTITUTION,[[Unit-e]])')
    else:
        main(unit_e_branch, bitcoin_branch)
