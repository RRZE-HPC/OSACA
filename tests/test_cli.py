#!/usr/bin/env python3
"""
Unit tests for the CLI of OSACA and running the sample kernels in examples/
"""

import argparse
import os
import unittest
from io import StringIO
from shutil import copyfile
from unittest.mock import patch

import osaca.osaca as osaca
from osaca.parser import ParserAArch64v81, ParserX86ATT
from osaca.semantics import MachineModel


class ErrorRaisingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)  # reraise an error


class TestCLI(unittest.TestCase):

    ###########
    # Tests
    ###########

    def test_check_arguments(self):
        parser = osaca.create_parser(parser=ErrorRaisingArgumentParser())
        args = parser.parse_args(['--arch', 'WRONG_ARCH', self._find_file('gs', 'csx', 'gcc')])
        with self.assertRaises(ValueError):
            osaca.check_arguments(args, parser)
        args = parser.parse_args(
            ['--arch', 'csx', '--import', 'WRONG_BENCH', self._find_file('gs', 'csx', 'gcc')]
        )
        with self.assertRaises(ValueError):
            osaca.check_arguments(args, parser)

    def test_import_data(self):
        parser = osaca.create_parser(parser=ErrorRaisingArgumentParser())
        args = parser.parse_args(
            [
                '--arch',
                'tx2',
                '--import',
                'ibench',
                self._find_test_file('ibench_import_aarch64.dat'),
            ]
        )
        output = StringIO()
        osaca.run(args, output_file=output)
        args = parser.parse_args(
            [
                '--arch',
                'tx2',
                '--import',
                'asmbench',
                self._find_test_file('asmbench_import_aarch64.dat'),
            ]
        )
        osaca.run(args, output_file=output)

    def test_check_db(self):
        parser = osaca.create_parser(parser=ErrorRaisingArgumentParser())
        args = parser.parse_args(
            ['--arch', 'tx2', '--db-check', '--verbose', self._find_test_file('triad_x86_iaca.s')]
        )
        output = StringIO()
        osaca.run(args, output_file=output)

    def test_get_parser(self):
        self.assertTrue(isinstance(osaca.get_asm_parser('csx'), ParserX86ATT))
        self.assertTrue(isinstance(osaca.get_asm_parser('tx2'), ParserAArch64v81))
        with self.assertRaises(ValueError):
            osaca.get_asm_parser('UNKNOWN')

    def test_marker_insert_x86(self):
        # copy file to add markers
        name = self._find_test_file('kernel_x86.s')
        name_copy = name + '.copy.s'
        copyfile(name, name_copy)

        user_input = ['.L10']
        output = StringIO()
        parser = osaca.create_parser()
        args = parser.parse_args(['--arch', 'csx', '--insert-marker', name_copy])
        with patch('builtins.input', side_effect=user_input):
            osaca.run(args, output_file=output)

        lines_orig = len(open(name).readlines())
        lines_copy = len(open(name_copy).readlines())
        self.assertEqual(lines_copy, lines_orig + 5 + 4)
        # remove copy again
        os.remove(name_copy)

    def test_marker_insert_aarch64(self):
        # copy file to add markers
        name = self._find_test_file('kernel_aarch64.s')
        name_copy = name + '.copy.s'
        copyfile(name, name_copy)

        user_input = ['.LBB0_32', '64']
        parser = osaca.create_parser()
        args = parser.parse_args(['--arch', 'tx2', '--insert-marker', name_copy])
        with patch('builtins.input', side_effect=user_input):
            osaca.run(args)

        lines_orig = len(open(name).readlines())
        lines_copy = len(open(name_copy).readlines())
        self.assertEqual(lines_copy, lines_orig + 3 + 2)
        # remove copy again
        os.remove(name_copy)

    def test_examples(self):
        kernels = [
            'add',
            'copy',
            'daxpy',
            'gs',
            'j2d',
            'striad',
            'sum_reduction',
            'triad',
            'update',
        ]
        archs = ['csx', 'tx2', 'zen1']
        comps = {'csx': ['gcc', 'icc'], 'tx2': ['gcc', 'clang'], 'zen1': ['gcc']}
        parser = osaca.create_parser()
        # Analyze all asm files resulting out of kernels, archs and comps
        for k in kernels:
            for a in archs:
                for c in comps[a]:
                    with self.subTest(kernel=k, arch=a, comp=c):
                        args = parser.parse_args(
                            ['--arch', a, self._find_file(k, a, c), '--export-graph', '/dev/null']
                        )
                        output = StringIO()
                        osaca.run(args, output_file=output)
                        self.assertTrue('WARNING' not in output.getvalue())

    def test_architectures(self):
        parser = osaca.create_parser()
        # Run the test kernel for all architectures
        archs = osaca.SUPPORTED_ARCHS
        for arch in archs:
            with self.subTest(micro_arch=arch):
                isa = MachineModel.get_isa_for_arch(arch)
                kernel = 'kernel_{}.s'.format(isa)
                args = parser.parse_args(
                    ['--arch', arch, self._find_test_file(kernel)]
                )
                output = StringIO()
                osaca.run(args, output_file=output)

    ##################
    # Helper functions
    ##################

    @staticmethod
    def _find_file(kernel, arch, comp):
        testdir = os.path.dirname(__file__)
        name = os.path.join(
            testdir,
            '../examples',
            kernel,
            kernel + '.s.' + arch[:3].lower() + '.' + comp.lower() + '.s',
        )
        if kernel == 'j2d' and arch.lower() == 'csx':
            name = name[:-1] + 'AVX.s'
        assert os.path.exists(name)
        return name

    @staticmethod
    def _find_test_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'test_files', name)
        assert os.path.exists(name)
        return name


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCLI)
    unittest.TextTestRunner(verbosity=2).run(suite)
