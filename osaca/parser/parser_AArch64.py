#!/usr/bin/env python3
from copy import deepcopy
import pyparsing as pp

from osaca.parser import BaseParser
from osaca.parser.instruction_form import InstructionForm
from osaca.parser.operand import Operand
from osaca.parser.directive import DirectiveOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.label import LabelOperand
from osaca.parser.register import RegisterOperand
from osaca.parser.identifier import IdentifierOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.condition import ConditionOperand
from osaca.parser.prefetch import PrefetchOperand


class ParserAArch64(BaseParser):
    _instance = None

    # Singelton pattern, as this is created very many times
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParserAArch64, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.isa = "aarch64"

    def construct_parser(self):
        """Create parser for ARM AArch64 ISA."""
        # Comment
        symbol_comment = "//"
        self.comment = pp.Literal(symbol_comment) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables))
        ).setResultsName(self.comment_id)
        # Define ARM assembly identifier
        decimal_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Word(pp.nums)
        ).setResultsName("value")
        hex_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Literal("0x") + pp.Word(pp.hexnums)
        ).setResultsName("value")
        relocation = pp.Combine(pp.Literal(":") + pp.Word(pp.alphanums + "_") + pp.Literal(":"))
        first = pp.Word(pp.alphas + "_.", exact=1)
        rest = pp.Word(pp.alphanums + "_.")
        identifier = pp.Group(
            pp.Optional(relocation).setResultsName("relocation")
            + pp.Combine(first + pp.Optional(rest)).setResultsName("name")
            + pp.Optional(
                pp.Suppress(pp.Literal("+"))
                + (hex_number | decimal_number).setResultsName("offset")
            )
        ).setResultsName(self.identifier)
        # Label
        self.label = pp.Group(
            identifier.setResultsName("name") + pp.Literal(":") + pp.Optional(self.comment)
        ).setResultsName(self.label_id)
        # Directive
        directive_option = pp.Combine(
            pp.Word(pp.alphas + "#@.%", exact=1)
            + pp.Optional(pp.Word(pp.printables + " ", excludeChars=","))
        )
        directive_parameter = (
            pp.quotedString | directive_option | identifier | hex_number | decimal_number
        )
        commaSeparatedList = pp.delimitedList(pp.Optional(directive_parameter), delim=",")
        self.directive = pp.Group(
            pp.Literal(".")
            + pp.Word(pp.alphanums + "_").setResultsName("name")
            + (pp.OneOrMore(directive_parameter) ^ commaSeparatedList).setResultsName("parameters")
            + pp.Optional(self.comment)
        ).setResultsName(self.directive_id)
        # LLVM-MCA markers
        self.llvm_markers = pp.Group(
            pp.Literal("#")
            + pp.Combine(
                pp.CaselessLiteral("LLVM-MCA-")
                + (pp.CaselessLiteral("BEGIN") | pp.CaselessLiteral("END"))
            )
            + pp.Optional(self.comment)
        ).setResultsName(self.comment_id)

        ##############################
        # Instructions
        # Mnemonic
        # (?P<instr>[a-zA-Z][a-zA-Z0-9]*)(?P<setflg>S?)(P?<CC>.[a-zA-Z]{2})
        mnemonic = pp.Word(pp.alphanums + ".").setResultsName("mnemonic")
        # Immediate:
        # int: ^-?[0-9]+ | hex: ^0x[0-9a-fA-F]+ | fp: ^[0-9]{1}.[0-9]+[eE]{1}[\+-]{1}[0-9]+[fF]?
        symbol_immediate = "#"
        mantissa = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Word(pp.nums) + pp.Literal(".") + pp.Word(pp.nums)
        ).setResultsName("mantissa")
        exponent = (
            pp.CaselessLiteral("e")
            + pp.Word("+-").setResultsName("e_sign")
            + pp.Word(pp.nums).setResultsName("exponent")
        )
        float_ = pp.Group(
            mantissa + pp.Optional(exponent) + pp.CaselessLiteral("f")
        ).setResultsName("float")
        double_ = pp.Group(mantissa + pp.Optional(exponent)).setResultsName("double")
        immediate = pp.Group(
            pp.Optional(pp.Literal(symbol_immediate))
            + (hex_number ^ decimal_number ^ float_ ^ double_)
            | (pp.Optional(pp.Literal(symbol_immediate)) + identifier)
        ).setResultsName(self.immediate_id)
        shift_op = (
            pp.CaselessLiteral("lsl")
            ^ pp.CaselessLiteral("lsr")
            ^ pp.CaselessLiteral("asr")
            ^ pp.CaselessLiteral("ror")
            ^ pp.CaselessLiteral("sxtw")
            ^ pp.CaselessLiteral("uxtw")
            ^ pp.CaselessLiteral("uxtb")
            ^ pp.CaselessLiteral("mul vl")
        )
        arith_immediate = pp.Group(
            immediate.setResultsName("base_immediate")
            + pp.Suppress(pp.Literal(","))
            + shift_op.setResultsName("shift_op")
            + pp.Optional(immediate).setResultsName("shift")
        ).setResultsName(self.immediate_id)
        # Register:
        # scalar: [XWBHSDQ][0-9]{1,2}  |   vector: [VZ][0-9]{1,2}(\.[12468]{1,2}[BHSD])?
        #  | predicate: P[0-9]{1,2}(/[ZM])?
        # ignore vector len control ZCR_EL[123] for now
        # define SP, ZR register aliases as regex, due to pyparsing does not support
        # proper lookahead
        alias_r31_sp = pp.Regex("(?P<prefix>[a-zA-Z])?(?P<name>(sp|SP))")
        alias_r31_zr = pp.Regex("(?P<prefix>[a-zA-Z])?(?P<name>(zr|ZR))")
        scalar = pp.Word("xwbhsdqXWBHSDQ", exact=1).setResultsName("prefix") + pp.Word(
            pp.nums
        ).setResultsName("name")
        index = pp.Literal("[") + pp.Word(pp.nums).setResultsName("index") + pp.Literal("]")
        vector = (
            pp.oneOf("v z", caseless=True).setResultsName("prefix")
            + pp.Word(pp.nums).setResultsName("name")
            + pp.Optional(
                pp.Literal(".")
                + pp.Optional(pp.Word("12468")).setResultsName("lanes")
                + pp.Word(pp.alphas, exact=1).setResultsName("shape")
            )
            + pp.Optional(index)
        )
        predicate = (
            pp.CaselessLiteral("p").setResultsName("prefix")
            + pp.Word(pp.nums).setResultsName("name")
            + pp.Optional(
                (
                    pp.Suppress(pp.Literal("/"))
                    + pp.oneOf("z m", caseless=True).setResultsName("predication")
                )
                | (
                    pp.Literal(".")
                    + pp.Optional(pp.Word("12468")).setResultsName("lanes")
                    + pp.Word(pp.alphas, exact=1).setResultsName("shape")
                )
            )
        )
        self.list_element = vector ^ scalar
        register_list = (
            pp.Literal("{")
            + (
                pp.delimitedList(pp.Combine(self.list_element), delim=",").setResultsName("list")
                ^ pp.delimitedList(pp.Combine(self.list_element), delim="-").setResultsName(
                    "range"
                )
            )
            + pp.Literal("}")
            + pp.Optional(index)
        )
        register = pp.Group(
            (alias_r31_sp | alias_r31_zr | vector | scalar | predicate | register_list)
            # (alias_r31_sp | alias_r31_zr | vector | scalar | predicate | register_list)
            + pp.Optional(
                pp.Suppress(pp.Literal(","))
                + shift_op.setResultsName("shift_op")
                + pp.Optional(immediate).setResultsName("shift")
            )
        ).setResultsName(self.register_id)
        self.register = register
        # Memory
        register_index = register.setResultsName("index") + pp.Optional(
            pp.Literal(",") + pp.Word(pp.alphas) + immediate.setResultsName("scale")
        )
        memory = pp.Group(
            pp.Literal("[")
            + pp.Optional(register.setResultsName("base"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(register_index ^ (immediate ^ arith_immediate).setResultsName("offset"))
            + pp.Literal("]")
            + pp.Optional(
                pp.Literal("!").setResultsName("pre_indexed")
                | (pp.Suppress(pp.Literal(",")) + immediate.setResultsName("post_indexed"))
            )
        ).setResultsName(self.memory_id)
        prefetch_op = pp.Group(
            pp.Group(pp.CaselessLiteral("PLD") ^ pp.CaselessLiteral("PST")).setResultsName("type")
            + pp.Group(
                pp.CaselessLiteral("L1") ^ pp.CaselessLiteral("L2") ^ pp.CaselessLiteral("L3")
            ).setResultsName("target")
            + pp.Group(pp.CaselessLiteral("KEEP") ^ pp.CaselessLiteral("STRM")).setResultsName(
                "policy"
            )
        ).setResultsName("prfop")
        # Condition codes, based on http://tiny.cc/armcc
        condition = (
            pp.CaselessLiteral("EQ")  # z set
            ^ pp.CaselessLiteral("NE")  # z clear
            ^ pp.CaselessLiteral("CS")  # c set
            ^ pp.CaselessLiteral("HS")  # c set
            ^ pp.CaselessLiteral("CC")  # c clear
            ^ pp.CaselessLiteral("LO")  # c clear
            ^ pp.CaselessLiteral("MI")  # n set
            ^ pp.CaselessLiteral("PL")  # n clear
            ^ pp.CaselessLiteral("VS")  # v set
            ^ pp.CaselessLiteral("VC")  # v clear
            ^ pp.CaselessLiteral("HI")  # c set and z clear
            ^ pp.CaselessLiteral("LS")  # c clear or z set
            ^ pp.CaselessLiteral("GE")  # n and v the same
            ^ pp.CaselessLiteral("LT")  # n and v different
            ^ pp.CaselessLiteral("GT")  # z clear, and n and v the same
            ^ pp.CaselessLiteral("LE")  # z set, or n and v different
            ^ pp.CaselessLiteral("AL")  # any
        ).setResultsName("condition")
        self.condition = condition
        # Combine to instruction form
        operand_first = pp.Group(
            register ^ (prefetch_op | immediate) ^ memory ^ arith_immediate ^ identifier
        )
        operand_rest = pp.Group(
            (register ^ condition ^ immediate ^ memory ^ arith_immediate) | identifier
        )
        self.instruction_parser = (
            mnemonic
            + pp.Optional(operand_first.setResultsName("operand1"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand2"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand3"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand4"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand5"))
            + pp.Optional(self.comment)
        )

        # for testing
        self.predicate = predicate
        self.vector = vector
        self.register = register

    def parse_line(self, line, line_number=None):
        """
        Parse line and return instruction form.

        :param str line: line of assembly code
        :param line_number: identifier of instruction form, defautls to None
        :type line_number: int, optional
        :return: `dict` -- parsed asm line (comment, label, directive or instruction form)
        """
        instruction_form = InstructionForm(
            mnemonic=None,
            operands=[],
            directive_id=None,
            comment_id=None,
            label_id=None,
            line=line,
            line_number=line_number,
        )
        result = None

        # 1. Parse comment
        try:
            result = self.process_operand(self.comment.parseString(line, parseAll=True).asDict())
            instruction_form.comment = " ".join(result[self.comment_id])
        except pp.ParseException:
            pass
        # 1.2 check for llvm-mca marker
        try:
            result = self.process_operand(
                self.llvm_markers.parseString(line, parseAll=True).asDict()
            )
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
                # returns directive with label operand and comment, if any
                result = self.process_operand(
                    self.directive.parseString(line, parseAll=True).asDict()
                )
                instruction_form.directive = DirectiveOperand(
                    name=result[0].name, parameters=result[0].parameters
                )
                if result[1] is not None:
                    instruction_form.comment = " ".join(result[1])
            except pp.ParseException:
                pass

        # 4. Parse instruction
        if result is None:
            try:
                result = self.parse_instruction(line)
            except (pp.ParseException, KeyError) as e:
                raise ValueError(
                    "Unable to parse {!r} on line {}".format(line, line_number)
                ) from e
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
            operand = self.process_operand(result["operand1"])
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check second operand
        if "operand2" in result:
            operand = self.process_operand(result["operand2"])
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check third operand
        if "operand3" in result:
            operand = self.process_operand(result["operand3"])
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check fourth operand
        if "operand4" in result:
            operand = self.process_operand(result["operand4"])
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check fifth operand
        if "operand5" in result:
            operand = self.process_operand(result["operand5"])
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        return_dict = InstructionForm(
            mnemonic=result["mnemonic"],
            operands=operands,
            comment_id=" ".join(result[self.comment_id]) if self.comment_id in result else None,
        )
        return return_dict

    def process_operand(self, operand):
        """Post-process operand"""
        # structure memory addresses
        if self.memory_id in operand:
            return self.process_memory_address(operand[self.memory_id])
        # structure register lists
        if self.register_id in operand and (
            "list" in operand[self.register_id] or "range" in operand[self.register_id]
        ):
            # resolve ranges and lists
            return self.resolve_range_list(self.process_register_list(operand[self.register_id]))
        if self.register_id in operand and operand[self.register_id]["name"].lower() == "sp":
            return self.process_sp_register(operand[self.register_id])
        # add value attribute to floating point immediates without exponent
        if self.immediate_id in operand:
            return self.process_immediate(operand[self.immediate_id])
        if self.label_id in operand:
            return self.process_label(operand[self.label_id])
        if self.identifier in operand:
            return self.process_identifier(operand[self.identifier])
        if self.register_id in operand:
            return self.process_register_operand(operand[self.register_id])
        if self.directive_id in operand:
            return self.process_directive_operand(operand[self.directive_id])
        if self.condition_id in operand:
            return self.process_condition(operand[self.condition_id])
        if self.prefetch in operand:
            return self.process_prefetch_operand(operand[self.prefetch])
        return operand

    def process_prefetch_operand(self, operand):
        return PrefetchOperand(
            type_id=operand["type"] if "type" in operand else None,
            target=operand["target"] if "target" in operand else None,
            policy=operand["policy"] if "policy" in operand else None,
        )

    def process_directive_operand(self, operand):
        return (
            DirectiveOperand(
                name=operand["name"],
                parameters=operand["parameters"],
            ),
            operand["comment"] if "comment" in operand else None,
        )

    def process_register_operand(self, operand):
        return RegisterOperand(
            prefix=operand["prefix"].lower(),
            name=operand["name"],
            shape=operand["shape"].lower() if "shape" in operand else None,
            lanes=operand["lanes"] if "lanes" in operand else None,
            index=operand["index"] if "index" in operand else None,
            predication=operand["predication"].lower() if "predication" in operand else None,
        )

    def process_memory_address(self, memory_address):
        """Post-process memory address operand"""
        # Remove unnecessarily created dictionary entries during parsing
        offset = memory_address.get("offset", None)
        if isinstance(offset, list) and len(offset) == 1:
            offset = offset[0]
        if offset is not None and "value" in offset:
            offset = ImmediateOperand(value=int(offset["value"], 0))
        if isinstance(offset, dict) and "identifier" in offset:
            offset = self.process_identifier(offset["identifier"])
        base = memory_address.get("base", None)
        index = memory_address.get("index", None)
        scale = 1
        if base is not None and "name" in base and base["name"].lower() == "sp":
            base["prefix"] = "x"
        if index is not None and "name" in index and index["name"].lower() == "sp":
            index["prefix"] = "x"
        if base is not None and "name" in base and base["name"].lower() == "zr":
            base["prefix"] = "x"
        if index is not None and "name" in index and index["name"].lower() == "zr":
            index["prefix"] = "x"
        valid_shift_ops = ["lsl", "uxtw", "uxtb", "sxtw"]
        if "index" in memory_address:
            if "shift" in memory_address["index"]:
                if memory_address["index"]["shift_op"].lower() in valid_shift_ops:
                    scale = 2 ** int(memory_address["index"]["shift"][0]["value"])
        if index is not None:
            index = RegisterOperand(
                name=index["name"],
                prefix=index["prefix"] if "prefix" in index else None,
                shift=index["shift"] if "shift" in index else None,
                shift_op=index["shift_op"] if "shift_op" in index else None,
            )
        new_dict = MemoryOperand(
            offset=offset,
            base=RegisterOperand(name=base["name"], prefix=base["prefix"]),
            index=index,
            scale=scale,
        )
        if "pre_indexed" in memory_address:
            new_dict.pre_indexed = True
        if "post_indexed" in memory_address:
            if "value" in memory_address["post_indexed"]:
                new_dict.post_indexed = {"value": int(memory_address["post_indexed"]["value"], 0)}
            else:
                new_dict.post_indexed = memory_address["post_indexed"]
        return new_dict

    def process_sp_register(self, register):
        """Post-process stack pointer register"""
        return RegisterOperand(prefix="x", name="sp")

    def process_condition(self, condition):
        return ConditionOperand(ccode=condition.upper())

    def resolve_range_list(self, operand):
        """
        Resolve range or list register operand to list of registers.
        Returns None if neither list nor range
        """
        if "list" in operand["register"]:
            index = operand["register"].get("index", None)
            range_list = []
            processed_list = []
            for reg in operand["register"]["list"]:
                reg = deepcopy(reg)
                if index is not None:
                    reg["index"] = int(index, 0)
                range_list.append(reg)
            for reg in range_list:
                processed_list.append(self.process_register_operand(reg))
            return processed_list
            # return range_list
        elif "range" in operand["register"]:
            base_register = operand["register"]["range"][0]
            index = operand["register"].get("index", None)
            range_list = []
            processed_list = []
            start_name = base_register["name"]
            end_name = operand["register"]["range"][1]["name"]
            for name in range(int(start_name), int(end_name) + 1):
                reg = deepcopy(base_register)
                if index is not None:
                    reg["index"] = int(index, 0)
                reg["name"] = str(name)
                range_list.append(reg)
            for reg in range_list:
                processed_list.append(self.process_register_operand(reg))
            return processed_list
        # neither register list nor range, return unmodified
        return operand

    def process_register_list(self, register_list):
        """Post-process register lists (e.g., {r0,r3,r5}) and register ranges (e.g., {r0-r7})"""
        # Remove unnecessarily created dictionary entries during parsing
        rlist = []
        dict_name = ""
        if "list" in register_list:
            dict_name = "list"
        if "range" in register_list:
            dict_name = "range"
        for r in register_list[dict_name]:
            rlist.append(self.list_element.parseString(r, parseAll=True).asDict())
        index = register_list.get("index", None)
        new_dict = {dict_name: rlist, "index": index}
        return {self.register_id: new_dict}

    def process_immediate(self, immediate):
        """Post-process immediate operand"""
        dict_name = ""
        if "identifier" in immediate:
            # actually an identifier, change declaration
            return self.process_identifier(immediate["identifier"])
        if "value" in immediate:
            # normal integer value
            immediate["type"] = "int"
            # convert hex/bin immediates to dec
            new_immediate = ImmediateOperand(imd_type=immediate["type"], value=immediate["value"])
            new_immediate.value = self.normalize_imd(new_immediate)
            return new_immediate
        if "base_immediate" in immediate:
            # arithmetic immediate, add calculated value as value
            immediate["shift"] = immediate["shift"][0]
            temp_immediate = ImmediateOperand(value=immediate["base_immediate"]["value"])
            immediate["type"] = "int"
            new_immediate = ImmediateOperand(
                imd_type=immediate["type"], value=None, shift=immediate["shift"]
            )
            new_immediate.value = self.normalize_imd(temp_immediate) << int(
                immediate["shift"]["value"]
            )
            return new_immediate
        if "float" in immediate:
            dict_name = "float"
        if "double" in immediate:
            dict_name = "double"
        if "exponent" in immediate[dict_name]:
            immediate["type"] = dict_name
            return ImmediateOperand(imd_type=immediate["type"], value=immediate[immediate["type"]])
        else:
            # change 'mantissa' key to 'value'
            return ImmediateOperand(value=immediate[dict_name]["mantissa"], imd_type=dict_name)

    def process_label(self, label):
        """Post-process label asm line"""
        # remove duplicated 'name' level due to identifier
        return (
            LabelOperand(name=label["name"]["name"]),
            label["comment"] if self.comment_id in label else None,
        )

    def process_identifier(self, identifier):
        """Post-process identifier operand"""
        return IdentifierOperand(
            name=identifier["name"] if "name" in identifier else None,
            offset=identifier["offset"] if "offset" in identifier else None,
            relocation=identifier["relocation"] if "relocation" in identifier else None,
        )

    def get_full_reg_name(self, register):
        """Return one register name string including all attributes"""
        name = register.prefix + str(register.name)
        if register.shape is not None:
            name += (
                "." + str(register.lanes if register.lanes is not None else "") + register.shape
            )
        if register.index is not None:
            name += "[" + str(register.index) + "]"
        return name

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if isinstance(imd, IdentifierOperand):
            return imd
        if imd.value is not None and imd.imd_type == "float":
            return self.ieee_to_float(imd.value)
        elif imd.value is not None and imd.imd_type == "double":
            return self.ieee_to_float(imd.value)
        elif imd.value is not None:
            if isinstance(imd.value, str):
                # hex or bin, return decimal
                return int(imd.value, 0)
            else:
                return imd.value
        # identifier
        return imd

    def ieee_to_float(self, ieee_val):
        """Convert IEEE representation to python float"""
        exponent = int(ieee_val["exponent"], 10)
        if ieee_val["e_sign"] == "-":
            exponent *= -1
        return float(ieee_val["mantissa"]) * (10**exponent)

    def parse_register(self, register_string):
        raise NotImplementedError

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        if register.prefix in "wx":
            return True
        return False

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        if register.prefix in "bhsdqvz":
            return True
        return False

    def is_flag_dependend_of(self, flag_a, flag_b):
        """Check if ``flag_a`` is dependent on ``flag_b``"""
        # we assume flags are independent of each other, e.g., CF can be read while ZF gets written
        # TODO validate this assumption
        return flag_a.name == flag_b.name

    def is_reg_dependend_of(self, reg_a, reg_b):
        """Check if ``reg_a`` is dependent on ``reg_b``"""
        # if not isinstance(reg_b, Operand):
        #    print(reg_b)
        if not isinstance(reg_a, Operand):
            reg_a = RegisterOperand(name=reg_a["name"])
        prefixes_gpr = "wx"
        prefixes_vec = "bhsdqvz"
        if reg_a.name == reg_b.name:
            if reg_a.prefix.lower() in prefixes_gpr and reg_b.prefix.lower() in prefixes_gpr:
                return True
            if reg_a.prefix.lower() in prefixes_vec and reg_b.prefix.lower() in prefixes_vec:
                return True
        return False

    def get_reg_type(self, register):
        """Get register type"""
        return register.prefix
