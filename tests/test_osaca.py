#!/usr/bin/env python3

import sys
from io import StringIO
import os

import unittest

sys.path.insert(0, '..')
from osaca import osaca


class TestOsaca(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])

    @unittest.skip("Binary analysis is error prone and currently not working with FSF's objdump")
    def testIACABinary(self):
        assembly = osaca.get_assembly_from_binary(self.curr_dir + '/testfiles/taxCalc-ivb-iaca')
        osa = osaca.OSACA('IVB', assembly)
        result = osa.generate_text_output()
        result = result[result.find('Port Binding in Cycles Per Iteration:'):]
        with open(self.curr_dir + '/test_osaca_iaca.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion.replace(' ', ''), result.replace(' ', ''))

    # Test ASM file with IACA marker in two lines
    def testIACAasm1(self):
        with open(self.curr_dir + '/testfiles/taxCalc-ivb-iaca.S') as f:
            osa = osaca.OSACA('IVB', f.read())
        result = osa.generate_text_output()
        result = result[result.find('Port Binding in Cycles Per Iteration:'):]
        with open(self.curr_dir + '/test_osaca_iaca_asm.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion.replace(' ', ''), result.replace(' ', ''))

    # Test ASM file with IACA marker in four lines
    def testIACAasm2(self):
        with open(self.curr_dir + '/testfiles/taxCalc-ivb-iaca2.S') as f:
            osa = osaca.OSACA('IVB', f.read())
        result = osa.generate_text_output()
        result = result[result.find('Port Binding in Cycles Per Iteration:'):]
        with open(self.curr_dir + '/test_osaca_iaca_asm.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion.replace(' ', ''), result.replace(' ', ''))

    #@unittest.skip("Skip until required instructions are supported.")
    def test_asm_API(self):
        with open(self.curr_dir + '/testfiles/3d-7pt.icc.skx.avx512.iaca_marked.s') as f:
            osa = osaca.OSACA('SKX', f.read())

        text_output = osa.create_output()
        print(text_output)
        # Derived from IACA (and manually considering OSACAs equal distribution to ports)
        self.assertEqual(dict(osa.get_port_occupation_cycles()),
                         {'0': 4.0,
                          '0DV': 0.0,
                          '1': 3.5,
                          '2': 3.5,
                          '3': 3.5,
                          '4': 1.0,
                          '5': 4.5,
                          '6': 3.5,
                          '7': 0.0})
        # TODO consider frontend bottleneck -> 6.25 cy
        self.assertEqual(osa.get_total_throughput(),
                         4.5)
