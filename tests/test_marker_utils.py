#!/usr/bin/env python3
"""
Unit tests for IACA/OSACA marker utilities
"""
import os
import unittest
from collections import OrderedDict

from osaca.semantics import (
    reduce_to_section,
    find_basic_blocks,
    find_jump_labels,
    find_basic_loop_bodies,
)
from osaca.parser import ParserAArch64, ParserX86ATT


class TestMarkerUtils(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser_AArch = ParserAArch64()
        self.parser_x86 = ParserX86ATT()
        with open(self._find_file("triad_arm_iaca.s")) as f:
            triad_code_arm = f.read()
        with open(self._find_file("triad_x86_iaca.s")) as f:
            triad_code_x86 = f.read()
        self.parsed_AArch = self.parser_AArch.parse_file(triad_code_arm)
        self.parsed_x86 = self.parser_x86.parse_file(triad_code_x86)

    #################
    # Test
    #################

    def test_marker_detection_AArch64(self):
        kernel = reduce_to_section(self.parsed_AArch, "AArch64")
        self.assertEqual(len(kernel), 138)
        self.assertEqual(kernel[0].line_number, 307)
        self.assertEqual(kernel[-1].line_number, 444)

    def test_marker_detection_x86(self):
        kernel = reduce_to_section(self.parsed_x86, "x86")
        self.assertEqual(len(kernel), 9)
        self.assertEqual(kernel[0].line_number, 146)
        self.assertEqual(kernel[-1].line_number, 154)

    def test_marker_matching_AArch64(self):
        # preparation
        bytes_1_line = ".byte     213,3,32,31\n"
        bytes_2_lines_1 = ".byte     213,3,32\n" + ".byte 31\n"
        bytes_2_lines_2 = ".byte     213,3\n" + ".byte 32,31\n"
        bytes_2_lines_3 = ".byte     213\n" + ".byte 3,32,31\n"
        bytes_3_lines_1 = ".byte     213,3\n" + ".byte     32\n" + ".byte     31\n"
        bytes_3_lines_2 = ".byte     213\n" + ".byte     3,32\n" + ".byte     31\n"
        bytes_3_lines_3 = ".byte     213\n" + ".byte     3\n" + ".byte     32,31\n"
        bytes_4_lines = ".byte     213\n" + ".byte     3\n" + ".byte     32\n" + ".byte     31\n"
        mov_start_1 = "mov      x1, #111\n"
        mov_start_2 = "mov      x1, 111  // should work as well\n"
        mov_end_1 = "mov      x1, #222 // preferred way\n"
        mov_end_2 = "mov      x1, 222\n"
        prologue = (
            "mov x12, xzr\n"
            + "\tldp x9, x10, [sp, #16]      // 8-byte Folded Reload\n"
            + "     .p2align    6\n"
        )
        kernel = (
            ".LBB0_28:\n"
            + "fmul    v7.2d, v7.2d, v19.2d\n"
            + "stp q0, q1, [x10, #-32]\n"
            + "b.ne    .LBB0_28\n"
        )
        epilogue = ".LBB0_29:   //   Parent Loop BB0_20 Depth=1\n" + "bl    dummy\n"
        kernel_length = len(list(filter(None, kernel.split("\n"))))

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
                            sample_kernel = reduce_to_section(sample_parsed, "AArch64")
                            self.assertEqual(len(sample_kernel), kernel_length)
                            kernel_start = len(
                                list(
                                    filter(
                                        None, (prologue + mov_start_var + bytes_var_1).split("\n")
                                    )
                                )
                            )
                            parsed_kernel = self.parser_AArch.parse_file(
                                kernel, start_line=kernel_start
                            )
                            self.assertEqual(sample_kernel, parsed_kernel)

    def test_marker_matching_x86(self):
        # preparation
        bytes_1_line = ".byte     100,103,144\n"
        bytes_2_lines_1 = ".byte     100,103\n" + ".byte 144\n"
        bytes_2_lines_2 = ".byte     100\n" + ".byte 103,144\n"
        bytes_3_lines = (
            ".byte     100 # IACA MARKER UTILITY\n"
            + ".byte     103 # IACA MARKER UTILITY\n"
            + ".byte     144 # IACA MARKER UTILITY\n"
        )
        mov_start_1 = "movl      $111, %ebx # IACA START\n"
        mov_start_2 = "mov      $111, %ebx # IACA START\n"
        mov_end_1 = "movl      $222, %ebx # IACA END\n"
        mov_end_2 = "mov      $222, %ebx # IACA END\n"
        prologue = "movl    -92(%rbp), %r11d\n" + "movl      $111, %ebx\n"
        kernel = (
            "vfmadd132sd (%r15,%rcx,8), %xmm5, %xmm0\n"
            + "vmovsd  %xmm0, (%r14,%rcx,8)\n"
            + "cmpl    %ebx, %ecx\n"
            + "jge .L8\n"
        )
        epilogue = ".LE9:\t\t#12.2\n" "call    dummy\n"
        kernel_length = len(list(filter(None, kernel.split("\n"))))

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
                            sample_kernel = reduce_to_section(sample_parsed, "x86")
                            self.assertEqual(len(sample_kernel), kernel_length)
                            kernel_start = len(
                                list(
                                    filter(
                                        None, (prologue + mov_start_var + bytes_var_1).split("\n")
                                    )
                                )
                            )
                            parsed_kernel = self.parser_x86.parse_file(
                                kernel, start_line=kernel_start
                            )
                            self.assertEqual(sample_kernel, parsed_kernel)

    def test_marker_special_cases_AArch(self):
        bytes_line = ".byte     213,3,32,31\n"
        start_marker = "mov      x1, #111\n" + bytes_line
        end_marker = "mov      x1, #222\n" + bytes_line
        prologue = "dup v0.2d, x14\n" "neg x9, x9\n" ".p2align    6\n"
        kernel = (
            ".LBB0_28:\n"
            + "fmul    v7.2d, v7.2d, v19.2d\n"
            + "stp q0, q1, [x10, #-32]\n"
            + "b.ne    .LBB0_28\n"
        )
        epilogue = ".LBB0_29:   //   Parent Loop BB0_20 Depth=1\n" "bl    dummy\n"

        samples = [
            # (test name,
            #  ignored prologue, section to be extraced, ignored epilogue)
            ("markers", prologue + start_marker, kernel, end_marker + epilogue),
            ("marker at file start", start_marker, kernel, end_marker + epilogue),
            ("no start marker", "", prologue + kernel, end_marker + epilogue),
            ("marker at file end", prologue + start_marker, kernel, end_marker),
            ("no end marker", prologue + start_marker, kernel + epilogue, ""),
            ("empty kernel", prologue + start_marker, "", end_marker + epilogue),
        ]

        for test_name, pro, kernel, epi in samples:
            code = pro + kernel + epi
            parsed = self.parser_AArch.parse_file(code)
            test_kernel = reduce_to_section(parsed, "AArch64")
            if kernel:
                kernel_length = len(kernel.strip().split("\n"))
            else:
                kernel_length = 0
            self.assertEqual(
                len(test_kernel),
                kernel_length,
                msg="Invalid exctracted kernel length on {!r} sample".format(test_name),
            )
            if pro:
                kernel_start = len((pro).strip().split("\n"))
            else:
                kernel_start = 0
            parsed_kernel = self.parser_AArch.parse_file(kernel, start_line=kernel_start)
            self.assertEqual(
                test_kernel,
                parsed_kernel,
                msg="Invalid exctracted kernel on {!r}".format(test_name),
            )

    def test_marker_special_cases_x86(self):
        bytes_line = ".byte     100\n" ".byte     103\n" ".byte     144\n"
        start_marker = "movl     $111, %ebx\n" + bytes_line
        end_marker = "movl     $222, %ebx\n" + bytes_line
        prologue = "movl    -88(%rbp), %r10d\n" "xorl    %r11d, %r11d\n" ".p2align 4,,10\n"
        kernel = (
            ".L3: #L3\n"
            "vmovsd  .LC1(%rip), %xmm0\n"
            "vmovsd  %xmm0, (%r15,%rcx,8)\n"
            "cmpl    %ecx, %ebx\n"
            "jle .L3\n"
        )
        epilogue = "leaq    -56(%rbp), %rsi\n" "movl    %r10d, -88(%rbp)\n" "call    timing\n"
        samples = [
            # (test name,
            #  ignored prologue, section to be extraced, ignored epilogue)
            ("markers", prologue + start_marker, kernel, end_marker + epilogue),
            ("marker at file start", start_marker, kernel, end_marker + epilogue),
            ("no start marker", "", prologue + kernel, end_marker + epilogue),
            ("marker at file end", prologue + start_marker, kernel, end_marker),
            ("no end marker", prologue + start_marker, kernel + epilogue, ""),
            ("empty kernel", prologue + start_marker, "", end_marker + epilogue),
        ]

        for test_name, pro, kernel, epi in samples:
            code = pro + kernel + epi
            parsed = self.parser_x86.parse_file(code)
            test_kernel = reduce_to_section(parsed, "x86")
            if kernel:
                kernel_length = len(kernel.strip().split("\n"))
            else:
                kernel_length = 0
            self.assertEqual(
                len(test_kernel),
                kernel_length,
                msg="Invalid exctracted kernel length on {!r} sample".format(test_name),
            )
            if pro:
                kernel_start = len((pro).strip().split("\n"))
            else:
                kernel_start = 0
            parsed_kernel = self.parser_x86.parse_file(kernel, start_line=kernel_start)
            self.assertEqual(
                test_kernel,
                parsed_kernel,
                msg="Invalid exctracted kernel on {!r}".format(test_name),
            )

    def test_find_jump_labels(self):
        self.assertEqual(
            find_jump_labels(self.parsed_x86),
            OrderedDict(
                [
                    (".LFB24", 10),
                    (".L4", 65),
                    (".L3", 79),
                    (".L2", 102),
                    (".L13", 111),
                    (".L12", 120),
                    (".L6", 132),
                    (".L10", 145),
                    (".L9", 161),
                    (".L8", 183),
                    (".L15", 252),
                    (".L26", 256),
                    (".L14", 259),
                    (".LFB25", 277),
                    (".L28", 289),
                ]
            ),
        )

        self.assertEqual(
            find_jump_labels(self.parsed_AArch),
            OrderedDict(
                [
                    ("triad", 18),
                    (".LBB0_3", 71),
                    (".LBB0_4", 76),
                    (".LBB0_5", 84),
                    (".LBB0_7", 92),
                    (".LBB0_8", 95),
                    (".LBB0_9", 106),
                    (".LBB0_11", 118),
                    (".LBB0_12", 133),
                    (".LBB0_14", 177),
                    (".LBB0_15", 190),
                    (".LBB0_16", 205),
                    (".LBB0_17", 208),
                    (".LBB0_18", 221),
                    (".LBB0_19", 228),
                    (".LBB0_20", 260),
                    (".LBB0_22", 272),
                    (".LBB0_24", 283),
                    (".LBB0_26", 290),
                    (".LBB0_28", 298),
                    (".LBB0_29", 306),
                    (".LBB0_31", 448),
                    (".LBB0_32", 458),
                    (".LBB0_33", 480),
                    (".LBB0_34", 484),
                    (".LBB0_35", 493),
                    (".LBB0_36", 504),
                    (".LBB0_37", 508),
                    (".LBB0_38", 518),
                    ("main", 574),
                ]
            ),
        )

    def test_find_basic_blocks(self):
        self.assertEqual(
            [
                (k, v[0]["line_number"], v[-1]["line_number"])
                for k, v in find_basic_blocks(self.parsed_x86).items()
            ],
            [
                (".LFB24", 11, 56),
                (".L4", 66, 74),
                (".L3", 80, 89),
                (".L2", 103, 112),
                (".L13", 112, 121),
                (".L12", 121, 125),
                (".L6", 133, 135),
                (".L10", 146, 154),
                (".L9", 162, 170),
                (".L8", 184, 187),
                (".L15", 253, 256),
                (".L26", 257, 259),
                (".L14", 260, 262),
                (".LFB25", 278, 290),
                (".L28", 290, 300),
            ],
        )

        self.assertEqual(
            [
                (k, v[0]["line_number"], v[-1]["line_number"])
                for k, v in find_basic_blocks(self.parsed_AArch).items()
            ],
            [
                ("triad", 19, 64),
                (".LBB0_3", 72, 77),
                (".LBB0_4", 77, 83),
                (".LBB0_5", 85, 89),
                (".LBB0_7", 93, 95),
                (".LBB0_8", 96, 105),
                (".LBB0_9", 107, 114),
                (".LBB0_11", 119, 134),
                (".LBB0_12", 134, 173),
                (".LBB0_14", 178, 191),
                (".LBB0_15", 191, 205),
                (".LBB0_16", 206, 208),
                (".LBB0_17", 209, 222),
                (".LBB0_18", 222, 228),
                (".LBB0_19", 229, 261),
                (".LBB0_20", 261, 269),
                (".LBB0_22", 273, 280),
                (".LBB0_24", 284, 286),
                (".LBB0_26", 291, 293),
                (".LBB0_28", 299, 307),
                (".LBB0_29", 307, 444),
                (".LBB0_31", 449, 459),
                (".LBB0_32", 459, 480),
                (".LBB0_33", 481, 484),
                (".LBB0_34", 485, 494),
                (".LBB0_35", 494, 504),
                (".LBB0_36", 505, 508),
                (".LBB0_37", 509, 518),
                (".LBB0_38", 519, 568),
                ("main", 575, 590),
            ],
        )

    def test_find_basic_loop_body(self):
        self.assertEqual(
            [
                (k, v[0]["line_number"], v[-1]["line_number"])
                for k, v in find_basic_loop_bodies(self.parsed_x86).items()
            ],
            [(".L4", 66, 74), (".L10", 146, 154), (".L28", 290, 300)],
        )

        self.assertEqual(
            [
                (k, v[0]["line_number"], v[-1]["line_number"])
                for k, v in find_basic_loop_bodies(self.parsed_AArch).items()
            ],
            [
                (".LBB0_12", 134, 173),
                (".LBB0_15", 191, 205),
                (".LBB0_18", 222, 228),
                (".LBB0_29", 307, 444),
                (".LBB0_32", 459, 480),
                (".LBB0_35", 494, 504),
            ],
        )

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarkerUtils)
    unittest.TextTestRunner(verbosity=2).run(suite)
