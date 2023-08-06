#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" autosys package """
# copyright (c) 2019 Michael Treanor
# https://www.github.com/skeptycal/autosys
# https://www.twitter.com/skeptycal

# `AutoSys` is licensed under the `MIT <https://opensource.org/licenses/MIT>`.

from __future__ import absolute_import, print_function
from _as_version import *
import os
import pathlib
import sys

# resolve absolute path of this script
SCRIPT_PATH = pathlib.Path(__file__).resolve().parents[0].as_posix()

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath('autosys'))


if True:  # import dependencies
    from matplotlib import colors


if __name__ == "__main__":  # CLI tests
    print(sys.version)
    # print(f"{SCRIPT_PATH=}")
    # print(f"{__file__=}")
    # print(f"{sys.path[0]=}")
