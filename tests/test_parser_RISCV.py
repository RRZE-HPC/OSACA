#!/usr/bin/env python3
"""
Unit tests for RISC-V assembly parser
"""

import os
import unittest

from pyparsing import ParseException

from osaca.parser import ParserRISCV
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
        # Test common label patterns from kernel_riscv.s
        self.assertEqual(self._get_label(self.parser, "saxpy_golden:")[0].name, "saxpy_golden")
        self.assertEqual(self._get_label(self.parser, ".L4:")[0].name, ".L4")
        self.assertEqual(self._get_label(self.parser, ".L25:\t\t\t# Return")[0].name, ".L25")
        self.assertEqual(
            " ".join(self._get_label(self.parser, ".L25:\t\t\t# Return")[1]),
            "Return",
        )
        with self.assertRaises(ParseException):
            self._get_label(self.parser, "\t.word 1113498583")

    def test_directive_parser(self):
        self.assertEqual(self._get_directive(self.parser, "\t.text")[0].name, "text")
        self.assertEqual(len(self._get_directive(self.parser, "\t.text")[0].parameters), 0)
        self.assertEqual(self._get_directive(self.parser, "\t.word\t1113498583")[0].name, "word")
        self.assertEqual(
            len(self._get_directive(self.parser, "\t.word\t1113498583")[0].parameters), 1
        )
        self.assertEqual(
            self._get_directive(self.parser, "\t.word\t1113498583")[0].parameters[0], "1113498583"
        )
        # Test string directive
        self.assertEqual(
            self._get_directive(self.parser, '.string "fail, %f=!%f\\n"')[0].name, "string"
        )
        self.assertEqual(
            self._get_directive(self.parser, '.string "fail, %f=!%f\\n"')[0].parameters[0], 
            '"fail, %f=!%f\\n"'
        )
        # Test set directive
        self.assertEqual(
            self._get_directive(self.parser, "\t.set\t.LANCHOR0,. + 0")[0].name, "set"
        )
        self.assertEqual(
            len(self._get_directive(self.parser, "\t.set\t.LANCHOR0,. + 0")[0].parameters), 2
        )

    def test_parse_instruction(self):
        """Test parsing of instructions."""
        # Test 1: Simple instruction
        parsed_1 = self.parser.parse_instruction("addi x10, x10, 1")
        self.assertEqual(parsed_1.mnemonic, "addi")
        self.assertEqual(len(parsed_1.operands), 3)
        self.assertEqual(parsed_1.operands[0].name, "10")
        self.assertEqual(parsed_1.operands[1].name, "10")
        self.assertEqual(parsed_1.operands[2].value, 1)

        # Test 2: Vector instruction
        parsed_2 = self.parser.parse_instruction("vle64.v v1, (x11)")
        self.assertEqual(parsed_2.mnemonic, "vle64.v")
        self.assertEqual(len(parsed_2.operands), 2)
        self.assertEqual(parsed_2.operands[0].name, "1")
        self.assertEqual(parsed_2.operands[1].base.name, "11")

        # Test 3: Floating point instruction
        parsed_3 = self.parser.parse_instruction("fmul.d f10, f10, f11")
        self.assertEqual(parsed_3.mnemonic, "fmul.d")
        self.assertEqual(len(parsed_3.operands), 3)
        self.assertEqual(parsed_3.operands[0].name, "10")
        self.assertEqual(parsed_3.operands[1].name, "10")
        self.assertEqual(parsed_3.operands[2].name, "11")

    def test_parse_line(self):
        """Test parsing of complete lines."""
        # Test 1: Line with label and instruction
        parsed_1 = self.parser.parse_line(".L2:")
        self.assertEqual(parsed_1.label, ".L2")

        # Test 2: Line with instruction and comment
        parsed_2 = self.parser.parse_line("addi x10, x10, 1 # increment")
        self.assertEqual(parsed_2.mnemonic, "addi")
        self.assertEqual(len(parsed_2.operands), 3)
        self.assertEqual(parsed_2.operands[0].name, "10")
        self.assertEqual(parsed_2.operands[1].name, "10")
        self.assertEqual(parsed_2.operands[2].value, 1)
        self.assertEqual(parsed_2.comment, "increment")

    def test_parse_file(self):
        parsed = self.parser.parse_file(self.riscv_code)
        self.assertGreater(len(parsed), 10)  # There should be multiple lines

        # Find common elements that should exist in any RISC-V file
        # without being tied to specific line numbers

        # Verify that we can find at least one label
        label_forms = [form for form in parsed if form.label is not None]
        self.assertGreater(len(label_forms), 0, "No labels found in the file")

        # Verify that we can find at least one branch instruction
        branch_forms = [form for form in parsed if form.mnemonic and form.mnemonic.startswith("b")]
        self.assertGreater(len(branch_forms), 0, "No branch instructions found in the file")
        
        # Verify that we can find at least one store/load instruction
        mem_forms = [form for form in parsed if form.mnemonic and (
            form.mnemonic.startswith("s") or 
            form.mnemonic.startswith("l"))]
        self.assertGreater(len(mem_forms), 0, "No memory instructions found in the file")
        
        # Verify that we can find at least one directive
        directive_forms = [form for form in parsed if form.directive is not None]
        self.assertGreater(len(directive_forms), 0, "No directives found in the file")

    def test_register_dependency(self):
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
        reg_x5 = RegisterOperand(prefix="x", name="5")  # Define reg_x5 for use in tests below
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

        # Test floating-point registers
        reg_fa0 = RegisterOperand(prefix="f", name="a0")
        reg_f10 = RegisterOperand(prefix="f", name="10")

        # Test vector registers
        reg_v1 = RegisterOperand(prefix="v", name="1")

        # Test register type detection
        self.assertTrue(self.parser.is_gpr(reg_a0))
        self.assertTrue(self.parser.is_gpr(reg_x5))
        self.assertTrue(self.parser.is_gpr(reg_sp))

        self.assertFalse(self.parser.is_gpr(reg_fa0))
        self.assertFalse(self.parser.is_gpr(reg_f10))

        self.assertTrue(self.parser.is_vector_register(reg_v1))
        self.assertFalse(self.parser.is_vector_register(reg_x10))
        self.assertFalse(self.parser.is_vector_register(reg_fa0))

    def test_normalize_imd(self):
        imd_decimal = ImmediateOperand(value="42")
        imd_hex = ImmediateOperand(value="0x2A")
        imd_negative = ImmediateOperand(value="-12")
        identifier = IdentifierOperand(name="function")

        self.assertEqual(self.parser.normalize_imd(imd_decimal), 42)
        self.assertEqual(self.parser.normalize_imd(imd_hex), 42)
        self.assertEqual(self.parser.normalize_imd(imd_negative), -12)
        self.assertEqual(self.parser.normalize_imd(identifier), identifier)

    def test_memory_operand_parsing(self):
        """Test parsing of memory operands."""
        # Test 1: Basic memory operand
        parsed1 = self.parser.parse_instruction("vle8.v v1, (x11)")
        self.assertEqual(parsed1.mnemonic, "vle8.v")
        self.assertEqual(len(parsed1.operands), 2)
        self.assertEqual(parsed1.operands[0].name, "1")
        self.assertEqual(parsed1.operands[1].base.name, "11")
        self.assertEqual(parsed1.operands[1].offset, None)
        self.assertEqual(parsed1.operands[1].index, None)

        # Test 2: Memory operand with offset
        parsed2 = self.parser.parse_instruction("vle8.v v1, 8(x11)")
        self.assertEqual(parsed2.mnemonic, "vle8.v")
        self.assertEqual(len(parsed2.operands), 2)
        self.assertEqual(parsed2.operands[0].name, "1")
        self.assertEqual(parsed2.operands[1].base.name, "11")
        self.assertEqual(parsed2.operands[1].offset.value, 8)
        self.assertEqual(parsed2.operands[1].index, None)

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