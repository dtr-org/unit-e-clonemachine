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
from pathlib import Path
import yaml

class Processor:
    def __init__(self, config):
        self.config = config

    def to_lower(self, s: str) -> str:
        return s.translate(str.maketrans(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'abcdefghijklmnopqrstuvwxyz'
        ))

    def substitute(self, string: str,
                needle: str,
                replacer: Callable[[str], str],
                match_before: str = "",
                match_after: str = "",
                case_sensitive: bool = True,
                blacklist: Sequence[str] = []) -> str:
        haystack = string if case_sensitive else self.to_lower(string)
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
                item_haystack = item if case_sensitive else self.to_lower(item)
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

    def replace_recursively(self, needle: str,
                            replacement: str,
                            match_before: str = "$|[^a-zA-Z0-9]",
                            match_after: str = "$|[^a-zA-Z0-9]"):
        files = subprocess.run(["git", "grep", "-l", needle], stdout=subprocess.PIPE)
        for f in files.stdout.splitlines():
            path = f.decode('utf8')
            if self.is_hidden_file(path) or self.is_in_excluded_path(path):
                continue
            with open(path, 'r') as source_file:
                contents = source_file.read()
            out = self.substitute(contents, needle, lambda x: replacement, match_before, match_after)
            with open(path, 'w') as source_file:
                source_file.write(out)

    def replace_in_file(self, path: str,
                        needle: str,
                        replacement: str,
                        match_before: str = "$|[^a-zA-Z0-9]",
                        match_after: str = "$|[^a-zA-Z0-9]"):
        if not os.path.exists(path):
            print(f"WARNING: File '{path}' does not exist for replacement of '{needle}' by '{replacement}'",
                  file=sys.stderr)
            return
        with open(path, 'r') as source_file:
            contents = source_file.read()
        out = self.substitute(contents, needle, lambda x: replacement, match_before, match_after)
        with open(path, 'w') as source_file:
            source_file.write(out)

    def is_hidden_file(self, path):
        return any(map(lambda x: len(x) > 1 and x.startswith('.'), path.split('/')[:-1]))

    def is_in_excluded_path(self, path):
        normalized = "/".join(filter(lambda x: x != '.' and len(x) > 0, path.split('/')))
        for excl in self.config.excluded_paths:
            if normalized.startswith(excl):
                return True
        return False

    def apply_recursively(self, func, command=['find', '.', '-type', 'f']):
        files = subprocess.run(command, stdout=subprocess.PIPE)
        for f in files.stdout.splitlines():
            path = f.decode('utf8')
            if self.is_hidden_file(path) or self.is_in_excluded_path(path):
                continue
            func(path)

    def remove_trailing_whitespace(self, file_pattern):
        if sys.platform == "linux":
            sed = "sed"
        elif sys.platform == "darwin":
            sed = "gsed"
        else:
            raise RuntimeError(f"Unsupported platform: '{sys.platform}'")
        subprocess.run(['find', '.', '-type', 'f', '-name', file_pattern,
        '-exec', sed, '--in-place', r's/[[:space:]]\+$//', '{}', '+'])

    def git_move_file(self, path, needle, replacement):
        target = path.replace(needle, replacement)
        if target == path:
            return
        target_parent = '/'.join(target.split('/')[:-1])
        subprocess.run(['mkdir', '-p', target_parent])
        result = subprocess.run(["git", "mv", path, target])
        if result.returncode != 0:
            exit(result.returncode)

    def replace_bitcoin_identifier(self, occurence: str):
        if occurence == 'bitcoin':
            return 'unite'
        if occurence == 'BITCOIN':
            return 'UNIT-E'
        if occurence == 'Bitcoin':
            return 'Unit-e'
        raise Exception(f"Don't know how to handle {occurence}")

    def replace_bitcoin_core_identifier(self, occurence: str):
        if occurence in ['bitcoin core', 'Bitcoin Core', 'Bitcoin core']:
            return 'unit-e'
        raise Exception(f"Don't know how to handle {occurence}")

    def substitute_bitcoin_identifier_in_file(self, path):
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
            contents = self.substitute(string = contents,
                                needle = substitution[0],
                                match_after = substitution[1],
                                replacer = lambda occurence: substitution[2],
                                case_sensitive=True,
                                blacklist = self.config.substitution_blacklist)
        altered = self.substitute(string = contents,
                            needle = "bitcoin",
                            replacer = self.replace_bitcoin_identifier,
                            case_sensitive=False,
                            blacklist=self.config.substitution_blacklist)
        with open(path, 'w') as target_file:
            target_file.write(altered)

    def substitute_bitcoin_core_identifier_in_file(self, path):
        with open(path, 'r') as source_file:
            contents = source_file.read()
        altered = self.substitute(string = contents,
                            needle = "bitcoin core",
                            replacer = self.replace_bitcoin_core_identifier,
                            case_sensitive=False,
                            blacklist=self.config.substitution_blacklist)
        with open(path, 'w') as target_file:
            target_file.write(altered)

    def substitute_any(self, substitutions):
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

    def read_config(self, branch: str, config_key: str, initial_value: List[str]) -> set:
        combined_value = set(initial_value)
        if branch:
            result = subprocess.run(['git', 'show', branch + ':.clonemachine'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                config = yaml.safe_load(result.stdout.decode('utf-8'))
                combined_value = set(config[config_key]).union(initial_value)
        return combined_value

    def appropriate_files(self, branch):
        for file in self.read_config(branch, "appropriated_files", self.config.appropriated_files):
            subprocess.run(['git', 'checkout', branch, file])
        result = subprocess.run(['git', 'rev-parse', branch], stdout=subprocess.PIPE)
        return result.stdout.decode('utf-8').rstrip()

    def remove_files(self, branch):
        for file in self.read_config(branch, "removed_files", self.config.removed_files):
            if os.path.exists(file):
                subprocess.run(['git', 'rm', file])
