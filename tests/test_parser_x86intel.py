#!/usr/bin/env python3
"""
Unit tests for x86 Intel assembly parser
"""

import os
import unittest

from osaca.parser import ParserX86Intel, InstructionForm
from osaca.parser.directive import DirectiveOperand
from osaca.parser.identifier import IdentifierOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.label import LabelOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand


class TestParserX86Intel(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = ParserX86Intel()
        with open(self._find_file("triad_x86_intel.s")) as f:
            self.triad_code = f.read()
        with open(self._find_file("triad_x86_intel_iaca.s")) as f:
            self.triad_iaca_code = f.read()
        with open(self._find_file("gs_x86_icc.s")) as f:
            self.gs_icc_code = f.read()
        with open(self._find_file("gs_x86_gcc.s")) as f:
            self.gs_gcc_code = f.read()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(self._get_comment(self.parser, "; some comments"), "some comments")
        self.assertEqual(self._get_comment(self.parser, "\t\t;AA BB CC \t end \t"), "AA BB CC end")
        self.assertEqual(
            self._get_comment(self.parser, "\t;; comment ;; comment"),
            "; comment ;; comment",
        )

    def test_label_parser(self):
        self.assertEqual(self._get_label(self.parser, "main:")[0].name, "main")
        self.assertEqual(self._get_label(self.parser, "$$B1?10:")[0].name, "$$B1?10")
        self.assertEqual(
            self._get_label(self.parser, "$LN9:\tcall\t__CheckForDebuggerJustMyCode")[0].name,
            "$LN9",
        )
        self.assertEqual(
            self._get_label(self.parser, "$LN9:\tcall\t__CheckForDebuggerJustMyCode")[1],
            InstructionForm(
                mnemonic="call",
                operands=[
                    {"identifier": {"name": "__CheckForDebuggerJustMyCode"}},
                ],
                directive_id=None,
                comment_id=None,
                label_id=None,
                line=None,
                line_number=None,
            ),
        )

    def test_directive_parser(self):
        self.assertEqual(
            self._get_directive(self.parser, "\t.allocstack 16")[0],
            DirectiveOperand(name=".allocstack", parameters=["16"]),
        )
        self.assertEqual(
            self._get_directive(self.parser, "INCLUDELIB MSVCRTD")[0],
            DirectiveOperand(name="INCLUDELIB", parameters=["MSVCRTD"]),
        )
        self.assertEqual(
            self._get_directive(self.parser, "msvcjmc\tSEGMENT")[0],
            DirectiveOperand(name="SEGMENT", parameters=["msvcjmc"]),
        )
        self.assertEqual(
            self._get_directive(self.parser, "EXTRN\t_RTC_InitBase:PROC")[0],
            DirectiveOperand(name="EXTRN", parameters=["_RTC_InitBase:PROC"]),
        )
        self.assertEqual(
            self._get_directive(self.parser, "$pdata$kernel DD imagerel $LN9")[0],
            DirectiveOperand(name="DD", parameters=["$pdata$kernel", "imagerel", "$LN9"]),
        )
        self.assertEqual(
            self._get_directive(self.parser, "repeat$ = 320")[0],
            DirectiveOperand(name="=", parameters=["repeat$", "320"]),
        )

    def test_parse_instruction(self):
        instr1 = "\tsub\trsp, 296\t\t\t\t; 00000128H"
        instr2 = "  fst ST(3)\t; Good ol' x87."
        instr3 = "\tmulsd\txmm0, QWORD PTR [rdx+rcx*8]"
        instr4 = "\tmov\teax, DWORD PTR cur_elements$[rbp]"
        instr5 = "\tmov\tQWORD PTR [rsp+24], r8"
        instr6 = "\tjmp\tSHORT $LN2@kernel"
        instr7 = "\tlea\trcx, OFFSET FLAT:__FAC6D534_triad@c"
        instr8 = "\tmov\tBYTE PTR gs:111, al"
        instr9 = "\tlea\tr8, QWORD PTR [r8*4]"
        instr10 = "\tmovsd\txmm1, QWORD PTR boost@@XZ@4V456@A+16"
        instr11 = "\tlea\trcx, OFFSET FLAT:??_R0N@8+8"
        instr12 = "\tvfmadd213sd xmm0, xmm1, QWORD PTR __real@bfc5555555555555"
        instr13 = "\tjmp\t$LN18@operator"
        instr14 = "vaddsd  xmm0, xmm0, QWORD PTR [rdx+8+rax*8]"
        instr15 = "vextractf128 xmm1, ymm2, 0x2"
        instr16 = "vmovupd xmm0, [rax+123R]"

        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        parsed_7 = self.parser.parse_instruction(instr7)
        parsed_8 = self.parser.parse_instruction(instr8)
        parsed_9 = self.parser.parse_instruction(instr9)
        parsed_10 = self.parser.parse_instruction(instr10)
        parsed_11 = self.parser.parse_instruction(instr11)
        parsed_12 = self.parser.parse_instruction(instr12)
        parsed_13 = self.parser.parse_instruction(instr13)
        parsed_14 = self.parser.parse_instruction(instr14)
        parsed_15 = self.parser.parse_instruction(instr15)
        parsed_16 = self.parser.parse_instruction(instr16)

        self.assertEqual(parsed_1.mnemonic, "sub")
        self.assertEqual(parsed_1.operands[0], RegisterOperand(name="RSP"))
        self.assertEqual(parsed_1.operands[1], ImmediateOperand(value=296))
        self.assertEqual(parsed_1.comment, "00000128H")

        self.assertEqual(parsed_2.mnemonic, "fst")
        self.assertEqual(parsed_2.operands[0], RegisterOperand(name="ST(3)"))
        self.assertEqual(parsed_2.comment, "Good ol' x87.")

        self.assertEqual(parsed_3.mnemonic, "mulsd")
        self.assertEqual(parsed_3.operands[0], RegisterOperand(name="XMM0"))
        self.assertEqual(
            parsed_3.operands[1],
            MemoryOperand(
                base=RegisterOperand(name="RDX"), index=RegisterOperand(name="RCX"), scale=8
            ),
        )

        self.assertEqual(parsed_4.mnemonic, "mov")
        self.assertEqual(parsed_4.operands[0], RegisterOperand(name="EAX"))
        self.assertEqual(
            parsed_4.operands[1],
            MemoryOperand(
                offset=ImmediateOperand(identifier="cur_elements$", value=104),
                base=RegisterOperand(name="RBP"),
            ),
        )
        self.assertEqual(parsed_5.mnemonic, "mov")
        self.assertEqual(
            parsed_5.operands[0],
            MemoryOperand(offset=ImmediateOperand(value=24), base=RegisterOperand(name="RSP")),
        )
        self.assertEqual(parsed_5.operands[1], RegisterOperand(name="R8"))

        self.assertEqual(parsed_6.mnemonic, "jmp")
        self.assertEqual(parsed_6.operands[0], LabelOperand(name="$LN2@kernel"))

        self.assertEqual(parsed_7.mnemonic, "lea")
        self.assertEqual(parsed_7.operands[0], RegisterOperand(name="RCX"))
        self.assertEqual(
            parsed_7.operands[1],
            MemoryOperand(offset=IdentifierOperand(name="__FAC6D534_triad@c")),
        )

        self.assertEqual(parsed_8.mnemonic, "mov")
        self.assertEqual(
            parsed_8.operands[0],
            MemoryOperand(base=RegisterOperand(name="GS"), offset=ImmediateOperand(value=111)),
        )
        self.assertEqual(parsed_8.operands[1], RegisterOperand(name="AL"))

        self.assertEqual(parsed_9.mnemonic, "lea")
        self.assertEqual(parsed_9.operands[0], RegisterOperand(name="R8"))
        self.assertEqual(
            parsed_9.operands[1],
            MemoryOperand(base=None, index=RegisterOperand(name="R8"), scale=4),
        )

        self.assertEqual(parsed_10.mnemonic, "movsd")
        self.assertEqual(parsed_10.operands[0], RegisterOperand(name="XMM1"))
        self.assertEqual(
            parsed_10.operands[1],
            MemoryOperand(
                offset=IdentifierOperand(
                    name="boost@@XZ@4V456@A", offset=ImmediateOperand(value=16)
                )
            ),
        )

        self.assertEqual(parsed_11.mnemonic, "lea")
        self.assertEqual(parsed_11.operands[0], RegisterOperand(name="RCX"))
        self.assertEqual(
            parsed_11.operands[1],
            MemoryOperand(
                offset=IdentifierOperand(name="??_R0N@8", offset=ImmediateOperand(value=8))
            ),
        )

        self.assertEqual(parsed_12.mnemonic, "vfmadd213sd")
        self.assertEqual(parsed_12.operands[0], RegisterOperand(name="XMM0"))
        self.assertEqual(parsed_12.operands[1], RegisterOperand(name="XMM1"))
        self.assertEqual(
            parsed_12.operands[2],
            MemoryOperand(offset=IdentifierOperand(name="__real@bfc5555555555555")),
        )

        self.assertEqual(parsed_13.mnemonic, "jmp")
        self.assertEqual(parsed_13.operands[0], IdentifierOperand(name="$LN18@operator"))

        self.assertEqual(parsed_14.mnemonic, "vaddsd")
        self.assertEqual(parsed_14.operands[0], RegisterOperand(name="XMM0"))
        self.assertEqual(parsed_14.operands[1], RegisterOperand(name="XMM0"))
        self.assertEqual(
            parsed_14.operands[2],
            MemoryOperand(
                base=RegisterOperand(name="RDX"),
                offset=ImmediateOperand(value=8),
                index=RegisterOperand(name="RAX"),
                scale=8,
            ),
        )

        self.assertEqual(parsed_15.mnemonic, "vextractf128")
        self.assertEqual(parsed_15.operands[0], RegisterOperand(name="XMM1"))
        self.assertEqual(parsed_15.operands[1], RegisterOperand(name="YMM2"))
        self.assertEqual(parsed_15.operands[2], ImmediateOperand(value=2))

        self.assertEqual(parsed_16.mnemonic, "vmovupd")
        self.assertEqual(parsed_16.operands[0], RegisterOperand(name="XMM0"))
        self.assertEqual(
            parsed_16.operands[1],
            MemoryOperand(base=RegisterOperand(name="RAX"), offset=ImmediateOperand(value=291)),
        )

    def test_parse_line(self):
        line_comment = "; -- Begin  main"
        line_instruction = "\tret\t0"

        instruction_form_1 = InstructionForm(
            mnemonic=None,
            operands=[],
            directive_id=None,
            comment_id="-- Begin main",
            label_id=None,
            line="; -- Begin  main",
            line_number=1,
        )
        instruction_form_2 = InstructionForm(
            mnemonic="ret",
            operands=[
                {"immediate": {"value": 0}},
            ],
            directive_id=None,
            comment_id=None,
            label_id=None,
            line="\tret\t0",
            line_number=2,
        )

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_instruction, 2)

        self.assertEqual(parsed_1, instruction_form_1)
        self.assertEqual(parsed_2, instruction_form_2)

    def test_parse_register(self):
        register_str_1 = "rax"
        register_str_2 = "r9"
        register_str_3 = "xmm1"
        register_str_4 = "ST(4)"

        parsed_reg_1 = RegisterOperand(name="RAX")
        parsed_reg_2 = RegisterOperand(name="R9")
        parsed_reg_3 = RegisterOperand(name="XMM1")
        parsed_reg_4 = RegisterOperand(name="ST(4)")

        self.assertEqual(self.parser.parse_register(register_str_1), parsed_reg_1)
        self.assertEqual(self.parser.parse_register(register_str_2), parsed_reg_2)
        self.assertEqual(self.parser.parse_register(register_str_3), parsed_reg_3)
        self.assertEqual(self.parser.parse_register(register_str_4), parsed_reg_4)

    def test_parse_file1(self):
        parsed = self.parser.parse_file(self.triad_code)
        self.assertEqual(parsed[0].line_number, 1)
        # Check specifically that the values of the symbols defined by "=" were correctly
        # propagated.
        self.assertEqual(
            parsed[69],
            InstructionForm(
                mnemonic="mov",
                operands=[
                    MemoryOperand(
                        base=RegisterOperand("RBP"),
                        offset=ImmediateOperand(value=4, identifier="r$1"),
                    ),
                    ImmediateOperand(value=0),
                ],
                line="\tmov\tDWORD PTR r$1[rbp], 0",
                line_number=73,
            ),
        )
        # Check a few lines to make sure that we produced something reasonable.
        self.assertEqual(
            parsed[60],
            InstructionForm(
                mnemonic="mov",
                operands=[
                    MemoryOperand(base=RegisterOperand("RSP"), offset=ImmediateOperand(value=8)),
                    RegisterOperand(name="RCX"),
                ],
                line="\tmov\tQWORD PTR [rsp+8], rcx",
                line_number=64,
            ),
        )
        self.assertEqual(
            parsed[120],
            InstructionForm(
                directive_id=DirectiveOperand(name="END"), line="END", line_number=124
            ),
        )
        self.assertEqual(len(parsed), 121)

    def test_parse_file2(self):
        parsed = self.parser.parse_file(self.triad_iaca_code)
        self.assertEqual(parsed[0].line_number, 1)
        # Check a few lines to make sure that we produced something reasonable.
        self.assertEqual(
            parsed[68],
            InstructionForm(
                directive_id=DirectiveOperand(name="=", parameters=["s$", "88"]),
                line="s$ = 88",
                line_number=72,
            ),
        )
        self.assertEqual(
            parsed[135],
            InstructionForm(
                directive_id=DirectiveOperand(name="END"), line="END", line_number=139
            ),
        )
        self.assertEqual(len(parsed), 136)

    def test_parse_file3(self):
        parsed = self.parser.parse_file(self.gs_icc_code)
        self.assertEqual(parsed[0].line_number, 1)
        # Check a few lines to make sure that we produced something reasonable.
        self.assertEqual(
            parsed[113],
            InstructionForm(
                mnemonic="vmovsd",
                operands=[
                    RegisterOperand("XMM5"),
                    MemoryOperand(
                        base=RegisterOperand("R11"),
                        index=RegisterOperand("R10"),
                        scale=1,
                        offset=ImmediateOperand(value=16),
                    ),
                ],
                comment_id="26.19",
                line="        vmovsd    xmm5, QWORD PTR [16+r11+r10]" + "                  #26.19",
                line_number=114,
            ),
        )
        self.assertEqual(
            parsed[226],
            InstructionForm(
                directive_id=DirectiveOperand(name=".long", parameters=["681509"]),
                line="        .long   681509",
                line_number=227,
            ),
        )
        self.assertEqual(len(parsed), 227)

    def test_parse_file4(self):
        parsed = self.parser.parse_file(self.gs_gcc_code)
        self.assertEqual(parsed[0].line_number, 1)
        # Check a few lines to make sure that we produced something reasonable.
        self.assertEqual(
            parsed[61],
            InstructionForm(
                mnemonic="vaddsd",
                operands=[
                    RegisterOperand("XMM0"),
                    RegisterOperand("XMM0"),
                    MemoryOperand(
                        base=RegisterOperand("RDX"),
                        index=RegisterOperand("RAX"),
                        scale=8,
                        offset=ImmediateOperand(value=8),
                    ),
                ],
                line="        vaddsd  xmm0, xmm0, QWORD PTR [rdx+8+rax*8]",
                line_number=62,
            ),
        )
        self.assertEqual(
            parsed[101],
            InstructionForm(
                directive_id=DirectiveOperand(name=".long", parameters=["1072939201"]),
                line="        .long   1072939201",
                line_number=102,
            ),
        )
        self.assertEqual(len(parsed), 102)

    def test_normalize_imd(self):
        imd_binary = ImmediateOperand(value="1001111B")
        imd_octal = ImmediateOperand(value="117O")
        imd_decimal = ImmediateOperand(value="79")
        imd_hex = ImmediateOperand(value="4fH")
        imd_float = ImmediateOperand(value="-79.34")
        self.assertEqual(
            self.parser.normalize_imd(imd_binary),
            self.parser.normalize_imd(imd_octal),
        )
        self.assertEqual(
            self.parser.normalize_imd(imd_octal),
            self.parser.normalize_imd(imd_decimal),
        )
        self.assertEqual(
            self.parser.normalize_imd(imd_decimal),
            self.parser.normalize_imd(imd_hex),
        )
        self.assertEqual(self.parser.normalize_imd(ImmediateOperand(value="-79")), -79)
        self.assertEqual(self.parser.normalize_imd(imd_float), -79.34)

    ##################
    # Helper functions
    ##################
    def _get_comment(self, parser, comment):
        return " ".join(
            parser.process_operand(parser.comment.parseString(comment, parseAll=True))["comment"]
        )

    def _get_label(self, parser, label):
        return parser.process_operand(parser.label.parseString(label, parseAll=True))

    def _get_directive(self, parser, directive):
        return parser.process_operand(parser.directive.parseString(directive, parseAll=True))

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, "test_files", name)
        assert os.path.exists(name)
        return name


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserX86Intel)
    unittest.TextTestRunner(verbosity=2).run(suite)
