#!/usr/bin/env python3
"""
Unit tests for RISC-V assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import ParserRISCV, InstructionForm
from osaca.parser.directive import DirectiveOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.identifier import IdentifierOperand


class TestParserRISCV(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = ParserRISCV()
        with open(self._find_file("kernel_riscv.s")) as f:
            self.riscv_code = f.read()

    ##################
    # Test
    ##################

    def test_comment_parser(self):
        self.assertEqual(self._get_comment(self.parser, "# some comments"), "some comments")
        self.assertEqual(
            self._get_comment(self.parser, "\t\t# RISC-V comment \t end \t"), "RISC-V comment end"
        )
        self.assertEqual(
            self._get_comment(self.parser, "\t## comment ## comment"),
            "# comment ## comment",
        )

    def test_label_parser(self):
        self.assertEqual(self._get_label(self.parser, "main:")[0].name, "main")
        self.assertEqual(self._get_label(self.parser, "loop_start:")[0].name, "loop_start")
        self.assertEqual(self._get_label(self.parser, ".L1:\t\t\t# comment")[0].name, ".L1")
        self.assertEqual(
            " ".join(self._get_label(self.parser, ".L1:\t\t\t# comment")[1]),
            "comment",
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, "\t.cfi_startproc")

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, "\t.text")[0].name, "text")
        self.assertEqual(len(self._get_directive(self.parser, "\t.text")[0].parameters), 0)
        self.assertEqual(self._get_directive(self.parser, "\t.align\t4")[0].name, "align")
        self.assertEqual(
            len(self._get_directive(self.parser, "\t.align\t4")[0].parameters), 1
        )
        self.assertEqual(
            self._get_directive(self.parser, "\t.align\t4")[0].parameters[0], "4"
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       # IACA START")[
                0
            ].name,
            "byte",
        )
        self.assertEqual(
            self._get_directive(self.parser, "        .byte 100,103,144       # IACA START")[
                0
            ].parameters[2],
            "144",
        )
        self.assertEqual(
            " ".join(
                self._get_directive(self.parser, "        .byte 100,103,144       # IACA START")[1]
            ),
            "IACA START",
        )

    def test_parse_instruction(self):
        instr1 = "addi t0, zero, 1"
        instr2 = "lw a0, 8(sp)"
        instr3 = "beq t0, t1, loop_start"
        instr4 = "lui a0, %hi(data)"
        instr5 = "sw ra, -4(sp)"
        instr6 = "jal ra, function"
        
        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        
        # Verify addi instruction
        self.assertEqual(parsed_1.mnemonic, "addi")
        self.assertEqual(parsed_1.operands[0].name, "t0")
        self.assertEqual(parsed_1.operands[1].name, "zero")
        self.assertEqual(parsed_1.operands[2].value, 1)
        
        # Verify lw instruction
        self.assertEqual(parsed_2.mnemonic, "lw")
        self.assertEqual(parsed_2.operands[0].name, "a0")
        self.assertEqual(parsed_2.operands[1].offset.value, 8)
        self.assertEqual(parsed_2.operands[1].base.name, "sp")
        
        # Verify beq instruction
        self.assertEqual(parsed_3.mnemonic, "beq")
        self.assertEqual(parsed_3.operands[0].name, "t0")
        self.assertEqual(parsed_3.operands[1].name, "t1")
        self.assertEqual(parsed_3.operands[2].name, "loop_start")
        
        # Verify lui instruction with high bits relocation
        self.assertEqual(parsed_4.mnemonic, "lui")
        self.assertEqual(parsed_4.operands[0].name, "a0")
        self.assertEqual(parsed_4.operands[1].name, "data")
        
        # Verify sw instruction with negative offset
        self.assertEqual(parsed_5.mnemonic, "sw")
        self.assertEqual(parsed_5.operands[0].name, "ra")
        self.assertEqual(parsed_5.operands[1].offset.value, -4)
        self.assertEqual(parsed_5.operands[1].base.name, "sp")
        
        # Verify jal instruction
        self.assertEqual(parsed_6.mnemonic, "jal")
        self.assertEqual(parsed_6.operands[0].name, "ra")
        self.assertEqual(parsed_6.operands[1].name, "function")

    def test_parse_line(self):
        line_comment = "# -- Begin  main"
        line_label = ".LBB0_1:              # Loop Header"
        line_directive = ".cfi_def_cfa sp, 0"
        line_instruction = "addi sp, sp, -16    # allocate stack frame"
        
        instruction_form_1 = InstructionForm(
            mnemonic=None,
            operands=[],
            directive_id=None,
            comment_id="-- Begin main",
            label_id=None,
            line="# -- Begin  main",
            line_number=1,
        )

        instruction_form_2 = InstructionForm(
            mnemonic=None,
            operands=[],
            directive_id=None,
            comment_id="Loop Header",
            label_id=".LBB0_1",
            line=".LBB0_1:              # Loop Header",
            line_number=2,
        )
        
        instruction_form_3 = InstructionForm(
            mnemonic=None,
            operands=[],
            directive_id=DirectiveOperand(name="cfi_def_cfa", parameters=["sp", "0"]),
            comment_id=None,
            label_id=None,
            line=".cfi_def_cfa sp, 0",
            line_number=3,
        )
        
        instruction_form_4 = InstructionForm(
            mnemonic="addi",
            operands=[
                RegisterOperand(prefix="x", name="sp"),
                RegisterOperand(prefix="x", name="sp"),
                ImmediateOperand(value=-16, imd_type="int"),
            ],
            directive_id=None,
            comment_id="allocate stack frame",
            label_id=None,
            line="addi sp, sp, -16    # allocate stack frame",
            line_number=4,
        )

        parsed_1 = self.parser.parse_line(line_comment, 1)
        parsed_2 = self.parser.parse_line(line_label, 2)
        parsed_3 = self.parser.parse_line(line_directive, 3)
        parsed_4 = self.parser.parse_line(line_instruction, 4)

        self.assertEqual(parsed_1.comment, instruction_form_1.comment)
        self.assertEqual(parsed_2.label, instruction_form_2.label)
        self.assertEqual(parsed_3.directive.name, instruction_form_3.directive.name)
        self.assertEqual(parsed_3.directive.parameters, instruction_form_3.directive.parameters)
        self.assertEqual(parsed_4.mnemonic, instruction_form_4.mnemonic)
        self.assertEqual(parsed_4.operands[0].name, instruction_form_4.operands[0].name)
        self.assertEqual(parsed_4.operands[2].value, instruction_form_4.operands[2].value)
        self.assertEqual(parsed_4.comment, instruction_form_4.comment)

    def test_parse_file(self):
        parsed = self.parser.parse_file(self.riscv_code)
        self.assertEqual(parsed[0].line_number, 1)
        self.assertGreater(len(parsed), 80)  # More than 80 lines should be parsed
        
        # Test parsing specific parts of the file
        # Find saxpy_vec label (which is the vector routine in the updated file)
        vector_idx = next((i for i, instr in enumerate(parsed) if instr.label == "saxpy_vec"), None)
        self.assertIsNotNone(vector_idx)
        
        # Find floating-point instructions
        flw_idx = next((i for i, instr in enumerate(parsed) if instr.mnemonic == "flw"), None)
        self.assertIsNotNone(flw_idx)
        
        # Find vector instructions
        vle_idx = next((i for i, instr in enumerate(parsed) if instr.mnemonic and instr.mnemonic.startswith("vle")), None)
        self.assertIsNotNone(vle_idx)
        
        # Find CSR instructions
        csr_idx = next((i for i, instr in enumerate(parsed) if instr.mnemonic == "csrr"), None)
        self.assertIsNotNone(csr_idx)

    def test_register_mapping(self):
        # Test ABI name to register number mapping
        reg_zero = RegisterOperand(name="zero")
        reg_ra = RegisterOperand(name="ra")
        reg_sp = RegisterOperand(name="sp")
        reg_a0 = RegisterOperand(name="a0")
        reg_t1 = RegisterOperand(name="t1")
        reg_s2 = RegisterOperand(name="s2")
        
        reg_x0 = RegisterOperand(prefix="x", name="0")
        reg_x1 = RegisterOperand(prefix="x", name="1")
        reg_x2 = RegisterOperand(prefix="x", name="2")
        reg_x10 = RegisterOperand(prefix="x", name="10")
        reg_x6 = RegisterOperand(prefix="x", name="6")
        reg_x18 = RegisterOperand(prefix="x", name="18")
        
        # Test canonical name conversion
        self.assertEqual(self.parser._get_canonical_reg_name(reg_zero), "x0")
        self.assertEqual(self.parser._get_canonical_reg_name(reg_ra), "x1")
        self.assertEqual(self.parser._get_canonical_reg_name(reg_sp), "x2")
        self.assertEqual(self.parser._get_canonical_reg_name(reg_a0), "x10")
        self.assertEqual(self.parser._get_canonical_reg_name(reg_t1), "x6")
        self.assertEqual(self.parser._get_canonical_reg_name(reg_s2), "x18")
        
        # Test register dependency
        self.assertTrue(self.parser.is_reg_dependend_of(reg_zero, reg_x0))
        self.assertTrue(self.parser.is_reg_dependend_of(reg_ra, reg_x1))
        self.assertTrue(self.parser.is_reg_dependend_of(reg_sp, reg_x2))
        self.assertTrue(self.parser.is_reg_dependend_of(reg_a0, reg_x10))
        self.assertTrue(self.parser.is_reg_dependend_of(reg_t1, reg_x6))
        self.assertTrue(self.parser.is_reg_dependend_of(reg_s2, reg_x18))
        
        # Test non-dependent registers
        self.assertFalse(self.parser.is_reg_dependend_of(reg_zero, reg_x1))
        self.assertFalse(self.parser.is_reg_dependend_of(reg_ra, reg_x2))
        self.assertFalse(self.parser.is_reg_dependend_of(reg_a0, reg_t1))

    def test_normalize_imd(self):
        imd_decimal = ImmediateOperand(value="42")
        imd_hex = ImmediateOperand(value="0x2A")
        imd_negative = ImmediateOperand(value="-12")
        identifier = IdentifierOperand(name="function")

        self.assertEqual(self.parser.normalize_imd(imd_decimal), 42)
        self.assertEqual(self.parser.normalize_imd(imd_hex), 42)
        self.assertEqual(self.parser.normalize_imd(imd_negative), -12)
        self.assertEqual(self.parser.normalize_imd(identifier), identifier)

    def test_is_gpr(self):
        # Test integer registers
        reg_x5 = RegisterOperand(prefix="x", name="5")
        reg_t0 = RegisterOperand(name="t0")
        reg_sp = RegisterOperand(name="sp")
        
        # Test floating point registers
        reg_f10 = RegisterOperand(prefix="f", name="10")
        reg_fa0 = RegisterOperand(name="fa0")
        
        # Test vector registers
        reg_v3 = RegisterOperand(prefix="v", name="3")
        
        self.assertTrue(self.parser.is_gpr(reg_x5))
        self.assertTrue(self.parser.is_gpr(reg_t0))
        self.assertTrue(self.parser.is_gpr(reg_sp))
        
        self.assertFalse(self.parser.is_gpr(reg_f10))
        self.assertFalse(self.parser.is_gpr(reg_fa0))
        self.assertFalse(self.parser.is_gpr(reg_v3))
        
    def test_is_vector_register(self):
        reg_v3 = RegisterOperand(prefix="v", name="3")
        reg_x5 = RegisterOperand(prefix="x", name="5")
        reg_f10 = RegisterOperand(prefix="f", name="10")
        
        self.assertTrue(self.parser.is_vector_register(reg_v3))
        self.assertFalse(self.parser.is_vector_register(reg_x5))
        self.assertFalse(self.parser.is_vector_register(reg_f10))

    ##################
    # Helper functions
    ##################
    def _get_comment(self, parser, comment):
        return " ".join(
            parser.process_operand(parser.comment.parseString(comment, parseAll=True).asDict())[
                "comment"
            ]
        )

    def _get_label(self, parser, label):
        return parser.process_operand(parser.label.parseString(label, parseAll=True).asDict())

    def _get_directive(self, parser, directive):
        return parser.process_operand(
            parser.directive.parseString(directive, parseAll=True).asDict()
        )

    @staticmethod
    def _find_file(name):
        testdir = os.path.dirname(__file__)
        name = os.path.join(testdir, "test_files", name)
        assert os.path.exists(name)
        return name


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParserRISCV)
    unittest.TextTestRunner(verbosity=2).run(suite) 