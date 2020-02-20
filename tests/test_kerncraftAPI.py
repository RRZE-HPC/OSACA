#!/usr/bin/env python3
"""
Unit tests for OSACA Kerncraft API
"""

import os
import unittest

from collections import OrderedDict

from osaca.api import KerncraftAPI
from osaca.parser import ParserAArch64v81, ParserX86ATT


class TestKerncraftAPI(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # set up parser and kernels
        self.parser_x86 = ParserX86ATT()
        self.parser_AArch64 = ParserAArch64v81()
        with open(self._find_file('triad_x86_iaca.s')) as f:
            self.code_x86 = f.read()
        with open(self._find_file('triad_arm_iaca.s')) as f:
            self.code_AArch64 = f.read()

    ###########
    # Tests
    ###########

    def test_kerncraft_API_x86(self):
        kapi = KerncraftAPI('csx', self.code_x86)

        kapi.create_output()
        self.assertEqual(kapi.get_unmatched_instruction_ratio(), 0.0)
        port_occupation = OrderedDict(
            [
                ('0', 1.25),
                ('0DV', 0.0),
                ('1', 1.25),
                ('2', 2.0),
                ('2D', 1.5),
                ('3', 2.0),
                ('3D', 1.5),
                ('4', 1.0),
                ('5', 0.75),
                ('6', 0.75),
                ('7', 0.0),
            ]
        )
        self.assertEqual(kapi.get_port_occupation_cycles(), port_occupation)
        self.assertEqual(kapi.get_total_throughput(), 2.0)
        # TODO: LCD would be 2 with OF flag LCD --> still to discuss
        self.assertEqual(kapi.get_latency(), (1.0, 8.0))

    def test_kerncraft_API_AArch64(self):
        kapi = KerncraftAPI('tx2', self.code_AArch64)

        kapi.create_output()
        self.assertEqual(kapi.get_unmatched_instruction_ratio(), 0.0)
        port_occupation = OrderedDict(
            [
                ('0', 34.0),
                ('0DV', 0.0),
                ('1', 34.0),
                ('1DV', 0.0),
                ('2', 2.0),
                ('3', 64.0),
                ('4', 64.0),
                ('5', 32.0),
            ]
        )
        self.assertEqual(kapi.get_port_occupation_cycles(), port_occupation)
        self.assertEqual(kapi.get_total_throughput(), 64.0)
        # TODO add missing latency values
        # self.assertEqual(kapi.get_latency(kernel), 20.0)

    ##################
    # Helper functions
    ##################

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'test_files', name)
        assert os.path.exists(name)
        return name


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKerncraftAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)
