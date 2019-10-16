#!/usr/bin/env python3


import pyparsing as pp

from osaca.parser import AttrDict, BaseParser


class ParserAArch64v81(BaseParser):
    def __init__(self):
        super().__init__()

    def construct_parser(self):
        # Comment
        symbol_comment = '//'
        self.comment = pp.Literal(symbol_comment) + pp.Group(
            pp.ZeroOrMore(pp.Word(pp.printables))
        ).setResultsName(self.COMMENT_ID)
        # Define ARM assembly identifier
        relocation = pp.Combine(pp.Literal(':') + pp.Word(pp.alphanums + '_') + pp.Literal(':'))
        first = pp.Word(pp.alphas + '_.', exact=1)
        rest = pp.Word(pp.alphanums + '_.')
        identifier = pp.Group(
            pp.Optional(relocation).setResultsName('relocation')
            + pp.Combine(first + pp.Optional(rest)).setResultsName('name')
        ).setResultsName('identifier')
        # Label
        self.label = pp.Group(
            identifier.setResultsName('name') + pp.Literal(':') + pp.Optional(self.comment)
        ).setResultsName(self.LABEL_ID)
        # Directive
        decimal_number = pp.Combine(
            pp.Optional(pp.Literal('-')) + pp.Word(pp.nums)
        ).setResultsName('value')
        hex_number = pp.Combine(pp.Literal('0x') + pp.Word(pp.hexnums)).setResultsName('value')
        directive_option = pp.Combine(
            pp.Word(pp.alphas + '#@.%', exact=1)
            + pp.Optional(pp.Word(pp.printables + ' ', excludeChars=','))
        )
        directive_parameter = (
            pp.quotedString | directive_option | identifier | hex_number | decimal_number
        )
        commaSeparatedList = pp.delimitedList(pp.Optional(directive_parameter), delim=',')
        self.directive = pp.Group(
            pp.Literal('.')
            + pp.Word(pp.alphanums + '_').setResultsName('name')
            + commaSeparatedList.setResultsName('parameters')
            + pp.Optional(self.comment)
        ).setResultsName(self.DIRECTIVE_ID)

        ##############################
        # Instructions
        # Mnemonic
        # (?P<instr>[a-zA-Z][a-zA-Z0-9]*)(?P<setflg>S?)(P?<CC>.[a-zA-Z]{2})
        mnemonic = pp.Word(pp.alphanums + '.').setResultsName('mnemonic')
        # Immediate:
        # int: ^-?[0-9]+ | hex: ^0x[0-9a-fA-F]+ | fp: ^[0-9]{1}.[0-9]+[eE]{1}[\+-]{1}[0-9]+[fF]?
        symbol_immediate = '#'
        mantissa = pp.Combine(
            pp.Optional(pp.Literal('-')) + pp.Word(pp.nums) + pp.Literal('.') + pp.Word(pp.nums)
        ).setResultsName('mantissa')
        exponent = (
            pp.CaselessLiteral('e')
            + pp.Word('+-').setResultsName('e_sign')
            + pp.Word(pp.nums).setResultsName('exponent')
        )
        float_ = pp.Group(
            mantissa + pp.Optional(exponent) + pp.CaselessLiteral('f')
        ).setResultsName('float')
        double_ = pp.Group(mantissa + pp.Optional(exponent)).setResultsName('double')
        immediate = pp.Group(
            pp.Optional(pp.Literal(symbol_immediate))
            + (hex_number ^ decimal_number ^ float_ ^ double_)
            | (pp.Optional(pp.Literal(symbol_immediate)) + identifier)
        ).setResultsName(self.IMMEDIATE_ID)
        shift_op = (
            pp.CaselessLiteral('lsl')
            ^ pp.CaselessLiteral('lsr')
            ^ pp.CaselessLiteral('asr')
            ^ pp.CaselessLiteral('ror')
            ^ pp.CaselessLiteral('sxtw')
            ^ pp.CaselessLiteral('uxtw')
        )
        arith_immediate = pp.Group(
            immediate.setResultsName('base_immediate')
            + pp.Suppress(pp.Literal(','))
            + shift_op.setResultsName('shift_op')
            + immediate.setResultsName('shift')
        ).setResultsName(self.IMMEDIATE_ID)
        # Register:
        # scalar: [XWBHSDQ][0-9]{1,2}  |   vector: V[0-9]{1,2}\.[12468]{1,2}[BHSD]()?
        # define SP and ZR register aliases as regex, due to pyparsing does not support
        # proper lookahead
        alias_r31_sp = pp.Regex('(?P<prefix>[a-zA-Z])?(?P<name>(sp|SP))')
        alias_r31_zr = pp.Regex('(?P<prefix>[a-zA-Z])?(?P<name>(zr|ZR))')
        scalar = pp.Word(pp.alphas, exact=1).setResultsName('prefix') + pp.Word(
            pp.nums
        ).setResultsName('name')
        index = pp.Literal('[') + pp.Word(pp.nums).setResultsName('index') + pp.Literal(']')
        vector = (
            pp.CaselessLiteral('v').setResultsName('prefix')
            + pp.Word(pp.nums).setResultsName('name')
            + pp.Literal('.')
            + pp.Optional(pp.Word('12468')).setResultsName('lanes')
            + pp.Word(pp.alphas, exact=1).setResultsName('shape')
            + pp.Optional(index)
        )
        self.list_element = vector ^ scalar
        register_list = (
            pp.Literal('{')
            + (
                pp.delimitedList(pp.Combine(self.list_element), delim=',').setResultsName('list')
                ^ pp.delimitedList(pp.Combine(self.list_element), delim='-').setResultsName(
                    'range'
                )
            )
            + pp.Literal('}')
            + pp.Optional(index)
        )
        register = pp.Group(
            (alias_r31_sp | alias_r31_zr | vector | scalar | register_list)
            + pp.Optional(
                pp.Suppress(pp.Literal(','))
                + shift_op.setResultsName('shift_op')
                + immediate.setResultsName('shift')
            )
        ).setResultsName(self.REGISTER_ID)
        # Memory
        register_index = register.setResultsName('index') + pp.Optional(
            pp.Literal(',') + pp.Word(pp.alphas) + immediate.setResultsName('scale')
        )
        memory = pp.Group(
            pp.Literal('[')
            + pp.Optional(register.setResultsName('base'))
            + pp.Optional(pp.Suppress(pp.Literal(',')))
            + pp.Optional(register_index ^ immediate.setResultsName('offset'))
            + pp.Literal(']')
            + pp.Optional(
                pp.Literal('!').setResultsName('pre_indexed')
                | (pp.Suppress(pp.Literal(',')) + immediate.setResultsName('post_indexed'))
            )
        ).setResultsName(self.MEMORY_ID)
        prefetch_op = pp.Group(
            pp.Group(pp.CaselessLiteral('PLD') ^ pp.CaselessLiteral('PST')).setResultsName('type')
            + pp.Group(
                pp.CaselessLiteral('L1') ^ pp.CaselessLiteral('L2') ^ pp.CaselessLiteral('L3')
            ).setResultsName('target')
            + pp.Group(pp.CaselessLiteral('KEEP') ^ pp.CaselessLiteral('STRM')).setResultsName(
                'policy'
            )
        ).setResultsName('prfop')
        # Combine to instruction form
        operand_first = pp.Group(
            register ^ (prefetch_op | immediate) ^ memory ^ arith_immediate ^ identifier
        )
        operand_rest = pp.Group((register ^ immediate ^ memory ^ arith_immediate) | identifier)
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
                instruction_form[self.LABEL_ID] = result[self.LABEL_ID].name
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
                        'name': result[self.DIRECTIVE_ID].name,
                        'parameters': result[self.DIRECTIVE_ID].parameters,
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
            except (pp.ParseException, KeyError):
                print(
                    '\n\n*-*-*-*-*-*-*-*-*-*-\n{}: {}\n*-*-*-*-*-*-*-*-*-*-\n\n'.format(
                        line_number, line
                    )
                )
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
                self.INSTRUCTION_ID: result.mnemonic,
                self.OPERANDS_ID: operands,
                self.COMMENT_ID: ' '.join(result[self.COMMENT_ID])
                if self.COMMENT_ID in result
                else None,
            }
        )
        return return_dict

    def process_operand(self, operand):
        # structure memory addresses
        if self.MEMORY_ID in operand:
            return self.substitute_memory_address(operand[self.MEMORY_ID])
        # structure register lists
        if self.REGISTER_ID in operand and (
            'list' in operand[self.REGISTER_ID] or 'range' in operand[self.REGISTER_ID]
        ):
            # TODO: discuss if ranges should be converted to lists
            return self.substitute_register_list(operand[self.REGISTER_ID])
        if self.REGISTER_ID in operand and operand[self.REGISTER_ID]['name'] == 'sp':
            return self.substitute_sp_register(operand[self.REGISTER_ID])
        # add value attribute to floating point immediates without exponent
        if self.IMMEDIATE_ID in operand:
            return self.substitute_immediate(operand[self.IMMEDIATE_ID])
        if self.LABEL_ID in operand:
            return self.substitute_label(operand[self.LABEL_ID])
        return operand

    def substitute_memory_address(self, memory_address):
        # Remove unnecessarily created dictionary entries during parsing
        offset = None if 'offset' not in memory_address else memory_address['offset']
        base = None if 'base' not in memory_address else memory_address['base']
        index = None if 'index' not in memory_address else memory_address['index']
        scale = 1
        if base is not None and 'name' in base and base['name'] == 'sp':
            base['prefix'] = 'x'
        if index is not None and 'name' in index and index['name'] == 'sp':
            index['prefix'] = 'x'
        valid_shift_ops = ['lsl', 'uxtw', 'sxtw']
        if 'index' in memory_address:
            if 'shift' in memory_address['index']:
                if memory_address['index']['shift_op'].lower() in valid_shift_ops:
                    scale = 2 ** int(memory_address['index']['shift']['value'])
        new_dict = AttrDict({'offset': offset, 'base': base, 'index': index, 'scale': scale})
        if 'pre_indexed' in memory_address:
            new_dict['pre_indexed'] = True
        if 'post_indexed' in memory_address:
            new_dict['post_indexed'] = memory_address['post_indexed']
        return AttrDict({self.MEMORY_ID: new_dict})

    def substitute_sp_register(self, register):
        reg = register
        reg['prefix'] = 'x'
        return AttrDict({self.REGISTER_ID: reg})

    def substitute_register_list(self, register_list):
        # Remove unnecessarily created dictionary entries during parsing
        vlist = []
        dict_name = ''
        if 'list' in register_list:
            dict_name = 'list'
        if 'range' in register_list:
            dict_name = 'range'
        for v in register_list[dict_name]:
            vlist.append(
                AttrDict.convert_dict(self.list_element.parseString(v, parseAll=True).asDict())
            )
        index = None if 'index' not in register_list else register_list['index']
        new_dict = AttrDict({dict_name: vlist, 'index': index})
        return AttrDict({self.REGISTER_ID: new_dict})

    def substitute_immediate(self, immediate):
        dict_name = ''
        if 'identifier' in immediate:
            # actually an identifier, change declaration
            return immediate
        if 'value' in immediate:
            # normal integer value, nothing to do
            return AttrDict({self.IMMEDIATE_ID: immediate})
        if 'base_immediate' in immediate:
            # arithmetic immediate, nothing to do
            return AttrDict({self.IMMEDIATE_ID: immediate})
        if 'float' in immediate:
            dict_name = 'float'
        if 'double' in immediate:
            dict_name = 'double'
        if 'exponent' in immediate[dict_name]:
            # nothing to do
            return AttrDict({self.IMMEDIATE_ID: immediate})
        else:
            # change 'mantissa' key to 'value'
            return AttrDict(
                {self.IMMEDIATE_ID: AttrDict({'value': immediate[dict_name]['mantissa']})}
            )

    def substitute_label(self, label):
        # remove duplicated 'name' level due to identifier
        label['name'] = label['name']['name']
        return AttrDict({self.LABEL_ID: label})

    def get_full_reg_name(self, register):
        if 'lanes' in register:
            return (
                register['prefix']
                + str(register['name'])
                + '.'
                + str(register['lanes'])
                + register['shape']
            )
        return register['prefix'] + str(register['name'])

    def normalize_imd(self, imd):
        if 'value' in imd:
            if imd['value'].lower().startswith('0x'):
                # hex, return decimal
                return int(imd['value'], 16)
            return int(imd['value'], 10)
        elif 'float' in imd:
            return self.ieee_to_int(imd['float'])
        elif 'double' in imd:
            return self.ieee_to_int(imd['double'])
        # identifier
        return imd

    def ieee_to_int(self, ieee_val):
        exponent = int(ieee_val['exponent'], 10)
        if ieee_val['e_sign'] == '-':
            exponent *= -1
        return float(ieee_val['mantissa']) * (10 ** exponent)

    def parse_register(self, register_string):
        raise NotImplementedError

    def is_gpr(self, register):
        if register['prefix'] in 'wx':
            return True
        return False

    def is_vector_register(self, register):
        if register['prefix'] in 'bhsdqv':
            return True
        return False

    def is_reg_dependend_of(self, reg_a, reg_b):
        prefixes_gpr = 'wx'
        prefixes_vec = 'bhsdqv'
        if reg_a['name'] == reg_b['name']:
            if reg_a['prefix'].lower() in prefixes_gpr and reg_b['prefix'].lower() in prefixes_gpr:
                return True
            if reg_a['prefix'].lower() in prefixes_vec and reg_b['prefix'].lower() in prefixes_vec:
                return True
        return False

    def get_reg_type(self, register):
        return register['prefix']
