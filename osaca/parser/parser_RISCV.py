#!/usr/bin/env python3
import re
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


class ParserRISCV(BaseParser):
    _instance = None

    # Singleton pattern, as this is created very many times
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParserRISCV, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        # Initialize parser, but don't set 'isa' directly as an attribute
        self._isa_str = "riscv"

    def isa(self):
        """Return the ISA string."""
        return self._isa_str

    def start_marker(self):
        """Return the OSACA start marker for RISC-V assembly."""
        # Parse the RISC-V start marker (li a1, 111 followed by NOP)
        # This matches how start marker is defined in marker_utils.py for RISC-V
        marker_str = (
            "li        a1, 111    # OSACA START MARKER\n"
            ".byte     19,0,0,0   # OSACA START MARKER\n"
        )
        return self.parse_file(marker_str)

    def end_marker(self):
        """Return the OSACA end marker for RISC-V assembly."""
        # Parse the RISC-V end marker (li a1, 222 followed by NOP)
        # This matches how end marker is defined in marker_utils.py for RISC-V
        marker_str = (
            "li        a1, 222    # OSACA END MARKER\n"
            ".byte     19,0,0,0   # OSACA END MARKER\n"
        )
        return self.parse_file(marker_str)

    def construct_parser(self):
        """Create parser for RISC-V ISA."""
        # Comment - RISC-V uses # for comments
        symbol_comment = "#"
        self.comment = pp.Literal(symbol_comment) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables))
        ).setResultsName(self.comment_id)

        # Define RISC-V assembly identifier
        decimal_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Word(pp.nums)
        ).setResultsName("value")
        hex_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Literal("0x") + pp.Word(pp.hexnums)
        ).setResultsName("value")

        # RISC-V specific relocation attributes
        reloc_type = (
            pp.Literal("%hi")
            | pp.Literal("%lo")
            | pp.Literal("%pcrel_hi")
            | pp.Literal("%pcrel_lo")
            | pp.Literal("%tprel_hi")
            | pp.Literal("%tprel_lo")
            | pp.Literal("%tprel_add")
        ).setResultsName("reloc_type")

        reloc_expr = pp.Group(
            reloc_type
            + pp.Suppress("(")
            + pp.Word(pp.alphas + pp.nums + "_").setResultsName("symbol")
            + pp.Suppress(")")
        ).setResultsName("relocation")

        # First character of an identifier
        first = pp.Word(pp.alphas + "_.", exact=1)
        # Rest of the identifier
        rest = pp.Word(pp.alphanums + "_.")
        # PLT suffix (@plt) for calls to shared libraries
        plt_suffix = pp.Optional(pp.Literal("@") + pp.Word(pp.alphas))

        identifier = pp.Group(
            (pp.Combine(first + pp.Optional(rest) + plt_suffix)).setResultsName("name")
            + pp.Optional(
                pp.Suppress(pp.Literal("+"))
                + (hex_number | decimal_number).setResultsName("offset")
            )
        ).setResultsName(self.identifier)

        # Immediate with optional relocation
        immediate = pp.Group(
            reloc_expr | (hex_number ^ decimal_number) | identifier
        ).setResultsName(self.immediate_id)

        # Label
        self.label = pp.Group(
            identifier.setResultsName("name")
            + pp.Literal(":")
            + pp.Optional(self.comment)
        ).setResultsName(self.label_id)

        # Directive
        directive_option = pp.Combine(
            pp.Word(pp.alphas + "#@.%", exact=1)
            + pp.Optional(pp.Word(pp.printables + " ", excludeChars=","))
        )

        directive_parameter = (
            pp.quotedString
            | directive_option
            | identifier
            | hex_number
            | decimal_number
        )
        commaSeparatedList = pp.delimitedList(
            pp.Optional(directive_parameter), delim=","
        )
        self.directive = pp.Group(
            pp.Literal(".")
            + pp.Word(pp.alphanums + "_").setResultsName("name")
            + (pp.OneOrMore(directive_parameter) ^ commaSeparatedList).setResultsName(
                "parameters"
            )
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
        mnemonic = pp.Word(pp.alphanums + ".").setResultsName("mnemonic")

        # Register:
        # RISC-V has two main types of registers:
        # 1. Integer registers (x0-x31 or ABI names)
        # 2. Floating-point registers (f0-f31 or ABI names)

        # Integer register ABI names
        integer_reg_abi = (
            pp.CaselessLiteral("zero")
            | pp.CaselessLiteral("ra")
            | pp.CaselessLiteral("sp")
            | pp.CaselessLiteral("gp")
            | pp.CaselessLiteral("tp")
            | pp.Regex(r"[tas][0-9]+")  # t0-t6, a0-a7, s0-s11
        ).setResultsName("name")

        # Integer registers x0-x31
        integer_reg_x = pp.CaselessLiteral("x").setResultsName("prefix") + pp.Word(
            pp.nums
        ).setResultsName("name")

        # Floating point registers
        fp_reg_abi = pp.Regex(r"f[tas][0-9]+").setResultsName(
            "name"
        )  # ft0-ft11, fa0-fa7, fs0-fs11

        fp_reg_f = pp.CaselessLiteral("f").setResultsName("prefix") + pp.Word(
            pp.nums
        ).setResultsName("name")

        # Control and status registers (CSRs)
        csr_reg = pp.Combine(
            pp.CaselessLiteral("csr") + pp.Word(pp.alphanums + "_")
        ).setResultsName("name")

        # Vector registers (for the "V" extension)
        vector_reg = pp.CaselessLiteral("v").setResultsName("prefix") + pp.Word(
            pp.nums
        ).setResultsName("name")

        # Combined register definition
        register = pp.Group(
            integer_reg_x
            | integer_reg_abi
            | fp_reg_f
            | fp_reg_abi
            | vector_reg
            | csr_reg
        ).setResultsName(self.register_id)

        self.register = register

        # Memory addressing mode in RISC-V: offset(base_register)
        memory = pp.Group(
            pp.Optional(immediate.setResultsName("offset"))
            + pp.Suppress(pp.Literal("("))
            + register.setResultsName("base")
            + pp.Suppress(pp.Literal(")"))
        ).setResultsName(self.memory_id)

        # Combine to instruction form
        operand_first = pp.Group(register ^ immediate ^ memory ^ identifier)
        operand_rest = pp.Group(register ^ immediate ^ memory ^ identifier)

        # Handle additional vector parameters
        additional_params = pp.ZeroOrMore(
            pp.Suppress(pp.Literal(","))
            + pp.Word(pp.alphas + pp.nums).setResultsName(
                "vector_param", listAllMatches=True
            )
        )

        # Main instruction parser
        self.instruction_parser = (
            mnemonic
            + pp.Optional(operand_first.setResultsName("operand1"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand2"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand3"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand_rest.setResultsName("operand4"))
            + pp.Optional(additional_params)
            + pp.Optional(self.comment)
        )

    def parse_line(self, line, line_number=None):
        """
        Parse line and return instruction form.

        :param str line: line of assembly code
        :param line_number: identifier of instruction form, defaults to None
        :type line_number: int, optional
        :return: `dict` -- parsed asm line (comment, label, directive or
                 instruction form)
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
            result = self.process_operand(
                self.comment.parseString(line, parseAll=True).asDict()
            )
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
                result = self.process_operand(
                    self.label.parseString(line, parseAll=True).asDict()
                )
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
        # Store current instruction for context in operand processing
        if instruction.startswith("vsetvli"):
            self.current_instruction = "vsetvli"
        else:
            # Extract mnemonic for context
            parts = instruction.split("#")[0].strip().split()
            self.current_instruction = parts[0] if parts else None

        # Special handling for vector instructions like vsetvli with many parameters
        if instruction.startswith("vsetvli"):
            # Split into mnemonic and operands part
            parts = (
                instruction.split("#")[0].strip().split(None, 1)
            )  # Split on first whitespace only
            mnemonic = parts[0]

            # Split operands by commas
            if len(parts) > 1:
                operand_part = parts[1]
                operands_list = [op.strip() for op in operand_part.split(",")]

                # Process each operand
                operands = []
                for op in operands_list:
                    if (
                        op.startswith("x")
                        or op in ["zero", "ra", "sp", "gp", "tp"]
                        or re.match(r"[tas][0-9]+", op)
                    ):
                        operands.append(RegisterOperand(name=op))
                    else:
                        # Vector parameters get appropriate attributes
                        if op.startswith("e"):  # Element width
                            operands.append(IdentifierOperand(name=op))
                        elif op.startswith("m"):  # LMUL setting
                            operands.append(IdentifierOperand(name=op))
                        elif op in ["ta", "tu", "ma", "mu"]:  # Tail/mask policies
                            operands.append(IdentifierOperand(name=op))
                        else:
                            operands.append(IdentifierOperand(name=op))

                # Get comment if present
                comment = None
                if "#" in instruction:
                    comment = instruction.split("#", 1)[1].strip()

                return InstructionForm(
                    mnemonic=mnemonic, operands=operands, comment_id=comment
                )

        # Regular instruction parsing
        try:
            result = self.instruction_parser.parseString(
                instruction, parseAll=True
            ).asDict()
            operands = []

            # Process operands
            for i in range(1, 5):
                operand_key = f"operand{i}"
                if operand_key in result:
                    operand = self.process_operand(result[operand_key])
                    (
                        operands.extend(operand)
                        if isinstance(operand, list)
                        else operands.append(operand)
                    )

            # Handle vector parameters as identifiers with appropriate attributes
            if "vector_param" in result:
                if isinstance(result["vector_param"], list):
                    for param in result["vector_param"]:
                        if param.startswith("e"):  # Element width
                            operands.append(IdentifierOperand(name=param))
                        elif param.startswith("m"):  # LMUL setting
                            operands.append(IdentifierOperand(name=param))
                        else:
                            operands.append(IdentifierOperand(name=param))
                else:
                    operands.append(IdentifierOperand(name=result["vector_param"]))

            return_dict = InstructionForm(
                mnemonic=result["mnemonic"],
                operands=operands,
                comment_id=(
                    " ".join(result[self.comment_id])
                    if self.comment_id in result
                    else None
                ),
            )
            return return_dict

        except Exception:
            # For special vector instructions or ones with % in them
            if "%" in instruction or instruction.startswith("v"):
                parts = instruction.split("#")[0].strip().split(None, 1)
                mnemonic = parts[0]
                operands = []
                if len(parts) > 1:
                    operand_part = parts[1]
                    operands_list = [op.strip() for op in operand_part.split(",")]
                    for op in operands_list:
                        # Process '%hi(data)' to 'data' for certain operands
                        if op.startswith("%") and "(" in op and ")" in op:
                            reloc_type = op[: op.index("(")]
                            symbol = op[op.index("(") + 1 : op.index(")")]
                            operands.append(
                                ImmediateOperand(
                                    imd_type="reloc",
                                    value=None,
                                    reloc_type=reloc_type,
                                    symbol=symbol,
                                )
                            )
                        else:
                            operands.append(IdentifierOperand(name=op))

                comment = None
                if "#" in instruction:
                    comment = instruction.split("#", 1)[1].strip()

                return InstructionForm(
                    mnemonic=mnemonic, operands=operands, comment_id=comment
                )
            else:
                raise

    def process_operand(self, operand):
        """Post-process operand"""
        # structure memory addresses
        if self.memory_id in operand:
            return self.process_memory_address(operand[self.memory_id])
        # add value attribute to immediates
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
        return operand

    def process_directive_operand(self, operand):
        return (
            DirectiveOperand(
                name=operand["name"],
                parameters=operand["parameters"],
            ),
            operand["comment"] if "comment" in operand else None,
        )

    def process_register_operand(self, operand):
        """Process register operands, including ABI name to x-register mapping
        and vector attributes"""
        # If already has prefix (x#, f#, v#), process with appropriate attributes
        if "prefix" in operand:
            prefix = operand["prefix"].lower()

            # Special handling for vector registers
            if prefix == "v":
                return RegisterOperand(
                    prefix=prefix,
                    name=operand["name"],
                    regtype="vector",
                    # Vector registers can have different element widths (e8,e16,e32,e64)
                    width=operand.get("width", None),
                    # Number of elements (m1,m2,m4,m8)
                    lanes=operand.get("lanes", None),
                    # For vector mask registers
                    mask=operand.get("mask", False),
                    # For tail agnostic/undisturbed policies
                    zeroing=operand.get("zeroing", False),
                )
            # For floating point registers
            elif prefix == "f":
                return RegisterOperand(
                    prefix=prefix,
                    name=operand["name"],
                    regtype="float",
                    width=64,  # RISC-V typically uses 64-bit float registers
                )
            # For integer registers
            elif prefix == "x":
                return RegisterOperand(
                    prefix=prefix,
                    name=operand["name"],
                    regtype="int",
                    width=64,  # RV64 uses 64-bit registers
                )

        # Handle ABI names by converting to x-register numbers
        name = operand["name"].lower()

        # ABI name mapping for integer registers
        abi_to_x = {
            "zero": "x0",
            "ra": "x1",
            "sp": "x2",
            "gp": "x3",
            "tp": "x4",
            "t0": "x5",
            "t1": "x6",
            "t2": "x7",
            "s0": "x8",
            "s1": "x9",
            "a0": "x10",
            "a1": "x11",
            "a2": "x12",
            "a3": "x13",
            "a4": "x14",
            "a5": "x15",
            "a6": "x16",
            "a7": "x17",
            "s2": "x18",
            "s3": "x19",
            "s4": "x20",
            "s5": "x21",
            "s6": "x22",
            "s7": "x23",
            "s8": "x24",
            "s9": "x25",
            "s10": "x26",
            "s11": "x27",
            "t3": "x28",
            "t4": "x29",
            "t5": "x30",
            "t6": "x31",
        }

        # Integer register ABI names
        if name in abi_to_x:
            return RegisterOperand(
                prefix="x",
                name=abi_to_x[name],
                regtype="int",
                width=64,  # RV64 uses 64-bit registers
            )
        # Floating point register ABI names
        elif name.startswith("f") and name[1] in ["t", "a", "s"]:
            if name[1] == "a":  # fa0-fa7
                idx = int(name[2:])
                return RegisterOperand(
                    prefix="f", name=str(idx + 10), regtype="float", width=64
                )
            elif name[1] == "s":  # fs0-fs11
                idx = int(name[2:])
                if idx <= 1:
                    return RegisterOperand(
                        prefix="f", name=str(idx + 8), regtype="float", width=64
                    )
                else:
                    return RegisterOperand(
                        prefix="f", name=str(idx + 16), regtype="float", width=64
                    )
            elif name[1] == "t":  # ft0-ft11
                idx = int(name[2:])
                if idx <= 7:
                    return RegisterOperand(
                        prefix="f", name=str(idx), regtype="float", width=64
                    )
                else:
                    return RegisterOperand(
                        prefix="f", name=str(idx + 20), regtype="float", width=64
                    )
        # CSR registers
        elif name.startswith("csr"):
            return RegisterOperand(prefix="", name=name, regtype="csr")

        # If no mapping found, return as is
        return RegisterOperand(prefix="", name=name)

    def process_memory_address(self, memory_address):
        """Post-process memory address operand with RISC-V specific attributes"""
        # Process offset
        offset = memory_address.get("offset", None)
        if isinstance(offset, list) and len(offset) == 1:
            offset = offset[0]
        if offset is not None and "value" in offset:
            offset = ImmediateOperand(value=int(offset["value"], 0))
        if isinstance(offset, dict) and "identifier" in offset:
            offset = self.process_identifier(offset["identifier"])

        # Process base register
        base = memory_address.get("base", None)
        if base is not None:
            base = self.process_register_operand(base)

        # Determine data type from instruction context if available
        # RISC-V load/store instructions encode the data width in the mnemonic
        # e.g., lw (word), lh (half), lb (byte), etc.
        data_type = None
        if hasattr(self, "current_instruction"):
            mnemonic = self.current_instruction.lower()
            if any(x in mnemonic for x in ["b", "bu"]):  # byte operations
                data_type = "byte"
            elif any(x in mnemonic for x in ["h", "hu"]):  # halfword operations
                data_type = "halfword"
            elif any(x in mnemonic for x in ["w", "wu"]):  # word operations
                data_type = "word"
            elif "d" in mnemonic:  # doubleword operations
                data_type = "doubleword"

        # Create memory operand with enhanced attributes
        return MemoryOperand(
            offset=offset,
            base=base,
            index=None,  # RISC-V doesn't use index registers
            scale=1,  # RISC-V doesn't use scaling
            data_type=data_type,
            # Handle vector memory operations
            mask=memory_address.get("mask", None),  # For vector masked loads/stores
            src=memory_address.get("src", None),  # Source register type for stores
            dst=memory_address.get("dst", None),  # Destination register type for loads
        )

    def process_label(self, label):
        """Post-process label asm line"""
        return (
            LabelOperand(name=label["name"]["name"]),
            label["comment"] if self.comment_id in label else None,
        )

    def process_identifier(self, identifier):
        """Post-process identifier operand"""
        return IdentifierOperand(
            name=identifier["name"] if "name" in identifier else None,
            offset=identifier["offset"] if "offset" in identifier else None,
        )

    def process_immediate(self, immediate):
        """Post-process immediate operand with RISC-V specific handling"""
        # Handle relocations
        if "relocation" in immediate:
            reloc = immediate["relocation"]
            return ImmediateOperand(
                imd_type="reloc",
                value=None,
                reloc_type=reloc["reloc_type"],
                symbol=reloc["symbol"],
            )

        # Handle identifiers
        if "identifier" in immediate:
            return self.process_identifier(immediate["identifier"])

        # Handle numeric values with validation
        if "value" in immediate:
            value = int(
                immediate["value"], 0
            )  # Convert to integer, handling hex/decimal

            # Determine immediate type and validate range based on instruction type
            if hasattr(self, "current_instruction"):
                mnemonic = self.current_instruction.lower()

                # I-type instructions (12-bit signed immediate)
                if any(
                    x in mnemonic
                    for x in [
                        "addi",
                        "slti",
                        "xori",
                        "ori",
                        "andi",
                        "slli",
                        "srli",
                        "srai",
                    ]
                ):
                    if not -2048 <= value <= 2047:
                        raise ValueError(
                            f"Immediate value {value} out of range for I-type "
                            f"instruction (-2048 to 2047)"
                        )
                    return ImmediateOperand(imd_type="I", value=value)

                # S-type instructions (12-bit signed immediate for store)
                elif any(x in mnemonic for x in ["sb", "sh", "sw", "sd"]):
                    if not -2048 <= value <= 2047:
                        raise ValueError(
                            f"Immediate value {value} out of range for S-type "
                            f"instruction (-2048 to 2047)"
                        )
                    return ImmediateOperand(imd_type="S", value=value)

                # B-type instructions (13-bit signed immediate for branches, must be even)
                elif any(
                    x in mnemonic for x in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]
                ):
                    if not -4096 <= value <= 4095 or value % 2 != 0:
                        raise ValueError(
                            f"Immediate value {value} out of range or not even "
                            f"for B-type instruction (-4096 to 4095, must be even)"
                        )
                    return ImmediateOperand(imd_type="B", value=value)

                # U-type instructions (20-bit upper immediate)
                elif any(x in mnemonic for x in ["lui", "auipc"]):
                    if not 0 <= value <= 1048575:
                        raise ValueError(
                            f"Immediate value {value} out of range for U-type "
                            f"instruction (0 to 1048575)"
                        )
                    return ImmediateOperand(imd_type="U", value=value)

                # J-type instructions (21-bit signed immediate for jumps, must be even)
                elif any(x in mnemonic for x in ["jal"]):
                    if not -1048576 <= value <= 1048575 or value % 2 != 0:
                        raise ValueError(
                            f"Immediate value {value} out of range or not even "
                            f"for J-type instruction (-1048576 to 1048575, must be even)"
                        )
                    return ImmediateOperand(imd_type="J", value=value)

                # Vector instructions might have specific immediate ranges
                elif mnemonic.startswith("v"):
                    # Handle vector specific immediates (implementation specific)
                    return ImmediateOperand(imd_type="V", value=value)

            # Default case - no specific validation
            return ImmediateOperand(imd_type="int", value=value)

        return immediate

    def get_full_reg_name(self, register):
        """Return one register name string including all attributes"""
        if register.prefix and register.name:
            return register.prefix + str(register.name)
        return str(register.name)

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if isinstance(imd, IdentifierOperand):
            return imd
        elif imd.value is not None:
            if isinstance(imd.value, str):
                # hex or bin, return decimal
                return int(imd.value, 0)
            else:
                return imd.value
        # identifier
        return imd

    def parse_register(self, register_string):
        """
        Parse register string and return register dictionary.

        :param str register_string: register representation as string
        :returns: dict with register info
        """
        # Remove any leading/trailing whitespace
        register_string = register_string.strip()

        # Check for integer registers (x0-x31)
        x_match = re.match(r"^x([0-9]|[1-2][0-9]|3[0-1])$", register_string)
        if x_match:
            reg_num = int(x_match.group(1))
            return {
                "class": "register",
                "register": {"prefix": "x", "name": str(reg_num)},
            }

        # Check for floating-point registers (f0-f31)
        f_match = re.match(r"^f([0-9]|[1-2][0-9]|3[0-1])$", register_string)
        if f_match:
            reg_num = int(f_match.group(1))
            return {
                "class": "register",
                "register": {"prefix": "f", "name": str(reg_num)},
            }

        # Check for vector registers (v0-v31)
        v_match = re.match(r"^v([0-9]|[1-2][0-9]|3[0-1])$", register_string)
        if v_match:
            reg_num = int(v_match.group(1))
            return {
                "class": "register",
                "register": {"prefix": "v", "name": str(reg_num)},
            }

        # Check for ABI names
        abi_names = {
            "zero": 0,
            "ra": 1,
            "sp": 2,
            "gp": 3,
            "tp": 4,
            "t0": 5,
            "t1": 6,
            "t2": 7,
            "s0": 8,
            "fp": 8,
            "s1": 9,
            "a0": 10,
            "a1": 11,
            "a2": 12,
            "a3": 13,
            "a4": 14,
            "a5": 15,
            "a6": 16,
            "a7": 17,
            "s2": 18,
            "s3": 19,
            "s4": 20,
            "s5": 21,
            "s6": 22,
            "s7": 23,
            "s8": 24,
            "s9": 25,
            "s10": 26,
            "s11": 27,
            "t3": 28,
            "t4": 29,
            "t5": 30,
            "t6": 31,
        }

        if register_string in abi_names:
            return {
                "class": "register",
                "register": {"prefix": "", "name": register_string},
            }

        # If no match is found
        return None

    def is_gpr(self, register):
        """Check if register is a general purpose register"""
        # Integer registers: x0-x31 or ABI names
        if register.prefix == "x":
            return True
        if not register.prefix and register.name in ["zero", "ra", "sp", "gp", "tp"]:
            return True
        if not register.prefix and register.name[0] in ["t", "a", "s"]:
            return True
        return False

    def is_vector_register(self, register):
        """Check if register is a vector register"""
        # Vector registers: v0-v31
        if register.prefix == "v":
            return True
        return False

    def is_flag_dependend_of(self, flag_a, flag_b):
        """Check if ``flag_a`` is dependent on ``flag_b``"""
        # RISC-V doesn't have explicit flags like x86 or AArch64
        return flag_a.name == flag_b.name

    def is_reg_dependend_of(self, reg_a, reg_b):
        """Check if ``reg_a`` is dependent on ``reg_b``"""
        if not isinstance(reg_a, Operand):
            reg_a = RegisterOperand(name=reg_a["name"])

        # Get canonical register names
        reg_a_canonical = self._get_canonical_reg_name(reg_a)
        reg_b_canonical = self._get_canonical_reg_name(reg_b)

        # Same register type and number means dependency
        return reg_a_canonical == reg_b_canonical

    def _get_canonical_reg_name(self, register):
        """Get the canonical form of a register (x-form for integer, f-form for FP)"""
        # If already in canonical form (x# or f#)
        if register.prefix in ["x", "f", "v"] and register.name.isdigit():
            return f"{register.prefix}{register.name}"

        # ABI name mapping for integer registers
        abi_to_x = {
            "zero": "x0",
            "ra": "x1",
            "sp": "x2",
            "gp": "x3",
            "tp": "x4",
            "t0": "x5",
            "t1": "x6",
            "t2": "x7",
            "s0": "x8",
            "s1": "x9",
            "a0": "x10",
            "a1": "x11",
            "a2": "x12",
            "a3": "x13",
            "a4": "x14",
            "a5": "x15",
            "a6": "x16",
            "a7": "x17",
            "s2": "x18",
            "s3": "x19",
            "s4": "x20",
            "s5": "x21",
            "s6": "x22",
            "s7": "x23",
            "s8": "x24",
            "s9": "x25",
            "s10": "x26",
            "s11": "x27",
            "t3": "x28",
            "t4": "x29",
            "t5": "x30",
            "t6": "x31",
        }

        # For integer register ABI names
        name = register.name.lower()
        if name in abi_to_x:
            return abi_to_x[name]

        # For FP register ABI names like fa0, fs1, etc.
        if name.startswith("f") and len(name) > 1:
            if name[1] == "a":  # fa0-fa7
                idx = int(name[2:])
                return f"f{idx + 10}"
            elif name[1] == "s":  # fs0-fs11
                idx = int(name[2:])
                if idx <= 1:
                    return f"f{idx + 8}"
                else:
                    return f"f{idx + 16}"
            elif name[1] == "t":  # ft0-ft11
                idx = int(name[2:])
                if idx <= 7:
                    return f"f{idx}"
                else:
                    return f"f{idx + 20}"

        # Return as is if no mapping found
        return f"{register.prefix}{register.name}"

    def get_reg_type(self, register):
        """Get register type"""
        # Return register prefix if exists
        if register.prefix:
            return register.prefix

        # Determine type from ABI name
        name = register.name.lower()
        if name in ["zero", "ra", "sp", "gp", "tp"] or name[0] in ["t", "a", "s"]:
            return "x"  # Integer register
        elif name.startswith("f"):
            return "f"  # Floating point register
        elif name.startswith("csr"):
            return "csr"  # Control and Status Register

        return "unknown"

    def normalize_instruction_form(self, instruction_form, isa_model, arch_model):
        """
        Normalize instruction form for RISC-V instructions.

        :param instruction_form: instruction form to normalize
        :param isa_model: ISA model to use for normalization
        :param arch_model: architecture model to use for normalization
        """
        if instruction_form.normalized:
            return

        if instruction_form.mnemonic is None:
            instruction_form.normalized = True
            return

        # Normalize the mnemonic if needed
        if instruction_form.mnemonic:
            # Handle any RISC-V specific mnemonic normalization
            # For example, convert aliases or pseudo-instructions to their base form
            pass

        # Normalize the operands if needed
        for i, operand in enumerate(instruction_form.operands):
            if isinstance(operand, ImmediateOperand):
                # Normalize immediate operands
                instruction_form.operands[i] = self.normalize_imd(operand)
            elif isinstance(operand, RegisterOperand):
                # Convert register names to canonical form if needed
                pass

        instruction_form.normalized = True

    def get_regular_source_operands(self, instruction_form):
        """Get source operand of given instruction form assuming regular src/dst behavior."""
        # For RISC-V, the first operand is typically the destination,
        # and the rest are sources
        if len(instruction_form.operands) == 1:
            return [instruction_form.operands[0]]
        else:
            return [op for op in instruction_form.operands[1:]]

    def get_regular_destination_operands(self, instruction_form):
        """Get destination operand of given instruction form assuming regular src/dst behavior."""
        # For RISC-V, the first operand is typically the destination
        if len(instruction_form.operands) == 1:
            return []
        else:
            return instruction_form.operands[:1]

    def process_immediate_operand(self, operand):
        """Process immediate operands, converting them to ImmediateOperand objects"""
        if isinstance(operand, (int, str)):
            # For raw integer values or string immediates
            return ImmediateOperand(
                imd_type="int",
                value=str(operand) if isinstance(operand, int) else operand,
            )
        elif isinstance(operand, dict) and "imd" in operand:
            # For immediate operands from instruction definitions
            return ImmediateOperand(
                imd_type=operand["imd"],
                value=operand.get("value"),
                identifier=operand.get("identifier"),
                shift=operand.get("shift"),
            )
        else:
            # For any other immediate format
            return ImmediateOperand(imd_type="int", value=str(operand))
