#!/usr/bin/env python3

import string
import re

import pyparsing as pp

from osaca.parser import (
    BaseParser,
    DirectiveOperand,
    IdentifierOperand,
    ImmediateOperand,
    MemoryOperand,
    RegisterOperand,
    InstructionForm,
)


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
        ).setResultsName("COMMENT")
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
        ).setResultsName("IDENTIFIER")
        # Label
        label_rest = pp.Word(pp.alphanums + "$_.+-()")
        label_identifier = pp.Group(
            pp.Optional(id_offset).setResultsName("offset")
            + pp.Combine(
                pp.delimitedList(pp.Combine(first + pp.Optional(label_rest)), delim="::"),
                joinString="::",
            ).setResultsName("name")
            + pp.Optional(relocation).setResultsName("relocation")
        ).setResultsName("IDENTIFIER")
        numeric_identifier = pp.Group(
            pp.Word(pp.nums).setResultsName("name")
            + pp.Optional(pp.oneOf("b f", caseless=True).setResultsName("suffix"))
        ).setResultsName("IDENTIFIER")
        self.label = pp.Group(
            (label_identifier | numeric_identifier).setResultsName("name")
            + pp.Literal(":")
            + pp.Optional(self.comment)
        ).setResultsName("LABEL")
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
        ).setResultsName("REGISTER")
        # Immediate: pp.Regex('^\$(-?[0-9]+)|(0x[0-9a-fA-F]+),?')
        symbol_immediate = "$"
        immediate = pp.Group(
            pp.Literal(symbol_immediate) + (hex_number | decimal_number | identifier)
        ).setResultsName("IMMEDIATE")

        # Memory preparations
        offset = pp.Group(hex_number | decimal_number | identifier).setResultsName("IMMEDIATE")
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
            pp.Optional(pp.Suppress(pp.Literal("*")))
            + self.register.setResultsName("base")
            + pp.Literal(":")
            + segment_extension.setResultsName("SEGMENT_EXTENSION")
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
        ).setResultsName("MEMORY")

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
        ).setResultsName("DIRECTIVE")

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
            result = self.comment.parseString(line, parseAll=True).asDict()
            instruction_form.comment = " ".join(result["COMMENT"])
        except pp.ParseException:
            pass

        # 2. Parse label
        if result is None:
            try:
                result = self.process_operand(self.label.parseString(line, parseAll=True).asDict())
                instruction_form.label = result["LABEL"]["name"]
                if "COMMENT" in result:
                    instruction_form.comment = " ".join(result["COMMENT"])
            except pp.ParseException:
                pass

        # 3. Parse directive
        if result is None:
            try:
                result = self.process_operand(
                    self.directive.parseString(line, parseAll=True).asDict()
                )
                instruction_form.directive = DirectiveOperand(
                    ".{} {}".format(result["name"], ",".join(result["parameters"])),
                    result["name"],
                    result["parameters"],
                )
                if "COMMENT" in result:
                    instruction_form.comment = " ".join(result["COMMENT"])
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
            instruction_form.mnemonic = result["MNEMONIC"]
            instruction_form.operands += result["OPERANDS"]
            instruction_form.comment = result["COMMENT"]

        return instruction_form

    def parse_instruction(self, instruction):
        """
        Parse instruction in asm line.

        :param str instruction: Assembly line string.
        :returns: `dict` -- parsed instruction form
        """
        result = self.instruction_parser.parseString(instruction, parseAll=True).asDict()
        operands = []
        operand_strings = [op[:-1] if op[-1] == "," else op for op in instruction.split()[1:]]
        # Add operands to list
        # Check first operand
        if "operand1" in result:
            op = self.process_operand(result["operand1"])
            op.name = operand_strings[0]
            operands.append(op)
        # Check second operand
        if "operand2" in result:
            op = self.process_operand(result["operand2"])
            op.name = operand_strings[1]
            operands.append(op)
        # Check third operand
        if "operand3" in result:
            op = self.process_operand(result["operand3"])
            op.name = operand_strings[2]
            operands.append(op)
        # Check fourth operand
        if "operand4" in result:
            op = self.process_operand(result["operand4"])
            op.name = operand_strings[3]
            operands.append(op)
        return_dict = {
            "MNEMONIC": result["mnemonic"].split(",")[0],
            "OPERANDS": operands,
            "COMMENT": " ".join(result["COMMENT"]) if "COMMENT" in result else None,
        }
        return return_dict

    def process_operand(self, operand):
        """Post-process operand"""
        if "REGISTER" in operand:
            return self.process_register(operand["REGISTER"])
        if "MEMORY" in operand:
            return self.process_memory_address(operand["MEMORY"])
        if "IMMEDIATE" in operand:
            return self.process_immediate(operand["IMMEDIATE"])
        if "IDENTIFIER" in operand:
            return self.process_identifier(operand["IDENTIFIER"])
        if "LABEL" in operand:
            return self.process_label(operand["LABEL"])
        if "DIRECTIVE" in operand:
            return self.process_directive(operand["DIRECTIVE"])
        return operand

    def process_register(self, register):
        return self.get_regop_info_by_reg(register)

    def process_identifier(self, identifier):
        return IdentifierOperand(identifier["name"], identifier.get("offset", None))

    def process_directive(self, directive):
        directive_new = {"name": directive["name"], "parameters": []}
        if "parameters" in directive:
            directive_new["parameters"] = directive["parameters"]
        if "comment" in directive:
            directive_new["COMMENT"] = directive["comment"]
        return directive_new

    def process_memory_address(self, memory_address):
        """Post-process memory address operand"""
        # Remove unecessarily created dictionary entries during memory address parsing
        offset = memory_address.get("offset", None)
        base = memory_address.get("base", None)
        index = memory_address.get("index", None)
        scale = 1 if "scale" not in memory_address else int(memory_address["scale"], 0)
        # convert Offset to operand
        if isinstance(offset, str) and base is None and index is None:
            offset = ImmediateOperand(offset)
        elif offset is not None and "value" in offset:
            offset = ImmediateOperand(offset["value"])
        # convert Base to operand
        if base is not None and "name" in base:
            base = self.get_regop_info_by_reg(base)
        # convert index to operand
        if index is not None and "name" in index:
            index = self.get_regop_info_by_reg(index)
        new_op = MemoryOperand("", offset=offset, base=base, index=index, scale=scale)
        # Add segmentation extension if existing
        if "SEGMENT_EXTENSION" in memory_address:
            new_op.segment_extension = memory_address["SEGMENT_EXTENSION"]
        return new_op

    def process_label(self, label):
        """Post-process label asm line"""
        # remove duplicated 'name' level due to identifier
        label["name"] = label["name"][0]["name"]
        return {"LABEL": label}

    def process_immediate(self, immediate):
        """Post-process immediate operand"""
        if "IDENTIFIER" in immediate:
            # actually an identifier, change declaration
            return IdentifierOperand(immediate["IDENTIFIER"])
        # otherwise convert value to operand
        immediate = ImmediateOperand(immediate["value"])
        return immediate

    def get_regop_info_by_reg(self, reg):
        if "name" not in reg:
            return None
        basename = reg["name"].lower()
        # check for masking
        mask = None
        if "mask" in reg:
            mask_str = reg["mask"].lower()
            mask_prefix = mask_str.rstrip(string.digits)
            mask_id = mask_str.lstrip(string.ascii_letters)
            mask = RegisterOperand(
                "{" + mask_str + "}", width=64, prefix=mask_prefix, regid=mask_id, regtype="mask"
            )
        # check for zeroing
        zeroing = False
        if reg.get("zeroing", None) == "z":
            zeroing = True
        reg_dict = {"name": basename}
        regtype = self.get_reg_type(reg_dict)
        prefix = basename.rstrip(string.digits)
        regid = basename.lstrip(string.ascii_letters)
        if regid == "":
            regid = None
        # determine width
        if self.is_gpr(reg_dict):
            if basename[0] == "r":
                width = 64
            elif len(basename) == 3:
                width = 32
            elif basename[-1] == "x" or basename in ["sp", "si", "di"]:
                width = 16
            else:
                width = 8
        elif self.is_vector_register(reg_dict):
            if len(basename) == 2:
                width = 64
            elif basename[0] == "x":
                width = 128
            elif basename[0] == "y":
                width = 256
            else:
                width = 512
        elif regtype == "mask":
            width = 64
        else:
            width = None
        name_str = "%{}{}{}{}".format(
            prefix,
            regid if regid is not None else "",
            mask.name if mask is not None else "",
            "{z}" if zeroing else "",
        )
        reg = RegisterOperand(
            name_str,
            width=width,
            prefix=prefix,
            regid=regid,
            regtype=regtype,
            mask=mask,
            zeroing=zeroing,
        )
        return reg

    def get_full_reg_name(self, register):
        """Return one register name string including all attributes"""
        # nothing to do
        return register.name

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if "value" in imd:
            if isinstance(imd["value"], str):
                # return decimal
                return int(imd["value"], 0)
            else:
                return imd["value"]
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
        # Check if they are the same registers
        if reg_a.name == reg_b.name:
            return True
        # Check vector registers first
        if self.is_vector_register(reg_a):
            if self.is_vector_register(reg_b):
                if reg_a.regid == reg_b.regid:
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
                    if reg_a.name in dep_group:
                        if reg_b.name in dep_group:
                            return True
            return False

        # Check other GPRs
        ma = re.match(r"R([0-9]+)[DWB]?", reg_a.name)
        mb = re.match(r"R([0-9]+)[DWB]?", reg_b.name)
        if ma and mb and ma.group(1) == mb.group(1):
            return True

        # No dependencies
        return False

    def is_basic_gpr(self, register):
        """Check if register is a basic general purpose register (ebi, rax, ...)"""
        if isinstance(register, RegisterOperand):
            if register.regtype != "gpr" or any(char.isdigit() for char in register.name):
                return False
            return True
        if any(char.isdigit() for char in register["name"]) or any(
            register["name"].lower().startswith(x) for x in ["mm", "xmm", "ymm", "zmm"]
        ):
            return False
        return True

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        if register is None:
            return False
        if isinstance(register, RegisterOperand):
            return "gpr" == register.regtype
        if self.is_basic_gpr(register):
            return True
        return re.match(r"R([0-9]+)[DWB]?", register["name"], re.IGNORECASE)

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        if register is None:
            return False
        if isinstance(register, RegisterOperand):
            return "vector" == register.regtype
        if register["name"].rstrip(string.digits).lower() in [
            "mm",
            "xmm",
            "ymm",
            "zmm",
        ]:
            return True
        return False

    def get_reg_type(self, register):
        """Get register type"""
        if isinstance(register, RegisterOperand):
            return register.regtype
        if register is None:
            return False
        if self.is_gpr(register):
            return "gpr"
        elif self.is_vector_register(register):
            return "vector"
        elif register["name"][0] == "k":
            return "mask"
        raise ValueError
