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
        # Use generic RISC-V instructions for testing, not tied to a specific file
        instr1 = "beq     a0,zero,.L12"  # Branch instruction
        instr2 = "vsetvli a5,zero,e32,m1,ta,ma"  # Vector instruction
        instr3 = "vle32.v v1,0(a1)"  # Vector load instruction
        instr4 = "fmadd.s fa5,fa0,fa5,fa4"  # Floating-point instruction
        instr5 = "addi    sp,sp,-64"  # Integer immediate instruction
        instr6 = "csrr    a4,vlenb"  # CSR instruction
        instr7 = "ret"  # Return instruction
        instr8 = "lui     a0,%hi(data)"  # Load upper immediate with relocation
        instr9 = "sw      ra,-4(sp)"  # Store with negative offset
        
        parsed_1 = self.parser.parse_instruction(instr1)
        parsed_2 = self.parser.parse_instruction(instr2)
        parsed_3 = self.parser.parse_instruction(instr3)
        parsed_4 = self.parser.parse_instruction(instr4)
        parsed_5 = self.parser.parse_instruction(instr5)
        parsed_6 = self.parser.parse_instruction(instr6)
        parsed_7 = self.parser.parse_instruction(instr7)
        parsed_8 = self.parser.parse_instruction(instr8)
        parsed_9 = self.parser.parse_instruction(instr9)
        
        # Verify branch instruction
        self.assertEqual(parsed_1.mnemonic, "beq")
        self.assertEqual(len(parsed_1.operands), 3)
        self.assertTrue(isinstance(parsed_1.operands[0], RegisterOperand))
        self.assertEqual(parsed_1.operands[0].name, "a0")
        self.assertTrue(isinstance(parsed_1.operands[1], RegisterOperand))
        self.assertEqual(parsed_1.operands[1].name, "zero")
        self.assertTrue(isinstance(parsed_1.operands[2], IdentifierOperand))
        self.assertEqual(parsed_1.operands[2].name, ".L12")
        
        # Verify vector configuration instruction
        self.assertEqual(parsed_2.mnemonic, "vsetvli")
        self.assertEqual(len(parsed_2.operands), 6)  # Verify correct operand count
        self.assertEqual(parsed_2.operands[0].name, "a5")
        self.assertEqual(parsed_2.operands[1].name, "zero")
        
        # Verify vector load instruction
        self.assertEqual(parsed_3.mnemonic, "vle32.v")
        self.assertEqual(len(parsed_3.operands), 2)
        self.assertEqual(parsed_3.operands[0].prefix, "v")
        self.assertEqual(parsed_3.operands[0].name, "1")
        self.assertTrue(isinstance(parsed_3.operands[1], MemoryOperand))
        self.assertEqual(parsed_3.operands[1].base.name, "a1")
        
        # Verify floating-point instruction
        self.assertEqual(parsed_4.mnemonic, "fmadd.s")
        self.assertEqual(len(parsed_4.operands), 4)
        self.assertEqual(parsed_4.operands[0].prefix, "f")
        
        # Verify integer immediate instruction
        self.assertEqual(parsed_5.mnemonic, "addi")
        self.assertEqual(len(parsed_5.operands), 3)
        self.assertEqual(parsed_5.operands[0].name, "sp")
        self.assertEqual(parsed_5.operands[1].name, "sp")
        self.assertTrue(isinstance(parsed_5.operands[2], ImmediateOperand))
        self.assertEqual(parsed_5.operands[2].value, -64)
        
        # Verify CSR instruction
        self.assertEqual(parsed_6.mnemonic, "csrr")
        self.assertEqual(len(parsed_6.operands), 2)
        self.assertEqual(parsed_6.operands[0].name, "a4")
        self.assertEqual(parsed_6.operands[1].name, "vlenb")
        
        # Verify return instruction
        self.assertEqual(parsed_7.mnemonic, "ret")
        self.assertEqual(len(parsed_7.operands), 0)
        
        # Verify load upper immediate with relocation
        self.assertEqual(parsed_8.mnemonic, "lui")
        self.assertEqual(len(parsed_8.operands), 2)
        self.assertEqual(parsed_8.operands[0].name, "a0")
        self.assertEqual(parsed_8.operands[1].name, "data")
        
        # Verify store with negative offset
        self.assertEqual(parsed_9.mnemonic, "sw")
        self.assertEqual(len(parsed_9.operands), 2)
        self.assertEqual(parsed_9.operands[0].name, "ra")
        self.assertTrue(isinstance(parsed_9.operands[1], MemoryOperand))
        self.assertEqual(parsed_9.operands[1].base.name, "sp")
        self.assertEqual(parsed_9.operands[1].offset.value, -4)

    def test_parse_line(self):
        # Use generic RISC-V lines for testing
        line_label = "saxpy_golden:"
        line_branch = "        beq     a0,zero,.L12"
        line_memory = "        vle32.v v1,0(a1)"
        line_directive = "        .word   1113498583"
        line_with_comment = "        ret           # Return from function"
        
        parsed_1 = self.parser.parse_line(line_label, 1)
        parsed_2 = self.parser.parse_line(line_branch, 2)
        parsed_3 = self.parser.parse_line(line_memory, 3)
        parsed_4 = self.parser.parse_line(line_directive, 4)
        parsed_5 = self.parser.parse_line(line_with_comment, 5)

        # Verify label parsing
        self.assertEqual(parsed_1.label, "saxpy_golden")
        self.assertIsNone(parsed_1.mnemonic)
        
        # Verify branch instruction parsing
        self.assertEqual(parsed_2.mnemonic, "beq")
        self.assertEqual(len(parsed_2.operands), 3)
        self.assertEqual(parsed_2.operands[0].name, "a0")
        self.assertEqual(parsed_2.operands[1].name, "zero")
        self.assertEqual(parsed_2.operands[2].name, ".L12")
        
        # Verify memory instruction parsing
        self.assertEqual(parsed_3.mnemonic, "vle32.v")
        self.assertEqual(len(parsed_3.operands), 2)
        self.assertEqual(parsed_3.operands[0].prefix, "v")
        self.assertEqual(parsed_3.operands[0].name, "1")
        self.assertTrue(isinstance(parsed_3.operands[1], MemoryOperand))
        
        # Verify directive parsing
        self.assertIsNone(parsed_4.mnemonic)
        self.assertEqual(parsed_4.directive.name, "word")
        self.assertEqual(parsed_4.directive.parameters[0], "1113498583")
        
        # Verify comment parsing
        self.assertEqual(parsed_5.mnemonic, "ret")
        self.assertEqual(parsed_5.comment, "Return from function")

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
        reg_fa1 = RegisterOperand(prefix="f", name="a1")
        reg_f10 = RegisterOperand(prefix="f", name="10")
        
        # Test vector registers
        reg_v1 = RegisterOperand(prefix="v", name="1")
        reg_v2 = RegisterOperand(prefix="v", name="2")
        
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
        # Test memory operand parsing with different offsets and base registers
        
        # Parse memory operands from real instructions
        instr1 = "vle32.v v1,0(a1)"
        instr2 = "lw a0,8(sp)"
        instr3 = "sw ra,-4(sp)"
        
        parsed1 = self.parser.parse_instruction(instr1)
        parsed2 = self.parser.parse_instruction(instr2)
        parsed3 = self.parser.parse_instruction(instr3)
        
        # Verify memory operands
        self.assertTrue(isinstance(parsed1.operands[1], MemoryOperand))
        self.assertEqual(parsed1.operands[1].base.name, "a1")
        self.assertEqual(parsed1.operands[1].offset.value, 0)
        
        self.assertTrue(isinstance(parsed2.operands[1], MemoryOperand))
        self.assertEqual(parsed2.operands[1].base.name, "sp")
        self.assertEqual(parsed2.operands[1].offset.value, 8)
        
        self.assertTrue(isinstance(parsed3.operands[1], MemoryOperand))
        self.assertEqual(parsed3.operands[1].base.name, "sp")
        self.assertEqual(parsed3.operands[1].offset.value, -4)

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