#!/usr/bin/env python3
"""
Unit tests for OSACA Frontend
"""

import os
import unittest

from osaca.frontend import Frontend
from osaca.parser import ParserAArch64, ParserX86ATT
from osaca.semantics import ArchSemantics, KernelDG, MachineModel


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
            self.machine_model_csx, path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "isa/x86.yml")
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
            self.kernel_AArch64, self.parser_AArch64, self.machine_model_tx2, self.semantics_tx2)
        fe = Frontend(path_to_yaml=os.path.join(self.MODULE_DATA_DIR, "tx2.yml"))
        fe.full_analysis(self.kernel_AArch64, dg, verbose=True)
        # TODO compare output with checked string

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
