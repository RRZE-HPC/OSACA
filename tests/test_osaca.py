#!/usr/bin/env python3

import sys
from io import StringIO
import os

import unittest

sys.path.insert(0, '..')
from osaca.osaca import Osaca

class TestOsaca(unittest.TestCase):
    def testIACABinary(self):
        out = StringIO()
        curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        osa = Osaca('IVB', curr_dir+'/testfiles/taxCalc-ivb-iaca', out)
        osa.inspect_with_iaca()
        result = out.getvalue()
        result = '\n'.join(result.split('\n')[-27:])
        with open(curr_dir+'/test_osaca_iaca.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion, result)
    
    # Test ASM file with IACA marker in two lines
    def testIACAasm1(self):
        out = StringIO()
        curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        osa = Osaca('IVB', curr_dir+'/testfiles/taxCalc-ivb-iaca.S', out)
        osa.inspect_with_iaca()
        result = out.getvalue()
        result = '\n'.join(result.split('\n')[-27:])
        with open(curr_dir+'/test_osaca_iaca_asm.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion, result)

    # Test ASM file with IACA marker in four lines
    def testIACAasm2(self):
        out = StringIO()
        curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        osa = Osaca('IVB', curr_dir+'/testfiles/taxCalc-ivb-iaca2.S', out)
        osa.inspect_with_iaca()
        result = out.getvalue()
        result = '\n'.join(result.split('\n')[-27:])
        with open(curr_dir+'/test_osaca_iaca_asm.out', encoding='utf-8') as f:
            assertion = f.read()
        self.assertEqual(assertion, result)
