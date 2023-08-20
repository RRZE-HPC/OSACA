#!/usr/bin/env python3
"""
Unit tests for x86 AT&T assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import AttrDict, ParserX86ATT, InstructionForm

class TestParserX86ATT(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = ParserX86ATT()
        with open(self._find_file("triad_x86_iaca.s")) as f:
            self.triad_code = f.read()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(self._get_comment(self.parser, "# some comments"), "some comments")
        self.assertEqual(self._get_comment(self.parser, "\t\t#AA BB CC \t end \t"), "AA BB CC end")
        self.assertEqual(
            self._get_comment(self.parser, "\t## comment ## comment"),
            "# comment ## comment",
        )

    def test_label_parser(self):
        self.assertEqual(self._get_label(self.parser, "main:").name, "main")
        self.assertEqual(self._get_label(self.parser, "..B1.10:").name, "..B1.10")
        self.assertEqual(self._get_label(self.parser, ".2.3_2_pack.3:").name, ".2.3_2_pack.3")
        self.assertEqual(self._get_label(self.parser, ".L1:\t\t\t#label1").name, ".L1")
        self.assertEqual(
            " ".join(self._get_label(self.parser, ".L1:\t\t\t#label1").comment),
            "label1",
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, "\t.cfi_startproc")

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, "\t.text").name, "text")
        self.assertEqual(len(self._get_directive(self.parser, "\t.text").parameters), 0)
        self.assertEqual(self._get_directive(self.parser, "\t.align\t16,0x90").name, "align")
        self.assertEqual(len(self._get_directive(self.parser, "\t.align\t16,0x90").parameters), 2)
        self.assertEqual(len(self._get_directive(self.parser, ".text").parameters), 0)
        self.assertEqual(
            len(self._get_directive(self.parser, '.file\t1 "path/to/file.c"').parameters),
            2,
        )
        self.assertEqual(
            self._get_directive(self.parser, '.file\t1 "path/to/file.c"').parameters[1],
            '"path/to/file.c"',
        )
        self.assertEqual(
            self._get_directive(self.parser, "\t.set\tL$set$0,LECIE1-LSCIE1").parameters,
            ["L$set$0", "LECIE1-LSCIE1"],
        )
        self.assertEqual(
            self._get_directive(
                self.parser,
                "\t.section __TEXT,__eh_frame,coalesced,no_toc+strip_static_syms+live_support",
            ).parameters,
            [
                "__TEXT",
                "__eh_frame",
                "coalesced",
                "no_toc+strip_static_syms+live_support",
            ],
        )
        self.assertEqual(
            self._get_directive(
                self.parser, "\t.section\t__TEXT,__literal16,16byte_literals"
            ).parameters,
            ["__TEXT", "__literal16", "16byte_literals"],
        )
        self.assertEqual(
            self._get_directive(self.parser, "\t.align\t16,0x90").parameters[1], "0x90"
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       #IACA START").name,
            "byte",
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       #IACA START").parameters[2],
            "144",
        )
        self.assertEqual(
            " ".join(
                self._get_directive(self.parser, "        .byte 100,103,144       #IACA START").comment
            ),
            "IACA START",
        )

    def test_parse_instruction(self):
        instr1 = "\t\tvcvtsi2ss %edx, %xmm2, %xmm2\t\t\t#12.27"
        instr2 = "jb        ..B1.4 \t"
        instr3 = "        movl $222,%ebx          #IACA END"
        instr4 = "vmovss    %xmm4, -4(%rsp,%rax,8) #12.9"
        instr5 = "mov %ebx,var(,1)"
        instr6 = "lea (,%rax,8),%rbx"
        instr7 = "vinsertf128 $0x1, %xmm0, %ymm1, %ymm1"

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        parsed_7 = self.parser.parse_instruction(instr7)

        self.assertEqual(parsed_1.instruction, "vcvtsi2ss")
        self.assertEqual(parsed_1.operands[0].register.name, "edx")
        self.assertEqual(parsed_1.operands[1].register.name, "xmm2")
        self.assertEqual(parsed_1.comment, "12.27")

        self.assertEqual(parsed_2.instruction, "jb")
        self.assertEqual(parsed_2.operands[0].identifier.name, "..B1.4")
        self.assertEqual(len(parsed_2.operands), 1)
        self.assertIsNone(parsed_2.comment)

        self.assertEqual(parsed_3.instruction, "movl")
        self.assertEqual(parsed_3.operands[0].immediate.value, 222)
        self.assertEqual(parsed_3.operands[1].register.name, "ebx")
        self.assertEqual(parsed_3.comment, "IACA END")

        self.assertEqual(parsed_4.instruction, "vmovss")
        self.assertEqual(parsed_4.operands[1].memory.offset.value, -4)
        self.assertEqual(parsed_4.operands[1].memory.base.name, "rsp")
        self.assertEqual(parsed_4.operands[1].memory.index.name, "rax")
        self.assertEqual(parsed_4.operands[1].memory.scale, 8)
        self.assertEqual(parsed_4.operands[0].register.name, "xmm4")
        self.assertEqual(parsed_4.comment, "12.9")

        self.assertEqual(parsed_5.instruction, "mov")
        self.assertEqual(parsed_5.operands[1].memory.offset.identifier.name, "var")
        self.assertIsNone(parsed_5.operands[1].memory.base)
        self.assertIsNone(parsed_5.operands[1].memory.index)
        self.assertEqual(parsed_5.operands[1].memory.scale, 1)
        self.assertEqual(parsed_5.operands[0].register.name, "ebx")

        self.assertEqual(parsed_6.instruction, "lea")
        self.assertIsNone(parsed_6.operands[0].memory.offset)
        self.assertIsNone(parsed_6.operands[0].memory.base)
        self.assertEqual(parsed_6.operands[0].memory.index.name, "rax")
        self.assertEqual(parsed_6.operands[0].memory.scale, 8)
        self.assertEqual(parsed_6.operands[1].register.name, "rbx")

        self.assertEqual(parsed_7.operands[0].immediate.value, 0x1)
        self.assertEqual(parsed_7.operands[1].register.name, "xmm0")
        self.assertEqual(parsed_7.operands[2].register.name, "ymm1")
        self.assertEqual(parsed_7.operands[3].register.name, "ymm1")

    def test_parse_line(self):
        line_comment = "# -- Begin  main"
        line_label = "..B1.7:                         # Preds ..B1.6"
        line_directive = ".quad   .2.3_2__kmpc_loc_pack.2 #qed"
        line_instruction = "lea       2(%rax,%rax), %ecx #12.9"

        instruction_form_1 = InstructionForm(
            INSTRUCTION_ID =  None,
            OPERANDS_ID = [],
            DIRECTIVE_ID = None,
            COMMENT_ID = "-- Begin main",
            LABEL_ID = None,
            LINE = "# -- Begin  main",
            LINE_NUMBER = 1,
        )
        instruction_form_2 =  InstructionForm(
            INSTRUCTION_ID = None,
            OPERANDS_ID = [],
            DIRECTIVE_ID = None,
            COMMENT_ID = "Preds ..B1.6",
            LABEL_ID = "..B1.7",
            LINE = "..B1.7:                         # Preds ..B1.6",
            LINE_NUMBER = 2,
        )
        instruction_form_3 =  InstructionForm(
            INSTRUCTION_ID = None,
            OPERANDS_ID = [],
            DIRECTIVE_ID = {"name": "quad", "parameters": [".2.3_2__kmpc_loc_pack.2"]},
            COMMENT_ID = "qed",
            LABEL_ID = None,
            LINE = ".quad   .2.3_2__kmpc_loc_pack.2 #qed",
            LINE_NUMBER = 3,
        )
        instruction_form_4 =  InstructionForm(
            INSTRUCTION_ID = "lea",
            OPERANDS_ID = [
                {
                    "memory": {
                        "offset": {"value": 2},
                        "base": {"name": "rax"},
                        "index": {"name": "rax"},
                        "scale": 1,
                    }
                },
                {"register": {"name": "ecx"}},
            ],
            DIRECTIVE_ID = None,
            COMMENT_ID = "12.9",
            LABEL_ID = None,
            LINE = "lea       2(%rax,%rax), %ecx #12.9",
            LINE_NUMBER = 4,
        )

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        parsed_4 = self.parser.parse_line(line_instruction, 4)

        #self.assertEqual(parsed_1, instruction_form_1)
        #self.assertEqual(parsed_2, instruction_form_2)
        #self.assertEqual(parsed_3, instruction_form_3)
        #self.assertEqual(parsed_4, instruction_form_4)

    def test_parse_file(self):
        parsed = self.parser.parse_file(self.triad_code)
        self.assertEqual(parsed[0].line_number, 1)
        self.assertEqual(len(parsed), 353)

    def test_parse_register(self):
        register_str_1 = "%rax"
        register_str_2 = "%r9"
        register_str_3 = "%xmm1"
        register_str_4 = "%rip"

        parsed_reg_1 = {"register": {"name": "rax"}}
        parsed_reg_2 = {"register": {"name": "r9"}}
        parsed_reg_3 = {"register": {"name": "xmm1"}}
        parsed_reg_4 = {"register": {"name": "rip"}}

        self.assertEqual(self.parser.parse_register(register_str_1), parsed_reg_1)
        self.assertEqual(self.parser.parse_register(register_str_2), parsed_reg_2)
        self.assertEqual(self.parser.parse_register(register_str_3), parsed_reg_3)
        self.assertEqual(self.parser.parse_register(register_str_4), parsed_reg_4)
        self.assertIsNone(self.parser.parse_register("rax"))

    def test_normalize_imd(self):
        imd_decimal_1 = {"value": "79"}
        imd_hex_1 = {"value": "0x4f"}
        imd_decimal_2 = {"value": "8"}
        imd_hex_2 = {"value": "8"}
        self.assertEqual(
            self.parser.normalize_imd(imd_decimal_1),
            self.parser.normalize_imd(imd_hex_1),
        )
        self.assertEqual(
            self.parser.normalize_imd(imd_decimal_2),
            self.parser.normalize_imd(imd_hex_2),
        )

    def test_reg_dependency(self):
        reg_a1 = {"name": "rax"}
        reg_a2 = {"name": "eax"}
        reg_a3 = {"name": "ax"}
        reg_a4 = {"name": "al"}
        reg_r11 = {"name": "r11"}
        reg_r11b = {"name": "r11b"}
        reg_r11d = {"name": "r11d"}
        reg_r11w = {"name": "r11w"}
        reg_xmm1 = {"name": "xmm1"}
        reg_ymm1 = {"name": "ymm1"}
        reg_zmm1 = {"name": "zmm1"}

        reg_b1 = {"name": "rbx"}
        reg_r15 = {"name": "r15"}
        reg_xmm2 = {"name": "xmm2"}
        reg_ymm3 = {"name": "ymm3"}

        reg_a = [reg_a1, reg_a2, reg_a3, reg_a4]
        reg_r = [reg_r11, reg_r11b, reg_r11d, reg_r11w]
        reg_vec_1 = [reg_xmm1, reg_ymm1, reg_zmm1]
        reg_others = [reg_b1, reg_r15, reg_xmm2, reg_ymm3]
        regs = reg_a + reg_r + reg_vec_1 + reg_others

        # test each register against each other
        for ri in reg_a:
            for rj in regs:
                assert_value = True if rj in reg_a else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_r:
            for rj in regs:
                assert_value = True if rj in reg_r else False
                with self.subTest(reg_a=ri, reg_b=rj, assert_val=assert_value):
                    self.assertEqual(self.parser.is_reg_dependend_of(ri, rj), assert_value)
        for ri in reg_vec_1:
            for rj in regs:
                assert_value = True if rj in reg_vec_1 else False
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
            AttrDict.convert_dict(
                parser.process_operand(parser.comment.parseString(comment, parseAll=True).asDict())
            ).comment
        )

    def _get_label(self, parser, label):
        return parser.process_operand(parser.label.parseString(label, parseAll=True).asDict()).label

    def _get_directive(self, parser, directive):
        return parser.process_operand(parser.directive.parseString(directive, parseAll=True).asDict()).directive

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, "test_files", name)
        assert os.path.exists(name)
        return name


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserX86ATT)
    unittest.TextTestRunner(verbosity=2).run(suite)
