#!/usr/bin/env python3
"""
Unit tests for base assembly parser
"""

import os
import unittest

from osaca.parser import AttrDict, BaseParser


class TestBaseParser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        try:
            self.parser = BaseParser()
        except NotImplementedError:
            pass
        with open(self._find_file('triad_x86_iaca.s')) as f:
            self.triad_code = f.read()
        with open(self._find_file('triad_arm_iaca.s')) as f:
            self.triad_code_arm = f.read()
        with open(self._find_file('kernel_x86.s')) as f:
            self.x86_code = f.read()
        with open(self._find_file('kernel_aarch64.s')) as f:
            self.aarch64_code = f.read()

    ##################
    # Test
    ##################

    def test_parse_file(self):
        with self.assertRaises(NotImplementedError):
            self.parser.parse_file(self.triad_code)

    def test_parse_line(self):
        line_instruction = '\t\tlea       2(%rax,%rax), %ecx #12.9'
        with self.assertRaises(NotImplementedError):
            self.parser.parse_line(line_instruction)

    def test_parse_instruction(self):
        instr1 = '\t\tvcvtsi2ss %edx, %xmm2, %xmm2\t\t\t#12.27'
        with self.assertRaises(NotImplementedError):
            self.parser.parse_instruction(instr1)

    def test_register_funcs(self):
        reg_a1 = AttrDict({'name': 'rax'})
        reg_a2 = AttrDict({'name': 'eax'})
        register_string = 'v1.2d'
        with self.assertRaises(NotImplementedError):
            self.parser.is_reg_dependend_of(reg_a1, reg_a2)
        with self.assertRaises(NotImplementedError):
            self.parser.parse_register(register_string)
        with self.assertRaises(NotImplementedError):
            self.parser.is_gpr(reg_a1)
        with self.assertRaises(NotImplementedError):
            self.parser.is_vector_register(reg_a1)
        with self.assertRaises(NotImplementedError):
            self.parser.process_operand(reg_a1)
        with self.assertRaises(NotImplementedError):
            self.parser.get_full_reg_name(reg_a1)

    def test_normalize_imd(self):
        imd_hex_1 = {'value': '0x4f'}
        with self.assertRaises(NotImplementedError):
            self.parser.normalize_imd(imd_hex_1)

    def test_detect_ISA(self):
        self.assertEqual(BaseParser.detect_ISA(self.triad_code), 'x86')
        self.assertEqual(BaseParser.detect_ISA(self.triad_code_arm), 'aarch64')
        self.assertEqual(BaseParser.detect_ISA(self.x86_code), 'x86')
        self.assertEqual(BaseParser.detect_ISA(self.aarch64_code), 'aarch64')

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBaseParser)
    unittest.TextTestRunner(verbosity=2).run(suite)
