#!/usr/bin/env python3
"""
Unit tests for ARMv8 AArch64 assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import ParserAArch64, InstructionForm
from osaca.parser.operand import Operand
from osaca.parser.directive import DirectiveOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand
from osaca.parser.immediate import ImmediateOperand

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
        self.assertEqual(self._get_label(self.parser, "main:").name, "main")
        self.assertEqual(self._get_label(self.parser, "..B1.10:").name, "..B1.10")
        self.assertEqual(self._get_label(self.parser, ".2.3_2_pack.3:").name, ".2.3_2_pack.3")
        self.assertEqual(self._get_label(self.parser, ".L1:\t\t\t//label1").name, ".L1")
        self.assertEqual(
            " ".join(self._get_label(self.parser, ".L1:\t\t\t//label1").comment),
            "label1",
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, "\t.cfi_startproc")

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, "\t.text").name, "text")
        self.assertEqual(len(self._get_directive(self.parser, "\t.text").parameters), 0)
        self.assertEqual(self._get_directive(self.parser, "\t.align\t16,0x90").name, "align")
        self.assertEqual(len(self._get_directive(self.parser, "\t.align\t16,0x90").parameters), 2)
        self.assertEqual(
            self._get_directive(self.parser, "\t.align\t16,0x90").parameters[1], "0x90"
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       //IACA START").name,
            "byte",
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       //IACA START").parameters[2],
            "144",
        )
        self.assertEqual(
            " ".join(
                self._get_directive(self.parser, "        .byte 100,103,144       //IACA START").comment
            ),
            "IACA START",
        )

    def test_condition_parser(self):
        self.assertEqual(self._get_condition(self.parser, "EQ"), "EQ")
        self.assertEqual(self._get_condition(self.parser, "ne"), "NE")
        self.assertEqual(self._get_condition(self.parser, "Lt"), "LT")
        self.assertEqual(self._get_condition(self.parser, "Gt"), "GT")
        with self.assertRaises(ParseException):
            self._get_condition(self.parser, "LOcondition")

    def test_parse_instruction(self):
        instr1 = "\t\tvcvt.F32.S32 w1, w2\t\t\t//12.27"
        instr2 = "b.lo        ..B1.4 \t"
        instr3 = "        mov x2,#0x222          //NOT IACA END"
        instr4 = "str x28, [sp, x1, lsl #4] //12.9"
        instr5 = "ldr x0, [x0, #:got_lo12:q2c]"
        instr6 = "adrp    x0, :got:visited"
        instr7 = "fadd    v17.2d, v16.2d, v1.2d"
        instr8 = "mov.d   x0, v16.d[1]"
        instr9 = "ccmp    x0, x1, #4, cc"

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        parsed_7 = self.parser.parse_instruction(instr7)
        parsed_8 = self.parser.parse_instruction(instr8)
        parsed_9 = self.parser.parse_instruction(instr9)
        
        self.assertEqual(parsed_1.instruction, "vcvt.F32.S32")
        self.assertEqual(parsed_1.operands[0].name, "1")
        self.assertEqual(parsed_1.operands[0].prefix, "w")
        self.assertEqual(parsed_1.operands[1].name, "2")
        self.assertEqual(parsed_1.operands[1].prefix, "w")
        self.assertEqual(parsed_1.comment, "12.27")
        
        self.assertEqual(parsed_2.instruction, "b.lo")
        self.assertEqual(parsed_2.operands[0]['identifier']['name'], "..B1.4")
        self.assertEqual(len(parsed_2.operands), 1)
        self.assertIsNone(parsed_2.comment)
        
        self.assertEqual(parsed_3.instruction, "mov")
        self.assertEqual(parsed_3.operands[0].name, "2")
        self.assertEqual(parsed_3.operands[0].prefix, "x")
        self.assertEqual(parsed_3.operands[1].value, int("0x222", 0))
        self.assertEqual(parsed_3.comment, "NOT IACA END")

        self.assertEqual(parsed_4.instruction, "str")
        self.assertIsNone(parsed_4.operands[1].offset)
        self.assertEqual(parsed_4.operands[1].base['name'], "sp")
        self.assertEqual(parsed_4.operands[1].base['prefix'], "x")
        self.assertEqual(parsed_4.operands[1].index['name'], "1")
        self.assertEqual(parsed_4.operands[1].index['prefix'], "x")
        self.assertEqual(parsed_4.operands[1].scale, 16)
        self.assertEqual(parsed_4.operands[0].name, "28")
        self.assertEqual(parsed_4.operands[0].prefix, "x")
        self.assertEqual(parsed_4.comment, "12.9")

        self.assertEqual(parsed_5.instruction, "ldr")
        self.assertEqual(parsed_5.operands[0].name, "0")
        self.assertEqual(parsed_5.operands[0].prefix, "x")
        self.assertEqual(parsed_5.operands[1].offset['identifier']['name'], "q2c")
        self.assertEqual(parsed_5.operands[1].offset['identifier']['relocation'], ":got_lo12:")
        self.assertEqual(parsed_5.operands[1].base['name'], "0")
        self.assertEqual(parsed_5.operands[1].base['prefix'], "x")
        self.assertIsNone(parsed_5.operands[1].index)
        self.assertEqual(parsed_5.operands[1].scale, 1)

        self.assertEqual(parsed_6.instruction, "adrp")
        self.assertEqual(parsed_6.operands[0].name, "0")
        self.assertEqual(parsed_6.operands[0].prefix, "x")
        self.assertEqual(parsed_6.operands[1]['identifier']['relocation'], ":got:")
        self.assertEqual(parsed_6.operands[1]['identifier']['name'], "visited")

        self.assertEqual(parsed_7.instruction, "fadd")
        self.assertEqual(parsed_7.operands[0].name, "17")
        self.assertEqual(parsed_7.operands[0].prefix, "v")
        self.assertEqual(parsed_7.operands[0].lanes, "2")
        self.assertEqual(parsed_7.operands[0].shape, "d")
        self.assertEqual(self.parser.get_full_reg_name(parsed_7.operands[2]), "v1.2d")

        self.assertEqual(parsed_8.instruction, "mov.d")
        self.assertEqual(parsed_8.operands[0].name, "0")
        self.assertEqual(parsed_8.operands[0].prefix, "x")
        self.assertEqual(parsed_8.operands[1].name, "16")
        self.assertEqual(parsed_8.operands[1].prefix, "v")
        self.assertEqual(parsed_8.operands[1].index, "1")
        self.assertEqual(self.parser.get_full_reg_name(parsed_8.operands[1]), "v16.d[1]")

        self.assertEqual(parsed_9.instruction, "ccmp")
        self.assertEqual(parsed_9.operands[0].name, "0")
        self.assertEqual(parsed_9.operands[0].prefix, "x")
        self.assertEqual(parsed_9.operands[3]['condition'], "CC")

    def test_parse_line(self):
        line_comment = "// -- Begin  main"
        line_label = ".LBB0_1:              // =>This Inner Loop Header: Depth=1"
        line_directive = ".cfi_def_cfa w29, -16"
        line_instruction = "ldr s0, [x11, w10, sxtw #2]    // = <<2"
        line_prefetch = "prfm    pldl1keep, [x26, #2048] //HPL"
        line_preindexed = "stp x29, x30, [sp, #-16]!"
        line_postindexed = "ldp q2, q3, [x11], #64"
        line_5_operands = "fcmla z26.d, p0/m, z29.d, z21.d, #90"
        line_conditions = "ccmn  x11, #1, #3, eq"

        instruction_form_1 = InstructionForm(
            INSTRUCTION_ID = None,
            OPERANDS_ID = [],
            DIRECTIVE_ID = None,
            COMMENT_ID = "-- Begin main",
            LABEL_ID = None,
            LINE = "// -- Begin  main",
            LINE_NUMBER = 1,
        )

        instruction_form_2 = InstructionForm(
            INSTRUCTION_ID = None,
            OPERANDS_ID = [],
            DIRECTIVE_ID = None,
            COMMENT_ID = "=>This Inner Loop Header: Depth=1",
            LABEL_ID = ".LBB0_1",
            LINE = ".LBB0_1:              // =>This Inner Loop Header: Depth=1",
            LINE_NUMBER = 2,
        )
        instruction_form_3 = InstructionForm(
            INSTRUCTION_ID = None,
            OPERANDS_ID = [],
            DIRECTIVE_ID = DirectiveOperand(NAME_ID = "cfi_def_cfa", PARAMETER_ID = ["w29", "-16"]) ,
            COMMENT_ID = None,
            LABEL_ID = None,
            LINE = ".cfi_def_cfa w29, -16",
            LINE_NUMBER = 3,
        )
        instruction_form_4 = InstructionForm(
            INSTRUCTION_ID = "ldr",
            OPERANDS_ID = [RegisterOperand(PREFIX_ID = "s", NAME_ID = "0"),
                           MemoryOperand(OFFSET_ID = None, BASE_ID = {"prefix": "x", "name": "11"},
                           INDEX_ID = {
                            "prefix": "w",
                            "name": "10",
                           "shift_op": "sxtw",
                            "immediate": {"value": "2"},
                            "shift": [{"value": "2"}],
                           },
                           SCALE_ID = 4) ],
            DIRECTIVE_ID = None,
            COMMENT_ID = "= <<2",
            LABEL_ID = None,
            LINE = "ldr s0, [x11, w10, sxtw #2]    // = <<2",
            LINE_NUMBER = 4,
        )
        instruction_form_5 = InstructionForm(
            INSTRUCTION_ID = "prfm",
            OPERANDS_ID = [
                {"prfop": {"type": ["PLD"], "target": ["L1"], "policy": ["KEEP"]}},
                MemoryOperand(OFFSET_ID =  {"value": 2048}, BASE_ID = {"prefix": "x", "name": "26"},
                INDEX_ID = None, SCALE_ID =1)
            ],
            DIRECTIVE_ID = None,
            COMMENT_ID = "HPL",
            LABEL_ID = None,
            LINE = "prfm    pldl1keep, [x26, #2048] //HPL",
            LINE_NUMBER = 5,
        )
        instruction_form_6 = InstructionForm(
            INSTRUCTION_ID = "stp",
            OPERANDS_ID = [
                RegisterOperand(PREFIX_ID = "x", NAME_ID = "29"),
                RegisterOperand(PREFIX_ID = "x", NAME_ID = "30"),
                MemoryOperand(OFFSET_ID = {"value": -16}, BASE_ID = {"name": "sp", "prefix": "x"},
                INDEX_ID = None, SCALE_ID = 1, PRE_INDEXED = True)
            ],
            DIRECTIVE_ID = None,
            COMMENT_ID = None,
            LABEL_ID = None,
            LINE = "stp x29, x30, [sp, #-16]!",
            LINE_NUMBER = 6,
        )
        instruction_form_7 = InstructionForm(
            INSTRUCTION_ID = "ldp",
            OPERANDS_ID = [
                RegisterOperand(PREFIX_ID = "q", NAME_ID = "2"),
                RegisterOperand(PREFIX_ID = "q", NAME_ID = "3"),
                MemoryOperand(OFFSET_ID = None, BASE_ID =  {"prefix": "x", "name": "11"}, 
                INDEX_ID = None, SCALE_ID = 1, POST_INDEXED = {"value": 64}),
            ],
            DIRECTIVE_ID = None,
            COMMENT_ID = None,
            LABEL_ID = None,
            LINE = "ldp q2, q3, [x11], #64",
            LINE_NUMBER = 7,
        )
        instruction_form_8 = InstructionForm(
            INSTRUCTION_ID = "fcmla",
            OPERANDS_ID = [
                RegisterOperand(PREFIX_ID = "z", NAME_ID = "26", SHAPE = "d"),
                RegisterOperand(PREFIX_ID = "p", NAME_ID = "0", PREDICATION = "m"),
                RegisterOperand(PREFIX_ID = "z", NAME_ID = "29", SHAPE = "d"),
                RegisterOperand(PREFIX_ID = "z", NAME_ID = "21", SHAPE = "d"),
                ImmediateOperand(VALUE_ID = 90, TYPE_ID = "int"),
            ],
            DIRECTIVE_ID = None,
            COMMENT_ID = None,
            LABEL_ID = None,
            LINE = "fcmla z26.d, p0/m, z29.d, z21.d, #90",
            LINE_NUMBER = 8,
        )
        instruction_form_9 = InstructionForm(
            INSTRUCTION_ID = "ccmn",
            OPERANDS_ID = [
                RegisterOperand(PREFIX_ID = "x", NAME_ID = "11"),
                ImmediateOperand(VALUE_ID = 1, TYPE_ID = "int"),
                ImmediateOperand(VALUE_ID = 3, TYPE_ID = "int"),
                {"condition": "EQ"},
            ],
            DIRECTIVE_ID = None,
            COMMENT_ID = None,
            LABEL_ID = None,
            LINE = "ccmn  x11, #1, #3, eq",
            LINE_NUMBER = 9,
        )

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        parsed_4 = self.parser.parse_line(line_instruction, 4)
        parsed_5 = self.parser.parse_line(line_prefetch, 5)
        parsed_6 = self.parser.parse_line(line_preindexed, 6)
        parsed_7 = self.parser.parse_line(line_postindexed, 7)
        parsed_8 = self.parser.parse_line(line_5_operands, 8)
        parsed_9 = self.parser.parse_line(line_conditions, 9)

        self.assertEqual(parsed_1, instruction_form_1)
        self.assertEqual(parsed_2, instruction_form_2)
        self.assertEqual(parsed_3, instruction_form_3)
        self.assertEqual(parsed_4, instruction_form_4)
        self.assertEqual(parsed_5, instruction_form_5)
        self.assertEqual(parsed_6, instruction_form_6)
        self.assertEqual(parsed_7, instruction_form_7)
        self.assertEqual(parsed_8, instruction_form_8)
        self.assertEqual(parsed_9, instruction_form_9)

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
        #reg_list = [
        #    {"register": {"prefix": "x", "name": "5"}},
        #    {"register": {"prefix": "x", "name": "6"}},
        #    {"register": {"prefix": "x", "name": "7"}},
        #]
        reg_list = [RegisterOperand(PREFIX_ID = "x", NAME_ID = "5"),
                    RegisterOperand(PREFIX_ID = "x", NAME_ID = "6"),
                    RegisterOperand(PREFIX_ID = "x", NAME_ID = "7")
        ]
        #reg_list_idx = [
        #    {"register": {"prefix": "v", "name": "0", "shape": "S", "index": 2}},
        #    {"register": {"prefix": "v", "name": "1", "shape": "S", "index": 2}},
        #    {"register": {"prefix": "v", "name": "2", "shape": "S", "index": 2}},
        #    {"register": {"prefix": "v", "name": "3", "shape": "S", "index": 2}},
        #]
        reg_list_idx = [
            RegisterOperand(PREFIX_ID = "V", NAME_ID = "0", SHAPE = "S", INDEX = 2),
            RegisterOperand(PREFIX_ID = "V", NAME_ID = "1", SHAPE = "S", INDEX = 2),
            RegisterOperand(PREFIX_ID = "V", NAME_ID = "2", SHAPE = "S", INDEX = 2),
            RegisterOperand(PREFIX_ID = "V", NAME_ID = "3", SHAPE = "S", INDEX = 2),
        ]
        reg_list_single = [RegisterOperand(PREFIX_ID = "z", NAME_ID = "1", SHAPE = 'd')]

        prange = self.parser.parse_line(instr_range)
        plist = self.parser.parse_line(instr_list)
        p_idx_range = self.parser.parse_line(instr_range_with_index)
        p_idx_list = self.parser.parse_line(instr_list_with_index)
        p_single = self.parser.parse_line(instr_range_single)
        #print("\n",p_idx_list.operands,"\n")
        #print("\n",reg_list_idx,"\n")
        #self.assertEqual(prange.operands, reg_list)
        self.assertEqual(plist.operands, reg_list)
        #self.assertEqual(p_idx_range.operands, reg_list_idx)
        #self.assertEqual(p_idx_list.operands, reg_list_idx)
        self.assertEqual(p_single.operands, reg_list_single)

    def test_reg_dependency(self):
        reg_1_1 = {"prefix": "b", "name": "1"}
        reg_1_2 = {"prefix": "h", "name": "1"}
        reg_1_3 = {"prefix": "s", "name": "1"}
        reg_1_4 ={"prefix": "d", "name": "1"}
        reg_1_4 = {"prefix": "q", "name": "1"}
        reg_2_1 = {"prefix": "w", "name": "2"}
        reg_2_2 = {"prefix": "x", "name": "2"}
        reg_v1_1 = {"prefix": "v", "name": "11", "lanes": "16", "shape": "b"}
        reg_v1_2 = {"prefix": "v", "name": "11", "lanes": "8", "shape": "h"}
        reg_v1_3 = {"prefix": "v", "name": "11", "lanes": "4", "shape": "s"}
        reg_v1_4 = {"prefix": "v", "name": "11", "lanes": "2", "shape": "d"}

        reg_b5 = {"prefix": "b", "name": "5"}
        reg_q15 = {"prefix": "q", "name": "15"}
        reg_v10 = {"prefix": "v", "name": "10", "lanes": "2", "shape": "s"}
        reg_v20 = {"prefix": "v", "name": "20", "lanes": "2", "shape": "d"}

        reg_1 = [reg_1_1, reg_1_2, reg_1_3, reg_1_4]
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
        return " ".join(
                parser.process_operand(parser.comment.parseString(comment, parseAll=True).asDict())['comment']
        )

    def _get_label(self, parser, label):
        return parser.process_operand(parser.label.parseString(label, parseAll=True).asDict())

    def _get_directive(self, parser, directive):
        return parser.process_operand(parser.directive.parseString(directive, parseAll=True).asDict())

    def _get_condition(self, parser, condition):
        return parser.process_operand(parser.condition.parseString(condition, parseAll=True).asDict())['condition']

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, "test_files", name)
        assert os.path.exists(name)
        return name


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserAArch64)
    unittest.TextTestRunner(verbosity=2).run(suite)