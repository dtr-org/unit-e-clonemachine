# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.
class UnitESubstituter:
    """
    Logic for substituting strings in the unit-e codebase. This is needed when
    changing substitutions in clonemachine. The UnitESubstituter then is used to
    create the corresponding changes in the unit-e codebase, so that it's moved
    from the version created by an older clonemachine to the version created by
    the changed newer clonemachine.
    """

    def substitute_naming(self, processor):
        """
        Replace `UnitE` by `Unit-e` and `UnitE Core` by `unit-e`.
        """
        processor.replace_recursively("unite core", "unit-e")
        processor.replace_recursively("UnitE Core", "unit-e")
        processor.replace_in_file("src/init.h", "UnitE core", "unit-e")

        processor.replace_recursively("UnitE", "Unit-e")

        processor.replace_recursively("unite address", "Unit-e address")
        processor.replace_recursively("unite addresses", "Unit-e addresses")
        processor.replace_recursively("unite transaction", "Unit-e transaction")

        # Follow convention "BITCOIN" -> "UNIT-E" where dashes are allowed
        processor.replace_in_file("doc/man/unite-cli.1", "UNITE-CLI", "UNIT-E-CLI")
        processor.replace_in_file("doc/man/unite-qt.1", "UNITE-QT", "UNIT-E-QT")
        processor.replace_in_file("doc/man/unite-cli.1", "UNITE-CLI", "UNIT-E-CLI")
        processor.replace_in_file("doc/man/unite-tx.1", "UNITE-TX", "UNIT-E-TX")
        processor.replace_in_file("doc/tor.md", "UNITE", "UNIT-E")

        # Handle special cases
        processor.replace_in_file("doc/zmq.md", "UnitEd", "The unit-e daemon")
        processor.replace_in_file("test/functional/wallet_labels.py", "UnitEs", "UTEs")
        processor.replace_in_file("test/functional/rpc_signmessage.py",
            "expected_signature = 'HzSnrVR/sJC1Rg4SQqeecq9GAmIFtlj1u87aIh5i6Mi1bEkm7b+bsI7pIKWJsRZkjAQRkKhcTTYuVJAl0bmdWvY='",
            "expected_signature = 'IBn0HqnF0UhqTgGOiEaQouMyisWG4AOVQS+OJwVXGF2eK+11/YswSl3poGNeDLqYcNIIfTxMMy7o3XfEnxozgIM='")

        # Has already been removed. It's only here to satisfy the tests
        processor.replace_in_file("doc/shared-libraries.md", "NUnitE", "NUnit-e")
        # Has already been fixed. It's only here to satisfy the tests
        processor.replace_in_file("src/util.cpp", '.find("unit-e")', '.find("Unit-e")')
        processor.replace_in_file("src/util.cpp", 'strPrefix + "The Bitcoin Core developers";',
                                        'strPrefix + "The Unit-e developers";')
        processor.replace_in_file('configure.ac', 'COPYRIGHT_HOLDERS_SUBSTITUTION,[[unit-e]])',
                                        'COPYRIGHT_HOLDERS_SUBSTITUTION,[[Unit-e]])')

    def substitute_urls(self, processor):
        processor.replace_recursively("github.com/unite/bips", "github.com/bitcoin/bips")
        processor.replace_recursively("github.com/unite/unite", "github.com/bitcoin/bitcoin")
        processor.replace_in_file("contrib/devtools/README.md", "unite/unite", "dtr-org/unit-e")
        processor.replace_in_file_regex("src/protocol.h",
            r"https://unite.org/en/developer-reference#(\w+)",
            r"https://docs.unit-e.io/reference/p2p/\1.html")
        processor.replace_recursively("www.unite.org", "unit-e.io")
        processor.replace_recursively("unite.org", "bitcoin.org")
