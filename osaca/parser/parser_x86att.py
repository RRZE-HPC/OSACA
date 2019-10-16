#!/usr/bin/env python3

import pyparsing as pp

from osaca.parser import AttrDict, BaseParser


class ParserX86ATT(BaseParser):
    def __init__(self):
        super().__init__()

    def construct_parser(self):
        decimal_number = pp.Combine(
            pp.Optional(pp.Literal('-')) + pp.Word(pp.nums)
        ).setResultsName('value')
        hex_number = pp.Combine(pp.Literal('0x') + pp.Word(pp.hexnums)).setResultsName('value')
        # Comment
        symbol_comment = '#'
        self.comment = pp.Literal(symbol_comment) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables))
        ).setResultsName(self.COMMENT_ID)
        # Define x86 assembly identifier
        id_offset = pp.Word(pp.nums) + pp.Suppress(pp.Literal('+'))
        first = pp.Word(pp.alphas + '_.', exact=1)
        rest = pp.Word(pp.alphanums + '$_.')
        identifier = pp.Group(
            pp.Optional(id_offset).setResultsName('offset')
            + pp.Combine(first + pp.Optional(rest)).setResultsName('name')
        ).setResultsName('identifier')
        # Label
        self.label = pp.Group(
            identifier.setResultsName('name') + pp.Literal(':') + pp.Optional(self.comment)
        ).setResultsName(self.LABEL_ID)
        # Register: pp.Regex('^%[0-9a-zA-Z]+,?')
        self.register = pp.Group(
            pp.Literal('%')
            + pp.Word(pp.alphanums).setResultsName('name')
            + pp.Optional(
                pp.Literal('{')
                + pp.Literal('%')
                + pp.Word(pp.alphanums).setResultsName('mask')
                + pp.Literal('}')
            )
        ).setResultsName(self.REGISTER_ID)
        # Immediate: pp.Regex('^\$(-?[0-9]+)|(0x[0-9a-fA-F]+),?')
        symbol_immediate = '$'
        immediate = pp.Group(
            pp.Literal(symbol_immediate) + (hex_number | decimal_number | identifier)
        ).setResultsName(self.IMMEDIATE_ID)
        # Memory: offset(base, index, scale)
        offset = pp.Group(identifier | hex_number | decimal_number).setResultsName(
            self.IMMEDIATE_ID
        )
        scale = pp.Word('1248', exact=1)
        memory = pp.Group(
            pp.Optional(offset.setResultsName('offset'))
            + pp.Literal('(')
            + pp.Optional(self.register.setResultsName('base'))
            + pp.Optional(pp.Suppress(pp.Literal(',')))
            + pp.Optional(self.register.setResultsName('index'))
            + pp.Optional(pp.Suppress(pp.Literal(',')))
            + pp.Optional(scale.setResultsName('scale'))
            + pp.Literal(')')
        ).setResultsName(self.MEMORY_ID)

        # Directive
        directive_option = pp.Combine(
            pp.Word('#@.', exact=1) + pp.Word(pp.printables, excludeChars=',')
        )
        directive_parameter = (pp.quotedString | directive_option | identifier | hex_number |
                               decimal_number | self.register
        )
        commaSeparatedList = pp.delimitedList(pp.Optional(directive_parameter), delim=',')
        self.directive = pp.Group(
            pp.Literal('.')
            + pp.Word(pp.alphanums + '_').setResultsName('name')
            + commaSeparatedList.setResultsName('parameters')
            + pp.Optional(self.comment)
        ).setResultsName(self.DIRECTIVE_ID)

        # Instructions
        # Mnemonic
        mnemonic = pp.ZeroOrMore(pp.Literal('data16') | pp.Literal('data32')) + pp.Word(
            pp.alphanums
        ).setResultsName('mnemonic')
        # Combine to instruction form
        operand_first = pp.Group(self.register ^ immediate ^ memory ^ identifier)
        operand_rest = pp.Group(self.register ^ immediate ^ memory)
        self.instruction_parser = (
            mnemonic
            + pp.Optional(operand_first.setResultsName('operand1'))
            + pp.Optional(pp.Suppress(pp.Literal(',')))
            + pp.Optional(operand_rest.setResultsName('operand2'))
            + pp.Optional(pp.Suppress(pp.Literal(',')))
            + pp.Optional(operand_rest.setResultsName('operand3'))
            + pp.Optional(pp.Suppress(pp.Literal(',')))
            + pp.Optional(operand_rest.setResultsName('operand4'))
            + pp.Optional(self.comment)
        )

    def parse_register(self, register_string):
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
        :param int line_id: default None, identifier of instruction form
        :return: parsed instruction form
        """
        instruction_form = AttrDict(
            {
                self.INSTRUCTION_ID: None,
                self.OPERANDS_ID: None,
                self.DIRECTIVE_ID: None,
                self.COMMENT_ID: None,
                self.LABEL_ID: None,
                'line': line.strip(),
                'line_number': line_number,
            }
        )
        result = None

        # 1. Parse comment
        try:
            result = self.process_operand(self.comment.parseString(line, parseAll=True).asDict())
            result = AttrDict.convert_dict(result)
            instruction_form[self.COMMENT_ID] = ' '.join(result[self.COMMENT_ID])
        except pp.ParseException:
            pass

        # 2. Parse label
        if result is None:
            try:
                result = self.process_operand(self.label.parseString(line, parseAll=True).asDict())
                result = AttrDict.convert_dict(result)
                instruction_form[self.LABEL_ID] = result[self.LABEL_ID]['name']
                if self.COMMENT_ID in result[self.LABEL_ID]:
                    instruction_form[self.COMMENT_ID] = ' '.join(
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
                        'name': result[self.DIRECTIVE_ID]['name'],
                        'parameters': result[self.DIRECTIVE_ID]['parameters'],
                    }
                )
                if self.COMMENT_ID in result[self.DIRECTIVE_ID]:
                    instruction_form[self.COMMENT_ID] = ' '.join(
                        result[self.DIRECTIVE_ID][self.COMMENT_ID]
                    )
            except pp.ParseException:
                pass

        # 4. Parse instruction
        if result is None:
            try:
                result = self.parse_instruction(line)
            except pp.ParseException as e:
                raise ValueError('Could not parse instruction on line {}: {!r}'.format(
                    line_number, line))
            instruction_form[self.INSTRUCTION_ID] = result[self.INSTRUCTION_ID]
            instruction_form[self.OPERANDS_ID] = result[self.OPERANDS_ID]
            instruction_form[self.COMMENT_ID] = result[self.COMMENT_ID]

        return instruction_form

    def parse_instruction(self, instruction):
        result = self.instruction_parser.parseString(instruction, parseAll=True).asDict()
        result = AttrDict.convert_dict(result)
        operands = []
        # Add operands to list
        # Check first operand
        if 'operand1' in result:
            operands.append(self.process_operand(result['operand1']))
        # Check second operand
        if 'operand2' in result:
            operands.append(self.process_operand(result['operand2']))
        # Check third operand
        if 'operand3' in result:
            operands.append(self.process_operand(result['operand3']))
        # Check fourth operand
        if 'operand4' in result:
            operands.append(self.process_operand(result['operand4']))
        return_dict = AttrDict(
            {
                self.INSTRUCTION_ID: result['mnemonic'],
                self.OPERANDS_ID: operands,
                self.COMMENT_ID:
                    ' '.join(result[self.COMMENT_ID]) if self.COMMENT_ID in result else None,
            }
        )
        return return_dict

    def process_operand(self, operand):
        # For the moment, only used to structure memory addresses
        if self.MEMORY_ID in operand:
            return self.substitute_memory_address(operand[self.MEMORY_ID])
        if self.IMMEDIATE_ID in operand:
            return self.substitue_immediate(operand[self.IMMEDIATE_ID])
        if self.LABEL_ID in operand:
            return self.substitute_label(operand[self.LABEL_ID])
        return operand

    def substitute_memory_address(self, memory_address):
        # Remove unecessarily created dictionary entries during memory address parsing
        offset = None if 'offset' not in memory_address else memory_address['offset']
        base = None if 'base' not in memory_address else memory_address['base']
        index = None if 'index' not in memory_address else memory_address['index']
        scale = 1 if 'scale' not in memory_address else int(memory_address['scale'])
        new_dict = AttrDict({'offset': offset, 'base': base, 'index': index, 'scale': scale})
        return AttrDict({self.MEMORY_ID: new_dict})

    def substitute_label(self, label):
        # remove duplicated 'name' level due to identifier
        label['name'] = label['name']['name']
        return AttrDict({self.LABEL_ID: label})

    def substitue_immediate(self, immediate):
        if 'identifier' in immediate:
            # actually an identifier, change declaration
            return immediate
        # otherwise nothing to do
        return AttrDict({self.IMMEDIATE_ID: immediate})

    def get_full_reg_name(self, register):
        # nothing to do
        return register['name']

    def normalize_imd(self, imd):
        if 'value' in imd:
            if imd['value'].lower().startswith('0x'):
                # hex, return decimal
                return int(imd['value'], 16)
            return int(imd['value'], 10)
        # identifier
        return imd

    def is_reg_dependend_of(self, reg_a, reg_b):
        # Check if they are the same registers
        if reg_a.name == reg_b.name:
            return True
        # Check vector registers first
        if self.is_vector_register(reg_a):
            if self.is_vector_register(reg_b):
                if reg_a.name[1:] == reg_b.name[1:]:
                    # Registers in the same vector space
                    return True
            return False
        # Check basic GPRs
        a_dep = ['RAX', 'EAX', 'AX', 'AH', 'AL']
        b_dep = ['RBX', 'EBX', 'BX', 'BH', 'BL']
        c_dep = ['RCX', 'ECX', 'CX', 'CH', 'CL']
        d_dep = ['RDX', 'EDX', 'DX', 'DH', 'DL']
        sp_dep = ['RSP', 'ESP', 'SP', 'SPL']
        src_dep = ['RSI', 'ESI', 'SI', 'SIL']
        dst_dep = ['RDI', 'EDI', 'DI', 'DIL']
        basic_gprs = [a_dep, b_dep, c_dep, d_dep, sp_dep, src_dep, dst_dep]
        if self.is_basic_gpr(reg_a):
            if self.is_basic_gpr(reg_b):
                for dep_group in basic_gprs:
                    if reg_a['name'].upper() in dep_group:
                        if reg_b['name'].upper() in dep_group:
                            return True
            return False
        # Check other GPRs
        gpr_parser = (
            pp.CaselessLiteral('R')
            + pp.Word(pp.nums).setResultsName('id')
            + pp.Optional(pp.Word('dwbDWB', exact=1))
        )
        try:
            id_a = gpr_parser.parseString(reg_a['name'], parseAll=True).asDict()['id']
            id_b = gpr_parser.parseString(reg_b['name'], parseAll=True).asDict()['id']
            if id_a == id_b:
                return True
        except pp.ParseException:
            return False
        # No dependencies
        return False

    def is_basic_gpr(self, register):
        if any(char.isdigit() for char in register['name']):
            return False
        return True

    def is_gpr(self, register):
        gpr_parser = (
            pp.CaselessLiteral('R')
            + pp.Word(pp.nums).setResultsName('id')
            + pp.Optional(pp.Word('dwbDWB', exact=1))
        )
        if self.is_basic_gpr(register):
            return True
        else:
            try:
                gpr_parser.parseString(register['name'], parseAll=True)
                return True
            except pp.ParseException:
                return False

    def is_vector_register(self, register):
        if len(register['name']) > 2 and register['name'][1:3].lower() == 'mm':
            return True
        return False

    def get_reg_type(self, register):
        if self.is_gpr(register):
            return 'gpr'
        elif self.is_vector_register(register):
            return register['name'][:3].lower()
        raise ValueError
