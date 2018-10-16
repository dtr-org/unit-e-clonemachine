# Unit tests for clonemachine
#
# Run them with `python3 -m unittest -v test_fork`

import unittest

import tempfile
import os

from fork import substitute_bitcoin_identifier_in_file

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

if __name__ == '__main__':
    unittest.main()
