#!/usr//bin/env python

import sys

import unittest


sys.path[0:0] = ['.', '..']
suite = unittest.TestLoader().loadTestsFromNames(
    [
        'test_osaca'
    ]
)

testresult = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if testresult.wasSuccessful() else 1)
