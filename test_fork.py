# Copyright (c) 2018 The unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Unit tests for clonemachine
#
# Run them with `python3 -m unittest -v test_fork`

import unittest

import tempfile
import os
from pathlib import Path

from fork import substitute_bitcoin_identifier_in_file
from fork import substitute_bitcoin_core_identifier_in_file
from fork import remove_trailing_whitespace

class TestSubstituteBitcoinIdentifier(unittest.TestCase):
    def run_and_test_substitution(self, original, expected_result):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as file:
                file.write(original.encode('utf-8'))

            substitute_bitcoin_identifier_in_file(file.name)

            with open(file.name) as result_file:
                result = result_file.read()

            self.assertEqual(result, expected_result)
        finally:
            os.remove(file.name)

    def test_git_clone(self):
        original = '''
     git clone https://github.com/bitcoin/bitcoin.git
     cd bitcoin/
'''
        expected_result = '''
     git clone https://github.com/unite/unite.git
     cd unite/
'''
        self.run_and_test_substitution(original, expected_result)

    def test_bitcoincore(self):
        original = '''
FALLBACK_DOWNLOAD_PATH ?= https://bitcoincore.org/depends-sources
'''
        self.run_and_test_substitution(original, original)

    def test_ppa(self):
        original = '''
    sudo add-apt-repository ppa:bitcoin/bitcoin
'''
        self.run_and_test_substitution(original, original)

class TestRemoveTrailingWhitespace(unittest.TestCase):
    def test_whitespace(self):
        try:
            tmp_dir = Path(tempfile.mkdtemp())

            original = "one \ntwo  two  \nno\n"
            expected_result = "one\ntwo  two\nno\n"

            file_name = tmp_dir / "test.py"
            with open(file_name, "w") as file:
                file.write(original)

            old_dir = os.getcwd()
            os.chdir(tmp_dir)
            remove_trailing_whitespace("*.py")
            os.chdir(old_dir)

            with open(file_name) as result_file:
                result = result_file.read()

            self.assertEqual(result, expected_result)
        finally:
            os.remove(file_name)
            os.rmdir(tmp_dir)

class TestSubstituteBitcoinIdentifierInFile(unittest.TestCase):
    def test_bitcoin(self):
        try:
            tmp_dir = Path(tempfile.mkdtemp())

            original = """
A Bitcoin is a BITCOIN
bitcoin
A bitcoin address
Variables: BITCOIN_CONFIG, BITCOIND_BIN, BUILD_BITCOIND
BITCOIND=${BITCOIND:-$BINDIR/bitcoind}
BITCOINCLI=${BITCOINCLI:-$BINDIR/bitcoin-cli}
BITCOINTX=${BITCOINTX:-$BINDIR/bitcoin-tx}
BITCOINQT=${BITCOINQT:-$BINDIR/qt/bitcoin-qt}
static void SetupBitcoinTxArgs()
BITCOINCONSENSUS_API_VER
"""
            expected_result = """
A Unit-e is a UNIT-E
unite
A Unit-e address
Variables: UNITE_CONFIG, UNITED_BIN, BUILD_UNITED
UNITED=${UNITED:-$BINDIR/united}
UNITECLI=${UNITECLI:-$BINDIR/unite-cli}
UNITETX=${UNITETX:-$BINDIR/unite-tx}
UNITEQT=${UNITEQT:-$BINDIR/qt/unite-qt}
static void SetupUnitETxArgs()
UNITECONSENSUS_API_VER
"""

            file_name = tmp_dir / "test"
            with open(file_name, "w") as file:
                file.write(original)

            old_dir = os.getcwd()
            os.chdir(tmp_dir)
            substitute_bitcoin_identifier_in_file(file_name)
            os.chdir(old_dir)

            with open(file_name) as result_file:
                result = result_file.read()

            self.assertEqual(result, expected_result)
        finally:
            os.remove(file_name)
            os.rmdir(tmp_dir)

class TestSubstituteBitcoinCoreIdentifierInFile(unittest.TestCase):
    def test_bitcoin_core(self):
        try:
            tmp_dir = Path(tempfile.mkdtemp())

            original = """
Bitcoin Core
# Copyright (c) 2016-2017 Bitcoin Core Developers
"""
            expected_result = """
unit-e
# Copyright (c) 2016-2017 Bitcoin Core Developers
"""

            file_name = tmp_dir / "test"
            with open(file_name, "w") as file:
                file.write(original)

            old_dir = os.getcwd()
            os.chdir(tmp_dir)
            substitute_bitcoin_core_identifier_in_file(file_name)
            os.chdir(old_dir)

            with open(file_name) as result_file:
                result = result_file.read()

            self.assertEqual(result, expected_result)
        finally:
            os.remove(file_name)
            os.rmdir(tmp_dir)

if __name__ == '__main__':
    unittest.main()
