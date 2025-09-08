#!/usr/bin/env python3

import pyparsing as pp
import unicodedata

from osaca.parser import ParserX86
from osaca.parser.directive import DirectiveOperand
from osaca.parser.identifier import IdentifierOperand
from osaca.parser.immediate import ImmediateOperand
from osaca.parser.instruction_form import InstructionForm
from osaca.parser.label import LabelOperand
from osaca.parser.memory import MemoryOperand
from osaca.parser.register import RegisterOperand

# We assume any non-ASCII characters except control characters and line terminators can be part of
# identifiers; this is based on the assumption that no assembler uses non-ASCII white space and
# syntax characters.
# This approach is described at the end of https://www.unicode.org/reports/tr55/#Whitespace-Syntax.
# It is appropriate for tools, such as this one, which process source code but do not fully validate
# it (in this case, that’s the job of the assembler).
NON_ASCII_PRINTABLE_CHARACTERS = "".join(
    chr(cp)
    for cp in range(0x80, 0x10FFFF + 1)
    if unicodedata.category(chr(cp)) not in ("Cc", "Zl", "Zp", "Cs", "Cn")
)


# References:
#   ASM386 Assembly Language Reference, document number 469165-003, https://mirror.math.princeton.edu/pub/oldlinux/Linux.old/Ref-docs/asm-ref.pdf.
#   Microsoft Macro Assembler BNF Grammar, https://learn.microsoft.com/en-us/cpp/assembler/masm/masm-bnf-grammar?view=msvc-170.
#   Intel Architecture Code Analyzer User's Guide, https://www.intel.com/content/dam/develop/external/us/en/documents/intel-architecture-code-analyzer-3-0-users-guide-157552.pdf.
class ParserX86Intel(ParserX86):
    _instance = None

    # Singleton pattern, as this is created very many times.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParserX86Intel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self._equ = {}

    # The IACA manual says: "For For Microsoft* Visual C++ compiler, 64-bit version, use
    # IACA_VC64_START and IACA_VC64_END, instead" (of IACA_START and IACA_END).
    # TODO: Inconveniently, the code generated with optimization disabled (/Od) has two
    # instructions.  We should support both patterns, but then who runs OSACA with /Od?
    def start_marker(self):
        return [
            InstructionForm(
                mnemonic="mov",
                operands=[
                    MemoryOperand(
                        base=RegisterOperand(name="GS"), offset=ImmediateOperand(value=111)
                    ),
                    ImmediateOperand(value=111),
                ],
            ),
        ]

    def end_marker(self):
        return [
            InstructionForm(
                mnemonic="mov",
                operands=[
                    MemoryOperand(
                        base=RegisterOperand(name="GS"), offset=ImmediateOperand(value=222)
                    ),
                    ImmediateOperand(value=222),
                ],
            ),
        ]

    def normalize_instruction_form(self, instruction_form, isa_model, arch_model):
        """
        If the model indicates that this instruction has a single destination that is the last
        operand, move the first operand to the last position.  This effectively converts the Intel
        syntax to the AT&T one.
        """
        if instruction_form.normalized:
            return
        instruction_form.normalized = True

        mnemonic = instruction_form.mnemonic
        if not mnemonic:
            return

        # The model may only contain the VEX-encoded instruction and we may have the non-VEX-encoded
        # one, or vice-versa.  Note that this doesn't work when the arguments differ between VEX-
        # encoded and non-VEX-encoded, e.g., for psubq.
        if not arch_model.get_instruction(mnemonic, len(instruction_form.operands)):
            if mnemonic[0] == "v":
                unvexed_mnemonic = mnemonic[1:]
                if arch_model.get_instruction(unvexed_mnemonic, len(instruction_form.operands)):
                    mnemonic = unvexed_mnemonic
            else:
                vexed_mnemonic = "v" + mnemonic
                if arch_model.get_instruction(vexed_mnemonic, len(instruction_form.operands)):
                    mnemonic = vexed_mnemonic
            instruction_form.mnemonic = mnemonic

        # We cannot pass the operands because they may not match before the reordering.  We just
        # pass the arity instead.  Also, this must use the ISA model, because that's where the
        # source/destination information is found.
        model = isa_model.get_instruction(mnemonic, len(instruction_form.operands))
        has_single_destination_at_end = False
        has_destination = False
        if model:
            for o in model.operands:
                if o.source:
                    if has_destination:
                        has_single_destination_at_end = False
                if o.destination:
                    if has_destination:
                        has_single_destination_at_end = False
                    else:
                        has_destination = True
                        has_single_destination_at_end = True
        else:
            # if there is only one operand, assume it is a source operand
            has_single_destination_at_end = len(instruction_form.operands) > 1

        if has_single_destination_at_end:
            # It is important to reverse the operands, we cannot just move the first one last.  This
            # makes a difference for instructions with 3 operands or more, such as roundsd: the
            # model files expect the rounding mode (an immediate) first but the Intel syntax has it
            # last.
            instruction_form.operands.reverse()

        # A hack to help with comparison instruction: if the instruction is in the model, and has
        # exactly two sources, swap its operands.
        if (
            model
            and not has_destination
            and len(instruction_form.operands) == 2
            and not isa_model.get_instruction(mnemonic, instruction_form.operands)
            and not arch_model.get_instruction(mnemonic, instruction_form.operands)
        ):
            instruction_form.operands.reverse()

        # If the instruction has a well-known data type, append a suffix.
        data_type_to_suffix = {"DWORD": "d", "QWORD": "q"}
        for o in instruction_form.operands:
            if isinstance(o, MemoryOperand) and o.data_type:
                suffix = data_type_to_suffix.get(o.data_type, None)
                if suffix:
                    suffixed_mnemonic = mnemonic + suffix
                    if isa_model.get_instruction(
                        suffixed_mnemonic, len(instruction_form.operands)
                    ) or arch_model.get_instruction(
                        suffixed_mnemonic, len(instruction_form.operands)
                    ):
                        instruction_form.mnemonic = suffixed_mnemonic
                        break

    def construct_parser(self):
        """Create parser for x86 Intel ISA."""
        # Numeric literal.
        binary_number = pp.Combine(pp.Word("01") + pp.CaselessLiteral("B"))
        octal_number = pp.Combine(pp.Word("01234567") + pp.CaselessLiteral("O"))
        decimal_number = pp.Combine(pp.Optional(pp.Literal("-")) + pp.Word(pp.nums))
        hex_number_suffix = pp.Combine(
            pp.Word(pp.hexnums) + (pp.CaselessLiteral("H") ^ pp.CaselessLiteral("R"))
        )
        hex_number_0x = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Literal("0x") + pp.Word(pp.hexnums)
        )
        hex_number = hex_number_0x ^ hex_number_suffix
        float_number = pp.Combine(
            pp.Optional(pp.Literal("-")) + pp.Word(pp.nums) + pp.Word(".", pp.nums)
        ).setResultsName("value")
        integer_number = (
            hex_number ^ binary_number ^ octal_number ^ decimal_number
        ).setResultsName("value")

        # Comment.
        self.comment = pp.Word(";#", exact=1) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables + NON_ASCII_PRINTABLE_CHARACTERS))
        ).setResultsName(self.comment_id)

        # Types.
        data_type = (
            pp.CaselessKeyword("BYTE")
            | pp.CaselessKeyword("DWORD")
            | pp.CaselessKeyword("FWORD")
            | pp.CaselessKeyword("MMWORD")
            | pp.CaselessKeyword("OWORD")
            | pp.CaselessKeyword("QWORD")
            | pp.CaselessKeyword("REAL10")
            | pp.CaselessKeyword("REAL4")
            | pp.CaselessKeyword("REAL8")
            | pp.CaselessKeyword("SBYTE")
            | pp.CaselessKeyword("SDWORD")
            | pp.CaselessKeyword("SQWORD")
            | pp.CaselessKeyword("SWORD")
            | pp.CaselessKeyword("TBYTE")
            | pp.CaselessKeyword("WORD")
            | pp.CaselessKeyword("XMMWORD")
            | pp.CaselessKeyword("YMMWORD")
            | pp.CaselessKeyword("ZMMWORD")
        ).setResultsName("data_type")

        # Identifier.  Note that $ is not mentioned in the ASM386 Assembly Language Reference,
        # but it is mentioned in the MASM syntax.  < and > apparently show up in C++ mangled names.
        # ICC allows ".", at least in labels.
        first = pp.Word(pp.alphas + NON_ASCII_PRINTABLE_CHARACTERS + ".$?@_<>", exact=1)
        rest = pp.Word(pp.alphanums + NON_ASCII_PRINTABLE_CHARACTERS + ".$?@_<>")
        identifier = pp.Group(
            pp.Combine(first + pp.Optional(rest)).setResultsName("name")
        ).setResultsName("identifier")

        # Register.
        # This follows the MASM grammar.
        special_register = (
            pp.CaselessKeyword("CR0")
            | pp.CaselessKeyword("CR2")
            | pp.CaselessKeyword("CR3")
            | pp.CaselessKeyword("DR0")
            | pp.CaselessKeyword("DR1")
            | pp.CaselessKeyword("DR2")
            | pp.CaselessKeyword("DR3")
            | pp.CaselessKeyword("DR6")
            | pp.CaselessKeyword("DR7")
            | pp.CaselessKeyword("TR3")
            | pp.CaselessKeyword("TR4")
            | pp.CaselessKeyword("TR5")
            | pp.CaselessKeyword("TR6")
            | pp.CaselessKeyword("TR7")
        ).setResultsName("name")
        gp_register = (
            pp.CaselessKeyword("AX")
            | pp.CaselessKeyword("EAX")
            | pp.CaselessKeyword("CX")
            | pp.CaselessKeyword("ECX")
            | pp.CaselessKeyword("DX")
            | pp.CaselessKeyword("EDX")
            | pp.CaselessKeyword("BX")
            | pp.CaselessKeyword("EBX")
            | pp.CaselessKeyword("DI")
            | pp.CaselessKeyword("EDI")
            | pp.CaselessKeyword("SI")
            | pp.CaselessKeyword("ESI")
            | pp.CaselessKeyword("BP")
            | pp.CaselessKeyword("EBP")
            | pp.CaselessKeyword("SP")
            | pp.CaselessKeyword("ESP")
            | pp.CaselessKeyword("R8W")
            | pp.CaselessKeyword("R8D")
            | pp.CaselessKeyword("R9W")
            | pp.CaselessKeyword("R9D")
            | pp.CaselessKeyword("R12D")
            | pp.CaselessKeyword("R13W")
            | pp.CaselessKeyword("R13D")
            | pp.CaselessKeyword("R14W")
            | pp.CaselessKeyword("R14D")
        ).setResultsName("name")
        byte_register = (
            pp.CaselessKeyword("AL")
            | pp.CaselessKeyword("AH")
            | pp.CaselessKeyword("CL")
            | pp.CaselessKeyword("CH")
            | pp.CaselessKeyword("DL")
            | pp.CaselessKeyword("DH")
            | pp.CaselessKeyword("BL")
            | pp.CaselessKeyword("BH")
            | pp.CaselessKeyword("R8B")
            | pp.CaselessKeyword("R9B")
            | pp.CaselessKeyword("R10B")
            | pp.CaselessKeyword("R11B")
            | pp.CaselessKeyword("R12B")
            | pp.CaselessKeyword("R13B")
        ).setResultsName("name")
        qword_register = (
            pp.CaselessKeyword("RAX")
            | pp.CaselessKeyword("RCX")
            | pp.CaselessKeyword("RDX")
            | pp.CaselessKeyword("RBX")
            | pp.CaselessKeyword("RSP")
            | pp.CaselessKeyword("RBP")
            | pp.CaselessKeyword("RSI")
            | pp.CaselessKeyword("RDI")
            | pp.CaselessKeyword("R8")
            | pp.CaselessKeyword("R9")
            | pp.CaselessKeyword("R10")
            | pp.CaselessKeyword("R11")
            | pp.CaselessKeyword("R12")
            | pp.CaselessKeyword("R13")
            | pp.CaselessKeyword("R14")
            | pp.CaselessKeyword("R15")
        ).setResultsName("name")
        fpu_register = pp.Combine(
            pp.CaselessKeyword("ST")
            + pp.Optional(pp.Literal("(") + pp.Word("01234567") + pp.Literal(")"))
        ).setResultsName("name")
        simd_register = (
            pp.Combine(pp.CaselessLiteral("MM") + pp.Word(pp.nums))
            | pp.Combine(pp.CaselessLiteral("XMM") + pp.Word(pp.nums))
            | pp.Combine(pp.CaselessLiteral("YMM") + pp.Word(pp.nums))
            | pp.Combine(pp.CaselessLiteral("ZMM") + pp.Word(pp.nums))
        ).setResultsName("name") + pp.Optional(
            pp.Literal("{") + pp.Word(pp.alphanums).setResultsName("mask") + pp.Literal("}")
        )
        segment_register = (
            pp.CaselessKeyword("CS")
            | pp.CaselessKeyword("DS")
            | pp.CaselessKeyword("ES")
            | pp.CaselessKeyword("FS")
            | pp.CaselessKeyword("GS")
            | pp.CaselessKeyword("SS")
        ).setResultsName("name")
        self.register = pp.Group(
            special_register
            | gp_register
            | byte_register
            | qword_register
            | fpu_register
            | simd_register
            | segment_register
            | pp.CaselessKeyword("RIP")
        ).setResultsName(self.register_id)

        # Register expressions.
        base_register = self.register
        index_register = self.register
        scale = pp.Word("1248", exact=1)

        base = base_register.setResultsName("base")
        displacement = pp.Group(
            pp.Group(integer_number ^ identifier).setResultsName(self.immediate_id)
        ).setResultsName("displacement")
        short_indexed = index_register.setResultsName("index")
        long_indexed = (
            index_register.setResultsName("index")
            + pp.Literal("*")
            + scale.setResultsName("scale")
        )
        indexed = pp.Group(short_indexed ^ long_indexed).setResultsName("indexed")
        operator = pp.Word("+-", exact=1)
        operator_index = pp.Word("+-", exact=1).setResultsName("operator_idx")
        operator_displacement = pp.Word("+-", exact=1).setResultsName("operator_disp")

        # Syntax:
        #   `base` always preceedes `indexed`.
        #   `short_indexed` is only allowed if it follows `base`, not alone.
        #   `displacement` can go anywhere.
        # It's easier to list all the alternatives than to represent these rules using complicated
        # `Optional` and what not.
        register_expression = pp.Group(
            pp.Literal("[")
            + (
                base
                ^ (base + operator_displacement + displacement)
                ^ (base + operator_displacement + displacement + operator_index + indexed)
                ^ (base + operator_index + indexed)
                ^ (base + operator_index + indexed + operator_displacement + displacement)
                ^ (displacement + operator + base)
                ^ (displacement + operator + base + operator_index + indexed)
                ^ (
                    displacement
                    + operator_index
                    + pp.Group(long_indexed).setResultsName("indexed")
                )
                ^ pp.Group(long_indexed).setResultsName("indexed")
                ^ (
                    pp.Group(long_indexed).setResultsName("indexed")
                    + operator_displacement
                    + displacement
                )
            )
            + pp.Literal("]")
        ).setResultsName("register_expression")

        # Immediate.
        immediate = pp.Group(integer_number | float_number | identifier).setResultsName(
            self.immediate_id
        )

        # Expressions.
        # The ASM86 manual has weird expressions on page 130 (displacement outside of the register
        # expression, multiple register expressions).  Let's ignore those for now, but see
        # https://stackoverflow.com/questions/71540754/why-sometimes-use-offset-flatlabel-and-sometimes-not.
        address_expression = pp.Group(
            self.register.setResultsName("segment") + pp.Literal(":") + immediate
            ^ immediate + register_expression
            ^ register_expression
            ^ identifier + pp.Optional(operator + immediate)
        ).setResultsName("address_expression")

        offset_expression = pp.Group(
            pp.CaselessKeyword("OFFSET")
            + pp.Group(
                pp.CaselessKeyword("GROUP")
                | pp.CaselessKeyword("SEGMENT")
                | pp.CaselessKeyword("FLAT")
            )
            # The MASM grammar has the ":" immediately after "OFFSET", but that's not what MSVC
            # outputs.
            + pp.Literal(":")
            + identifier.setResultsName("identifier")
            + pp.Optional(pp.Literal("+") + immediate.setResultsName("displacement"))
        ).setResultsName("offset_expression")
        ptr_expression = pp.Group(
            data_type
            + (pp.CaselessKeyword("PTR") | pp.CaselessKeyword("BCST"))
            + address_expression
        ).setResultsName("ptr_expression")
        short_expression = pp.Group(pp.CaselessKeyword("SHORT") + identifier).setResultsName(
            "short_expression"
        )

        # Instructions.
        mnemonic = pp.Word(pp.alphas, pp.alphanums).setResultsName("mnemonic")
        operand = pp.Group(
            self.register
            | pp.Group(
                offset_expression | ptr_expression | short_expression | address_expression
            ).setResultsName(self.memory_id)
            | immediate
        )
        self.instruction_parser = (
            mnemonic
            + pp.Optional(operand.setResultsName("operand1"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand.setResultsName("operand2"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand.setResultsName("operand3"))
            + pp.Optional(pp.Suppress(pp.Literal(",")))
            + pp.Optional(operand.setResultsName("operand4"))
            + pp.Optional(self.comment)
        )

        # Label.
        self.label = pp.Group(
            identifier.setResultsName("name")
            + pp.Literal(":")
            + pp.Optional(self.instruction_parser)
            + pp.Optional(self.comment)
        ).setResultsName(self.label_id)

        # Directives.
        # The identifiers at the beginnig of a directive cannot start with a "." otherwise we end up
        # with ambiguities.
        directive_first = pp.Word(pp.alphas + NON_ASCII_PRINTABLE_CHARACTERS + "$?@_<>", exact=1)
        directive_rest = pp.Word(pp.alphanums + NON_ASCII_PRINTABLE_CHARACTERS + ".$?@_<>")
        directive_identifier = pp.Group(
            pp.Combine(directive_first + pp.Optional(directive_rest)).setResultsName("name")
        ).setResultsName("identifier")

        # Parameter can be any quoted string or sequence of characters besides ';' (for comments)
        # or ',' (parameter delimiter).  See ASM386 p. 38.
        directive_parameter = (
            pp.quotedString
            ^ (
                pp.Word(pp.printables + NON_ASCII_PRINTABLE_CHARACTERS, excludeChars=",;")
                + pp.Optional(pp.Suppress(pp.Literal(",")))
            )
            ^ pp.Suppress(pp.Literal(","))
        )
        # The directives that don't start with a "." are ambiguous with instructions, so we list
        # them explicitly.
        # TODO: The directives that are types introduce a nasty ambiguity with instructions.  Skip
        # them for now, apparently the MSVC output uses the short D? directives.
        directive_keywords = (
            pp.CaselessKeyword("ALIAS")
            | pp.CaselessKeyword("ALIGN")
            | pp.CaselessKeyword("ASSUME")
            # | pp.CaselessKeyword("BYTE")
            | pp.CaselessKeyword("CATSTR")
            | pp.CaselessKeyword("COMM")
            | pp.CaselessKeyword("COMMENT")
            | pp.CaselessKeyword("DB")
            | pp.CaselessKeyword("DD")
            | pp.CaselessKeyword("DF")
            | pp.CaselessKeyword("DQ")
            | pp.CaselessKeyword("DT")
            | pp.CaselessKeyword("DW")
            # | pp.CaselessKeyword("DWORD")
            | pp.CaselessKeyword("ECHO")
            | pp.CaselessKeyword("END")
            | pp.CaselessKeyword("ENDP")
            | pp.CaselessKeyword("ENDS")
            | pp.CaselessKeyword("EQU")
            | pp.CaselessKeyword("EVEN")
            | pp.CaselessKeyword("EXTRN")
            | pp.CaselessKeyword("EXTERNDEF")
            # | pp.CaselessKeyword("FWORD")
            | pp.CaselessKeyword("GROUP")
            | pp.CaselessKeyword("INCLUDE")
            | pp.CaselessKeyword("INCLUDELIB")
            | pp.CaselessKeyword("INSTR")
            | pp.CaselessKeyword("INVOKE")
            | pp.CaselessKeyword("LABEL")
            # | pp.CaselessKeyword("MMWORD")
            | pp.CaselessKeyword("OPTION")
            | pp.CaselessKeyword("ORG")
            | pp.CaselessKeyword("PAGE")
            | pp.CaselessKeyword("POPCONTEXT")
            | pp.CaselessKeyword("PROC")
            | pp.CaselessKeyword("PROTO")
            | pp.CaselessKeyword("PUBLIC")
            | pp.CaselessKeyword("PUSHCONTEXT")
            # | pp.CaselessKeyword("QWORD")
            # | pp.CaselessKeyword("REAL10")
            # | pp.CaselessKeyword("REAL4")
            # | pp.CaselessKeyword("REAL8")
            | pp.CaselessKeyword("RECORD")
            # | pp.CaselessKeyword("SBYTE")
            # | pp.CaselessKeyword("SDWORD")
            | pp.CaselessKeyword("SEGMENT")
            | pp.CaselessKeyword("SIZESTR")
            | pp.CaselessKeyword("STRUCT")
            | pp.CaselessKeyword("SUBSTR")
            | pp.CaselessKeyword("SUBTITLE")
            # | pp.CaselessKeyword("SWORD")
            # | pp.CaselessKeyword("TBYTE")
            | pp.CaselessKeyword("TEXTEQU")
            | pp.CaselessKeyword("TITLE")
            | pp.CaselessKeyword("TYPEDEF")
            | pp.CaselessKeyword("UNION")
            # | pp.CaselessKeyword("WORD")
            # | pp.CaselessKeyword("XMMWORD")
            # | pp.CaselessKeyword("YMMWORD")
        )
        self.directive = pp.Group(
            pp.Optional(~directive_keywords + directive_identifier)
            + (
                pp.Combine(pp.Literal(".") + pp.Word(pp.alphanums + "_"))
                | pp.Literal("=")
                | directive_keywords
            ).setResultsName("name")
            + pp.ZeroOrMore(directive_parameter).setResultsName("parameters")
            + pp.Optional(self.comment)
        ).setResultsName(self.directive_id)

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

        # 1. Parse comment.
        try:
            result = self.process_operand(self.comment.parseString(line, parseAll=True))
            instruction_form.comment = " ".join(result[self.comment_id])
        except pp.ParseException:
            pass

        # 2. Parse label.
        if not result:
            try:
                # Returns tuple with label operand and comment, if any.
                result = self.process_operand(self.label.parseString(line, parseAll=True))
                instruction_form.label = result[0].name
                if result[1]:
                    instruction_form.comment = " ".join(result[1])
            except pp.ParseException:
                pass

        # 3. Parse directive.
        if not result:
            try:
                # Returns tuple with directive operand and comment, if any.
                result = self.process_operand(self.directive.parseString(line, parseAll=True))
                instruction_form.directive = result[0]
                if result[1]:
                    instruction_form.comment = " ".join(result[1])
            except pp.ParseException:
                pass

        # 4. Parse instruction.
        if not result:
            try:
                result = self.parse_instruction(line)
            except pp.ParseException as e:
                raise ValueError(
                    "Could not parse instruction on line {}: {!r}".format(line_number, line)
                ) from e
            instruction_form.mnemonic = result.mnemonic
            instruction_form.operands = result.operands
            instruction_form.comment = result.comment
        return instruction_form

    def make_instruction(self, parse_result):
        """
        Parse instruction in asm line.

        :param parse_result: tuple resulting from calling `parseString` on the `instruction_parser`.
        :returns: `dict` -- parsed instruction form
        """
        operands = []
        # Add operands to list
        # Check first operand
        if "operand1" in parse_result:
            operands.append(self.process_operand(parse_result.operand1))
        # Check second operand
        if "operand2" in parse_result:
            operands.append(self.process_operand(parse_result.operand2))
        # Check third operand
        if "operand3" in parse_result:
            operands.append(self.process_operand(parse_result.operand3))
        # Check fourth operand
        if "operand4" in parse_result:
            operands.append(self.process_operand(parse_result.operand4))
        return_dict = InstructionForm(
            mnemonic=parse_result.mnemonic,
            operands=operands,
            label_id=None,
            comment_id=(
                " ".join(parse_result[self.comment_id])
                if self.comment_id in parse_result
                else None
            ),
        )

        return return_dict

    def parse_instruction(self, instruction):
        """
        Parse instruction in asm line.

        :param str instruction: Assembly line string.
        :returns: `dict` -- parsed instruction form
        """
        return self.make_instruction(
            self.instruction_parser.parseString(instruction, parseAll=True)
        )

    def parse_register(self, register_string):
        """Parse register string"""
        try:
            return self.process_operand(self.register.parseString(register_string, parseAll=True))
        except pp.ParseException:
            return None

    def process_operand(self, operand):
        """Post-process operand"""
        if self.directive_id in operand:
            return self.process_directive(operand[self.directive_id])
        if self.identifier in operand:
            return self.process_identifier(operand[self.identifier])
        if self.immediate_id in operand:
            return self.process_immediate(operand[self.immediate_id])
        if self.label_id in operand:
            return self.process_label(operand[self.label_id])
        if self.memory_id in operand:
            return self.process_memory_address(operand[self.memory_id])
        if self.register_id in operand:
            return self.process_register(operand[self.register_id])
        return operand

    def process_directive(self, directive):
        # TODO: This is putting the identifier in the parameters.  No idea if it's right.
        parameters = [directive.identifier.name] if "identifier" in directive else []
        parameters.extend(directive.parameters)
        directive_new = DirectiveOperand(name=directive.name, parameters=parameters or None)
        # Interpret the "=" directives because the generated assembly is full of symbols that are
        # defined there.
        if directive.name == "=":
            self._equ[parameters[0]] = parameters[1]
        return directive_new, directive.get("comment")

    def process_register(self, operand):
        return RegisterOperand(
            name=operand.name,
            mask=RegisterOperand(name=operand.mask) if "mask" in operand else None,
        )

    def process_register_expression(self, register_expression):
        base = register_expression.get("base")
        displacement = register_expression.get("displacement")
        indexed = register_expression.get("indexed")
        index = None
        scale = 1
        if indexed:
            index = indexed.get("index")
            scale = int(indexed.get("scale", "1"), 0)
            if register_expression.get("operator_index") == "-":
                scale *= -1
        displacement_op = self.process_immediate(displacement.immediate) if displacement else None
        if displacement_op and register_expression.get("operator_disp") == "-":
            displacement_op.value *= -1
        base_op = RegisterOperand(name=base.name) if base else None
        index_op = RegisterOperand(name=index.name) if index else None
        new_memory = MemoryOperand(
            offset=displacement_op, base=base_op, index=index_op, scale=scale
        )
        return new_memory

    def process_address_expression(self, address_expression, data_type=None):
        # TODO: It seems that we could have a prefix immediate operand, a displacement in the
        # brackets, and an offset.  How all of this works together is somewhat mysterious.
        immediate_operand = (
            self.process_immediate(address_expression.immediate)
            if "immediate" in address_expression
            else None
        )
        register_expression = (
            self.process_register_expression(address_expression.register_expression)
            if "register_expression" in address_expression
            else None
        )
        segment = (
            self.process_register(address_expression.segment)
            if "segment" in address_expression
            else None
        )
        identifier = (
            self.process_identifier(address_expression.identifier)
            if "identifier" in address_expression
            else None
        )
        if register_expression:
            if immediate_operand:
                register_expression.offset = immediate_operand
            if data_type:
                register_expression.data_type = data_type
            return register_expression
        elif segment:
            return MemoryOperand(base=segment, offset=immediate_operand, data_type=data_type)
        elif identifier:
            if immediate_operand:
                identifier.offset = immediate_operand
            elif not data_type:
                # An address expression without a data type or an offset is just an identifier.
                # This matters for jumps.
                return identifier
            return MemoryOperand(offset=identifier, data_type=data_type)
        else:
            return MemoryOperand(base=immediate_operand, data_type=data_type)

    def process_offset_expression(self, offset_expression):
        # TODO: Record that this is an offset expression.
        displacement = (
            self.process_immediate(offset_expression.displacement)
            if "displacement" in offset_expression
            else None
        )
        if displacement and "operator_disp" == "-":
            displacement.value *= -1
        identifier = self.process_identifier(offset_expression.identifier)
        identifier.offset = displacement
        return MemoryOperand(offset=identifier)

    def process_ptr_expression(self, ptr_expression):
        # TODO: Do something with the data_type.
        return self.process_address_expression(
            ptr_expression.address_expression, ptr_expression.data_type
        )

    def process_short_expression(self, short_expression):
        # TODO: Do something with the fact that it is short.
        return LabelOperand(name=short_expression.identifier.name)

    def process_memory_address(self, memory_address):
        """Post-process memory address operand"""
        if "address_expression" in memory_address:
            return self.process_address_expression(memory_address.address_expression)
        elif "offset_expression" in memory_address:
            return self.process_offset_expression(memory_address.offset_expression)
        elif "ptr_expression" in memory_address:
            return self.process_ptr_expression(memory_address.ptr_expression)
        elif "short_expression" in memory_address:
            return self.process_short_expression(memory_address.short_expression)
        return memory_address

    def process_label(self, label):
        """Post-process label asm line"""
        # Remove duplicated 'name' level due to identifier.  Note that there is no place to put the
        # comment, if any.
        label["name"] = label["name"]["name"]
        return (
            LabelOperand(name=label.name),
            self.make_instruction(label) if "mnemonic" in label else None,
        )

    def process_immediate(self, immediate):
        """Post-process immediate operand"""
        if "identifier" in immediate:
            # Actually an identifier, change declaration.
            return self.process_identifier(immediate.identifier)
        new_immediate = ImmediateOperand(value=immediate.get("sign", "") + immediate.value)
        new_immediate.value = self.normalize_imd(new_immediate)
        return new_immediate

    def process_identifier(self, identifier):
        if identifier.name in self._equ:
            # Actually an immediate, change declaration.
            new_immediate = ImmediateOperand(
                identifier=identifier.name, value=self._equ[identifier.name]
            )
            new_immediate.value = self.normalize_imd(new_immediate)
            return new_immediate
        return IdentifierOperand(name=identifier.name)

    def normalize_imd(self, imd):
        """Normalize immediate to decimal based representation"""
        if isinstance(imd.value, str):
            if "." in imd.value:
                return float(imd.value)
            if imd.value.startswith("0x"):
                return int(imd.value, 0)
            # Now parse depending on the base.
            base = {"B": 2, "O": 8, "H": 16, "R": 16}.get(imd.value[-1], 10)
            value = 0
            negative = imd.value[0] == "-"
            positive = imd.value[0] == "+"
            start = +(negative or positive)
            stop = len(imd.value) if base == 10 else -1
            for c in imd.value[start:stop]:
                value = value * base + int(c, base)
            return -value if negative else value
        else:
            return imd.value
