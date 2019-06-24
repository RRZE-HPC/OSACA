#!/usr/bin/env python3
"""
Unit tests for KernelDAG
"""

import os
import unittest

from osaca.dependency_finder import KernelDAG
from osaca.parser import AttrDict, ParserAArch64v81, ParserX86ATT


class TestDependencyFinder(unittest.TestCase):
    def setUp(self):
        self.parser_x86 = ParserX86ATT()
        self.parser_AArch64 = ParserAArch64v81()
        with open(self._find_file('kernel-x86.s')) as f:
            code_x86 = f.read()
        with open(self._find_file('kernel-AArch64.s')) as f:
            code_AArch64 = f.read()
        self.kernel_x86 = self.parser_x86.parse_file(code_x86)
        self.kernel_AArch64 = self.parser_AArch64.parse_file(code_AArch64)

    ###########
    # Tests
    ###########

    def test_is_read_is_written_x86(self):
        # independent form HW model
        dag = KernelDAG(self.kernel_x86, self.parser_x86, None)
        reg_rcx = AttrDict({'name': 'rcx'})
        reg_ymm1 = AttrDict({'name': 'ymm1'})

        instr_form_r_c = self.parser_x86.parse_line('vmovsd  %xmm0, (%r15,%rcx,8)')
        instr_form_non_r_c = self.parser_x86.parse_line('movl  %xmm0, (%r15,%rax,8)')
        instr_form_w_c = self.parser_x86.parse_line('movi $0x05ACA, %rcx')

        instr_form_rw_ymm_1 = self.parser_x86.parse_line('vinsertf128 $0x1, %xmm1, %ymm0, %ymm1')
        instr_form_rw_ymm_2 = self.parser_x86.parse_line('vinsertf128 $0x1, %xmm0, %ymm1, %ymm1')
        instr_form_r_ymm = self.parser_x86.parse_line('vmovapd %ymm1, %ymm0')

        self.assertTrue(dag.is_read(reg_rcx, instr_form_r_c))
        self.assertFalse(dag.is_read(reg_rcx, instr_form_non_r_c))
        self.assertFalse(dag.is_read(reg_rcx, instr_form_w_c))
        self.assertTrue(dag.is_written(reg_rcx, instr_form_w_c))
        self.assertFalse(dag.is_written(reg_rcx, instr_form_r_c))

        self.assertTrue(dag.is_read(reg_ymm1, instr_form_rw_ymm_1))
        self.assertTrue(dag.is_read(reg_ymm1, instr_form_rw_ymm_2))
        self.assertTrue(dag.is_read(reg_ymm1, instr_form_r_ymm))
        self.assertTrue(dag.is_written(reg_ymm1, instr_form_rw_ymm_1))
        self.assertTrue(dag.is_written(reg_ymm1, instr_form_rw_ymm_2))
        self.assertFalse(dag.is_written(reg_ymm1, instr_form_r_ymm))

    def test_is_read_is_written_AArch64(self):
        # independent form HW model
        dag = KernelDAG(self.kernel_AArch64, self.parser_AArch64, None)
        reg_x1 = AttrDict({'prefix': 'x', 'name': '1'})
        reg_q1 = AttrDict({'prefix': 'q', 'name': '1'})
        reg_v1 = AttrDict({'prefix': 'v', 'name': '1', 'lanes': '2', 'shape': 'd'})
        regs = [reg_x1, reg_q1, reg_v1]

        instr_form_r_1 = self.parser_AArch64.parse_line('stp q1, q3, [x12, #192]')
        instr_form_r_2 = self.parser_AArch64.parse_line('fadd v2.2d, v1.2d, v0.2d')
        instr_form_w_1 = self.parser_AArch64.parse_line('ldr x0, [x0, #:got_lo12:q2c]')
        instr_form_rw_1 = self.parser_AArch64.parse_line('fmul v1.2d, v1.2d, v0.2d')
        instr_form_rw_2 = self.parser_AArch64.parse_line('ldp q2, q4, [x1, #64]!')
        instr_form_rw_3 = self.parser_AArch64.parse_line('str x4, [x1], #64')
        instr_form_non_rw_1 = self.parser_AArch64.parse_line('adds x0, x11')

        for reg in regs:
            with self.subTest(reg=reg):
                self.assertTrue(dag.is_read(reg, instr_form_r_1))
                self.assertTrue(dag.is_read(reg, instr_form_r_2))
                self.assertTrue(dag.is_read(reg, instr_form_rw_1))
                self.assertTrue(dag.is_read(reg, instr_form_rw_2))
                self.assertTrue(dag.is_read(reg, instr_form_rw_3))
                self.assertFalse(dag.is_read(reg, instr_form_w_1))
                self.assertTrue(dag.is_written(reg, instr_form_rw_1))
                self.assertTrue(dag.is_written(reg, instr_form_rw_2))
                self.assertTrue(dag.is_written(reg, instr_form_rw_3))
                self.assertFalse(dag.is_written(reg, instr_form_non_rw_1))
                self.assertFalse(dag.is_written(reg, instr_form_non_rw_1))

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDependencyFinder)
    unittest.TextTestRunner(verbosity=2).run(suite)
