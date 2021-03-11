#!/usr/bin/env python3

import string
import re

import pyparsing as pp

from osaca.parser import AttrDict, BaseParser


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
        """Create parser for ARM AArch64 ISA."""
        decimal_number = pp.Combine(pp.Optional(pp.Literal("-")) + pp.Word(pp.nums)).setResultsName(
            "value"
        )
        hex_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Literal("0x") + pp.Word(pp.hexnums)
        ).setResultsName("value")
        # Comment - either '#' or '//' (icc)
        self.comment = (pp.Literal("#") | pp.Literal("//")) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables))
        ).setResultsName(self.COMMENT_ID)
        # Define x86 assembly identifier
        relocation = pp.Combine(pp.Literal("@") + pp.Word(pp.alphas))
        id_offset = pp.Word(pp.nums) + pp.Suppress(pp.Literal("+"))
        first = pp.Word(pp.alphas + "_.", exact=1)
        rest = pp.Word(pp.alphanums + "$_.+-")
        identifier = pp.Group(
            pp.Optional(id_offset).setResultsName("offset")
            + pp.Combine(
                pp.delimitedList(pp.Combine(first + pp.Optional(rest)), delim="::"), joinString="::"
            ).setResultsName("name")
            + pp.Optional(relocation).setResultsName("relocation")
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
        ).setResultsName(self.LABEL_ID)
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
        ).setResultsName(self.REGISTER_ID)
        # Immediate: pp.Regex('^\$(-?[0-9]+)|(0x[0-9a-fA-F]+),?')
        symbol_immediate = "$"
        immediate = pp.Group(
            pp.Literal(symbol_immediate) + (hex_number | decimal_number | identifier)
        ).setResultsName(self.IMMEDIATE_ID)

        # Memory preparations
        offset = pp.Group(identifier | hex_number | decimal_number).setResultsName(
            self.IMMEDIATE_ID
        )
        scale = pp.Word("1248", exact=1)
        # Segment register extension
        segment_extension = (
            hex_number
            ^ pp.Word(pp.nums)
            ^ pp.Group(
                pp.Optional(offset.setResultsName("offset"))
                + pp.Literal("(")
                + pp.Optional(self.register.setResultsName("base"))
                + pp.Optional(pp.Suppress(pp.Literal(",")))
                + pp.Optional(self.register.setResultsName("index"))
                + pp.Optional(pp.Suppress(pp.Literal(",")))
                + pp.Optional(scale.setResultsName("scale"))
                + pp.Literal(")")
            )
        )
        memory_segmentation = (
            self.register.setResultsName("base")
            + pp.Literal(":")
            + segment_extension.setResultsName(self.SEGMENT_EXT_ID)
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
        ).setResultsName(self.MEMORY_ID)

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
        ).setResultsName(self.DIRECTIVE_ID)

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
        instruction_form = AttrDict(
            {
                self.INSTRUCTION_ID: None,
                self.OPERANDS_ID: [],
                self.DIRECTIVE_ID: None,
                self.COMMENT_ID: None,
                self.LABEL_ID: None,
                "line": line,
                "line_number": line_number,
            }
        )
        result = None

        # 1. Parse comment
        try:
            result = self.process_operand(self.comment.parseString(line, parseAll=True).asDict())
            result = AttrDict.convert_dict(result)
            instruction_form[self.COMMENT_ID] = " ".join(result[self.COMMENT_ID])
        except pp.ParseException:
            pass

        # 2. Parse label
        if result is None:
            try:
                result = self.process_operand(self.label.parseString(line, parseAll=True).asDict())
                result = AttrDict.convert_dict(result)
                instruction_form[self.LABEL_ID] = result[self.LABEL_ID]["name"]
                if self.COMMENT_ID in result[self.LABEL_ID]:
                    instruction_form[self.COMMENT_ID] = " ".join(
                        result[self.LABEL_ID][self.COMMENT_ID]
                    )
            except pp.ParseException:
                pass

        # 3. Parse directive
        if result is None:
            try:
                result = self.process_operand(
                    self.directive.parseString(line, parseAll=True).asDict()
                )
                result = AttrDict.convert_dict(result)
                instruction_form[self.DIRECTIVE_ID] = AttrDict(
                    {
                        "name": result[self.DIRECTIVE_ID]["name"],
                        "parameters": result[self.DIRECTIVE_ID]["parameters"],
                    }
                )
                if self.COMMENT_ID in result[self.DIRECTIVE_ID]:
                    instruction_form[self.COMMENT_ID] = " ".join(
                        result[self.DIRECTIVE_ID][self.COMMENT_ID]
                    )
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
            instruction_form[self.INSTRUCTION_ID] = result[self.INSTRUCTION_ID]
            instruction_form[self.OPERANDS_ID] = result[self.OPERANDS_ID]
            instruction_form[self.COMMENT_ID] = result[self.COMMENT_ID]

        return instruction_form

    def parse_instruction(self, instruction):
        """
        Parse instruction in asm line.

        :param str instruction: Assembly line string.
        :returns: `dict` -- parsed instruction form
        """
        result = self.instruction_parser.parseString(instruction, parseAll=True).asDict()
        result = AttrDict.convert_dict(result)
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
        return_dict = AttrDict(
            {
                self.INSTRUCTION_ID: result["mnemonic"].split(",")[0],
                self.OPERANDS_ID: operands,
                self.COMMENT_ID: " ".join(result[self.COMMENT_ID])
                if self.COMMENT_ID in result
                else None,
            }
        )
        return return_dict

    def process_operand(self, operand):
        """Post-process operand"""
        # For the moment, only used to structure memory addresses
        if self.MEMORY_ID in operand:
            return self.process_memory_address(operand[self.MEMORY_ID])
        if self.IMMEDIATE_ID in operand:
            return self.process_immediate(operand[self.IMMEDIATE_ID])
        if self.LABEL_ID in operand:
            return self.process_label(operand[self.LABEL_ID])
        if self.DIRECTIVE_ID in operand:
            return self.process_directive(operand[self.DIRECTIVE_ID])
        return operand

    def process_directive(self, directive):
        directive_new = {"name": directive["name"], "parameters": []}
        if "parameters" in directive:
            directive_new["parameters"] = directive["parameters"]
        if "comment" in directive:
            directive_new["comment"] = directive["comment"]
        return AttrDict({self.DIRECTIVE_ID: directive_new})

    def process_memory_address(self, memory_address):
        """Post-process memory address operand"""
        # Remove unecessarily created dictionary entries during memory address parsing
        offset = memory_address.get("offset", None)
        base = memory_address.get("base", None)
        index = memory_address.get("index", None)
        scale = 1 if "scale" not in memory_address else int(memory_address["scale"])
        if isinstance(offset, str) and base is None and index is None:
            offset = {"value": offset}
        new_dict = AttrDict({"offset": offset, "base": base, "index": index, "scale": scale})
        # Add segmentation extension if existing
        if self.SEGMENT_EXT_ID in memory_address:
            new_dict[self.SEGMENT_EXT_ID] = memory_address[self.SEGMENT_EXT_ID]
        return AttrDict({self.MEMORY_ID: new_dict})

    def process_label(self, label):
        """Post-process label asm line"""
        # remove duplicated 'name' level due to identifier
        label["name"] = label["name"][0]["name"]
        return AttrDict({self.LABEL_ID: label})

    def process_immediate(self, immediate):
        """Post-process immediate operand"""
        if "identifier" in immediate:
            # actually an identifier, change declaration
            return immediate
        # otherwise nothing to do
        return AttrDict({self.IMMEDIATE_ID: immediate})

    def get_full_reg_name(self, register):
        """Return one register name string including all attributes"""
        # nothing to do
        return register["name"]

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if "value" in imd:
            if imd["value"].lower().startswith("0x"):
                # hex, return decimal
                return int(imd["value"], 16)
            return int(imd["value"], 10)
        # identifier
        return imd

    def is_flag_dependend_of(self, flag_a, flag_b):
        """Check if ``flag_a`` is dependent on ``flag_b``"""
        # we assume flags are independent of each other, e.g., CF can be read while ZF gets written
        # TODO validate this assumption
        if flag_a.name == flag_b.name:
            return True
        return False

    def is_reg_dependend_of(self, reg_a, reg_b):
        """Check if ``reg_a`` is dependent on ``reg_b``"""
        # Normalize name
        reg_a_name = reg_a["name"].upper()
        reg_b_name = reg_b["name"].upper()

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
        if any(char.isdigit() for char in register["name"]) or any(
            register["name"].lower().startswith(x) for x in ["mm", "xmm", "ymm", "zmm"]
        ):
            return False
        return True

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        if register is None:
            return False
        if self.is_basic_gpr(register):
            return True
        return re.match(r"R([0-9]+)[DWB]?", register["name"], re.IGNORECASE)

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        if register is None:
            return False
        if register["name"].rstrip(string.digits).lower() in ["mm", "xmm", "ymm", "zmm"]:
            return True
        return False

    def get_reg_type(self, register):
        """Get register type"""
        if register is None:
            return False
        if self.is_gpr(register):
            return "gpr"
        elif self.is_vector_register(register):
            return register["name"].rstrip(string.digits).lower()
        raise ValueError
