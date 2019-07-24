#!/usr/bin/env python3
"""
Unit tests for Semantic Analysis
"""

import networkx as nx
import os
import unittest

from osaca.frontend import Frontend
from osaca.parser import AttrDict, ParserAArch64v81, ParserX86ATT
from osaca.semantics.hw_model import MachineModel
from osaca.semantics.kernel_dg import KernelDG
from osaca.semantics.semanticsAppender import SemanticsAppender


class TestSemanticTools(unittest.TestCase):
    MODULE_DATA_DIR = os.path.join(
        os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), 'osaca/data/'
    )

    def setUp(self):
        # set up parser and kernels
        self.parser_x86 = ParserX86ATT()
        self.parser_AArch64 = ParserAArch64v81()
        with open(self._find_file('kernel-x86.s')) as f:
            code_x86 = f.read()
        with open(self._find_file('kernel-AArch64.s')) as f:
            code_AArch64 = f.read()
        self.kernel_x86 = self.parser_x86.parse_file(code_x86)
        self.kernel_AArch64 = self.parser_AArch64.parse_file(code_AArch64)

        # set up machine models
        self.machine_model_csl = MachineModel(
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'csl.yml')
        )
        self.machine_model_tx2 = MachineModel(
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'vulcan.yml')
        )
        self.semantics_csl = SemanticsAppender(
            self.machine_model_csl, path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'isa/x86.yml')
        )
        self.semantics_tx2 = SemanticsAppender(
            self.machine_model_tx2,
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'isa/AArch64.yml'),
        )
        for i in range(len(self.kernel_x86)):
            self.semantics_csl.assign_src_dst(self.kernel_x86[i])
            self.semantics_csl.assign_tp_lt(self.kernel_x86[i])
        for i in range(len(self.kernel_AArch64)):
            self.semantics_tx2.assign_src_dst(self.kernel_AArch64[i])
            self.semantics_tx2.assign_tp_lt(self.kernel_AArch64[i])

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

    def test_tp_lt_assignment_x86(self):
        port_num = len(self.machine_model_csl['ports'])
        for instruction_form in self.kernel_x86:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue('throughput' in instruction_form)
                self.assertTrue('latency' in instruction_form)
                self.assertIsInstance(instruction_form['port_pressure'], list)
                self.assertEqual(len(instruction_form['port_pressure']), port_num)

    def test_tp_lt_assignment_AArch64(self):
        port_num = len(self.machine_model_tx2['ports'])
        for instruction_form in self.kernel_AArch64:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue('throughput' in instruction_form)
                self.assertTrue('latency' in instruction_form)
                self.assertIsInstance(instruction_form['port_pressure'], list)
                self.assertEqual(len(instruction_form['port_pressure']), port_num)

    def test_kernelDG_x86(self):
        #
        #  3
        #   \___>5__>6
        #   /
        #  2
        #     4_______>8
        #
        dg = KernelDG(self.kernel_x86, self.parser_x86, self.machine_model_csl)
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=2))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=2)), 5)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=3))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=3)), 5)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=4))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=4)), 8)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=5))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=5)), 6)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=6))), 0)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=7))), 0)

        fe = Frontend(arch='CSL')
        fe.print_throughput_analysis(self.kernel_x86)
        fe.print_latency_analysis(dg.get_critical_path())

    def test_kernelDG_AArch64(self):
        dg = KernelDG(self.kernel_AArch64, self.parser_AArch64, self.machine_model_tx2)
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=2)), {6, 7})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=3)), {8, 9})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=4)), {6, 7})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=5)), {8, 9})
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=6)), 12)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=7)), 13)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=8)), 15)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=9)), 16)
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=10)), {12, 13})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=11)), {15, 16})
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=12)), 14)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=13)), 14)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=14))), 0)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=15)), 17)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=16)), 17)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=17))), 0)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=18))), 0)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=19))), 0)

        fe = Frontend(arch='vulcan')
        fe.print_throughput_analysis(self.kernel_AArch64)
        fe.print_latency_analysis(dg.get_critical_path())

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
