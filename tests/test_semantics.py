#!/usr/bin/env python3
"""
Unit tests for Semantic Analysis
"""

import os
import unittest
import time
from copy import deepcopy

import networkx as nx
from osaca.osaca import get_unmatched_instruction_ratio
from osaca.parser import ParserAArch64, ParserX86ATT, ParserX86Intel
from osaca.semantics import (
    INSTR_FLAGS,
    ArchSemantics,
    ISASemantics,
    KernelDG,
    MachineModel,
    reduce_to_section,
)
from osaca.parser.register import RegisterOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.identifier import IdentifierOperand


class TestSemanticTools(unittest.TestCase):
    MODULE_DATA_DIR = os.path.join(
        os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), "osaca/data/"
    )

    @classmethod
    def setUpClass(cls):
        # set up parser and kernels
        cls.parser_x86_att = ParserX86ATT()
        cls.parser_x86_intel = ParserX86Intel()
        cls.parser_AArch64 = ParserAArch64()
        with open(cls._find_file("kernel_x86.s")) as f:
            cls.code_x86 = f.read()
        with open(cls._find_file("kernel_x86_memdep.s")) as f:
            cls.code_x86_memdep = f.read()
        with open(cls._find_file("kernel_x86_long_LCD.s")) as f:
            cls.code_x86_long_LCD = f.read()
        with open(cls._find_file("kernel_x86_intel.s")) as f:
            cls.code_x86_intel = f.read()
        with open(cls._find_file("kernel_x86_intel_memdep.s")) as f:
            cls.code_x86_intel_memdep = f.read()
        with open(cls._find_file("kernel_aarch64_memdep.s")) as f:
            cls.code_aarch64_memdep = f.read()
        with open(cls._find_file("kernel_aarch64.s")) as f:
            cls.code_AArch64 = f.read()
        with open(cls._find_file("kernel_aarch64_sve.s")) as f:
            cls.code_AArch64_SVE = f.read()
        with open(cls._find_file("kernel_aarch64_deps.s")) as f:
            cls.code_AArch64_deps = f.read()
        with open(cls._find_file("mops_aarch64.s")) as f:
            cls.mops_1_code = f.read()
        cls.mops_2_code = cls.mops_1_code.replace("//ALT1 ", "")

        cls.kernel_x86 = reduce_to_section(
            cls.parser_x86_att.parse_file(cls.code_x86), cls.parser_x86_att
        )
        cls.kernel_x86_memdep = reduce_to_section(
            cls.parser_x86_att.parse_file(cls.code_x86_memdep), cls.parser_x86_att
        )
        cls.kernel_x86_long_LCD = reduce_to_section(
            cls.parser_x86_att.parse_file(cls.code_x86_long_LCD), cls.parser_x86_att
        )
        cls.kernel_x86_intel = reduce_to_section(
            cls.parser_x86_intel.parse_file(cls.code_x86_intel), cls.parser_x86_intel
        )
        cls.kernel_x86_intel_memdep = reduce_to_section(
            cls.parser_x86_intel.parse_file(cls.code_x86_intel_memdep), cls.parser_x86_intel
        )
        cls.kernel_AArch64 = reduce_to_section(
            cls.parser_AArch64.parse_file(cls.code_AArch64), cls.parser_AArch64
        )
        cls.kernel_aarch64_memdep = reduce_to_section(
            cls.parser_AArch64.parse_file(cls.code_aarch64_memdep), cls.parser_AArch64
        )
        cls.kernel_aarch64_SVE = reduce_to_section(
            cls.parser_AArch64.parse_file(cls.code_AArch64_SVE), cls.parser_AArch64
        )
        cls.kernel_aarch64_deps = reduce_to_section(
            cls.parser_AArch64.parse_file(cls.code_AArch64_deps), cls.parser_AArch64
        )

        # set up machine models
        cls.machine_model_csx = MachineModel(
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "csx.yml")
        )
        cls.machine_model_tx2 = MachineModel(
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "tx2.yml")
        )
        cls.machine_model_a64fx = MachineModel(
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "a64fx.yml")
        )
        cls.semantics_x86 = ISASemantics(cls.parser_x86_att)
        cls.semantics_csx = ArchSemantics(
            cls.parser_x86_att,
            cls.machine_model_csx,
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "isa/x86.yml"),
        )
        cls.semantics_x86_intel = ISASemantics(cls.parser_x86_intel)
        cls.semantics_csx_intel = ArchSemantics(
            cls.parser_x86_intel,
            cls.machine_model_csx,
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "isa/x86.yml"),
        )
        cls.semantics_aarch64 = ISASemantics(cls.parser_AArch64)
        cls.semantics_tx2 = ArchSemantics(
            cls.parser_AArch64,
            cls.machine_model_tx2,
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "isa/aarch64.yml"),
        )
        cls.semantics_a64fx = ArchSemantics(
            cls.parser_AArch64,
            cls.machine_model_a64fx,
            path_to_yaml=os.path.join(cls.MODULE_DATA_DIR, "isa/aarch64.yml"),
        )
        cls.machine_model_zen = MachineModel(arch="zen1")

        cls.semantics_csx.normalize_instruction_forms(cls.kernel_x86)
        for i in range(len(cls.kernel_x86)):
            cls.semantics_csx.assign_src_dst(cls.kernel_x86[i])
            cls.semantics_csx.assign_tp_lt(cls.kernel_x86[i])
        cls.semantics_csx.normalize_instruction_forms(cls.kernel_x86_memdep)
        for i in range(len(cls.kernel_x86_memdep)):
            cls.semantics_csx.assign_src_dst(cls.kernel_x86_memdep[i])
            cls.semantics_csx.assign_tp_lt(cls.kernel_x86_memdep[i])
        cls.semantics_csx.normalize_instruction_forms(cls.kernel_x86_long_LCD)
        for i in range(len(cls.kernel_x86_long_LCD)):
            cls.semantics_csx.assign_src_dst(cls.kernel_x86_long_LCD[i])
            cls.semantics_csx.assign_tp_lt(cls.kernel_x86_long_LCD[i])
        cls.semantics_csx_intel.normalize_instruction_forms(cls.kernel_x86_intel)
        for i in range(len(cls.kernel_x86_intel)):
            cls.semantics_csx_intel.assign_src_dst(cls.kernel_x86_intel[i])
            cls.semantics_csx_intel.assign_tp_lt(cls.kernel_x86_intel[i])
        cls.semantics_csx_intel.normalize_instruction_forms(cls.kernel_x86_intel_memdep)
        for i in range(len(cls.kernel_x86_intel_memdep)):
            cls.semantics_csx_intel.assign_src_dst(cls.kernel_x86_intel_memdep[i])
            cls.semantics_csx_intel.assign_tp_lt(cls.kernel_x86_intel_memdep[i])
        cls.semantics_tx2.normalize_instruction_forms(cls.kernel_AArch64)
        for i in range(len(cls.kernel_AArch64)):
            cls.semantics_tx2.assign_src_dst(cls.kernel_AArch64[i])
            cls.semantics_tx2.assign_tp_lt(cls.kernel_AArch64[i])
        cls.semantics_tx2.normalize_instruction_forms(cls.kernel_aarch64_memdep)
        for i in range(len(cls.kernel_aarch64_memdep)):
            cls.semantics_tx2.assign_src_dst(cls.kernel_aarch64_memdep[i])
            cls.semantics_tx2.assign_tp_lt(cls.kernel_aarch64_memdep[i])
        cls.semantics_a64fx.normalize_instruction_forms(cls.kernel_aarch64_SVE)
        for i in range(len(cls.kernel_aarch64_SVE)):
            cls.semantics_a64fx.assign_src_dst(cls.kernel_aarch64_SVE[i])
            cls.semantics_a64fx.assign_tp_lt(cls.kernel_aarch64_SVE[i])
        cls.semantics_a64fx.normalize_instruction_forms(cls.kernel_aarch64_deps)
        for i in range(len(cls.kernel_aarch64_deps)):
            cls.semantics_a64fx.assign_src_dst(cls.kernel_aarch64_deps[i])
            cls.semantics_a64fx.assign_tp_lt(cls.kernel_aarch64_deps[i])

    ###########
    # Tests
    ###########

    def test_creation_by_name(self):
        try:
            tmp_mm = MachineModel(arch="CSX")
            ArchSemantics(self.parser_x86_att, tmp_mm)
        except ValueError:
            self.fail()

    def test_machine_model_various_functions(self):
        # check dummy MachineModel creation
        try:
            MachineModel(isa="x86")
            MachineModel(isa="aarch64")
        except ValueError:
            self.fail()
        test_mm_x86 = MachineModel(path_to_yaml=self._find_file("test_db_x86.yml"))
        test_mm_arm = MachineModel(path_to_yaml=self._find_file("test_db_aarch64.yml"))

        # test get_instruction without mnemonic
        self.assertIsNone(test_mm_x86.get_instruction(None, []))
        self.assertIsNone(test_mm_arm.get_instruction(None, []))

        # test get_instruction from DB
        self.assertIsNone(test_mm_x86.get_instruction(None, []))
        self.assertIsNone(test_mm_arm.get_instruction(None, []))
        self.assertIsNone(test_mm_x86.get_instruction("NOT_IN_DB", []))
        self.assertIsNone(test_mm_arm.get_instruction("NOT_IN_DB", []))
        name_x86_1 = "vaddpd"
        operands_x86_1 = [
            RegisterOperand(name="xmm"),
            RegisterOperand(name="xmm"),
            RegisterOperand(name="xmm"),
        ]
        instr_form_x86_1 = test_mm_x86.get_instruction(name_x86_1, operands_x86_1)
        self.assertEqual(instr_form_x86_1, test_mm_x86.get_instruction(name_x86_1, operands_x86_1))
        self.assertEqual(
            test_mm_x86.get_instruction("jg", [IdentifierOperand()]),
            test_mm_x86.get_instruction("jg", [IdentifierOperand()]),
        )
        name_arm_1 = "fadd"
        operands_arm_1 = [
            RegisterOperand(prefix="v", shape="s"),
            RegisterOperand(prefix="v", shape="s"),
            RegisterOperand(prefix="v", shape="s"),
        ]
        instr_form_arm_1 = test_mm_arm.get_instruction(name_arm_1, operands_arm_1)
        self.assertEqual(instr_form_arm_1, test_mm_arm.get_instruction(name_arm_1, operands_arm_1))
        self.assertEqual(
            test_mm_arm.get_instruction("b.ne", [IdentifierOperand()]),
            test_mm_arm.get_instruction("b.ne", [IdentifierOperand()]),
        )
        self.assertEqual(
            test_mm_arm.get_instruction("b.someNameThatDoesNotExist", [IdentifierOperand()]),
            test_mm_arm.get_instruction("b.someOtherName", [IdentifierOperand()]),
        )

        # test get_store_tp
        self.assertEqual(
            test_mm_x86.get_store_throughput(
                MemoryOperand(base=RegisterOperand(name="x"), offset=None, index=None, scale=1)
            )[0][1],
            [[2, "237"], [2, "4"]],
        )

        self.assertEqual(
            test_mm_x86.get_store_throughput(
                MemoryOperand(
                    base=RegisterOperand(prefix="NOT_IN_DB"),
                    offset=None,
                    index="NOT_NONE",
                    scale=1,
                )
            )[0][1],
            [[1, "23"], [1, "4"]],
        )

        self.assertEqual(
            test_mm_arm.get_store_throughput(
                MemoryOperand(
                    base=RegisterOperand(prefix="x"),
                    offset=None,
                    index=None,
                    scale=1,
                )
            )[0][1],
            [[2, "34"], [2, "5"]],
        )

        self.assertEqual(
            test_mm_arm.get_store_throughput(
                MemoryOperand(
                    base=RegisterOperand(prefix="NOT_IN_DB"),
                    offset=None,
                    index=None,
                    scale=1,
                )
            )[0][1],
            [[1, "34"], [1, "5"]],
        )

        # test get_store_lt
        self.assertEqual(
            test_mm_x86.get_store_latency(
                MemoryOperand(base=RegisterOperand(name="x"), offset=None, index=None, scale=1)
            ),
            0,
        )
        self.assertEqual(
            test_mm_arm.get_store_latency(
                MemoryOperand(
                    base=RegisterOperand(prefix="x"),
                    offset=None,
                    index=None,
                    scale=1,
                )
            ),
            0,
        )

        # test has_hidden_load
        self.assertFalse(test_mm_x86.has_hidden_loads())

        # test default load tp
        self.assertEqual(
            test_mm_x86.get_load_throughput(
                MemoryOperand(base=RegisterOperand(name="x"), offset=None, index=None, scale=1)
            )[0][1],
            [[1, "23"], [1, ["2D", "3D"]]],
        )

        # test adding port
        test_mm_x86.add_port("dummyPort")
        test_mm_arm.add_port("dummyPort")

        # test dump of DB
        with open(os.devnull, "w") as dev_null:
            test_mm_x86.dump(stream=dev_null)
            test_mm_arm.dump(stream=dev_null)

    def test_src_dst_assignment_x86(self):
        for instruction_form in self.kernel_x86:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form.semantic_operands is not None:
                    self.assertTrue("source" in instruction_form.semantic_operands)
                    self.assertTrue("destination" in instruction_form.semantic_operands)
                    self.assertTrue("src_dst" in instruction_form.semantic_operands)

    def test_src_dst_assignment_x86_intel(self):
        for instruction_form in self.kernel_x86_intel:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form.semantic_operands is not None:
                    self.assertTrue("source" in instruction_form.semantic_operands)
                    self.assertTrue("destination" in instruction_form.semantic_operands)
                    self.assertTrue("src_dst" in instruction_form.semantic_operands)

    def test_src_dst_assignment_AArch64(self):
        for instruction_form in self.kernel_AArch64:
            with self.subTest(instruction_form=instruction_form):
                if instruction_form.semantic_operands is not None:
                    self.assertTrue("source" in instruction_form.semantic_operands)
                    self.assertTrue("destination" in instruction_form.semantic_operands)
                    self.assertTrue("src_dst" in instruction_form.semantic_operands)

    def test_tp_lt_assignment_x86(self):
        self.assertTrue("ports" in self.machine_model_csx)
        port_num = len(self.machine_model_csx["ports"])
        for instruction_form in self.kernel_x86:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue(instruction_form.throughput is not None)
                self.assertTrue(instruction_form.latency is not None)
                self.assertIsInstance(instruction_form.port_pressure, list)
                self.assertEqual(len(instruction_form.port_pressure), port_num)

    def test_tp_lt_assignment_x86_intel(self):
        self.assertTrue("ports" in self.machine_model_csx)
        port_num = len(self.machine_model_csx["ports"])
        for instruction_form in self.kernel_x86_intel:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue(instruction_form.throughput is not None)
                self.assertTrue(instruction_form.latency is not None)
                self.assertIsInstance(instruction_form.port_pressure, list)
                self.assertEqual(len(instruction_form.port_pressure), port_num)

    def test_tp_lt_assignment_AArch64(self):
        self.assertTrue("ports" in self.machine_model_tx2)
        port_num = len(self.machine_model_tx2["ports"])
        for instruction_form in self.kernel_AArch64:
            with self.subTest(instruction_form=instruction_form):
                self.assertTrue(instruction_form.throughput is not None)
                self.assertTrue(instruction_form.latency is not None)
                self.assertIsInstance(instruction_form.port_pressure, list)
                self.assertEqual(len(instruction_form.port_pressure), port_num)

    def test_optimal_throughput_assignment_x86(self):
        kernel_fixed = deepcopy(self.kernel_x86)
        self.semantics_csx.add_semantics(kernel_fixed)
        self.assertEqual(get_unmatched_instruction_ratio(kernel_fixed), 0)

        kernel_optimal = deepcopy(kernel_fixed)
        self.semantics_csx.assign_optimal_throughput(kernel_optimal)
        tp_fixed = self.semantics_csx.get_throughput_sum(kernel_fixed)
        tp_optimal = self.semantics_csx.get_throughput_sum(kernel_optimal)
        self.assertNotEqual(tp_fixed, tp_optimal)
        self.assertTrue(max(tp_optimal) <= max(tp_fixed))
        # test multiple port assignment options
        test_mm_x86 = MachineModel(path_to_yaml=self._find_file("test_db_x86.yml"))
        tmp_semantics = ArchSemantics(self.parser_x86_att, test_mm_x86)
        tmp_code_1 = "fantasyinstr1 %rax, %rax\n"
        tmp_code_2 = "fantasyinstr1 %rax, %rax\nfantasyinstr2 %rbx, %rbx\n"
        tmp_kernel_1 = self.parser_x86_att.parse_file(tmp_code_1)
        tmp_kernel_2 = self.parser_x86_att.parse_file(tmp_code_2)
        tmp_semantics.normalize_instruction_forms(tmp_kernel_1)
        tmp_semantics.normalize_instruction_forms(tmp_kernel_2)
        tmp_semantics.add_semantics(tmp_kernel_1)
        tmp_semantics.add_semantics(tmp_kernel_2)
        tmp_semantics.assign_optimal_throughput(tmp_kernel_1)
        tmp_semantics.assign_optimal_throughput(tmp_kernel_2)
        k1i1_pp = [round(x, 2) for x in tmp_kernel_1[0].port_pressure]
        k2i1_pp = [round(x, 2) for x in tmp_kernel_2[0].port_pressure]
        self.assertEqual(k1i1_pp, [0.33, 0.0, 0.33, 0.0, 0.0, 0.0, 0.0, 0.0, 0.33, 0.0, 0.0])
        self.assertEqual(k2i1_pp, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0])

    def test_optimal_throughput_assignment_x86_intel(self):
        kernel_fixed = deepcopy(self.kernel_x86_intel)
        self.semantics_csx_intel.add_semantics(kernel_fixed)
        self.assertEqual(get_unmatched_instruction_ratio(kernel_fixed), 0)

        kernel_optimal = deepcopy(kernel_fixed)
        self.semantics_csx_intel.assign_optimal_throughput(kernel_optimal)
        tp_fixed = self.semantics_csx_intel.get_throughput_sum(kernel_fixed)
        tp_optimal = self.semantics_csx_intel.get_throughput_sum(kernel_optimal)
        self.assertNotEqual(tp_fixed, tp_optimal)
        self.assertTrue(max(tp_optimal) <= max(tp_fixed))
        # test multiple port assignment options
        test_mm_x86 = MachineModel(path_to_yaml=self._find_file("test_db_x86.yml"))
        tmp_semantics = ArchSemantics(self.parser_x86_intel, test_mm_x86)
        tmp_code_1 = "fantasyinstr1 rax, rax\n"
        tmp_code_2 = "fantasyinstr1 rax, rax\nfantasyinstr2 rbx, rbx\n"
        tmp_kernel_1 = self.parser_x86_intel.parse_file(tmp_code_1)
        tmp_kernel_2 = self.parser_x86_intel.parse_file(tmp_code_2)
        tmp_semantics.normalize_instruction_forms(tmp_kernel_1)
        tmp_semantics.normalize_instruction_forms(tmp_kernel_2)
        tmp_semantics.add_semantics(tmp_kernel_1)
        tmp_semantics.add_semantics(tmp_kernel_2)
        tmp_semantics.assign_optimal_throughput(tmp_kernel_1)
        tmp_semantics.assign_optimal_throughput(tmp_kernel_2)
        k1i1_pp = [round(x, 2) for x in tmp_kernel_1[0].port_pressure]
        k2i1_pp = [round(x, 2) for x in tmp_kernel_2[0].port_pressure]
        self.assertEqual(k1i1_pp, [0.33, 0.0, 0.33, 0.0, 0.0, 0.0, 0.0, 0.0, 0.33, 0.0, 0.0])
        self.assertEqual(k2i1_pp, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0])

    def test_optimal_throughput_assignment_AArch64(self):
        kernel_fixed = deepcopy(self.kernel_AArch64)
        self.semantics_tx2.add_semantics(kernel_fixed)

        self.assertEqual(get_unmatched_instruction_ratio(kernel_fixed), 0)

        kernel_optimal = deepcopy(kernel_fixed)
        self.semantics_tx2.assign_optimal_throughput(kernel_optimal)
        tp_fixed = self.semantics_tx2.get_throughput_sum(kernel_fixed)
        tp_optimal = self.semantics_tx2.get_throughput_sum(kernel_optimal)
        self.assertNotEqual(tp_fixed, tp_optimal)
        self.assertTrue(max(tp_optimal) <= max(tp_fixed))

    def test_kernelDG_x86(self):
        #
        #  4
        #   \___>6__>7
        #   /
        #  3
        #     5_______>9
        #
        dg = KernelDG(
            self.kernel_x86, self.parser_x86_att, self.machine_model_csx, self.semantics_csx
        )
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=3))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=3)), 6)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=4))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=4)), 6)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=5))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=5)), 9)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=6))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=6)), 7)
        self.assertEqual(list(dg.get_dependent_instruction_forms(line_number=7)), [])
        self.assertEqual(list(dg.get_dependent_instruction_forms(line_number=8)), [])
        with self.assertRaises(ValueError):
            dg.get_dependent_instruction_forms()
        # test dot creation
        dg.export_graph(filepath=os.devnull)

    def test_kernelDG_x86_intel(self):
        #
        #  3
        #   \___>5__>6
        #   /  /
        #  4  /
        #    /
        #  5.1
        #
        dg = KernelDG(
            self.kernel_x86_intel,
            self.parser_x86_intel,
            self.machine_model_csx,
            self.semantics_csx_intel,
        )
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=3))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=3)), 5)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=4))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=4)), 5)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=5))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=5)), 6)
        self.assertEqual(len(list(dg.get_dependent_instruction_forms(line_number=5.1))), 1)
        self.assertEqual(next(dg.get_dependent_instruction_forms(line_number=5.1)), 5)
        self.assertEqual(list(dg.get_dependent_instruction_forms(line_number=6)), [])
        self.assertEqual(list(dg.get_dependent_instruction_forms(line_number=7)), [])
        self.assertEqual(list(dg.get_dependent_instruction_forms(line_number=8)), [])
        with self.assertRaises(ValueError):
            dg.get_dependent_instruction_forms()
        # test dot creation
        dg.export_graph(filepath=os.devnull)

    def test_memdependency_x86(self):
        dg = KernelDG(
            self.kernel_x86_memdep,
            self.parser_x86_att,
            self.machine_model_csx,
            self.semantics_csx,
        )
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=3)), {6, 8})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=5)), {10, 12})
        with self.assertRaises(ValueError):
            dg.get_dependent_instruction_forms()
        # test dot creation
        dg.export_graph(filepath=os.devnull)

    def test_memdependency_x86_intel(self):
        dg = KernelDG(
            self.kernel_x86_intel_memdep,
            self.parser_x86_intel,
            self.machine_model_csx,
            self.semantics_csx_intel,
        )
        self.assertTrue(nx.algorithms.dag.is_directed_acyclic_graph(dg.dg))
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=3)), {6, 8})
        self.assertEqual(set(dg.get_dependent_instruction_forms(line_number=5)), {10, 12})
        with self.assertRaises(ValueError):
            dg.get_dependent_instruction_forms()
        # test dot creation
        dg.export_graph(filepath=os.devnull)

    def test_kernelDG_AArch64(self):
        dg = KernelDG(
            self.kernel_AArch64,
            self.parser_AArch64,
            self.machine_model_tx2,
            self.semantics_tx2,
        )
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
        # test dot creation
        dg.export_graph(filepath=os.devnull)

    def test_kernelDG_SVE(self):
        KernelDG(
            self.kernel_aarch64_SVE,
            self.parser_AArch64,
            self.machine_model_a64fx,
            self.semantics_a64fx,
        )
        # TODO check for correct analysis

    def test_mops_deps_AArch64(self):
        self.kernel_mops_1 = reduce_to_section(
            self.parser_AArch64.parse_file(self.mops_1_code), self.parser_AArch64
        )
        self.kernel_mops_2 = reduce_to_section(
            self.parser_AArch64.parse_file(self.mops_2_code), self.parser_AArch64
        )
        self.semantics_a64fx.normalize_instruction_forms(self.kernel_mops_1)
        self.semantics_a64fx.normalize_instruction_forms(self.kernel_mops_2)
        for i in range(len(self.kernel_mops_1)):
            self.semantics_a64fx.assign_src_dst(self.kernel_mops_1[i])
        for i in range(len(self.kernel_mops_2)):
            self.semantics_a64fx.assign_src_dst(self.kernel_mops_2[i])

        mops_dest = MemoryOperand(
            offset=None,
            base=RegisterOperand(prefix="x", name="3"),
            index=None,
            scale=1,
            pre_indexed=True,
        )
        mops_src = MemoryOperand(
            offset=None,
            base=RegisterOperand(prefix="x", name="1"),
            index=None,
            scale=1,
            pre_indexed=True,
        )
        mops_n = RegisterOperand(prefix="x", name="2", pre_indexed=True)
        mops_x1 = RegisterOperand(prefix="x", name="1")
        for instruction_form in self.kernel_mops_1[:-1]:
            with self.subTest(instruction_form=instruction_form):
                if not instruction_form.line.startswith("//"):
                    self.assertTrue(mops_dest in instruction_form.semantic_operands["destination"])
                    self.assertTrue(mops_src in instruction_form.semantic_operands["source"])
                    self.assertTrue(mops_n in instruction_form.semantic_operands["src_dst"])
                    self.assertTrue(
                        mops_dest.base in instruction_form.semantic_operands["src_dst"]
                    )
                    self.assertTrue(mops_src.base in instruction_form.semantic_operands["src_dst"])
        for instruction_form in self.kernel_mops_2[-2:-1]:
            with self.subTest(instruction_form=instruction_form):
                if not instruction_form.line.startswith("//"):
                    self.assertTrue(mops_dest in instruction_form.semantic_operands["destination"])
                    self.assertTrue(mops_x1 in instruction_form.semantic_operands["source"])
                    self.assertTrue(mops_n in instruction_form.semantic_operands["src_dst"])
                    self.assertTrue(
                        mops_dest.base in instruction_form.semantic_operands["src_dst"]
                    )

    def test_hidden_load(self):
        machine_model_hld = MachineModel(
            path_to_yaml=self._find_file("hidden_load_machine_model.yml")
        )
        self.assertTrue(machine_model_hld.has_hidden_loads())
        semantics_hld = ArchSemantics(self.parser_x86_att, machine_model_hld)
        kernel_hld = self.parser_x86_att.parse_file(self.code_x86)
        kernel_hld_2 = self.parser_x86_att.parse_file(self.code_x86)
        kernel_hld_2 = self.parser_x86_att.parse_file(self.code_x86)[-3:]
        kernel_hld_3 = self.parser_x86_att.parse_file(self.code_x86)[5:8]

        semantics_hld.normalize_instruction_forms(kernel_hld)
        semantics_hld.normalize_instruction_forms(kernel_hld_2)
        semantics_hld.normalize_instruction_forms(kernel_hld_3)

        semantics_hld.add_semantics(kernel_hld)
        semantics_hld.add_semantics(kernel_hld_2)
        semantics_hld.add_semantics(kernel_hld_3)

        num_hidden_loads = len([x for x in kernel_hld if INSTR_FLAGS.HIDDEN_LD in x.flags])
        num_hidden_loads_2 = len([x for x in kernel_hld_2 if INSTR_FLAGS.HIDDEN_LD in x.flags])
        num_hidden_loads_3 = len([x for x in kernel_hld_3 if INSTR_FLAGS.HIDDEN_LD in x.flags])
        self.assertEqual(num_hidden_loads, 1)
        self.assertEqual(num_hidden_loads_2, 0)
        self.assertEqual(num_hidden_loads_3, 1)

    def test_cyclic_dag(self):
        dg = KernelDG(
            self.kernel_x86, self.parser_x86_att, self.machine_model_csx, self.semantics_csx
        )
        dg.dg.add_edge(100, 101, latency=1.0)
        dg.dg.add_edge(101, 102, latency=2.0)
        dg.dg.add_edge(102, 100, latency=3.0)
        with self.assertRaises(NotImplementedError):
            dg.get_critical_path()
        with self.assertRaises(NotImplementedError):
            dg.get_loopcarried_dependencies()

    def test_loop_carried_dependency_aarch64(self):
        dg = KernelDG(
            self.kernel_aarch64_memdep,
            self.parser_AArch64,
            self.machine_model_tx2,
            self.semantics_tx2,
        )

        lc_deps = dg.get_loopcarried_dependencies()
        self.assertEqual(len(lc_deps), 4)

        # based on line 6
        dep_path = "6-10-11-12-13-14"
        self.assertEqual(lc_deps[dep_path]["latency"], 29.0)
        self.assertEqual(
            [(iform.line_number, lat) for iform, lat in lc_deps[dep_path]["dependencies"]],
            [(6, 4.0), (10, 6.0), (11, 6.0), (12, 6.0), (13, 6.0), (14, 1.0)],
        )

        dg = KernelDG(
            self.kernel_aarch64_deps,
            self.parser_AArch64,
            self.machine_model_a64fx,
            self.semantics_a64fx,
            flag_dependencies=True,
        )
        lc_deps = dg.get_loopcarried_dependencies()
        self.assertEqual(len(lc_deps), 2)
        # based on line 4
        dep_path = "4-5-6-9-10-11-12"
        self.assertEqual(lc_deps[dep_path]["latency"], 7.0)
        self.assertEqual(
            [(iform.line_number, lat) for iform, lat in lc_deps[dep_path]["dependencies"]],
            [(4, 1.0), (5, 1.0), (6, 1.0), (9, 1.0), (10, 1.0), (11, 1.0), (12, 1.0)],
        )

        dg = KernelDG(
            self.kernel_aarch64_deps,
            self.parser_AArch64,
            self.machine_model_a64fx,
            self.semantics_a64fx,
            flag_dependencies=False,
        )
        lc_deps = dg.get_loopcarried_dependencies()
        self.assertEqual(len(lc_deps), 1)
        # based on line 4
        dep_path = "4-5-10-11-12"
        self.assertEqual(lc_deps[dep_path]["latency"], 5.0)
        self.assertEqual(
            [(iform.line_number, lat) for iform, lat in lc_deps[dep_path]["dependencies"]],
            [(4, 1.0), (5, 1.0), (10, 1.0), (11, 1.0), (12, 1.0)],
        )

    def test_loop_carried_dependency_x86(self):
        lcd_id = "8"
        lcd_id2 = "5"
        dg = KernelDG(
            self.kernel_x86, self.parser_x86_att, self.machine_model_csx, self.semantics_csx
        )
        lc_deps = dg.get_loopcarried_dependencies()
        # self.assertEqual(len(lc_deps), 2)
        # ID 8
        self.assertEqual(
            lc_deps[lcd_id]["root"], dg.dg.nodes(data=True)[int(lcd_id)]["instruction_form"]
        )
        self.assertEqual(len(lc_deps[lcd_id]["dependencies"]), 1)
        self.assertEqual(
            lc_deps[lcd_id]["dependencies"][0][0],
            dg.dg.nodes(data=True)[int(lcd_id)]["instruction_form"],
        )
        # w/  flag dependencies: ID 9 w/ len=2
        # w/o flag dependencies: ID 5 w/ len=1
        # TODO discuss
        self.assertEqual(
            lc_deps[lcd_id2]["root"],
            dg.dg.nodes(data=True)[int(lcd_id2)]["instruction_form"],
        )
        self.assertEqual(len(lc_deps[lcd_id2]["dependencies"]), 1)
        self.assertEqual(
            lc_deps[lcd_id2]["dependencies"][0][0],
            dg.dg.nodes(data=True)[int(lcd_id2)]["instruction_form"],
        )

    def test_loop_carried_dependency_x86_intel(self):
        lcd_id = "8"
        lcd_id2 = "7"
        dg = KernelDG(
            self.kernel_x86_intel,
            self.parser_x86_intel,
            self.machine_model_csx,
            self.semantics_csx_intel,
        )
        lc_deps = dg.get_loopcarried_dependencies()
        # self.assertEqual(len(lc_deps), 2)
        # ID 8
        self.assertEqual(
            lc_deps[lcd_id]["root"], dg.dg.nodes(data=True)[int(lcd_id)]["instruction_form"]
        )
        self.assertEqual(len(lc_deps[lcd_id]["dependencies"]), 1)
        self.assertEqual(
            lc_deps[lcd_id]["dependencies"][0][0],
            dg.dg.nodes(data=True)[int(lcd_id)]["instruction_form"],
        )
        # w/  flag dependencies: ID 9 w/ len=2
        # w/o flag dependencies: ID 5 w/ len=1
        # TODO discuss
        self.assertEqual(
            lc_deps[lcd_id2]["root"],
            dg.dg.nodes(data=True)[int(lcd_id2)]["instruction_form"],
        )
        self.assertEqual(len(lc_deps[lcd_id2]["dependencies"]), 1)
        self.assertEqual(
            lc_deps[lcd_id2]["dependencies"][0][0],
            dg.dg.nodes(data=True)[int(lcd_id2)]["instruction_form"],
        )

    def test_timeout_during_loop_carried_dependency(self):
        start_time = time.perf_counter()
        KernelDG(
            self.kernel_x86_long_LCD,
            self.parser_x86_att,
            self.machine_model_csx,
            self.semantics_x86,
            timeout=10,
        )
        end_time = time.perf_counter()
        time_10 = end_time - start_time
        start_time = time.perf_counter()
        KernelDG(
            self.kernel_x86_long_LCD,
            self.parser_x86_att,
            self.machine_model_csx,
            self.semantics_x86,
            timeout=2,
        )
        end_time = time.perf_counter()
        time_2 = end_time - start_time

        self.assertTrue(time_10 > 10)
        self.assertTrue(2 < time_2)
        self.assertTrue(time_2 < (time_10 - 7))

    def test_is_read_is_written_x86(self):
        # independent form HW model
        dag = KernelDG(self.kernel_x86, self.parser_x86_att, None, None)
        reg_rcx = RegisterOperand(name="rcx")
        reg_ymm1 = RegisterOperand(name="ymm1")

        instr_form_r_c = self.parser_x86_att.parse_line("vmovsd  %xmm0, (%r15,%rcx,8)")
        self.semantics_csx.normalize_instruction_form(instr_form_r_c)
        self.semantics_csx.assign_src_dst(instr_form_r_c)
        instr_form_non_r_c = self.parser_x86_att.parse_line("movl  %xmm0, (%r15,%rax,8)")
        self.semantics_csx.normalize_instruction_form(instr_form_non_r_c)
        self.semantics_csx.assign_src_dst(instr_form_non_r_c)
        instr_form_w_c = self.parser_x86_att.parse_line("movi $0x05ACA, %rcx")
        self.semantics_csx.normalize_instruction_form(instr_form_w_c)
        self.semantics_csx.assign_src_dst(instr_form_w_c)

        instr_form_rw_ymm_1 = self.parser_x86_att.parse_line(
            "vinsertf128 $0x1, %xmm1, %ymm0, %ymm1"
        )
        self.semantics_csx.normalize_instruction_form(instr_form_rw_ymm_1)
        self.semantics_csx.assign_src_dst(instr_form_rw_ymm_1)
        instr_form_rw_ymm_2 = self.parser_x86_att.parse_line(
            "vinsertf128 $0x1, %xmm0, %ymm1, %ymm1"
        )
        self.semantics_csx.normalize_instruction_form(instr_form_rw_ymm_2)
        self.semantics_csx.assign_src_dst(instr_form_rw_ymm_2)
        instr_form_r_ymm = self.parser_x86_att.parse_line("vmovapd %ymm1, %ymm0")
        self.semantics_csx.normalize_instruction_form(instr_form_r_ymm)
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

    def test_is_read_is_written_x86_intel(self):
        # independent form HW model
        dag = KernelDG(self.kernel_x86_intel, self.parser_x86_intel, None, None)
        reg_rcx = RegisterOperand(name="rcx")
        reg_ymm1 = RegisterOperand(name="ymm1")

        instr_form_r_c = self.parser_x86_intel.parse_line("vmovsd  QWORD PTR [r15+rcx*8], xmm0")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_r_c)
        self.semantics_csx_intel.assign_src_dst(instr_form_r_c)
        instr_form_non_r_c = self.parser_x86_intel.parse_line("mov  QWORD PTR [r15+rax*8], xmm0")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_non_r_c)
        self.semantics_csx_intel.assign_src_dst(instr_form_non_r_c)
        instr_form_w_c = self.parser_x86_intel.parse_line("mov rcx, H05ACA")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_w_c)
        self.semantics_csx_intel.assign_src_dst(instr_form_w_c)

        instr_form_rw_ymm_1 = self.parser_x86_intel.parse_line("vinsertf128 ymm1, ymm0, xmm1, 1")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_rw_ymm_1)
        self.semantics_csx_intel.assign_src_dst(instr_form_rw_ymm_1)
        instr_form_rw_ymm_2 = self.parser_x86_intel.parse_line("vinsertf128 ymm1, ymm1, xmm0, 1")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_rw_ymm_2)
        self.semantics_csx_intel.assign_src_dst(instr_form_rw_ymm_2)
        instr_form_r_ymm = self.parser_x86_intel.parse_line("vmovapd ymm0, ymm1")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_r_ymm)
        self.semantics_csx_intel.assign_src_dst(instr_form_r_ymm)
        instr_form_rw_sar = self.parser_x86_intel.parse_line("sar rcx, 43")
        self.semantics_csx_intel.normalize_instruction_form(instr_form_rw_sar)
        self.semantics_csx_intel.assign_src_dst(instr_form_rw_sar)
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
        self.assertTrue(dag.is_read(reg_rcx, instr_form_rw_sar))
        self.assertTrue(dag.is_written(reg_rcx, instr_form_rw_sar))

    def test_is_read_is_written_AArch64(self):
        # independent form HW model
        dag = KernelDG(self.kernel_AArch64, self.parser_AArch64, None, None)
        reg_x1 = RegisterOperand(prefix="x", name="1")
        reg_w1 = RegisterOperand(prefix="w", name="1")
        reg_d1 = RegisterOperand(prefix="d", name="1")
        reg_q1 = RegisterOperand(prefix="q", name="1")
        reg_v1 = RegisterOperand(prefix="v", name="1", lanes="2", shape="d")
        regs = [reg_d1, reg_q1, reg_v1]
        regs_gp = [reg_w1, reg_x1]

        instr_form_r_1 = self.parser_AArch64.parse_line("stp q1, q3, [x12, #192]")
        self.semantics_tx2.normalize_instruction_form(instr_form_r_1)
        self.semantics_tx2.assign_src_dst(instr_form_r_1)
        instr_form_r_2 = self.parser_AArch64.parse_line("fadd v2.2d, v1.2d, v0.2d")
        self.semantics_tx2.normalize_instruction_form(instr_form_r_2)
        self.semantics_tx2.assign_src_dst(instr_form_r_2)
        instr_form_w_1 = self.parser_AArch64.parse_line("ldr d1, [x1, #:got_lo12:q2c]")
        self.semantics_tx2.normalize_instruction_form(instr_form_w_1)
        self.semantics_tx2.assign_src_dst(instr_form_w_1)
        instr_form_non_w_1 = self.parser_AArch64.parse_line("ldr x1, [x1, #:got_lo12:q2c]")
        self.semantics_tx2.normalize_instruction_form(instr_form_non_w_1)
        self.semantics_tx2.assign_src_dst(instr_form_non_w_1)
        instr_form_rw_1 = self.parser_AArch64.parse_line("fmul v1.2d, v1.2d, v0.2d")
        self.semantics_tx2.normalize_instruction_form(instr_form_rw_1)
        self.semantics_tx2.assign_src_dst(instr_form_rw_1)
        instr_form_rw_2 = self.parser_AArch64.parse_line("ldp q2, q4, [x1, #64]!")
        self.semantics_tx2.normalize_instruction_form(instr_form_rw_2)
        self.semantics_tx2.assign_src_dst(instr_form_rw_2)
        instr_form_rw_3 = self.parser_AArch64.parse_line("str x4, [x1], #64")
        self.semantics_tx2.normalize_instruction_form(instr_form_rw_3)
        self.semantics_tx2.assign_src_dst(instr_form_rw_3)
        instr_form_non_rw_1 = self.parser_AArch64.parse_line("adds x1, x11")
        self.semantics_tx2.normalize_instruction_form(instr_form_non_rw_1)
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
            MachineModel(arch="CSX", path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "csx.yml"))
        with self.assertRaises(FileNotFoundError):
            MachineModel(arch="THE_MACHINE")
        with self.assertRaises(FileNotFoundError):
            MachineModel(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "THE_MACHINE.yml"))

    def test_MachineModel_getter(self):
        sample_operands = [
            MemoryOperand(
                offset=None,
                base=RegisterOperand(name="r12"),
                index=RegisterOperand(name="rcx"),
                scale=8,
            )
        ]
        self.assertIsNone(self.machine_model_csx.get_instruction("GETRESULT", sample_operands))
        self.assertIsNone(self.machine_model_tx2.get_instruction("GETRESULT", sample_operands))

        self.assertEqual(self.machine_model_csx.get_arch(), "csx")
        self.assertEqual(self.machine_model_tx2.get_arch(), "tx2")

        self.assertEqual(self.machine_model_csx.get_ISA(), "x86")
        self.assertEqual(self.machine_model_tx2.get_ISA(), "aarch64")

        ports_csx = ["0", "0DV", "1", "2", "2D", "3", "3D", "4", "5", "6", "7"]
        data_ports_csx = ["2D", "3D"]
        self.assertEqual(self.machine_model_csx.get_ports(), ports_csx)
        self.assertEqual(self.machine_model_csx.get_data_ports(), data_ports_csx)

        self.assertFalse(self.machine_model_tx2.has_hidden_loads())

        self.assertEqual(MachineModel.get_isa_for_arch("CSX"), "x86")
        self.assertEqual(MachineModel.get_isa_for_arch("tX2"), "aarch64")
        with self.assertRaises(ValueError):
            self.assertIsNone(MachineModel.get_isa_for_arch("THE_MACHINE"))

    ##################
    # Helper functions
    ##################

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, "test_files", name)
        assert os.path.exists(name)
        return name


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSemanticTools)
    unittest.TextTestRunner(verbosity=2).run(suite)
