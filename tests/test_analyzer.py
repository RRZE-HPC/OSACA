#!/usr/bin/env python3
"""
Unit tests for Analyzer object
"""
import os
import unittest

from osaca.analyzer import Analyzer
from osaca.parser import ParserAArch64v81, ParserX86ATT


class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.parser_AArch = ParserAArch64v81()
        self.parser_x86 = ParserX86ATT()
        with open(self._find_file('triad-arm-iaca.s')) as f:
            triad_code_arm = f.read()
        with open(self._find_file('triad-x86-iaca.s')) as f:
            triad_code_x86 = f.read()
        self.parsed_AArch = self.parser_AArch.parse_file(triad_code_arm)
        self.parsed_x86 = self.parser_x86.parse_file(triad_code_x86)

    #################
    # Test
    #################

    def test_marker_detection_AArch64(self):
        analyzer = Analyzer(self.parsed_AArch, 'AArch64')
        self.assertEquals(len(analyzer.kernel), 138)
        self.assertEquals(analyzer.kernel[0].line_number, 307)
        self.assertEquals(analyzer.kernel[-1].line_number, 444)

    def test_marker_detection_x86(self):
        analyzer = Analyzer(self.parsed_x86, 'x86')
        self.assertEquals(len(analyzer.kernel), 9)
        self.assertEquals(analyzer.kernel[0].line_number, 146)
        self.assertEquals(analyzer.kernel[-1].line_number, 154)

    def test_marker_matching_AArch64(self):
        # preparation
        bytes_1_line = '.byte     213,3,32,31\n'
        bytes_2_lines_1 = '.byte     213,3,32\n' + '.byte 31\n'
        bytes_2_lines_2 = '.byte     213,3\n' + '.byte 32,31\n'
        bytes_2_lines_3 = '.byte     213\n' + '.byte 3,32,31\n'
        bytes_3_lines_1 = '.byte     213,3\n' + '.byte     32\n' + '.byte     31\n'
        bytes_3_lines_2 = '.byte     213\n' + '.byte     3,32\n' + '.byte     31\n'
        bytes_3_lines_3 = '.byte     213\n' + '.byte     3\n' + '.byte     32,31\n'
        bytes_4_lines = '.byte     213\n' + '.byte     3\n' + '.byte     32\n' + '.byte     31\n'
        mov_start_1 = 'mov      x1, #111\n'
        mov_start_2 = 'mov      x1, 111  // should work as well\n'
        mov_end_1 = 'mov      x1, #222 // preferred way\n'
        mov_end_2 = 'mov      x1, 222\n'
        prologue = (
            'mov x12, xzr\n'
            + '\tldp x9, x10, [sp, #16]      // 8-byte Folded Reload\n'
            + '     .p2align    6\n'
        )
        kernel = (
            '.LBB0_28:\n'
            + 'fmul    v7.2d, v7.2d, v19.2d\n'
            + 'stp q0, q1, [x10, #-32]\n'
            + 'b.ne    .LBB0_28\n'
        )
        epilogue = '.LBB0_29:   //   Parent Loop BB0_20 Depth=1\n' + 'bl    dummy\n'
        kernel_length = len(list(filter(None, kernel.split('\n'))))

        bytes_variations = [
            bytes_1_line,
            bytes_2_lines_1,
            bytes_2_lines_2,
            bytes_2_lines_3,
            bytes_3_lines_1,
            bytes_3_lines_2,
            bytes_3_lines_3,
            bytes_4_lines,
        ]
        mov_start_variations = [mov_start_1, mov_start_2]
        mov_end_variations = [mov_end_1, mov_end_2]
        # actual tests
        for mov_start_var in mov_start_variations:
            for bytes_var_1 in bytes_variations:
                for mov_end_var in mov_end_variations:
                    for bytes_var_2 in bytes_variations:
                        sample_code = (
                            prologue
                            + mov_start_var
                            + bytes_var_1
                            + kernel
                            + mov_end_var
                            + bytes_var_2
                            + epilogue
                        )
                        with self.subTest(
                            mov_start=mov_start_var,
                            bytes_start=bytes_var_1,
                            mov_end=mov_end_var,
                            bytes_end=bytes_var_2,
                        ):
                            sample_parsed = self.parser_AArch.parse_file(sample_code)
                            analyzer = Analyzer(sample_parsed, 'AArch64')
                            self.assertEquals(len(analyzer.kernel), kernel_length)
                            kernel_start = len(
                                list(
                                    filter(
                                        None, (prologue + mov_start_var + bytes_var_1).split('\n')
                                    )
                                )
                            )
                            parsed_kernel = self.parser_AArch.parse_file(
                                kernel, start_line=kernel_start
                            )
                            self.assertEquals(analyzer.kernel, parsed_kernel)

    def test_marker_matching_x86(self):
        # preparation
        bytes_1_line = '.byte     100,103,144\n'
        bytes_2_lines_1 = '.byte     100,103\n' + '.byte 144\n'
        bytes_2_lines_2 = '.byte     100\n' + '.byte 103,144\n'
        bytes_3_lines = (
            '.byte     100 # IACA MARKER UTILITY\n'
            + '.byte     103 # IACA MARKER UTILITY\n'
            + '.byte     144 # IACA MARKER UTILITY\n'
        )
        mov_start_1 = 'movl      $111, %ebx # IACA START\n'
        mov_start_2 = 'mov      $111, %ebx # IACA START\n'
        mov_end_1 = 'movl      $222, %ebx # IACA END\n'
        mov_end_2 = 'mov      $222, %ebx # IACA END\n'
        prologue = 'movl    -92(%rbp), %r11d\n' + 'movl      $111, %ebx\n'
        kernel = (
            'vfmadd132sd (%r15,%rcx,8), %xmm5, %xmm0\n'
            + 'vmovsd  %xmm0, (%r14,%rcx,8)\n'
            + 'cmpl    %ebx, %ecx\n'
            + 'jge .L8\n'
        )
        epilogue = '.LE9:\t\t#12.2\n' 'call    dummy\n'
        kernel_length = len(list(filter(None, kernel.split('\n'))))

        bytes_variations = [bytes_1_line, bytes_2_lines_1, bytes_2_lines_2, bytes_3_lines]
        mov_start_variations = [mov_start_1, mov_start_2]
        mov_end_variations = [mov_end_1, mov_end_2]
        # actual tests
        for mov_start_var in mov_start_variations:
            for bytes_var_1 in bytes_variations:
                for mov_end_var in mov_end_variations:
                    for bytes_var_2 in bytes_variations:
                        sample_code = (
                            prologue
                            + mov_start_var
                            + bytes_var_1
                            + kernel
                            + mov_end_var
                            + bytes_var_2
                            + epilogue
                        )
                        with self.subTest(
                            mov_start=mov_start_var,
                            bytes_start=bytes_var_1,
                            mov_end=mov_end_var,
                            bytes_end=bytes_var_2,
                        ):
                            sample_parsed = self.parser_x86.parse_file(sample_code)
                            analyzer = Analyzer(sample_parsed, 'x86')
                            self.assertEquals(len(analyzer.kernel), kernel_length)
                            kernel_start = len(
                                list(
                                    filter(
                                        None, (prologue + mov_start_var + bytes_var_1).split('\n')
                                    )
                                )
                            )
                            parsed_kernel = self.parser_x86.parse_file(
                                kernel, start_line=kernel_start
                            )
                            self.assertEquals(analyzer.kernel, parsed_kernel)

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, 'test_files', name)
        assert os.path.exists(name)
        return name


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyzer)
    unittest.TextTestRunner(verbosity=2).run(suite)
