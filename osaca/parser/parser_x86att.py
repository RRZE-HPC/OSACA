#!/usr/bin/env python3

import string
import re

import pyparsing as pp

from osaca.parser import BaseParser
from osaca.parser.instruction_form import InstructionForm
from osaca.parser.directive import DirectiveOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.label import LabelOperand
from osaca.parser.register import RegisterOperand
from osaca.parser.identifier import IdentifierOperand
from osaca.parser.immediate import ImmediateOperand


class ParserX86ATT(BaseParser):
    _instance = None

    # Singelton pattern, as this is created very many times
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParserX86ATT, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.isa = "x86"

    def construct_parser(self):
        """Create parser for x86 AT&T ISA."""
        decimal_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Word(pp.nums)
        ).setResultsName("value")
        hex_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Literal("0x") + pp.Word(pp.hexnums)
        ).setResultsName("value")
        # Comment - either '#' or '//' (icc)
        self.comment = (pp.Literal("#") | pp.Literal("//")) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables))
        ).setResultsName(self.comment_id)
        # Define x86 assembly identifier
        relocation = pp.Combine(pp.Literal("@") + pp.Word(pp.alphas))
        id_offset = pp.Word(pp.nums) + pp.Suppress(pp.Literal("+"))
        first = pp.Word(pp.alphas + "-_.", exact=1)
        rest = pp.Word(pp.alphanums + "$_.+-")
        identifier = pp.Group(
            pp.Optional(id_offset).setResultsName("offset")
            + pp.Combine(
                pp.delimitedList(pp.Combine(first + pp.Optional(rest)), delim="::"),
                joinString="::",
            ).setResultsName("name")
            + pp.Optional(relocation).setResultsName("relocation")
            + pp.Optional(
                pp.Suppress(pp.Optional(pp.Literal("+"))) + decimal_number
            ).setResultsName("offset")
        ).setResultsName("identifier")
        # Label
        label_rest = pp.Word(pp.alphanums + "$_.+-()")
        label_identifier = pp.Group(
            pp.Optional(id_offset).setResultsName("offset")
            + pp.Combine(
                pp.delimitedList(pp.Combine(first + pp.Optional(label_rest)), delim="::"),
                joinString="::",
            ).setResultsName("name")
            + pp.Optional(relocation).setResultsName("relocation")
        ).setResultsName("identifier")
        numeric_identifier = pp.Group(
            pp.Word(pp.nums).setResultsName("name")
            + pp.Optional(pp.oneOf("b f", caseless=True).setResultsName("suffix"))
        ).setResultsName("identifier")
        self.label = pp.Group(
            (label_identifier | numeric_identifier).setResultsName("name")
            + pp.Literal(":")
            + pp.Optional(self.comment)
        ).setResultsName(self.label_id)
        # Register: pp.Regex('^%[0-9a-zA-Z]+{}{z},?')
        self.register = pp.Group(
            pp.Literal("%")
            + pp.Word(pp.alphanums).setResultsName("name")
            + pp.Optional(pp.Literal("(") + pp.Word(pp.nums) + pp.Literal(")"))
            + pp.Optional(
                pp.Literal("{")
                + pp.Optional(pp.Suppress(pp.Literal("%")))
                + pp.Word(pp.alphanums).setResultsName("mask")
                + pp.Literal("}")
                + pp.Optional(
                    pp.Suppress(pp.Literal("{"))
                    + pp.Literal("z").setResultsName("zeroing")
                    + pp.Suppress(pp.Literal("}"))
                )
            )
        ).setResultsName(self.register_id)
        # Immediate: pp.Regex('^\$(-?[0-9]+)|(0x[0-9a-fA-F]+),?')
        symbol_immediate = "$"
        immediate = pp.Group(
            pp.Literal(symbol_immediate) + (hex_number | decimal_number | identifier)
        ).setResultsName(self.immediate_id)

        # Memory preparations
        offset = pp.Group(hex_number | decimal_number | identifier).setResultsName(
            self.immediate_id
        )
        scale = pp.Word("1248", exact=1)
        # Segment register extension
        segment_extension = (
            hex_number
            ^ pp.Word(pp.nums)
            ^ pp.Group(
                pp.Optional(offset.setResultsName("offset"))
                + pp.Optional(
                    pp.Literal("(")
                    + pp.Optional(self.register.setResultsName("base"))
                    + pp.Optional(pp.Suppress(pp.Literal(",")))
                    + pp.Optional(self.register.setResultsName("index"))
                    + pp.Optional(pp.Suppress(pp.Literal(",")))
                    + pp.Optional(scale.setResultsName("scale"))
                    + pp.Literal(")")
                )
            )
        )
        memory_segmentation = (
            pp.Optional(pp.Suppress(pp.Literal("*")))
            + self.register.setResultsName("base")
            + pp.Literal(":")
            + segment_extension.setResultsName(self.segment_ext)
        )
        # Memory: offset | seg:seg_ext | offset(base, index, scale){mask}
        memory_abs = pp.Suppress(pp.Literal("*")) + (offset | self.register).setResultsName(
            "offset"
        )
        memory = pp.Group(
            (
                pp.Optional(pp.Suppress(pp.Literal("*")))
                + pp.Optional(offset.setResultsName("offset"))
                + pp.Literal("(")
                + pp.Optional(self.register.setResultsName("base"))
                + pp.Optional(pp.Suppress(pp.Literal(",")))
                + pp.Optional(self.register.setResultsName("index"))
                + pp.Optional(pp.Suppress(pp.Literal(",")))
                + pp.Optional(scale.setResultsName("scale"))
                + pp.Literal(")")
                + pp.Optional(
                    pp.Literal("{")
                    + pp.Optional(pp.Suppress(pp.Literal("%")))
                    + pp.Word(pp.alphanums).setResultsName("mask")
                    + pp.Literal("}")
                )
            )
            | memory_abs
            | memory_segmentation
            | (hex_number | pp.Word(pp.nums)).setResultsName("offset")
        ).setResultsName(self.memory_id)

        # Directive
        # parameter can be any quoted string or sequence of characters besides '#' (for comments)
        # or ',' (parameter delimiter)
        directive_parameter = (
            pp.quotedString
            ^ (
                pp.Word(pp.printables, excludeChars=",#")
                + pp.Optional(pp.Suppress(pp.Literal(",")))
            )
            ^ pp.Suppress(pp.Literal(","))
        )
        self.directive = pp.Group(
            pp.Literal(".")
            + pp.Word(pp.alphanums + "_").setResultsName("name")
            + pp.ZeroOrMore(directive_parameter).setResultsName("parameters")
            + pp.Optional(self.comment)
        ).setResultsName(self.directive_id)

        # Instructions
        # Mnemonic
        mnemonic = pp.ZeroOrMore(pp.Literal("data16") | pp.Literal("data32")) + pp.Word(
            pp.alphanums + ","
        ).setResultsName("mnemonic")
        # Combine to instruction form
        operand_first = pp.Group(
            self.register ^ immediate ^ memory ^ identifier ^ numeric_identifier
        )
        operand_rest = pp.Group(self.register ^ immediate ^ memory)
        self.instruction_parser = (
            mnemonic
            + pp.Optional(operand_first.setResultsName("operand1"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand2"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand3"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand4"))
            + pp.Optional(self.comment)
        )

    def parse_register(self, register_string):
        """Parse register string"""
        try:
            return self.process_operand(
                self.register.parseString(register_string, parseAll=True).asDict()
            )
        except pp.ParseException:
            return None

    def parse_line(self, line, line_number=None):
        """
        Parse line and return instruction form.

        :param str line: line of assembly code
        :param line_number: default None, identifier of instruction form
        :type line_number: int, optional
        :return: ``dict`` -- parsed asm line (comment, label, directive or instruction form)
        """
        instruction_form = InstructionForm(line=line, line_number=line_number)
        result = None

        # 1. Parse comment
        try:
            result = self.process_operand(self.comment.parseString(line, parseAll=True).asDict())
            instruction_form.comment = " ".join(result[self.comment_id])
        except pp.ParseException:
            pass

        # 2. Parse label
        if result is None:
            try:
                # returns tuple with label operand and comment, if any
                result = self.process_operand(self.label.parseString(line, parseAll=True).asDict())
                instruction_form.label = result[0].name
                if result[1] is not None:
                    instruction_form.comment = " ".join(result[1])
            except pp.ParseException:
                pass

        # 3. Parse directive
        if result is None:
            try:
                # returns tuple with directive operand and comment, if any
                result = self.process_operand(
                    self.directive.parseString(line, parseAll=True).asDict()
                )
                instruction_form.directive = DirectiveOperand(
                    name=result[0].name,
                    parameters=result[0].parameters,
                )

                if result[1] is not None:
                    instruction_form.comment = " ".join(result[1])
            except pp.ParseException:
                pass

        # 4. Parse instruction
        if result is None:
            try:
                result = self.parse_instruction(line)
            except pp.ParseException:
                raise ValueError(
                    "Could not parse instruction on line {}: {!r}".format(line_number, line)
                )
            instruction_form.mnemonic = result.mnemonic
            instruction_form.operands = result.operands
            instruction_form.comment = result.comment
        return instruction_form

    def parse_instruction(self, instruction):
        """
        Parse instruction in asm line.

        :param str instruction: Assembly line string.
        :returns: `dict` -- parsed instruction form
        """
        result = self.instruction_parser.parseString(instruction, parseAll=True).asDict()
        operands = []
        # Add operands to list
        # Check first operand
        if "operand1" in result:
            operands.append(self.process_operand(result["operand1"]))
        # Check second operand
        if "operand2" in result:
            operands.append(self.process_operand(result["operand2"]))
        # Check third operand
        if "operand3" in result:
            operands.append(self.process_operand(result["operand3"]))
        # Check fourth operand
        if "operand4" in result:
            operands.append(self.process_operand(result["operand4"]))
        return_dict = InstructionForm(
            mnemonic=result["mnemonic"].split(",")[0],
            operands=operands,
            comment_id=" ".join(result[self.comment_id]) if self.comment_id in result else None,
        )

        return return_dict

    def process_operand(self, operand):
        """Post-process operand"""
        # For the moment, only used to structure memory addresses
        if self.memory_id in operand:
            return self.process_memory_address(operand[self.memory_id])
        if self.immediate_id in operand:
            return self.process_immediate(operand[self.immediate_id])
        if self.label_id in operand:
            return self.process_label(operand[self.label_id])
        if self.directive_id in operand:
            return self.process_directive(operand[self.directive_id])
        if self.register_id in operand:
            return self.process_register(operand[self.register_id])
        if self.identifier in operand:
            return self.process_identifier(operand[self.identifier])
        return operand

    def process_register(self, operand):
        return RegisterOperand(
            prefix=operand["prefix"].lower() if "prefix" in operand else None,
            name=operand["name"],
            shape=operand["shape"].lower() if "shape" in operand else None,
            lanes=operand["lanes"] if "lanes" in operand else None,
            index=operand["index"] if "index" in operand else None,
            predication=operand["predication"].lower() if "predication" in operand else None,
        )

    def process_directive(self, directive):
        directive_new = DirectiveOperand(
            name=directive["name"],
            parameters=directive["parameters"] if "parameters" in directive else [],
        )
        return directive_new, directive["comment"] if "comment" in directive else None

    def process_memory_address(self, memory_address):
        """Post-process memory address operand"""
        # Remove unecessarily created dictionary entries during memory address parsing
        offset = memory_address.get("offset", None)
        base = memory_address.get("base", None)
        baseOp = None
        indexOp = None
        index = memory_address.get("index", None)
        scale = 1 if "scale" not in memory_address else int(memory_address["scale"], 0)
        if isinstance(offset, str) and base is None and index is None:
            try:
                offset = ImmediateOperand(value=int(offset, 0))
            except ValueError:
                offset = ImmediateOperand(value=offset)
        elif offset is not None and "value" in offset:
            offset = ImmediateOperand(value=int(offset["value"], 0))
        if base is not None:
            baseOp = RegisterOperand(
                name=base["name"], prefix=base["prefix"] if "prefix" in base else None
            )
        if index is not None:
            indexOp = RegisterOperand(
                name=index["name"], prefix=index["prefix"] if "prefix" in index else None
            )
        if isinstance(offset, dict) and "identifier" in offset:
            offset = IdentifierOperand(name=offset["identifier"]["name"])
        new_dict = MemoryOperand(offset=offset, base=baseOp, index=indexOp, scale=scale)
        # Add segmentation extension if existing
        if self.segment_ext in memory_address:
            new_dict.segment_ext = memory_address[self.segment_ext]
        return new_dict

    def process_label(self, label):
        """Post-process label asm line"""
        # remove duplicated 'name' level due to identifier
        label["name"] = label["name"][0]["name"]
        return LabelOperand(name=label["name"]), label["comment"] if "comment" in label else None

    def process_immediate(self, immediate):
        """Post-process immediate operand"""
        if "identifier" in immediate:
            # actually an identifier, change declaration
            return self.process_identifier(immediate["identifier"])
        # otherwise just make sure the immediate is a decimal
        new_immediate = ImmediateOperand(value=int(immediate["value"], 0))
        return new_immediate

    def process_identifier(self, identifier):
        return IdentifierOperand(name=identifier["name"])

    def get_full_reg_name(self, register):
        """Return one register name string including all attributes"""
        # nothing to do
        return register.name

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if isinstance(imd, IdentifierOperand):
            return imd
        if imd.value is not None:
            if isinstance(imd.value, str):
                # return decimal
                return int(imd.value, 0)
            else:
                return imd.value
        # identifier
        return imd

    def is_flag_dependend_of(self, flag_a, flag_b):
        """Check if ``flag_a`` is dependent on ``flag_b``"""
        # we assume flags are independent of each other, e.g., CF can be read while ZF gets written
        # TODO validate this assumption
        return flag_a.name == flag_b.name

    def is_reg_dependend_of(self, reg_a, reg_b):
        """Check if ``reg_a`` is dependent on ``reg_b``"""
        reg_a_name = reg_a.name.upper()
        reg_b_name = reg_b.name.upper()

        # Check if they are the same registers
        if reg_a_name == reg_b_name:
            return True
        # Check vector registers first
        if self.is_vector_register(reg_a):
            if self.is_vector_register(reg_b):
                if reg_a_name[1:] == reg_b_name[1:]:
                    # Registers in the same vector space
                    return True
            return False
        # Check basic GPRs
        gpr_groups = {
            "A": ["RAX", "EAX", "AX", "AH", "AL"],
            "B": ["RBX", "EBX", "BX", "BH", "BL"],
            "C": ["RCX", "ECX", "CX", "CH", "CL"],
            "D": ["RDX", "EDX", "DX", "DH", "DL"],
            "SP": ["RSP", "ESP", "SP", "SPL"],
            "SRC": ["RSI", "ESI", "SI", "SIL"],
            "DST": ["RDI", "EDI", "DI", "DIL"],
        }
        if self.is_basic_gpr(reg_a):
            if self.is_basic_gpr(reg_b):
                for dep_group in gpr_groups.values():
                    if reg_a_name in dep_group:
                        if reg_b_name in dep_group:
                            return True
            return False

        # Check other GPRs
        ma = re.match(r"R([0-9]+)[DWB]?", reg_a_name)
        mb = re.match(r"R([0-9]+)[DWB]?", reg_b_name)
        if ma and mb and ma.group(1) == mb.group(1):
            return True

        # No dependencies
        return False

    def is_basic_gpr(self, register):
        """Check if register is a basic general purpose register (ebi, rax, ...)"""
        if any(char.isdigit() for char in register.name) or any(
            register.name.lower().startswith(x) for x in ["mm", "xmm", "ymm", "zmm"]
        ):
            return False
        return True

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        if register is None:
            return False
        if self.is_basic_gpr(register):
            return True
        return re.match(r"R([0-9]+)[DWB]?", register.name, re.IGNORECASE)

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        if register is None or register.name is None:
            return False
        if register.name.rstrip(string.digits).lower() in [
            "mm",
            "xmm",
            "ymm",
            "zmm",
        ]:
            return True
        return False

    def get_reg_type(self, register):
        """Get register type"""
        if register is None:
            return False
        if self.is_gpr(register):
            return "gpr"
        elif self.is_vector_register(register):
            return register.name.rstrip(string.digits).lower()
        raise ValueError
