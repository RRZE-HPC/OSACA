#!/usr/bin/env python3
"""Parser superclass of specific parsers."""
import operator
import re


class BaseParser(object):
    # Identifiers for operand types
    comment_id = "comment"
    directive_id = "directive"
    immediate_id = "immediate"
    label_id = "label"
    identifier = "identifier"
    memory_id = "memory"
    register_id = "register"
    condition_id = "condition"
    segment_ext = "segment_extension"
    mnemonic = "instruction"
    operands = "operands"
    prefetch = "prfop"
    _parser_constructed = False

    def __init__(self):
        if not self._parser_constructed:
            self.construct_parser()
            self._parser_constructed = True

    def isa(self):
        # Done in derived classes
        raise NotImplementedError

    # The marker functions return lists of `InstructionForm` that are used to find the IACA markers
    # in the parsed code.  In addition to just a list, the marker may have a structure like
    # [I1, [I2, I3], I4, ...] where the nested list indicates that at least one of I2 and I3 must
    # match the second instruction in the fragment of parsed code.
    # If an instruction form is a `DirectiveOperand`, the match may happen over several directive
    # operands in the parsed code, provided that the directives have the same name and the
    # parameters are in sequence with respect to the pattern.  This provides an easy way to describe
    # a sequence of bytes irrespective of the way it was grouped in the assembly source.
    # Note that markers must be matched *before* normalization.
    def start_marker(self):
        # Done in derived classes
        raise NotImplementedError

    def end_marker(self):
        # Done in derived classes
        raise NotImplementedError

    # Performs all the normalization needed to match the instruction to the ISO/arch model.  This
    # method must set the `normalized` property of the instruction and must be idempotent.
    def normalize_instruction_form(self, instruction_form, isa_model, arch_model):
        raise NotImplementedError

    @staticmethod
    def detect_ISA(file_content):
        """
        Detect the ISA of the assembly based on the used registers and return the ISA code.

        :param str file_content: assembly code.
        :return: a tuple isa, syntax describing the architecture and the assembly syntax,
                 if appropriate.  If there is no notion of syntax, the second element is None.
        """
        # Check for the amount of registers in the code to determine the ISA
        # 1) Check for xmm, ymm, zmm, rax, rbx, rcx, and rdx registers in x86
        #    AT&T syntax.  There is a % before each register name.
        heuristics_x86ATT = [r"%[xyz]mm[0-9]", r"%[er][abcd]x[0-9]"]
        # 2) Same as above, but for the Intel syntax.  There is no % before the register names.
        heuristics_x86Intel = [r"[^%][xyz]mm[0-9]", r"[^%][er][abcd]x[0-9]"]
        # 3) check for v and z vector registers and x/w general-purpose registers
        heuristics_aarch64 = [r"[vz][0-9][0-9]?\.[0-9][0-9]?[bhsd]", r"[wx][0-9]"]
        matches = {("x86", "ATT"): 0, ("x86", "INTEL"): 0, ("aarch64", None): 0}

        for h in heuristics_x86ATT:
            matches[("x86", "ATT")] += len(re.findall(h, file_content))
        for h in heuristics_x86Intel:
            matches[("x86", "INTEL")] += len(re.findall(h, file_content))
        for h in heuristics_aarch64:
            matches[("aarch64", None)] += len(re.findall(h, file_content))

        return max(matches.items(), key=operator.itemgetter(1))[0]

    def parse_file(self, file_content, start_line=0):
        """
        Parse assembly file. This includes *not* extracting of the marked kernel and
        the parsing of the instruction forms.

        :param str file_content: assembly code
        :param int start_line: offset, if first line in file_content is meant to be not 1
        :return: list of instruction forms
        """
        # Create instruction form list
        asm_instructions = []
        lines = file_content.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "":
                continue
            asm_instructions.append(self.parse_line(line, i + 1 + start_line))
        return asm_instructions

    def parse_line(self, line, line_number=None):
        # Done in derived classes
        raise NotImplementedError

    def parse_instruction(self, instruction):
        # Done in derived classes
        raise NotImplementedError

    def parse_register(self, register_string):
        raise NotImplementedError

    def is_gpr(self, register):
        raise NotImplementedError

    def is_vector_register(self, register):
        raise NotImplementedError

    def get_reg_type(self, register):
        raise NotImplementedError

    def construct_parser(self):
        return
        # raise NotImplementedError

    ##################
    # Helper functions
    ##################

    def process_operand(self, operand):
        raise NotImplementedError

    def get_full_reg_name(self, register):
        raise NotImplementedError

    # Must be called on a *normalized* instruction.
    def get_regular_source_operands(self, instruction_form):
        raise NotImplementedError

    # Must be called on a *normalized* instruction.
    def get_regular_destination_operands(self, instruction_form):
        raise NotImplementedError

    def normalize_imd(self, imd):
        raise NotImplementedError

    def is_reg_dependend_of(self, reg_a, reg_b):
        raise NotImplementedError
