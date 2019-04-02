#!/usr/bin/env python3
# Copyright (c) 2019 The Unit-e developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/licenses/MIT.

import sys

from runner import Runner

if len(sys.argv) != 2:
    sys.exit("Usage: create_reference_data.py <label>")
label = sys.argv[1]

runner = Runner("unit-e")
runner.checkout_unit_e_clone()
runner.fetch_bitcoin()
runner.run_clonemachine()
runner.write_diff(label, expected=True, verbose=True)
