#!/usr/bin/env python3
# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.

import sys

from runner import Runner

if len(sys.argv) < 2 or len(sys.argv) > 3:
    sys.exit("Usage: create_reference_data.py <label> [bitcoin-branch]")
label = sys.argv[1]
bitcoin_branch = "0.17"
if len(sys.argv) == 3:
    bitcoin_branch = sys.argv[2]
runner = Runner("unit-e")
runner.checkout_unit_e_clone()
if bitcoin_branch:
    if not bitcoin_branch in ["0.17", "0.18"]:
        sys.exit("Unrecognized bitcoin branch: '{bitcoin_branch}'")
runner.fetch_bitcoin(bitcoin_branch)
runner.run_clonemachine()
runner.write_diff(label, expected=True, verbose=True)
