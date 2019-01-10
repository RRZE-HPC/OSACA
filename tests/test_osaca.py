#!/usr/bin/env python3

import sys
from io import StringIO
import os

import unittest

sys.path.insert(0, '..')
from osaca import osaca


class TestOsaca(unittest.TestCase):
    maxDiff = None

    @unittest.skip("Binary analysis is error prone and currently not working with FSF's objdump")
    def testIACABinary(self):
        curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        assembly = osaca.get_assembly_from_binary(curr_dir + '/testfiles/taxCalc-ivb-iaca')
        osa = osaca.OSACA('IVB', assembly)
        result = osa.generate_text_output()
        result = result[result.find('Port Binding in Cycles Per Iteration:'):]
        with open(curr_dir + '/test_osaca_iaca.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion.replace(' ', ''), result.replace(' ', ''))

    # Test ASM file with IACA marker in two lines
    def testIACAasm1(self):
        curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        with open(curr_dir + '/testfiles/taxCalc-ivb-iaca.S') as f:
            osa = osaca.OSACA('IVB', f.read())
        result = osa.generate_text_output()
        result = result[result.find('Port Binding in Cycles Per Iteration:'):]
        with open(curr_dir + '/test_osaca_iaca_asm.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion.replace(' ', ''), result.replace(' ', ''))

    # Test ASM file with IACA marker in four lines
    def testIACAasm2(self):
        curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        with open(curr_dir + '/testfiles/taxCalc-ivb-iaca2.S') as f:
            osa = osaca.OSACA('IVB', f.read())
        result = osa.generate_text_output()
        result = result[result.find('Port Binding in Cycles Per Iteration:'):]
        with open(curr_dir + '/test_osaca_iaca_asm.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion.replace(' ', ''), result.replace(' ', ''))
