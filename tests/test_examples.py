#!/usr/bin/env python3
"""
Unit tests for OSACA sample kernels in examples/
"""

import os
import unittest
from io import StringIO

import osaca.osaca as osaca


class TestExamples(unittest.TestCase):

    ###########
    # Tests
    ###########

    def test_examples(self):
        kernels = ['add', 'copy', 'daxpy', 'j2d', 'striad', 'sum_reduction', 'triad', 'update']
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestExamples)
    unittest.TextTestRunner(verbosity=2).run(suite)
