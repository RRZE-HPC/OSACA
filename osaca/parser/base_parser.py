#!usr/bin/env python3


class BaseParser(object):
    # Identifiers for operand types
    COMMENT_ID = 'comment'
    DIRECTIVE_ID = 'directive'
    IMMEDIATE_ID = 'immediate'
    LABEL_ID = 'label'
    MEMORY_ID = 'memory'
    REGISTER_ID = 'register'

    def __init__(self):
        self.construct_parser()

    def parse_file(self, file_content):
        '''
        Parse assembly file. This includes extracting of the marked kernel and
        the parsing of the instruction forms.

        :param str file_content: assembly code
        :return: list of instruction forms
        :raises ValueError: if the marker_type attribute is unknown by the
        function
        '''
        # Create instruction form list
        asm_instructions = []
        lines = file_content.split('\n')
        for i, line in enumerate(lines):
            if line == '':
                continue
            asm_instructions.append(self.parseLine(line, i + 1))
        return asm_instructions

    def parse_line(self, line, line_number):
        # Done in derived classes
        raise NotImplementedError()

    def parse_instruction(self, instruction):
        # Done in derived classes
        raise NotImplementedError()

    def parse_register(self, register):
        # Done in derived classed
        raise NotImplementedError()

    def parse_memory(self, memory_address):
        # Done in derived classed
        raise NotImplementedError()

    def parse_immediate(self, immediate):
        # Done in derived classed
        raise NotImplementedError()

    def construct_parser(self):
        raise NotImplementedError()
