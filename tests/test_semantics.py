#!/usr/bin/env python3
"""
Unit tests for Semantic Analysis
"""

import os
import unittest
from subprocess import call

import networkx as nx

from osaca.parser import AttrDict, ParserAArch64v81, ParserX86ATT
from osaca.semantics import (INSTR_FLAGS, KernelDG, MachineModel,
                             ArchSemantics)


class TestSemanticTools(unittest.TestCase):
    MODULE_DATA_DIR = os.path.join(
        os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), 'osaca/data/'
    )
    USER_DATA_DIR = os.path.join(os.path.expanduser('~'), '.osaca/')

    @classmethod
    def setUpClass(self):
        # copy db files in user directory
        if not os.path.isdir(os.path.join(self.USER_DATA_DIR, 'data')):
            os.makedirs(os.path.join(self.USER_DATA_DIR, 'data'))
            call(['cp', '-r', self.MODULE_DATA_DIR, self.USER_DATA_DIR])
        # set up parser and kernels
        self.parser_x86 = ParserX86ATT()
        self.parser_AArch64 = ParserAArch64v81()
        with open(self._find_file('kernel-x86.s')) as f:
            self.code_x86 = f.read()
        with open(self._find_file('kernel-AArch64.s')) as f:
            self.code_AArch64 = f.read()
        self.kernel_x86 = self.parser_x86.parse_file(self.code_x86)
        self.kernel_AArch64 = self.parser_AArch64.parse_file(self.code_AArch64)

        # set up machine models
        self.machine_model_csx = MachineModel(
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'csx.yml')
        )
        self.machine_model_tx2 = MachineModel(
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'tx2.yml')
        )
        self.semantics_csx = ArchSemantics(
            self.machine_model_csx, path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'isa/x86.yml')
        )
        self.semantics_tx2 = ArchSemantics(
            self.machine_model_tx2,
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'isa/aarch64.yml'),
        )
        self.machine_model_zen = MachineModel(arch='zen1')

        for i in range(len(self.kernel_x86)):
            self.semantics_csx.assign_src_dst(self.kernel_x86[i])
            self.semantics_csx.assign_tp_lt(self.kernel_x86[i])
        for i in range(len(self.kernel_AArch64)):
            self.semantics_tx2.assign_src_dst(self.kernel_AArch64[i])
            self.semantics_tx2.assign_tp_lt(self.kernel_AArch64[i])

    ###########
    # Tests
    ###########

    def test_creation_by_name(self):
        try:
            tmp_mm = MachineModel(arch='CSX')
            ArchSemantics(tmp_mm)
        except ValueError:
            self.fail()

    def test_src_dst_assignment_x86(self):
        for instruction_form in self.kernel_x86:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form['semantic_operands'] is not None:
                    self.assertTrue('source' in instruction_form['semantic_operands'])
                    self.assertTrue('destination' in instruction_form['semantic_operands'])
                    self.assertTrue('src_dst' in instruction_form['semantic_operands'])

    def test_src_dst_assignment_AArch64(self):
        for instruction_form in self.kernel_AArch64:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form['semantic_operands'] is not None:
                    self.assertTrue('source' in instruction_form['semantic_operands'])
                    self.assertTrue('destination' in instruction_form['semantic_operands'])
                    self.assertTrue('src_dst' in instruction_form['semantic_operands'])

    def test_tp_lt_assignment_x86(self):
        self.assertTrue('ports' in self.machine_model_csx)
        port_num = len(self.machine_model_csx['ports'])
        for instruction_form in self.kernel_x86:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue('throughput' in instruction_form)
                self.assertTrue('latency' in instruction_form)
                self.assertIsInstance(instruction_form['port_pressure'], list)
                self.assertEqual(len(instruction_form['port_pressure']), port_num)

    def test_tp_lt_assignment_AArch64(self):
        self.assertTrue('ports' in self.machine_model_tx2)
        port_num = len(self.machine_model_tx2['ports'])
        for instruction_form in self.kernel_AArch64:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue('throughput' in instruction_form)
                self.assertTrue('latency' in instruction_form)
                self.assertIsInstance(instruction_form['port_pressure'], list)
                self.assertEqual(len(instruction_form['port_pressure']), port_num)

    def test_kernelDG_x86(self):
        #
        #  4
        #   \___>6__>7
        #   /
        #  3
        #     5_______>9
        #
        dg = KernelDG(self.kernel_x86, self.parser_x86, self.machine_model_csx)
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=3))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=3)), 6)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=4))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=4)), 6)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=5))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=5)), 9)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=6))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=6)), 7)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=7))), 0)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=8))), 0)
        with self.assertRaises(ValueError):
            dg.get_dependent_instruction_forms()

    def test_kernelDG_AArch64(self):
        dg = KernelDG(self.kernel_AArch64, self.parser_AArch64, self.machine_model_tx2)
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=3)), {7, 8})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=4)), {9, 10})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=5)), {6, 7, 8})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=6)), {9, 10})
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=7)), 13)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=8)), 14)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=9)), 16)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=10)), 17)
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=11)), {13, 14})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=12)), {16, 17})
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=13)), 15)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=14)), 15)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=15))), 0)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=16)), 18)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=17)), 18)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=18))), 0)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=19))), 0)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=20))), 0)
        with self.assertRaises(ValueError):
            dg.get_dependent_instruction_forms()

    def test_hidden_load(self):
        machine_model_hld = MachineModel(
            path_to_yaml=self._find_file('hidden_load_machine_model.yml')
        )
        self.assertTrue(machine_model_hld.has_hidden_loads())
        semantics_hld = ArchSemantics(machine_model_hld)
        kernel_hld = self.parser_x86.parse_file(self.code_x86)
        kernel_hld_2 = self.parser_x86.parse_file(self.code_x86)
        kernel_hld_2 = self.parser_x86.parse_file(self.code_x86)[-3:]
        kernel_hld_3 = self.parser_x86.parse_file(self.code_x86)[5:8]
        semantics_hld.add_semantics(kernel_hld)
        semantics_hld.add_semantics(kernel_hld_2)
        semantics_hld.add_semantics(kernel_hld_3)

        num_hidden_loads = len([x for x in kernel_hld if INSTR_FLAGS.HIDDEN_LD in x['flags']])
        num_hidden_loads_2 = len([x for x in kernel_hld_2 if INSTR_FLAGS.HIDDEN_LD in x['flags']])
        num_hidden_loads_3 = len([x for x in kernel_hld_3 if INSTR_FLAGS.HIDDEN_LD in x['flags']])
        self.assertEqual(num_hidden_loads, 1)
        self.assertEqual(num_hidden_loads_2, 0)
        self.assertEqual(num_hidden_loads_3, 1)

    def test_cyclic_dag(self):
        dg = KernelDG(self.kernel_x86, self.parser_x86, self.machine_model_csx)
        dg.dg.add_edge(100, 101, latency=1.0)
        dg.dg.add_edge(101, 102, latency=2.0)
        dg.dg.add_edge(102, 100, latency=3.0)
        with self.assertRaises(NotImplementedError):
            dg.get_critical_path()
        with self.assertRaises(NotImplementedError):
            dg.get_loopcarried_dependencies()

    def test_loop_carried_dependency_x86(self):
        lcd_id = 8
        lcd_id2 = 9
        dg = KernelDG(self.kernel_x86, self.parser_x86, self.machine_model_csx)
        lc_deps = dg.get_loopcarried_dependencies()
        self.assertEqual(len(lc_deps), 2)
        # ID 8
        self.assertEqual(
            lc_deps[lcd_id]['root'], dg.dg.nodes(data=True)[lcd_id]['instruction_form']
        )
        self.assertEqual(len(lc_deps[lcd_id]['dependencies']), 1)
        self.assertEqual(
            lc_deps[lcd_id]['dependencies'][0], dg.dg.nodes(data=True)[lcd_id]['instruction_form']
        )
        # ID 9  ursprünglich ID 5 mit LCD zu ID 5 (len=1)
        # TODO discuss
        self.assertEqual(
            lc_deps[lcd_id2]['root'], dg.dg.nodes(data=True)[lcd_id2]['instruction_form']
        )
        self.assertEqual(len(lc_deps[lcd_id2]['dependencies']), 2)
        self.assertEqual(
            lc_deps[lcd_id2]['dependencies'][1],
            dg.dg.nodes(data=True)[lcd_id2]['instruction_form'],
        )

    def test_is_read_is_written_x86(self):
        # independent form HW model
        dag = KernelDG(self.kernel_x86, self.parser_x86, None)
        reg_rcx = AttrDict({'name': 'rcx'})
        reg_ymm1 = AttrDict({'name': 'ymm1'})

        instr_form_r_c = self.parser_x86.parse_line('vmovsd  %xmm0, (%r15,%rcx,8)')
        self.semantics_csx.assign_src_dst(instr_form_r_c)
        instr_form_non_r_c = self.parser_x86.parse_line('movl  %xmm0, (%r15,%rax,8)')
        self.semantics_csx.assign_src_dst(instr_form_non_r_c)
        instr_form_w_c = self.parser_x86.parse_line('movi $0x05ACA, %rcx')
        self.semantics_csx.assign_src_dst(instr_form_w_c)

        instr_form_rw_ymm_1 = self.parser_x86.parse_line('vinsertf128 $0x1, %xmm1, %ymm0, %ymm1')
        self.semantics_csx.assign_src_dst(instr_form_rw_ymm_1)
        instr_form_rw_ymm_2 = self.parser_x86.parse_line('vinsertf128 $0x1, %xmm0, %ymm1, %ymm1')
        self.semantics_csx.assign_src_dst(instr_form_rw_ymm_2)
        instr_form_r_ymm = self.parser_x86.parse_line('vmovapd %ymm1, %ymm0')
        self.semantics_csx.assign_src_dst(instr_form_r_ymm)

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
        reg_w1 = AttrDict({'prefix': 'w', 'name': '1'})
        reg_d1 = AttrDict({'prefix': 'd', 'name': '1'})
        reg_q1 = AttrDict({'prefix': 'q', 'name': '1'})
        reg_v1 = AttrDict({'prefix': 'v', 'name': '1', 'lanes': '2', 'shape': 'd'})
        regs = [reg_d1, reg_q1, reg_v1]
        regs_gp = [reg_w1, reg_x1]

        instr_form_r_1 = self.parser_AArch64.parse_line('stp q1, q3, [x12, #192]')
        self.semantics_tx2.assign_src_dst(instr_form_r_1)
        instr_form_r_2 = self.parser_AArch64.parse_line('fadd v2.2d, v1.2d, v0.2d')
        self.semantics_tx2.assign_src_dst(instr_form_r_2)
        instr_form_w_1 = self.parser_AArch64.parse_line('ldr d1, [x1, #:got_lo12:q2c]')
        self.semantics_tx2.assign_src_dst(instr_form_w_1)
        instr_form_non_w_1 = self.parser_AArch64.parse_line('ldr x1, [x1, #:got_lo12:q2c]')
        self.semantics_tx2.assign_src_dst(instr_form_non_w_1)
        instr_form_rw_1 = self.parser_AArch64.parse_line('fmul v1.2d, v1.2d, v0.2d')
        self.semantics_tx2.assign_src_dst(instr_form_rw_1)
        instr_form_rw_2 = self.parser_AArch64.parse_line('ldp q2, q4, [x1, #64]!')
        self.semantics_tx2.assign_src_dst(instr_form_rw_2)
        instr_form_rw_3 = self.parser_AArch64.parse_line('str x4, [x1], #64')
        self.semantics_tx2.assign_src_dst(instr_form_rw_3)
        instr_form_non_rw_1 = self.parser_AArch64.parse_line('adds x1, x11')
        self.semantics_tx2.assign_src_dst(instr_form_non_rw_1)

        for reg in regs:
            with self.subTest(reg=reg):
                self.assertTrue(dag.is_read(reg, instr_form_r_1))
                self.assertTrue(dag.is_read(reg, instr_form_r_2))
                self.assertTrue(dag.is_read(reg, instr_form_rw_1))
                self.assertFalse(dag.is_read(reg, instr_form_rw_2))
                self.assertFalse(dag.is_read(reg, instr_form_rw_3))
                self.assertFalse(dag.is_read(reg, instr_form_w_1))
                self.assertTrue(dag.is_written(reg, instr_form_w_1))
                self.assertTrue(dag.is_written(reg, instr_form_rw_1))
                self.assertFalse(dag.is_written(reg, instr_form_non_w_1))
                self.assertFalse(dag.is_written(reg, instr_form_rw_2))
                self.assertFalse(dag.is_written(reg, instr_form_rw_3))
                self.assertFalse(dag.is_written(reg, instr_form_non_rw_1))
                self.assertFalse(dag.is_written(reg, instr_form_non_rw_1))
        for reg in regs_gp:
            with self.subTest(reg=reg):
                self.assertFalse(dag.is_read(reg, instr_form_r_1))
                self.assertFalse(dag.is_read(reg, instr_form_r_2))
                self.assertFalse(dag.is_read(reg, instr_form_rw_1))
                self.assertTrue(dag.is_read(reg, instr_form_rw_2))
                self.assertTrue(dag.is_read(reg, instr_form_rw_3))
                self.assertTrue(dag.is_read(reg, instr_form_w_1))
                self.assertFalse(dag.is_written(reg, instr_form_w_1))
                self.assertFalse(dag.is_written(reg, instr_form_rw_1))
                self.assertTrue(dag.is_written(reg, instr_form_non_w_1))
                self.assertTrue(dag.is_written(reg, instr_form_rw_2))
                self.assertTrue(dag.is_written(reg, instr_form_rw_3))
                self.assertTrue(dag.is_written(reg, instr_form_non_rw_1))
                self.assertTrue(dag.is_written(reg, instr_form_non_rw_1))

    def test_invalid_MachineModel(self):
        with self.assertRaises(ValueError):
            MachineModel()
        with self.assertRaises(ValueError):
            MachineModel(arch='CSX', path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'csx.yml'))
        with self.assertRaises(FileNotFoundError):
            MachineModel(arch='THE_MACHINE')
        with self.assertRaises(FileNotFoundError):
            MachineModel(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, 'THE_MACHINE.yml'))

    def test_MachineModel_getter(self):
        sample_operands = [
            {
                'memory': {
                    'offset': None,
                    'base': {'name': 'r12'},
                    'index': {'name': 'rcx'},
                    'scale': 8,
                }
            }
        ]
        self.assertIsNone(self.machine_model_csx.get_instruction('GETRESULT', sample_operands))
        self.assertIsNone(self.machine_model_tx2.get_instruction('GETRESULT', sample_operands))

        self.assertEqual(self.machine_model_csx.get_arch(), 'csx')
        self.assertEqual(self.machine_model_tx2.get_arch(), 'tx2')

        self.assertEqual(self.machine_model_csx.get_ISA(), 'x86')
        self.assertEqual(self.machine_model_tx2.get_ISA(), 'aarch64')

        ports_csx = ['0', '0DV', '1', '2', '2D', '3', '3D', '4', '5', '6', '7']
        data_ports_csx = ['2D', '3D']
        self.assertEqual(self.machine_model_csx.get_ports(), ports_csx)
        self.assertEqual(self.machine_model_csx.get_data_ports(), data_ports_csx)

        self.assertFalse(self.machine_model_tx2.has_hidden_loads())

        self.assertEqual(MachineModel.get_isa_for_arch('CSX'), 'x86')
        self.assertEqual(MachineModel.get_isa_for_arch('tX2'), 'aarch64')
        with self.assertRaises(ValueError):
            self.assertIsNone(MachineModel.get_isa_for_arch('THE_MACHINE'))

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
