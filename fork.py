#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 expandtab
# Copyright (c) 2018 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import subprocess
import re
import sys
import os
from typing import *

substitution_blacklist = [
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

excluded_paths = [
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

other_substitutions = {
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

appropriated_files = [
    "README.md",
    "CONTRIBUTING.md",
    "doc/developer-notes.md",
    "contrib/devtools/copyright_header.py"
]

removed_files = [
    ".github/ISSUE_TEMPLATE.md",
]

def to_lower(s: str) -> str:
    return s.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'abcdefghijklmnopqrstuvwxyz'
    ))


def substitute(string: str,
               needle: str,
               replacer: Callable[[str], str],
               match_before: str = "",
               match_after: str = "",
               case_sensitive: bool = True,
               blacklist: Sequence[str] = []) -> str:
    haystack = string if case_sensitive else to_lower(string)
    out = []
    needle_length = len(needle)
    ix = 0
    begin_offset = haystack.find(needle, ix)
    while begin_offset >= 0:
        end_offset = begin_offset + needle_length
        before = string[begin_offset - 1: begin_offset]
        after = string[end_offset: end_offset + 1]
        match = string[begin_offset: end_offset]
        blacklisted = False
        for item in blacklist:
            item_haystack = item if case_sensitive else to_lower(item)
            item_ix = item_haystack.find(needle)
            while item_ix >= 0:
                ctx_begin_offset = begin_offset - item_ix
                ctx_end_offset = ctx_begin_offset + len(item)
                context = string[ctx_begin_offset: ctx_end_offset]
                if context == item:
                    blacklisted = True
                    break
                else:
                    item_ix = item_haystack.find(needle, item_ix + len(match))
            if blacklisted:
                break
        if not blacklisted and re.match(match_before, before) and re.match(match_after, after):
            out.append(string[ix: begin_offset])
            out.append(replacer(match))
        else:
            out.append(string[ix:end_offset])
        ix = end_offset
        begin_offset = haystack.find(needle, ix)
    out.append(string[ix: len(string)])
    return "".join(out)


def replace_recursively(needle: str,
                        replacement: str,
                        match_before: str = "$|[^a-zA-Z0-9]",
                        match_after: str = "$|[^a-zA-Z0-9]"):
    files = subprocess.run(["git", "grep", "-l", needle], stdout=subprocess.PIPE)
    for f in files.stdout.splitlines():
        path = f.decode('utf8')
        if is_hidden_file(path) or is_in_excluded_path(path):
            continue
        with open(path, 'r') as source_file:
            contents = source_file.read()
        out = substitute(contents, needle, lambda x: replacement, match_before, match_after)
        with open(path, 'w') as source_file:
            source_file.write(out)

def replace_in_file(path: str,
                    needle: str,
                    replacement: str,
                    match_before: str = "$|[^a-zA-Z0-9]",
                    match_after: str = "$|[^a-zA-Z0-9]"):
    if not os.path.exists(path):
        print("WARNING: File '%s' does not exist for replacement of '%s' by '%s'" % (
                path, needle, replacement), file=sys.stderr)
        return
    with open(path, 'r') as source_file:
        contents = source_file.read()
    out = substitute(contents, needle, lambda x: replacement, match_before, match_after)
    with open(path, 'w') as source_file:
        source_file.write(out)

def is_hidden_file(path):
    return any(map(lambda x: len(x) > 1 and x.startswith('.'), path.split('/')[:-1]))


def is_in_excluded_path(path):
    global excluded_paths
    normalized = "/".join(filter(lambda x: x != '.' and len(x) > 0, path.split('/')))
    for excl in excluded_paths:
        if normalized.startswith(excl):
            return True
    return False


def apply_recursively(func, command=['find', '.', '-type', 'f']):
    files = subprocess.run(command, stdout=subprocess.PIPE)
    for f in files.stdout.splitlines():
        path = f.decode('utf8')
        if is_hidden_file(path) or is_in_excluded_path(path):
            continue
        func(path)

def remove_trailing_whitespace(file_pattern):
    if sys.platform == "linux":
        sed = "sed"
    elif sys.platform == "darwin":
        sed = "gsed"
    else:
        raise RuntimeError(f"Unsupported platform: '{sys.platform}'")
    subprocess.run(['find', '.', '-type', 'f', '-name', file_pattern,
      '-exec', sed, '--in-place', r's/[[:space:]]\+$//', '{}', '+'])

def git_move_file(path, needle, replacement):
    target = path.replace(needle, replacement)
    if target == path:
        return
    target_parent = '/'.join(target.split('/')[:-1])
    subprocess.run(['mkdir', '-p', target_parent])
    result = subprocess.run(["git", "mv", path, target])
    if result.returncode != 0:
        exit(result.returncode)


def replace_bitcoin_identifier(occurence: str):
    if occurence == 'bitcoin':
        return 'unite'
    if occurence == 'BITCOIN':
        return 'UNIT-E'
    if occurence == 'Bitcoin':
        return 'Unit-e'
    raise Exception("Don't know how to handle %s" % occurence)


def replace_bitcoin_core_identifier(occurence: str):
    if occurence in ['bitcoin core', 'Bitcoin Core', 'Bitcoin core']:
      return 'unit-e'
    raise Exception("Don't know how to handle %s" % occurence)


def substitute_bitcoin_identifier_in_file(path):
    with open(path, 'r') as source_file:
        contents = source_file.read()
    # Substitutions in the form [needle, match_after, replacement_string]
    substitutions = [
        ["BITCOIND", "", "UNITED"],
        ["BITCOINCLI", "", "UNITECLI"],
        ["BITCOINTX", "", "UNITETX"],
        ["BITCOINQT", "", "UNITEQT"],
        ["BITCOIN", "[_C]", "UNITE"],
        ["bitcoin address", "", "Unit-e address"],
        ["bitcoin transaction", "", "Unit-e transaction"],
        ["Bitcoin", "[A-CE-Z]", "UnitE"],
    ]
    for substitution in substitutions:
        contents = substitute(string = contents,
                              needle = substitution[0],
                              match_after = substitution[1],
                              replacer = lambda occurence: substitution[2],
                              case_sensitive=True,
                              blacklist = substitution_blacklist)
    altered = substitute(string = contents,
                         needle = "bitcoin",
                         replacer = replace_bitcoin_identifier,
                         case_sensitive=False,
                         blacklist=substitution_blacklist)
    with open(path, 'w') as target_file:
        target_file.write(altered)


def substitute_bitcoin_core_identifier_in_file(path):
    with open(path, 'r') as source_file:
        contents = source_file.read()
    altered = substitute(string = contents,
                         needle = "bitcoin core",
                         replacer = replace_bitcoin_core_identifier,
                         case_sensitive=False,
                         blacklist=substitution_blacklist)
    with open(path, 'w') as target_file:
        target_file.write(altered)


def substitute_any(substitutions):
    def subst(path):
        basename = path.split('/')[-1]
        if basename in substitutions:
            with open(path, 'r') as source_file:
                contents = source_file.read()
            for needle, replacement in substitutions[basename].items():
                contents = contents.replace(needle, replacement)
            with open(path, 'w') as target_file:
                target_file.write(contents)

    return subst


def appropriate_files(branch):
    for file in appropriated_files:
        subprocess.run(['git', 'checkout', branch, file])
    result = subprocess.run(['git', 'rev-parse', branch], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').rstrip()


def remove_files():
    for file in removed_files:
        if os.path.exists(file):
            subprocess.run(['git', 'rm', file])


def main(unite_branch, bitcoin_branch):
    if unite_branch and bitcoin_branch:
        result = subprocess.run(['git', 'merge-base', 'HEAD', unite_branch], stdout=subprocess.PIPE)
        merge_base = result.stdout.decode('utf-8').rstrip()
        print("Changes of appropriated files since last merge:")
        for file in appropriated_files:
            subprocess.run(['git', 'log', '-p', merge_base + '..' + bitcoin_branch, file])
        print("Changes of removed files since last merge:")
        for file in removed_files:
            subprocess.run(['git', 'log', '-p', merge_base + '..' + bitcoin_branch, file])

    remove_files()
    subprocess.run(['git', 'commit', '-am', 'Remove files'])

    replace_recursively("8332", "7181")
    subprocess.run(['git', 'commit', '-am', 'Change mainnet rpc port 8332 into 7181'])

    replace_recursively("8333", "7182")
    subprocess.run(['git', 'commit', '-am', 'Change mainnet port 8333 into 7182'])

    replace_recursively("18332", "17181")
    subprocess.run(['git', 'commit', '-am', 'Change testnet rpc port 18332 into 17181'])

    replace_recursively("18333", "17182")
    subprocess.run(['git', 'commit', '-am', 'Change testnet port 18333 into 17182'])

    replace_recursively("18443", "17291")
    subprocess.run(['git', 'commit', '-am', 'Change regtest rpc port 18443 into 17291'])

    replace_recursively("18444", "17292")
    subprocess.run(['git', 'commit', '-am', 'Change regtest port 18444 into 17292'])

    replace_recursively("28332", "27181")
    subprocess.run(['git', 'commit', '-am', 'Change ssl rpc proxy port 28332 into 27181'])

    replace_recursively("BTC", "UTE", match_before="$|[^a-bd-ln-tv-zA-Z]")
    subprocess.run(['git', 'commit', '-am', 'Change currency token BTC to UTE'])

    apply_recursively(lambda path: git_move_file(path, "bitcoin", "unite"))
    subprocess.run(['git', 'commit', '-am', 'Move paths containing "bitcoin" to respective "unite" paths'])

    # Identifier in copyright statement
    replace_in_file('src/util.cpp', '.find("Bitcoin Core")', '.find("Unit-e")')
    replace_in_file('src/util.cpp', 'strPrefix + "The Bitcoin Core developers";',
                                    'strPrefix + "The Unit-e developers";')
    replace_in_file('configure.ac', 'COPYRIGHT_HOLDERS_SUBSTITUTION,[[Bitcoin Core]])',
                                    'COPYRIGHT_HOLDERS_SUBSTITUTION,[[Unit-e]])')
    # all other cases
    apply_recursively(substitute_bitcoin_core_identifier_in_file, ['git', 'grep', '-il', 'bitcoin core'])
    subprocess.run(['git', 'commit', '-am', 'Rename occurences of "bitcoin core" to "unit-e"'])

    # special case of daemon name at beginning of the sentence
    with open("doc/zmq.md") as file:
        print(file.read())
    replace_in_file('doc/zmq.md', 'Bitcoind appends', 'The unit-e daemon appends')
    # it's a unit, not a name, in this file
    replace_in_file('test/functional/wallet_labels.py', "50 Bitcoins", "50 UTEs")
    # all other cases
    apply_recursively(substitute_bitcoin_identifier_in_file, ['git', 'grep', '-il', 'bitcoin', '.'])
    subprocess.run(['git', 'commit', '-am', 'Rename occurences of "bitcoin" to "unit-e"'])

    apply_recursively(substitute_any(other_substitutions))
    subprocess.run(['git', 'commit', '-am', 'Apply adjustments to tests and constants for name changes'])

    replace_recursively("COIN", "UNIT")
    subprocess.run(['git', 'commit', '-am', 'Change identifier COIN to UNIT'])

    replace_recursively("CENT", "EEES")
    subprocess.run(['git', 'commit', '-am', 'Change identifier CENT to EEES'])

    remove_trailing_whitespace('*.md')
    remove_trailing_whitespace('*.py')
    subprocess.run(['git', 'commit', '-am', 'Remove trailing whitespace'])

    if unite_branch:
        source_revision = appropriate_files(unite_branch)
        subprocess.run(['git', 'commit', '-m', f'Appropriate files from unit-e\n\nSource revision: {source_revision}\n'])

if __name__ == '__main__':
    main(None, None)
