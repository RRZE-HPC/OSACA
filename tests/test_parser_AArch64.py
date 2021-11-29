#!/usr/bin/env python3
"""
Unit tests for ARMv8 AArch64 assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import ParserAArch64, IdentifierOperand, DirectiveOperand, ImmediateOperand, PrefetchOperand, RegisterOperand, MemoryOperand, InstructionForm


class TestParserAArch64(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = ParserAArch64()
        with open(self._find_file("triad_arm_iaca.s")) as f:
            self.triad_code = f.read()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(self._get_comment(self.parser, "// some comments"), "some comments")
        self.assertEqual(
            self._get_comment(self.parser, "\t\t//AA BB CC \t end \t"), "AA BB CC end"
        )
        self.assertEqual(
            self._get_comment(self.parser, "\t//// comment //// comment"),
            "// comment //// comment",
        )

    def test_label_parser(self):
        self.assertEqual(self._get_label(self.parser, "main:")["name"], "main")
        self.assertEqual(self._get_label(self.parser, "..B1.10:")["name"], "..B1.10")
        self.assertEqual(self._get_label(self.parser, ".2.3_2_pack.3:")["name"], ".2.3_2_pack.3")
        self.assertEqual(self._get_label(self.parser, ".L1:\t\t\t//label1")["name"], ".L1")
        self.assertEqual(
            " ".join(self._get_label(self.parser, ".L1:\t\t\t//label1")["COMMENT"]),
            "label1",
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, "\t.cfi_startproc")

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, "\t.text")["name"], "text")
        self.assertEqual(len(self._get_directive(self.parser, "\t.text")["parameters"]), 0)
        self.assertEqual(self._get_directive(self.parser, "\t.align\t16,0x90")["name"], "align")
        self.assertEqual(len(self._get_directive(self.parser, "\t.align\t16,0x90")["parameters"]), 2)
        self.assertEqual(
            self._get_directive(self.parser, "\t.align\t16,0x90")["parameters"][1], "0x90"
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       //IACA START")[
                "name"
            ],
            "byte",
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       //IACA START")[
                "parameters"
            ][2],
            "144",
        )
        self.assertEqual(
            " ".join(
                self._get_directive(self.parser, "        .byte 100,103,144       //IACA START")[
                    "COMMENT"
                ]
            ),
            "IACA START",
        )

    def test_parse_instruction(self):
        instr1 = "\t\tvcvt.F32.S32 w1, w2\t\t\t//12.27"
        instr2 = "b.lo        ..B1.4 \t"
        instr3 = "        mov x2,#0x222          //NOT IACA END"
        instr4 = "str x28, [sp, x1, lsl #4] //12.9"
        instr5 = "ldr x0, [x0, #:got_lo12:q2c]"
        instr6 = "adrp    x0, :got:visited"
        instr7 = "fadd    v17.2d, v16.2d, v1.2d"

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        parsed_7 = self.parser.parse_instruction(instr7)

        self.assertEqual(parsed_1["MNEMONIC"], "vcvt.F32.S32")
        self.assertEqual(parsed_1["OPERANDS"][0].regid, "1")
        self.assertEqual(parsed_1["OPERANDS"][0].prefix, "w")
        self.assertEqual(parsed_1["OPERANDS"][1].regid, "2")
        self.assertEqual(parsed_1["OPERANDS"][1].prefix, "w")
        self.assertEqual(parsed_1["COMMENT"], "12.27")

        self.assertEqual(parsed_2["MNEMONIC"], "b.lo")
        self.assertEqual(parsed_2["OPERANDS"][0].name, "..B1.4")
        self.assertEqual(len(parsed_2["OPERANDS"]), 1)
        self.assertIsNone(parsed_2["COMMENT"])

        self.assertEqual(parsed_3["MNEMONIC"], "mov")
        self.assertEqual(parsed_3["OPERANDS"][0].regid, "2")
        self.assertEqual(parsed_3["OPERANDS"][0].prefix, "x")
        self.assertEqual(parsed_3["OPERANDS"][1].value, int("0x222", 0))
        self.assertEqual(parsed_3["COMMENT"], "NOT IACA END")

        self.assertEqual(parsed_4["MNEMONIC"], "str")
        self.assertIsNone(parsed_4["OPERANDS"][1].offset)
        self.assertEqual(parsed_4["OPERANDS"][1].base.name, "sp")
        self.assertEqual(parsed_4["OPERANDS"][1].base.regid, "31")
        self.assertEqual(parsed_4["OPERANDS"][1].base.prefix, "x")
        self.assertEqual(parsed_4["OPERANDS"][1].index.regid, "1")
        self.assertEqual(parsed_4["OPERANDS"][1].index.prefix, "x")
        self.assertEqual(parsed_4["OPERANDS"][1].scale, 16)
        self.assertEqual(parsed_4["OPERANDS"][0].regid, "28")
        self.assertEqual(parsed_4["OPERANDS"][0].prefix, "x")
        self.assertEqual(parsed_4["COMMENT"], "12.9")

        self.assertEqual(parsed_5["MNEMONIC"], "ldr")
        self.assertEqual(parsed_5["OPERANDS"][0].regid, "0")
        self.assertEqual(parsed_5["OPERANDS"][0].prefix, "x")
        self.assertEqual(parsed_5["OPERANDS"][1].offset.name, "q2c")
        self.assertEqual(parsed_5["OPERANDS"][1].offset.relocation, ":got_lo12:")
        self.assertEqual(parsed_5["OPERANDS"][1].base.regid, "0")
        self.assertEqual(parsed_5["OPERANDS"][1].base.prefix, "x")
        self.assertIsNone(parsed_5["OPERANDS"][1].index)
        self.assertEqual(parsed_5["OPERANDS"][1].scale, 1)

        self.assertEqual(parsed_6["MNEMONIC"], "adrp")
        self.assertEqual(parsed_6["OPERANDS"][0].regid, "0")
        self.assertEqual(parsed_6["OPERANDS"][0].prefix, "x")
        self.assertEqual(parsed_6["OPERANDS"][1].relocation, ":got:")
        self.assertEqual(parsed_6["OPERANDS"][1].name, ":got:visited")

        self.assertEqual(parsed_7["MNEMONIC"], "fadd")
        self.assertEqual(parsed_7["OPERANDS"][0].regid, "17")
        self.assertEqual(parsed_7["OPERANDS"][0].prefix, "v")
        self.assertEqual(parsed_7["OPERANDS"][0].lanes, "2")
        self.assertEqual(parsed_7["OPERANDS"][0].shape, "d")
        self.assertEqual(self.parser.get_full_reg_name(parsed_7["OPERANDS"][2]), "v1.2d")

    def test_parse_line(self):
        line_comment = "// -- Begin  main"
        line_label = ".LBB0_1:              // =>This Inner Loop Header: Depth=1"
        line_directive = ".cfi_def_cfa w29, -16"
        line_instruction = "ldr s0, [x11, w10, sxtw #2]    // = <<2"
        line_prefetch = "prfm    pldl1keep, [x26, #2048] //HPL"
        line_preindexed = "stp x29, x30, [sp, #-16]!"
        line_postindexed = "ldp q2, q3, [x11], #64"
        line_5_operands = "fcmla z26.d, p0/m, z29.d, z21.d, #90"

        instruction_form_1 = InstructionForm("// -- Begin  main", comment="-- Begin main", line_number=1)
        instruction_form_2 = InstructionForm(
            ".LBB0_1:              // =>This Inner Loop Header: Depth=1",
            comment="=>This Inner Loop Header: Depth=1",
            label=IdentifierOperand(".LBB0_1"),
            line_number=2
        )
        instruction_form_3 = InstructionForm(
            ".cfi_def_cfa w29, -16",
            directive=DirectiveOperand(".cfi_def_cfa w29, -16", directive="cfi_def_cfa", parameters=["w29", "-16"]),
            line_number=3
        )
        instruction_form_4 = InstructionForm(
            "ldr s0, [x11, w10, sxtw #2]    // = <<2",
            mnemonic="ldr",
            operands=[
                RegisterOperand("s0", width=32, prefix="s", regid="0", regtype="vector"),
                MemoryOperand(
                    "[x11, w10, sxtw #2]",
                    base=RegisterOperand("x11", width=64, prefix="x", regid="11", regtype="gpr"),
                    index=RegisterOperand("w10", width=32, prefix="w", regid="10", regtype="gpr"),
                    scale=4
                ),
            ],
            comment="= <<2",
            line_number=4
        )
        instruction_form_5 = InstructionForm(
            "prfm    pldl1keep, [x26, #2048] //HPL",
            mnemonic="prfm",
            operands=[
                PrefetchOperand("PLD", "L1", "KEEP"),
                MemoryOperand("[x26, #2048]", base=RegisterOperand("x26", width=64, prefix="x", regid="26", regtype="gpr"), offset=ImmediateOperand(2048))
            ],
            comment="HPL",
            line_number=5
        )
        instruction_form_6 = InstructionForm(
            "stp x29, x30, [sp, #-16]!",
            mnemonic="stp",
            operands=[
                RegisterOperand("x29", width=64, prefix="x", regid="29", regtype="gpr"),
                RegisterOperand("x30", width=64, prefix="x", regid="30", regtype="gpr"),
                MemoryOperand("[sp, #-16]!", base=RegisterOperand("sp", width=64, prefix="x", regid="31", regtype="gpr"), offset=ImmediateOperand(-16), pre_indexed=True)
            ],
            line_number=6
        )
        instruction_form_7 = InstructionForm(
            "ldp q2, q3, [x11], #64",
            mnemonic="ldp",
            operands=[
                RegisterOperand("q2", width=128, prefix="q", regid="2", regtype="vector"),
                RegisterOperand("q3", width=128, prefix="q", regid="3", regtype="vector"),
                MemoryOperand("[x11]", base=RegisterOperand("x11", width=64, prefix="x", regid="11", regtype="gpr"), post_indexed=True, indexed_val=ImmediateOperand(64))
            ],
            line_number=7
        )
        instruction_form_8 = InstructionForm(
            "fcmla z26.d, p0/m, z29.d, z21.d, #90",
            mnemonic="fcmla",
            operands=[
                RegisterOperand("z26", width=512, prefix="z", regid="26", regtype="vector", shape="d"),
                RegisterOperand("p0/m", width=64, prefix="p", regid="0", regtype="predicate", zeroing=False),
                RegisterOperand("z29", width=512, prefix="z", regid="29", regtype="vector", shape="d"),
                RegisterOperand("z21", width=512, prefix="z", regid="21", regtype="vector", shape="d"),
                ImmediateOperand(90)
            ],
            line_number=8
        )

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        parsed_4 = self.parser.parse_line(line_instruction, 4)
        parsed_5 = self.parser.parse_line(line_prefetch, 5)
        parsed_6 = self.parser.parse_line(line_preindexed, 6)
        parsed_7 = self.parser.parse_line(line_postindexed, 7)
        parsed_8 = self.parser.parse_line(line_5_operands, 8)

        self.assertEqual(parsed_1, instruction_form_1)
        self.assertEqual(parsed_2, instruction_form_2)
        self.assertEqual(parsed_3, instruction_form_3)
        self.assertEqual(parsed_4, instruction_form_4)
        self.assertEqual(parsed_5, instruction_form_5)
        self.assertEqual(parsed_6, instruction_form_6)
        self.assertEqual(parsed_7, instruction_form_7)
        self.assertEqual(parsed_8, instruction_form_8)

    def test_parse_file(self):
        parsed = self.parser.parse_file(self.triad_code)
        self.assertEqual(parsed[0].line_number, 1)
        self.assertEqual(len(parsed), 645)

    def test_normalize_imd(self):
        imd_decimal_1 = {"value": "79"}
        imd_hex_1 = {"value": "0x4f"}
        imd_decimal_2 = {"value": "8"}
        imd_hex_2 = {"value": "0x8"}
        imd_float_11 = {"float": {"mantissa": "0.79", "e_sign": "+", "exponent": "2"}}
        imd_float_12 = {"float": {"mantissa": "790.0", "e_sign": "-", "exponent": "1"}}
        imd_double_11 = {"double": {"mantissa": "0.79", "e_sign": "+", "exponent": "2"}}
        imd_double_12 = {"double": {"mantissa": "790.0", "e_sign": "-", "exponent": "1"}}
        identifier = {"identifier": {"name": "..B1.4"}}

        value1 = self.parser.normalize_imd(imd_decimal_1)
        self.assertEqual(value1, self.parser.normalize_imd(imd_hex_1))
        self.assertEqual(
            self.parser.normalize_imd(imd_decimal_2),
            self.parser.normalize_imd(imd_hex_2),
        )
        self.assertEqual(self.parser.normalize_imd(imd_float_11), value1)
        self.assertEqual(self.parser.normalize_imd(imd_float_12), value1)
        self.assertEqual(self.parser.normalize_imd(imd_double_11), value1)
        self.assertEqual(self.parser.normalize_imd(imd_double_12), value1)
        self.assertEqual(self.parser.normalize_imd(identifier), identifier)

    def test_multiple_regs(self):
        instr_range = "PUSH {x5-x7}"
        instr_list = "POP {x5, x6, x7}"
        instr_range_with_index = "ld4 {v0.S - v3.S}[2]"
        instr_list_with_index = "ld4 {v0.S, v1.S, v2.S, v3.S}[2]"
        instr_range_single = "dummy  { z1.d }"
        reg_list = [
            RegisterOperand("x5", prefix="x", width=64, regid="5", regtype="gpr"),
            RegisterOperand("x6", prefix="x", width=64, regid="6", regtype="gpr"),
            RegisterOperand("x7", prefix="x", width=64, regid="7", regtype="gpr"),
        ]
        reg_list_idx = [
            RegisterOperand("v0.S", prefix="v", width=128, regid="0", regtype="vector", shape="s", index="2"),
            RegisterOperand("v1.S", prefix="v", width=128, regid="1", regtype="vector", shape="s", index="2"),
            RegisterOperand("v2.S", prefix="v", width=128, regid="2", regtype="vector", shape="s", index="2"),
            RegisterOperand("v3.S", prefix="v", width=128, regid="3", regtype="vector", shape="s", index="2"),
        ]
        reg_list_single = [RegisterOperand("z1.d", prefix="z", width=512, regid="1", regtype="vector", shape="d")]

        prange = self.parser.parse_line(instr_range)
        plist = self.parser.parse_line(instr_list)
        p_idx_range = self.parser.parse_line(instr_range_with_index)
        p_idx_list = self.parser.parse_line(instr_list_with_index)
        p_single = self.parser.parse_line(instr_range_single)

        for idx in range(len(prange.operands)):
            self.assertEqual(prange.operands[idx], reg_list[idx])
        for idx in range(len(plist.operands)):
            self.assertEqual(plist.operands[idx], reg_list[idx])
        for idx in range(len(p_idx_range.operands)):
            self.assertEqual(p_idx_range.operands[idx], reg_list_idx[idx])
        for idx in range(len(p_idx_list.operands)):
            self.assertEqual(p_idx_list.operands[idx], reg_list_idx[idx])
        self.assertEqual(p_single.operands, reg_list_single)

    def test_reg_dependency(self):
        reg_1_1 = RegisterOperand("b1", width=8, prefix="b", regid="1", regtype="vector")
        reg_1_2 = RegisterOperand("h1", width=16, prefix="h", regid="1", regtype="vector")
        reg_1_3 = RegisterOperand("s1", width=32, prefix="s", regid="1", regtype="vector")
        reg_1_4 = RegisterOperand("d1", width=64, prefix="d", regid="1", regtype="vector")
        reg_1_5 = RegisterOperand("q1", width=128, prefix="q", regid="1", regtype="vector")
        reg_2_1 = RegisterOperand("w2", width=32, prefix="w", regid="2", regtype="gpr")
        reg_2_2 = RegisterOperand("x2", width=64, prefix="x", regid="2", regtype="gpr")
        reg_v1_1 = RegisterOperand("v11", width=128, prefix="v", regid="11", regtype="vector", lanes=16, shape="b")
        reg_v1_2 = RegisterOperand("v11", width=128, prefix="v", regid="11", regtype="vector", lanes=8, shape="h")
        reg_v1_3 = RegisterOperand("v11", width=128, prefix="v", regid="11", regtype="vector", lanes=4, shape="s")
        reg_v1_4 = RegisterOperand("v11", width=128, prefix="v", regid="11", regtype="vector", lanes=2, shape="d")

        reg_b5 = RegisterOperand("b5", width=8, prefix="b", regid="5", regtype="vector")
        reg_q15 = RegisterOperand("q15", width=128, prefix="q", regid="15", regtype="vector")
        reg_v10 = RegisterOperand("v10", width=128, prefix="v", regid="10", regtype="vector", lanes=4, shape="s")
        reg_v20 = RegisterOperand("v20", width=128, prefix="v", regid="20", regtype="vector", lanes=2, shape="d")

        reg_1 = [reg_1_1, reg_1_2, reg_1_3, reg_1_4, reg_1_5]
        reg_2 = [reg_2_1, reg_2_2]
        reg_v = [reg_v1_1, reg_v1_2, reg_v1_3, reg_v1_4]
        reg_others = [reg_b5, reg_q15, reg_v10, reg_v20]
        regs = reg_1 + reg_2 + reg_v + reg_others

        # test each register against each other
        for ri in reg_1:
            for rj in regs:
                assert_value = True if rj in reg_1 else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_2:
            for rj in regs:
                assert_value = True if rj in reg_2 else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_v:
            for rj in regs:
                assert_value = True if rj in reg_v else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_others:
            for rj in regs:
                assert_value = True if rj == ri else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)

    ##################
    # Helper functions
    ##################
    def _get_comment(self, parser, comment):
        return " ".join(parser.process_operand(parser.comment.parseString(comment, parseAll=True).asDict())["COMMENT"])

    def _get_label(self, parser, label):
        return parser.process_operand(parser.label.parseString(label, parseAll=True).asDict())["LABEL"]

    def _get_directive(self, parser, directive):
        return parser.process_operand(parser.directive.parseString(directive, parseAll=True).asDict())["DIRECTIVE"]

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, "test_files", name)
        assert os.path.exists(name)
        return name


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserAArch64)
    unittest.TextTestRunner(verbosity=2).run(suite)
