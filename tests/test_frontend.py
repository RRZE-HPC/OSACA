#!/usr/bin/env python3
"""
Unit tests for OSACA Frontend
"""

import os
import unittest

from osaca.frontend import Frontend
from osaca.parser import ParserAArch64, ParserX86ATT
from osaca.semantics import ArchSemantics, KernelDG, MachineModel, reduce_to_section


class TestFrontend(unittest.TestCase):
    MODULE_DATA_DIR = os.path.join(
        os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), "osaca/data/"
    )

    @classmethod
    def setUpClass(self):
        # set up parser and kernels
        self.parser_x86 = ParserX86ATT()
        self.parser_AArch64 = ParserAArch64()
        with open(self._find_file("kernel_x86.s")) as f:
            code_x86 = f.read()
        with open(self._find_file("kernel_aarch64.s")) as f:
            code_AArch64 = f.read()
        self.kernel_x86 = self.parser_x86.parse_file(code_x86)
        self.kernel_AArch64 = self.parser_AArch64.parse_file(code_AArch64)

        # set up machine models
        self.machine_model_csx = MachineModel(
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "csx.yml")
        )
        self.machine_model_tx2 = MachineModel(arch="tx2")
        self.semantics_csx = ArchSemantics(
            self.machine_model_csx,
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "isa/x86.yml"),
        )
        self.semantics_tx2 = ArchSemantics(
            self.machine_model_tx2,
            path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "isa/aarch64.yml"),
        )

        for i in range(len(self.kernel_x86)):
            self.semantics_csx.assign_src_dst(self.kernel_x86[i])
            self.semantics_csx.assign_tp_lt(self.kernel_x86[i])
        for i in range(len(self.kernel_AArch64)):
            self.semantics_tx2.assign_src_dst(self.kernel_AArch64[i])
            self.semantics_tx2.assign_tp_lt(self.kernel_AArch64[i])

    ###########
    # Tests
    ###########

    def test_frontend_creation(self):
        with self.assertRaises(ValueError):
            Frontend()
        with self.assertRaises(ValueError):
            Frontend(arch="csx", path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "csx.yml"))
        with self.assertRaises(FileNotFoundError):
            Frontend(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "THE_MACHINE.yml"))
        with self.assertRaises(FileNotFoundError):
            Frontend(arch="THE_MACHINE")
        Frontend(arch="zen1")

    def test_frontend_x86(self):
        dg = KernelDG(self.kernel_x86, self.parser_x86, self.machine_model_csx, self.semantics_csx)
        fe = Frontend(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "csx.yml"))
        fe.throughput_analysis(self.kernel_x86, show_cmnts=False)
        fe.latency_analysis(dg.get_critical_path())
        # TODO compare output with checked string

    def test_frontend_AArch64(self):
        dg = KernelDG(
            self.kernel_AArch64,
            self.parser_AArch64,
            self.machine_model_tx2,
            self.semantics_tx2,
        )
        fe = Frontend(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "tx2.yml"))
        fe.full_analysis(self.kernel_AArch64, dg, verbose=True)
        # TODO compare output with checked string

    def test_dict_output_x86(self):
        dg = KernelDG(self.kernel_x86, self.parser_x86, self.machine_model_csx, self.semantics_csx)
        fe = Frontend(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "csx.yml"))
        analysis_dict = fe.full_analysis_dict(self.kernel_x86, dg)
        self.assertEqual(len(self.kernel_x86), len(analysis_dict["Kernel"]))
        self.assertEqual("csx", analysis_dict["Header"]["Architecture"])
        self.assertEqual(len(analysis_dict["Warnings"]), 0)
        for i, line in enumerate(self.kernel_x86):
            self.assertEqual(line.throughput, analysis_dict["Kernel"][i]["Throughput"])
            self.assertEqual(line.latency, analysis_dict["Kernel"][i]["Latency"])
            self.assertEqual(
                line.latency_wo_load, analysis_dict["Kernel"][i]["LatencyWithoutLoad"]
            )
            self.assertEqual(line.latency_cp, analysis_dict["Kernel"][i]["LatencyCP"])
            self.assertEqual(line.mnemonic, analysis_dict["Kernel"][i]["Instruction"])
            self.assertEqual(len(line.operands), len(analysis_dict["Kernel"][i]["Operands"]))
            self.assertEqual(
                len(line.semantic_operands["source"]),
                len(analysis_dict["Kernel"][i]["SemanticOperands"]["source"]),
            )
            self.assertEqual(
                len(line.semantic_operands["destination"]),
                len(analysis_dict["Kernel"][i]["SemanticOperands"]["destination"]),
            )
            self.assertEqual(
                len(line.semantic_operands["src_dst"]),
                len(analysis_dict["Kernel"][i]["SemanticOperands"]["src_dst"]),
            )
            self.assertEqual(line.flags, analysis_dict["Kernel"][i]["Flags"])
            self.assertEqual(line.line_number, analysis_dict["Kernel"][i]["LineNumber"])

    def test_dict_output_AArch64(self):
        reduced_kernel = reduce_to_section(self.kernel_AArch64, self.semantics_tx2._isa)
        dg = KernelDG(
            reduced_kernel,
            self.parser_AArch64,
            self.machine_model_tx2,
            self.semantics_tx2,
        )
        fe = Frontend(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "tx2.yml"))
        analysis_dict = fe.full_analysis_dict(reduced_kernel, dg)
        self.assertEqual(len(reduced_kernel), len(analysis_dict["Kernel"]))
        self.assertEqual("tx2", analysis_dict["Header"]["Architecture"])
        self.assertEqual(len(analysis_dict["Warnings"]), 0)
        for i, line in enumerate(reduced_kernel):
            self.assertEqual(line.throughput, analysis_dict["Kernel"][i]["Throughput"])
            self.assertEqual(line.latency, analysis_dict["Kernel"][i]["Latency"])
            self.assertEqual(
                line.latency_wo_load, analysis_dict["Kernel"][i]["LatencyWithoutLoad"]
            )
            self.assertEqual(line.latency_cp, analysis_dict["Kernel"][i]["LatencyCP"])
            self.assertEqual(line.mnemonic, analysis_dict["Kernel"][i]["Instruction"])
            self.assertEqual(len(line.operands), len(analysis_dict["Kernel"][i]["Operands"]))
            self.assertEqual(
                len(line.semantic_operands["source"]),
                len(analysis_dict["Kernel"][i]["SemanticOperands"]["source"]),
            )
            self.assertEqual(
                len(line.semantic_operands["destination"]),
                len(analysis_dict["Kernel"][i]["SemanticOperands"]["destination"]),
            )
            self.assertEqual(
                len(line.semantic_operands["src_dst"]),
                len(analysis_dict["Kernel"][i]["SemanticOperands"]["src_dst"]),
            )
            self.assertEqual(line.flags, analysis_dict["Kernel"][i]["Flags"])
            self.assertEqual(line.line_number, analysis_dict["Kernel"][i]["LineNumber"])

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFrontend)
    unittest.TextTestRunner(verbosity=2).run(suite)
