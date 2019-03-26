#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 expandtab
# Copyright (c) 2018 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess

from processor import Processor

class ForkConfig:
    def __init__(self):
        self.substitution_blacklist = [
            # the mac build downloads dependencies from here
            "bitcoincore.org",
            # copyright notice must be retained
            "The Bitcoin Core developers",
            # also copyright
            "Bitcoin Developer",
            # also copyright
            "Bitcoin Core Developers",
            # that's a test fixture which checks SHA256 hashing
            "As Bitcoin relies on 80 byte header hashes",
            # onion routing in feature_proxy.py
            "bitcoinostk4e4re",
            # binary data in 'custom_dsstore.py
            "\\x07bitcoin",
            # some comments link to discussions in bitcointalk
            "bitcointalk.org",
            # some comments link to discussions on stackexchange
            "bitcoin.stackexchange",
            # reference to secp256k1
            "github.com/bitcoin-core/secp256k1",
            # reference to ctaes
            "github.com/unite-core/ctaes",
            # Python packagages used in functional tests
            "python-bitcoinrpc",
            "python-bitcoinlib",
            # PPA for getting BDB 4.8 packages
            "ppa:bitcoin/bitcoin"
        ]

        self.excluded_paths = [
            # git subtrees
            "src/secp256k1",
            "src/crypto/ctaes",
            "src/univalue",
            "src/leveldb",
            # Removed directories
            "doc/release-notes",
            "src/qt",
            # Clonemachine can't handle CRLF line endings so ignoring this file for now
            "doc/README_windows.txt",
        ]

        self.other_substitutions = {
            'guiutil.cpp': {
                # "unite:" is 2 characters shorter than "bitcoin:"
                'uri.replace(0, 10, "unite:");': 'uri.replace(0, 8, "unite:");'
            },
            'addrman_tests.cpp': {
                # the address manager select tests draw 20 addresses which does not pop out our port, a hundred do though.
                'for (int i = 0; i < 20; ++i) {': 'for (int i = 0; i < 100; ++i) {'
            },
            'clientversion.cpp': {
                # this renames the client from 'Satoshi' to 'Feuerland'.
                'const std::string CLIENT_NAME("Satoshi");': 'const std::string CLIENT_NAME("Feuerland");'
            },
            'rpc_signmessage.py': {
                # the message now contains "Unit-e" in strMessageMagic instead of "Bitcoin", thus its signature changes
                "expected_signature = 'INbVnW4e6PeRmsv2Qgu8NuopvrVjkcxob+sX8OcZG0SALhWybUjzMLPdAsXI46YZGb0KQTRii+wWIQzRpG/U+S0='": \
                    "expected_signature = 'IBn0HqnF0UhqTgGOiEaQouMyisWG4AOVQS+OJwVXGF2eK+11/YswSl3poGNeDLqYcNIIfTxMMy7o3XfEnxozgIM='"
            }
        }

        self.appropriated_files = [
            "README.md",
            "CONTRIBUTING.md",
            "doc/developer-notes.md",
            "contrib/devtools/copyright_header.py",
        ]

        self.removed_files = [
            ".github/ISSUE_TEMPLATE.md",
        ]

class Fork:
    def __init__(self):
        self.config = ForkConfig()
        self.processor = Processor(self.config)

    def show_upstream_diff(self, unit_e_branch, bitcoin_branch):
        result = subprocess.run(['git', 'merge-base', 'HEAD', unit_e_branch], stdout=subprocess.PIPE)
        merge_base = result.stdout.decode('utf-8').rstrip()
        print("Changes of appropriated files since last merge:")
        for file in self.config.appropriated_files:
            subprocess.run(['git', 'log', '-p', merge_base + '..' + bitcoin_branch, file])
        print("Changes of removed files since last merge:")
        for file in self.config.removed_files:
            subprocess.run(['git', 'log', '-p', merge_base + '..' + bitcoin_branch, file])

    def commit(self, message):
        subprocess.run(['git', 'commit', '-am', message])

    def remove_files(self, unit_e_branch):
        self.processor.remove_files(unit_e_branch)
        self.commit('Remove files')

    def replace_ports(self):
        self.processor.replace_recursively("8332", "7181")
        self.commit('Change mainnet rpc port 8332 into 7181')

        self.processor.replace_recursively("8333", "7182")
        self.commit('Change mainnet port 8333 into 7182')

        self.processor.replace_recursively("18332", "17181")
        self.commit('Change testnet rpc port 18332 into 17181')

        self.processor.replace_recursively("18333", "17182")
        self.commit('Change testnet port 18333 into 17182')

        self.processor.replace_recursively("18443", "17291")
        self.commit('Change regtest rpc port 18443 into 17291')

        self.processor.replace_recursively("18444", "17292")
        self.commit('Change regtest port 18444 into 17292')

        self.processor.replace_recursively("28332", "27181")
        self.commit('Change ssl rpc proxy port 28332 into 27181')

    def replace_currency_symbol(self):
        self.processor.replace_recursively("BTC", "UTE", match_before="$|[^a-bd-ln-tv-zA-Z]")
        self.commit('Change currency token BTC to UTE')

    def move_paths(self):
        self.processor.apply_recursively(lambda path: self.processor.git_move_file(path, "bitcoin", "unite"))
        self.commit('Move paths containing "bitcoin" to respective "unite" paths')

    def replace_bitcoin_core_identifiers(self):
        # Identifier in copyright statement
        self.processor.replace_in_file('src/util.cpp', '.find("Bitcoin Core")', '.find("Unit-e")')
        self.processor.replace_in_file('src/util.cpp', 'strPrefix + "The Bitcoin Core developers";',
                                        'strPrefix + "The Unit-e developers";')
        self.processor.replace_in_file('configure.ac', 'COPYRIGHT_HOLDERS_SUBSTITUTION,[[Bitcoin Core]])',
                                        'COPYRIGHT_HOLDERS_SUBSTITUTION,[[Unit-e]])')
        # all other cases
        self.processor.apply_recursively(self.processor.substitute_bitcoin_core_identifier_in_file, ['git', 'grep', '-il', 'bitcoin core'])
        self.commit('Rename occurences of "bitcoin core" to "unit-e"')

    def replace_bitcoin_identifiers(self):
        # special case of daemon name at beginning of the sentence
        with open("doc/zmq.md") as file:
            print(file.read())
        self.processor.replace_in_file('doc/zmq.md', 'Bitcoind appends', 'The unit-e daemon appends')
        # it's a unit, not a name, in this file
        self.processor.replace_in_file('test/functional/wallet_labels.py', "50 Bitcoins", "50 UTEs")
        # all other cases
        self.processor.apply_recursively(self.processor.substitute_bitcoin_identifier_in_file, ['git', 'grep', '-il', 'bitcoin', '.'])
        self.commit('Rename occurences of "bitcoin" to "unit-e"')

    def adjust_code(self):
        self.processor.apply_recursively(self.processor.substitute_any(self.config.other_substitutions))
        self.commit('Apply adjustments to tests and constants for name changes')

    def replace_unit_names(self):
        self.processor.replace_recursively("COIN", "UNIT")
        self.commit('Change identifier COIN to UNIT')

        self.processor.replace_recursively("CENT", "EEES")
        self.commit('Change identifier CENT to EEES')

    def remove_trailing_whitespace(self):
        self.processor.remove_trailing_whitespace('*.md')
        self.processor.remove_trailing_whitespace('*.py')
        self.commit('Remove trailing whitespace')

    def appropriate_files(self, unit_e_branch):
        source_revision = self.processor.appropriate_files(unit_e_branch)
        self.commit(f'Appropriate files from unit-e\n\nSource revision: {source_revision}\n')

    def run(self, unit_e_branch, bitcoin_branch):
        if unit_e_branch and bitcoin_branch:
            self.show_upstream_diff(unit_e_branch, bitcoin_branch)

        self.remove_files(unit_e_branch)
        self.replace_ports()
        self.replace_currency_symbol()
        self.move_paths()
        self.replace_bitcoin_core_identifiers()
        self.replace_bitcoin_identifiers()
        self.adjust_code()
        self.replace_unit_names()
        self.remove_trailing_whitespace()
        if unit_e_branch:
            self.appropriate_files(unit_e_branch)
