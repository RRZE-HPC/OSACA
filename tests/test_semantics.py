#!/usr/bin/env python3
"""
Unit tests for Semantic Analysis
"""

import os
import unittest

from osaca.parser import AttrDict, ParserAArch64v81, ParserX86ATT
from osaca.semantics.kernel_dg import KernelDG
from osaca.semantics.hw_model import MachineModel
from osaca.semantics.semanticsAppender import SemanticsAppender


class TestSemanticTools(unittest.TestCase):
    def setUp(self):
        self.parser_x86 = ParserX86ATT()
        self.parser_AArch64 = ParserAArch64v81()
        with open(self._find_file('kernel-x86.s')) as f:
            code_x86 = f.read()
        with open(self._find_file('kernel-AArch64.s')) as f:
            code_AArch64 = f.read()
        self.kernel_x86 = self.parser_x86.parse_file(code_x86)
        self.kernel_AArch64 = self.parser_AArch64.parse_file(code_AArch64)

        self.machine_model_csl = MachineModel('csl')
        self.machine_model_tx2 = MachineModel('vulcan')
        self.semantics_csl = SemanticsAppender(self.machine_model_csl)
        self.semantics_tx2 = SemanticsAppender(self.machine_model_tx2)
        for i in range(len(self.kernel_x86)):
            self.semantics_csl.assign_src_dst(self.kernel_x86[i])
        for i in range(len(self.kernel_AArch64)):
            self.semantics_tx2.assign_src_dst(self.kernel_AArch64[i])

    ###########
    # Tests
    ###########

    def test_src_dst_assignment_x86(self):
        for instruction_form in self.kernel_x86:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form['operands'] is not None:
                    self.assertTrue('source' in instruction_form['operands'])
                    self.assertTrue('destination' in instruction_form['operands'])
                    self.assertTrue('src_dst' in instruction_form['operands'])

    def test_src_dst_assignment_AArch64(self):
        for instruction_form in self.kernel_AArch64:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form['operands'] is not None:
                    self.assertTrue('source' in instruction_form['operands'])
                    self.assertTrue('destination' in instruction_form['operands'])
                    self.assertTrue('src_dst' in instruction_form['operands'])

    def test_is_read_is_written_x86(self):
        # independent form HW model
        dag = KernelDG(self.kernel_x86, self.parser_x86, None)
        reg_rcx = AttrDict({'name': 'rcx'})
        reg_ymm1 = AttrDict({'name': 'ymm1'})

        instr_form_r_c = self.parser_x86.parse_line('vmovsd  %xmm0, (%r15,%rcx,8)')
        self.semantics_csl.assign_src_dst(instr_form_r_c)
        instr_form_non_r_c = self.parser_x86.parse_line('movl  %xmm0, (%r15,%rax,8)')
        self.semantics_csl.assign_src_dst(instr_form_non_r_c)
        instr_form_w_c = self.parser_x86.parse_line('movi $0x05ACA, %rcx')
        self.semantics_csl.assign_src_dst(instr_form_w_c)

        instr_form_rw_ymm_1 = self.parser_x86.parse_line('vinsertf128 $0x1, %xmm1, %ymm0, %ymm1')
        self.semantics_csl.assign_src_dst(instr_form_rw_ymm_1)
        instr_form_rw_ymm_2 = self.parser_x86.parse_line('vinsertf128 $0x1, %xmm0, %ymm1, %ymm1')
        self.semantics_csl.assign_src_dst(instr_form_rw_ymm_2)
        instr_form_r_ymm = self.parser_x86.parse_line('vmovapd %ymm1, %ymm0')
        self.semantics_csl.assign_src_dst(instr_form_r_ymm)

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
        dag = KernelDG(self.kernel_AArch64, self.parser_AArch64, None)
        reg_x1 = AttrDict({'prefix': 'x', 'name': '1'})
        reg_q1 = AttrDict({'prefix': 'q', 'name': '1'})
        reg_v1 = AttrDict({'prefix': 'v', 'name': '1', 'lanes': '2', 'shape': 'd'})
        regs = [reg_x1, reg_q1, reg_v1]

        instr_form_r_1 = self.parser_AArch64.parse_line('stp q1, q3, [x12, #192]')
        self.semantics_tx2.assign_src_dst(instr_form_r_1)
        instr_form_r_2 = self.parser_AArch64.parse_line('fadd v2.2d, v1.2d, v0.2d')
        self.semantics_tx2.assign_src_dst(instr_form_r_2)
        instr_form_w_1 = self.parser_AArch64.parse_line('ldr x0, [x0, #:got_lo12:q2c]')
        self.semantics_tx2.assign_src_dst(instr_form_w_1)
        instr_form_rw_1 = self.parser_AArch64.parse_line('fmul v1.2d, v1.2d, v0.2d')
        self.semantics_tx2.assign_src_dst(instr_form_rw_1)
        instr_form_rw_2 = self.parser_AArch64.parse_line('ldp q2, q4, [x1, #64]!')
        self.semantics_tx2.assign_src_dst(instr_form_rw_2)
        instr_form_rw_3 = self.parser_AArch64.parse_line('str x4, [x1], #64')
        self.semantics_tx2.assign_src_dst(instr_form_rw_3)
        instr_form_non_rw_1 = self.parser_AArch64.parse_line('adds x0, x11')
        self.semantics_tx2.assign_src_dst(instr_form_non_rw_1)

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSemanticTools)
    unittest.TextTestRunner(verbosity=2).run(suite)
