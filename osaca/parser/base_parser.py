#!/usr/bin/env python3
"""Parser superclass of specific parsers."""


class BaseParser(object):
    # Identifiers for operand types
    COMMENT_ID = 'comment'
    DIRECTIVE_ID = 'directive'
    IMMEDIATE_ID = 'immediate'
    LABEL_ID = 'label'
    MEMORY_ID = 'memory'
    REGISTER_ID = 'register'
    SEGMENT_EXT_ID = 'segment_extension'
    INSTRUCTION_ID = 'instruction'
    OPERANDS_ID = 'operands'

    def __init__(self):
        self.construct_parser()

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
        lines = file_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == '':
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

    def normalize_imd(self, imd):
        raise NotImplementedError

    def is_reg_dependend_of(self, reg_a, reg_b):
        raise NotImplementedError
