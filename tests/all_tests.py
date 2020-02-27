#!/usr/bin/env python3

import sys
import unittest

sys.path[0:0] = ['.', '..']
suite = unittest.TestLoader().loadTestsFromNames(
    [
        'test_base_parser',
        'test_parser_x86att',
        'test_parser_AArch64v81',
        'test_marker_utils',
        'test_semantics',
        'test_frontend',
        'test_db_interface',
        'test_kerncraftAPI',
        'test_cli',
    ]
)

testresult = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if testresult.wasSuccessful() else 1)
