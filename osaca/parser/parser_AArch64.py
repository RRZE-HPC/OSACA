#!/usr/bin/env python3
from copy import deepcopy
import pyparsing as pp

from osaca.parser import AttrDict, BaseParser, DirectiveOperand, IdentifierOperand, ImmediateOperand, MemoryOperand, RegisterOperand, PrefetchOperand, InstructionForm


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
        ).setResultsName("COMMENT")
        # Define ARM assembly identifier
        decimal_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Word(pp.nums)
        ).setResultsName("value")
        hex_number = pp.Combine(pp.Literal("0x") + pp.Word(pp.hexnums)).setResultsName("value")
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
        ).setResultsName("IDENTIFIER")
        # Label
        self.label = pp.Group(
            identifier.setResultsName("name") + pp.Literal(":") + pp.Optional(self.comment)
        ).setResultsName("LABEL")
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
        ).setResultsName("DIRECTIVE")
        # LLVM-MCA markers
        self.llvm_markers = pp.Group(
            pp.Literal("#")
            + pp.Combine(
                pp.CaselessLiteral("LLVM-MCA-")
                + (pp.CaselessLiteral("BEGIN") | pp.CaselessLiteral("END"))
            )
            + pp.Optional(self.comment)
        ).setResultsName("COMMENT")

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
        ).setResultsName("IMMEDIATE")
        shift_op = (
            pp.CaselessLiteral("lsl")
            ^ pp.CaselessLiteral("lsr")
            ^ pp.CaselessLiteral("asr")
            ^ pp.CaselessLiteral("ror")
            ^ pp.CaselessLiteral("sxtw")
            ^ pp.CaselessLiteral("uxtw")
            ^ pp.CaselessLiteral("mul vl")
        )
        arith_immediate = pp.Group(
            immediate.setResultsName("base_immediate")
            + pp.Suppress(pp.Literal(","))
            + shift_op.setResultsName("shift_op")
            + pp.Optional(immediate).setResultsName("shift")
        ).setResultsName("IMMEDIATE")
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
                + pp.Optional(index)
            )
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
        ).setResultsName("REGISTER")
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
        ).setResultsName("MEMORY")
        prefetch_op = pp.Group(
            pp.Group(pp.CaselessLiteral("PLD") ^ pp.CaselessLiteral("PST")).setResultsName("type")
            + pp.Group(
                pp.CaselessLiteral("L1") ^ pp.CaselessLiteral("L2") ^ pp.CaselessLiteral("L3")
            ).setResultsName("target")
            + pp.Group(pp.CaselessLiteral("KEEP") ^ pp.CaselessLiteral("STRM")).setResultsName(
                "policy"
            )
        ).setResultsName("PRFOP")
        # Combine to instruction form
        operand_first = pp.Group(
            register ^ (prefetch_op | immediate) ^ memory ^ arith_immediate ^ identifier
        )
        operand_rest = pp.Group((register ^ immediate ^ memory ^ arith_immediate) | identifier)
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
        instruction_form = InstructionForm(line=line, line_number=line_number)
        result = None

        # 1. Parse comment
        try:
            result = self.process_operand(self.comment.parseString(line, parseAll=True).asDict())
            instruction_form.comment = " ".join(result["COMMENT"])
        except pp.ParseException:
            pass
        # 1.2 check for llvm-mca marker
        try:
            result = self.process_operand(
                self.llvm_markers.parseString(line, parseAll=True).asDict()
            )
            instruction_form.comment = " ".join(result["COMMENT"])
        except pp.ParseException:
            pass
        # 2. Parse label
        if result is None:
            try:
                result = self.process_operand(self.label.parseString(line, parseAll=True).asDict())
                instruction_form.label = result["LABEL"]["name"]
                if "COMMENT" in result["LABEL"]:
                    instruction_form.comment = " ".join(
                        result["LABEL"]["COMMENT"]
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
                instruction_form["DIRECTIVE"] = AttrDict(
                    {
                        "name": result["DIRECTIVE"].name,
                        "parameters": result["DIRECTIVE"].parameters,
                    }
                )
                if "COMMENT" in result["DIRECTIVE"]:
                    instruction_form["COMMENT"] = " ".join(
                        result["DIRECTIVE"]["COMMENT"]
                    )
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
            operand = self.process_operand(result["operand1"])
            operand.name = operand_strings[0]
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check second operand
        if "operand2" in result:
            operand = self.process_operand(result["operand2"])
            operand.name = operand_strings[1]
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check third operand
        if "operand3" in result:
            operand = self.process_operand(result["operand3"])
            operand.name = operand_strings[2]
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check fourth operand
        if "operand4" in result:
            operand = self.process_operand(result["operand4"])
            operand.name = operand_strings[3]
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)
        # Check fifth operand
        if "operand5" in result:
            operand = self.process_operand(result["operand5"])
            operand.name = operand_strings[4]
            operands.extend(operand) if isinstance(operand, list) else operands.append(operand)

        return_dict = AttrDict(
            {
                "MNEMONIC": result["mnemonic"],
                "OPERANDS": operands,
                "COMMENT": " ".join(result["COMMENT"])
                if "COMMENT" in result
                else None,
            }
        )
        return return_dict

    def process_operand(self, operand):
        """Post-process operand"""
        if "REGISTER" in operand:
            return self.process_register(operand["REGISTER"])
        # structure memory addresses
        if "MEMORY" in operand:
            return self.process_memory_address(operand["MEMORY"])
        # add value attribute to floating point immediates without exponent
        if "IMMEDIATE" in operand:
            return self.process_immediate(operand["IMMEDIATE"])
        if "LABEL" in operand:
            return self.process_label(operand["LABEL"])
        if "IDENTIFIER" in operand:
            return self.process_identifier(operand["IDENTIFIER"])
        if "PRFOP" in operand:
            return self.process_prfop(operand["PRFOP"])
        return operand

    def process_register(self, register):
        # structure register lists
        if "list" in register or "range" in register:
            # resolve ranges and lists
            return self.resolve_range_list(self.process_register_list(register))
        return self.get_regop_info_by_reg(register)

    def process_memory_address(self, memory_address):
        """Post-process memory address operand"""
        # Remove unnecessarily created dictionary entries during parsing
        offset = memory_address.get("offset", None)
        base = memory_address.get("base", None)
        index = memory_address.get("index", None)
        scale = 1
        # convert offset to operand
        if isinstance(offset, list) and len(offset) == 1:
            offset = offset[0]
        if offset is not None and "value" in offset:
            offset = ImmediateOperand(offset["value"])
        # convert base to operand
        if base is not None and "name" in base:
            base = self.get_regop_info_by_reg(base)
        # convert index to operand
        if index is not None and "name" in index:
            index = self.get_regop_info_by_reg(index)
        valid_shift_ops = ["lsl", "uxtw", "sxtw"]
        scale = 1
        if "index" in memory_address:
            if "shift" in memory_address["index"]:
                if memory_address["index"]["shift_op"].lower() in valid_shift_ops:
                    scale = 2 ** int(memory_address["index"]["shift"][0]["value"])
        pre_indexed = True if "pre_indexed" in memory_address else False
        post_indexed = True if "post_indexed" in memory_address else False
        indexed_val = None
        if "post_indexed" in memory_address:
            if "value" in memory_address["post_indexed"]:
                indexed_val = ImmediateOperand(memory_address["post_indexed"]["value"])
        new_op = MemoryOperand("", offset=offset, base=base, index=index, scale=scale, pre_indexed=pre_indexed, post_indexed=post_indexed, indexed_val=indexed_val)
        return new_op

    def get_regop_info_by_reg(self, reg):
        if isinstance(reg, list):
            # range or list
            reglist = [self.get_regop_info_by_reg(r) for r in reg]
            return reglist
        if "name" not in reg:
            return None
        regid = reg["name"].lower()
        if regid == "sp":
            # special treatment for stack pointer
            reg["prefix"] = "x"
        name_str = self.get_full_reg_name(reg)
        regtype = self.get_reg_type(reg)
        prefix = reg["prefix"]
        shape = reg.get("shape", None)
        shape = shape.lower() if shape is not None else None
        index = reg.get("index", None)
        lanes = reg.get("lanes", None)
        if regtype == "gpr":
            if prefix == "w":
                width = 32
            else:
                width = 64
        else:
            # vector
            if prefix == "b":
                width = 8
            elif prefix == "h":
                width = 16
            elif prefix == "s":
                width = 32
            elif prefix == "d":
                width = 64
            elif prefix == "q":
                width = 128
            elif prefix == "v":
                width = 128
            else:
                # since SVE allows variable register widths, we cannot be sure about the size
                # actually used. Set 512 for now
                width = 512

        reg = RegisterOperand(
            name_str,
            width=width,
            prefix=prefix,
            regid=regid,
            regtype=regtype,
            lanes=lanes,
            shape=shape,
            index=index
        )
        return reg

    def resolve_range_list(self, operand):
        """Resolve range or list register operand to list of registers."""
        if "register" in operand:
            if "list" in operand["REGISTER"]:
                index = operand["REGISTER"].get("index")
                range_list = []
                for reg in operand["REGISTER"]["list"]:
                    reg = deepcopy(reg)
                    if index is not None:
                        reg["index"] = int(index, 0)
                    range_list.append({"REGISTER": reg})
                return range_list
            elif "range" in operand.register:
                base_register = operand["REGISTER"]["range"][0]
                index = operand["REGISTER"].get("index")
                range_list = []
                start_name = base_register["name"]
                end_name = operand["REGISTER"]["range"][1]["name"]
                for name in range(int(start_name), int(end_name) + 1):
                    reg = deepcopy(base_register)
                    if index is not None:
                        reg["index"] = int(index, 0)
                    reg["name"] = str(name)
                    range_list.append({"REGISTER": reg})
                return range_list
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
            rlist.append(
                self.list_element.parseString(r, parseAll=True).asDict()
            )
        index = register_list.get("index", None)
        new_dict = {dict_name: rlist, "index": index}
        if len(new_dict[dict_name]) == 1:
            return {"REGISTER": new_dict[dict_name][0]}
        return {"REGISTER": new_dict}

    def process_immediate(self, immediate):
        """Post-process immediate operand"""
        if "IDENTIFIER" in immediate:
            # actually an identifier, change declaration
            return IdentifierOperand(immediate["IDENTIFIER"])
        if "value" in immediate:
            return ImmediateOperand(immediate["value"])
        if "base_immediate" in immediate:
            # arithmetic immediate, add calculated value as value
            immediate["shift"] = immediate["shift"][0]
            immediate["value"] = self.normalize_imd(immediate["base_immediate"]) << int(
                immediate["shift"]["value"]
            )
            immediate["type"] = "int"
            return ImmediateOperand(immediate["value"])
        else:
            # change 'mantissa' key to 'value'
            return ImmediateOperand(immediate["mantissa"])

    def process_label(self, label):
        """Post-process label asm line"""
        # remove duplicated 'name' level due to identifier
        label["name"] = label["name"]["name"]
        return {"LABEL": label}

    def process_identifier(self, identifier):
        """Post-process identifier operand"""
        # remove value if it consists of symbol+offset
        return IdentifierOperand(identifier["name"], identifier.get("offset", None))

    def process_prfop(self, prfop):
        """Post-process prefetch operand"""
        return PrefetchOperand(prfop["type"], prfop["target"], prfop["policy"])

    def get_full_reg_name(self, register):
        """Return one register name string including all attributes"""
        if "lanes" in register:
            return (
                register["prefix"]
                + str(register["name"])
                + "."
                + str(register["lanes"])
                + register["shape"]
            )
        return register["prefix"] + str(register["name"])

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if "value" in imd:
            if isinstance(imd["value"], str):
                # hex or bin, return decimal
                return int(imd["value"], 0)
            else:
                return imd["value"]
        elif "float" in imd:
            return self.ieee_to_float(imd["float"])
        elif "double" in imd:
            return self.ieee_to_float(imd["double"])
        # identifier
        return imd

    def ieee_to_float(self, ieee_val):
        """Convert IEEE representation to python float"""
        exponent = int(ieee_val["exponent"], 10)
        if ieee_val["e_sign"] == "-":
            exponent *= -1
        return float(ieee_val["mantissa"]) * (10 ** exponent)

    def parse_register(self, register_string):
        raise NotImplementedError

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        if register is None:
            return False
        if isinstance(register, RegisterOperand):
            return "gpr" == register.regtype
        if register["prefix"] in "wx":
            return True
        return False

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        if register is None:
            return False
        if isinstance(register, RegisterOperand):
            return "vector" == register.regtype
        if register["prefix"] in "bhsdqvz":
            return True
        return False

    def is_flag_dependend_of(self, flag_a, flag_b):
        """Check if ``flag_a`` is dependent on ``flag_b``"""
        # we assume flags are independent of each other, e.g., CF can be read while ZF gets written
        # TODO validate this assumption
        if flag_a.name == flag_b.name:
            return True
        return False

    def is_reg_dependend_of(self, reg_a, reg_b):
        """Check if ``reg_a`` is dependent on ``reg_b``"""
        prefixes_gpr = "wx"
        prefixes_vec = "bhsdqvz"
        if reg_a.regid == reg_b.regid:
            if reg_a.prefix in prefixes_gpr and reg_b.prefix in prefixes_gpr:
                return True
            if reg_a.prefix in prefixes_vec and reg_b.prefix in prefixes_vec:
                return True
        return False

    def get_reg_type(self, register):
        """Get register type"""
        if self.is_gpr(register):
            return "gpr"
        if self.is_vector_register(register):
            return "vector"
        raise ValueError
