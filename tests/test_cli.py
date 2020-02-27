#!/usr/bin/env python3
"""
Unit tests for the CLI of OSACA and running the sample kernels in examples/
"""

import argparse
import os
import unittest
from io import StringIO

import osaca.osaca as osaca


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
        args = parser.parse_args(['--import', 'WRONG_BENCH', self._find_file('gs', 'csx', 'gcc')])
        with self.assertRaises(ValueError):
            osaca.check_arguments(args, parser)

    def test_import_data(self):
        parser = osaca.create_parser(parser=ErrorRaisingArgumentParser())
        args = parser.parse_args(
            ['--arch', 'csx', '--import', 'ibench', self._find_test_file('ibench_import_x86.dat')]
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

    def test_check_db(self):
        parser = osaca.create_parser(parser=ErrorRaisingArgumentParser())
        args = parser.parse_args(
            ['--arch', 'tx2', '--db-check', '--verbose', self._find_test_file('triad_x86_iaca.s')]
        )
        output = StringIO()
        osaca.run(args, output_file=output)

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
                        args = parser.parse_args(['--arch', a, self._find_file(k, a, c)])
                        output = StringIO()
                        osaca.run(args, output_file=output)
                        self.assertTrue('WARNING' not in output.getvalue())

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
