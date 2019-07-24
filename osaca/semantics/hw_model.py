#!/usr/bin/env python3

import os

from ruamel import yaml

from osaca.parser import ParserX86ATT


class MachineModel(object):
    def __init__(self, arch=None, path_to_yaml=None):
        if not arch and not path_to_yaml:
            raise ValueError('Either arch or path_to_yaml required.')
        if arch and path_to_yaml:
            raise ValueError('Only one of arch and path_to_yaml is allowed.')
        self._path = path_to_yaml
        self._arch = arch
        if arch:
            self._arch = arch.lower()
            try:
                with open(self._find_file(self._arch), 'r') as f:
                    self._data = yaml.load(f, Loader=yaml.Loader)
            except AssertionError:
                raise ValueError(
                    'Cannot find specified architecture. Make sure the machine file exists.'
                )
        elif path_to_yaml:
            try:
                with open(self._path, 'r') as f:
                    self._data = yaml.load(f, Loader=yaml.Loader)
            except AssertionError:
                raise ValueError(
                    'Cannot find specified path to YAML file. Make sure the machine file exists.'
                )

    def _find_file(self, name):
        data_dir = os.path.expanduser('~/.osaca/data')
        name = os.path.join(data_dir, name + '.yml')
        assert os.path.exists(name)
        return name

    def __getitem__(self, key):
        """Return configuration entry."""
        return self._data[key]

    def __contains__(self, key):
        """Return true if configuration key is present."""
        return key in self._data

    ######################################################

    def get_instruction(self, name, operands):
        try:
            return next(
                instruction_form
                for instruction_form in self._data['instruction_forms']
                if instruction_form['name'] == name
                and self._match_operands(instruction_form['operands'], operands)
            )
        except StopIteration:
            return None
        except TypeError:
            print('\nname: {}\noperands: {}'.format(name, operands))
            raise TypeError

    def get_ISA(self):
        return self._data['isa']

    ######################################################

    def _match_operands(self, i_operands, operands):
        if isinstance(operands, dict):
            operands = operands['operand_list']
        operands_ok = True
        if len(operands) != len(i_operands):
            return False
        for idx, operand in enumerate(operands):
            i_operand = i_operands[idx]
            operands_ok = operands_ok and self._check_operands(i_operand, operand)
        if operands_ok:
            return True
        else:
            return False

    def _check_operands(self, i_operands, operands):
        if self._data['isa'] == 'AArch64':
            return self._check_AArch64_operands(i_operands, operands)
        if self._data['isa'] == 'x86':
            return self._check_x86_operands(i_operands, operands)

    def _check_AArch64_operands(self, i_operand, operand):
        # register
        if 'register' in operand:
            if i_operand['class'] != 'register':
                return False
            return self._is_AArch64_reg_type(i_operand, operand['register'])
        # memory
        if 'memory' in operand:
            if i_operand['class'] != 'memory':
                return False
            return self._is_AArch64_mem_type(i_operand, operand['memory'])
        # immediate
        if 'value' in operand or ('immediate' in operand and 'value' in operand['immediate']):
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'int'
        if 'float' in operand or ('immediate' in operand and 'float' in operand['immediate']):
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'float'
        if 'double' in operand or ('immediate' in operand and 'double' in operand['immediate']):
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'double'
        if 'identifier' in operand or (
            'immediate' in operand and 'identifier' in operand['immediate']
        ):
            return i_operand['class'] == 'identifier'
        # prefetch option
        if 'prfop' in operand:
            return i_operand['class'] == 'prfop'
        # no match
        return False

    def _check_x86_operands(self, i_operand, operand):
        # register
        if 'register' in operand:
            if i_operand['class'] != 'register':
                return False
            return self._is_x86_reg_type(i_operand['name'], operand['register'])
        # memory
        if 'memory' in operand:
            if i_operand['class'] != 'memory':
                return False
            return self._is_x86_mem_type(i_operand, operand['memory'])
        # immediate
        if 'immediate' in operand or 'value' in operand:
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'int'
        # identifier (e.g., labels)
        if 'identifier' in operand:
            return i_operand['class'] == 'identifier'

    def _is_AArch64_reg_type(self, i_reg, reg):
        if reg['prefix'] != i_reg['prefix']:
            return False
        if 'shape' in reg:
            if 'shape' in i_reg and reg['shape'] == i_reg['shape']:
                return True
            return False
        return True

    def _is_x86_reg_type(self, i_reg_name, reg):
        # differentiate between vector registers (xmm, ymm, zmm) and others (gpr)
        parser_x86 = ParserX86ATT()
        if parser_x86.is_vector_register(reg):
            if reg['name'][0:3] == i_reg_name:
                return True
        else:
            if i_reg_name == 'gpr':
                return True
        return False

    def _is_AArch64_mem_type(self, i_mem, mem):
        if (
            # check base
            mem['base']['prefix'] == i_mem['base']
            # check offset
            and (
                mem['offset'] == i_mem['offset']
                or (
                    mem['offset'] is not None
                    and 'identifier' in mem['offset']
                    and i_mem['offset'] == 'identifier'
                )
                or (
                    mem['offset'] is not None
                    and 'value' in mem['offset']
                    and i_mem['offset'] == 'imd'
                )
            )
            # check index
            and (
                mem['index'] == i_mem['index']
                or (
                    mem['index'] is not None
                    and 'prefix' in mem['index']
                    and mem['index']['prefix'] == i_mem['index']
                )
            )
            and mem['scale'] == i_mem['scale']
            and (('pre_indexed' in mem) == (i_mem['pre-indexed']))
            and (('post_indexed' in mem) == (i_mem['post-indexed']))
        ):
            return True
        return False

    def _is_x86_mem_type(self, i_mem, mem):
        if (
            # check base
            self._is_x86_reg_type(i_mem['base'], mem['base'])
            # check offset
            and (
                mem['offset'] == i_mem['offset']
                or (
                    mem['offset'] is not None
                    and 'identifier' in mem['offset']
                    and i_mem['offset'] == 'identifier'
                )
                or (
                    mem['offset'] is not None
                    and 'value' in mem['offset']
                    and (
                        i_mem['offset'] == 'imd'
                        or (i_mem['offset'] is None and mem['offset']['value'] == '0')
                    )
                )
            )
            # check index
            and (
                mem['index'] == i_mem['index']
                or (
                    mem['index'] is not None
                    and 'name' in mem['index']
                    and self._is_x86_reg_type(i_mem['index'], mem['index'])
                )
            )
            and mem['scale'] == i_mem['scale']
        ):
            return True
        return False
