#!/usr/bin/env python3
# vim: ts=2 sw=2 sts=2 expandtab

import subprocess
import re
from typing import *

substitution_blacklist = [
  # the mac build downloads dependencies from here
  "bitcoincore.org",
  # copyright notice must be retained
  "The Bitcoin Core developers",
  # also copyright
  "Bitcoin Developer",
  # that's a test fixture which checks SHA256 hashing
  "As Bitcoin relies on 80 byte header hashes",
  # onion routing in feature_proxy.py
  "bitcoinostk4e4re",
  # binary data in 'custom_dsstore.py
  "\\x07bitcoin"
]

excluded_directories = [
  "src/secp256k1",
  "src/crypto/ctaes",
  "src/univalue",
  "src/leveldb"
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
    # the message now contains UnitE instead of Bitcoin, thus it's signature changes
    "expected_signature = 'INbVnW4e6PeRmsv2Qgu8NuopvrVjkcxob+sX8OcZG0SALhWybUjzMLPdAsXI46YZGb0KQTRii+wWIQzRpG/U+S0='": \
      "expected_signature = 'HzSnrVR/sJC1Rg4SQqeecq9GAmIFtlj1u87aIh5i6Mi1bEkm7b+bsI7pIKWJsRZkjAQRkKhcTTYuVJAl0bmdWvY='"
  }
}

protocol_economics_substitutions = {
  'validation.cpp': {
    # initial block reward in UnitE is 10 coins, as opposed to 50 in bitcoin
    'CAmount nSubsidy = 50 * COIN;': 'CAmount nSubsidy = 10 * COIN;',
    # block interval is 100M, as opposed to 210k in bitcoin
    '// Subsidy is cut in half every 210,000 blocks which will occur approximately every 4 years.':
      '// Subsidy is cut in half every 100M blocks which will occur approximately every 13 years.'
  },
  'amount.h': {
    # adds a comment to clarify the order of magnitude
    'static const CAmount COIN = 100000000;': 'static const CAmount COIN = 100000000; // 10 ** 8',
    # adds a comment to clarify the order of magnitude
    'static const CAmount CENT = 1000000;': 'static const CAmount CENT = 1000000;   // 10 ** 6',
    # adds a comment to explain the method of calculation
    # and changes MAX_MONEY (total supply) that value
    'static const CAmount MAX_MONEY = 21000000 * COIN;':
      'static const CAmount MAX_MONEY = 271828182845904544; // 1 bln * COIN * exp(1)',
    # get rid of a bitcoin specific comment
'''
 *
 * Note that this constant is *not* the total money supply, which in UnitE
 * currently happens to be less than 21,000,000 UNT for various reasons, but
 * rather a sanity check. As this sanity check is used by consensus-critical
 * validation code, the exact value of the MAX_MONEY constant is consensus
 * critical; in unusual circumstances like a(nother) overflow bug that allowed
 * for the creation of coins out of thin air modification could lead to a fork.
 *''': ''
  }
}

def toLower(s: str) -> str:
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
  haystack = string if case_sensitive else toLower(string)
  out = []
  needle_length = len(needle)
  ix = 0
  begin_offset = haystack.find(needle, ix)
  while begin_offset >= 0:
    end_offset = begin_offset + needle_length
    before = string[begin_offset - 1 : begin_offset]
    after = string[end_offset : end_offset + 1]
    match = string[begin_offset : end_offset]
    blacklisted = False
    for item in blacklist:
      item_haystack = item if case_sensitive else toLower(item)
      item_ix = item_haystack.find(needle)
      ctx_begin_offset = begin_offset - item_ix
      ctx_end_offset = ctx_begin_offset + len(item)
      context = string[ctx_begin_offset : ctx_end_offset]
      if context == item:
        blacklisted = True
        break
    if not blacklisted and re.match(match_before, before) and re.match(match_after, after):
      out.append(string[ix : begin_offset])
      out.append(replacer(match))
    else:
      out.append(string[ix:end_offset])
    ix = end_offset
    begin_offset = haystack.find(needle, ix)
  out.append(string[ix : len(string)])
  return "".join(out)

def replaceRecursively(needle: str,
                       replacement: str,
                       match_before: str = "$|[^a-zA-Z0-9]",
                       match_after: str = "$|[^a-zA-Z0-9]"):
  files = subprocess.run(["grep", "-RIF", "-l", needle, "."], stdout=subprocess.PIPE)
  for f in files.stdout.splitlines():
    path = f.decode('utf8')
    with open(path, 'r') as source_file:
      contents = source_file.read()
    out = substitute(contents, needle, lambda x: replacement, match_before, match_after)
    with open(path, 'w') as source_file:
      source_file.write(out)

def isHiddenFile(path):
  return any(map(lambda x: len(x) > 1 and x.startswith('.'), path.split('/')[:-1]))

def isInExcludedDirectory(path):
  global excluded_directories
  normalized = "/".join(filter(lambda x: x != '.' and len(x) > 0, path.split('/')))
  for excl in excluded_directories:
    if normalized.startswith(excl):
      return True
  return False

def applyRecursively(func, command = ['find', '.', '-type', 'f']):
  files = subprocess.run(command, stdout=subprocess.PIPE)
  for f in files.stdout.splitlines():
    path = f.decode('utf8')
    if isHiddenFile(path) or isInExcludedDirectory(path):
      continue;
    func(path)

def gitMoveFile(path, needle, replacement):
  target = path.replace(needle, replacement)
  if target == path:
    return
  target_parent = '/'.join(target.split('/')[:-1])
  subprocess.run(['mkdir', '-p', target_parent])
  result = subprocess.run(["git", "mv", path, target])
  if result.returncode != 0:
    exit(result.returncode)

def replaceBitcoinIdentifier(occurence: str):
  if occurence == 'bitcoin':
    return 'unite'
  if occurence == 'BITCOIN':
    return 'UNITE'
  if occurence == 'Bitcoin':
    return 'UnitE'
  raise Exception("Don't know how to handle %s" % occurence)

def substituteBitcoin(path):
  with open(path, 'r') as source_file:
    contents = source_file.read()
  altered = substitute(contents, "bitcoin", replaceBitcoinIdentifier, case_sensitive = False, blacklist = substitution_blacklist)
  with open(path, 'w') as target_file:
    target_file.write(altered)

# String -> (String -> IO ())
def substituteAny(substitutions):
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

replaceRecursively("8333", "7182")
subprocess.run(['git', 'commit', '-am', 'Turned mainnet port 8333 into 7182'])

replaceRecursively("18333", "17182")
subprocess.run(['git', 'commit', '-am', 'Turned testnet port 18333 into 17182'])

replaceRecursively("BTC", "UNT", match_before = "$|[^a-ln-tv-zA-Z]")
subprocess.run(['git', 'commit', '-am', 'Changed currency token BTC to UNT'])

applyRecursively(lambda path: gitMoveFile(path, "bitcoin", "unite"))
subprocess.run(['git', 'commit', '-am', 'Moved paths containing "bitcoin" to respective "unite" paths'])

applyRecursively(substituteBitcoin, ['grep', '-RIFil', 'bitcoin', '.'])
subprocess.run(['git', 'commit', '-am', 'Renamed occurences of "bitcoin" to "unite"'])

applyRecursively(substituteAny(other_substitutions))
subprocess.run(['git', 'commit', '-am', 'Apply adjustments to tests and constants for name changes'])

applyRecursively(substituteAny(protocol_economics_substitutions))
subprocess.run(['git', 'commit', '-am', 'Apply protocol economics changes (max supply, reward, ...)'])

replaceRecursively("COIN", "UNIT")
subprocess.run(['git', 'commit', '-am', 'Changed identifier COIN to UNIT'])

replaceRecursively("CENT", "EEES")
subprocess.run(['git', 'commit', '-am', 'Changed identifier CENT to EEES'])
