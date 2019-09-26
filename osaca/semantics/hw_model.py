#!/usr/bin/env python3

import os
import re

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
                assert os.path.exists(self._path)
                with open(self._path, 'r') as f:
                    self._data = yaml.load(f, Loader=yaml.Loader)
            except (AssertionError, FileNotFoundError):
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
        if name is None:
            return None
        try:
            return next(
                instruction_form
                for instruction_form in self._data['instruction_forms']
                if instruction_form['name'].lower() == name.lower()
                and self._match_operands(instruction_form['operands'], operands)
            )
        except StopIteration:
            return None
        except TypeError:
            print('\nname: {}\noperands: {}'.format(name, operands))
            raise TypeError

    def get_ISA(self):
        return self._data['isa']

    def get_arch(self):
        return self._data['arch_code']

    def get_ports(self):
        return self._data['ports']

    def has_hidden_loads(self):
        if 'hidden_loads' in self._data:
            return self._data['hidden_loads']
        return False

    def get_load_latency(self, reg_type):
        return self._data['load_latency'][reg_type]

    def get_load_throughput(self, memory):
        ld_tp = [m for m in self._data['load_throughput'] if self._match_mem_entries(memory, m)]
        if len(ld_tp) > 0:
            return ld_tp[0]['port_pressure']
        return None

    def _match_mem_entries(self, mem, i_mem):
        if self._data['isa'].lower() == 'aarch64':
            return self._is_AArch64_mem_type(i_mem, mem)
        if self._data['isa'].lower() == 'x86':
            return self._is_x86_mem_type(i_mem, mem)

    def get_data_ports(self):
        data_port = re.compile(r'^[0-9]+D$')
        data_ports = [x for x in filter(data_port.match, self._data['ports'])]
        return data_ports

    @staticmethod
    def get_isa_for_arch(arch):
        arch_dict = {
            'vulcan': 'aarch64',
            'zen1': 'x86',
            'snb': 'x86',
            'ivb': 'x86',
            'hsw': 'x86',
            'bdw': 'x86',
            'skl': 'x86',
            'skx': 'x86',
            'csx': 'x86',
        }
        arch = arch.lower()
        if arch in arch_dict:
            return arch_dict[arch].lower()
        return None

    ######################################################

    def _check_for_duplicate(self, name, operands):
        matches = [
            instruction_form
            for instruction_form in self._data['instruction_forms']
            if instruction_form['name'].lower() == name.lower()
            and self._match_operands(instruction_form['operands'], operands)
        ]
        if len(matches) > 1:
            return True
        return False

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
        if self._data['isa'].lower() == 'aarch64':
            return self._check_AArch64_operands(i_operands, operands)
        if self._data['isa'].lower() == 'x86':
            return self._check_x86_operands(i_operands, operands)

    def _check_AArch64_operands(self, i_operand, operand):
        if 'class' in operand:
            # compare two DB entries
            return self._compare_db_entries(i_operand, operand)
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
        if 'class' in operand:
            # compare two DB entries
            return self._compare_db_entries(i_operand, operand)
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

    def _compare_db_entries(self, operand_1, operand_2):
        operand_attributes = list(
            filter(lambda x: True if x != 'source' and x != 'destination' else False, operand_1)
        )
        for key in operand_attributes:
            try:
                if operand_1[key] != operand_2[key]:
                    return False
            except KeyError:
                return False
        return True

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
            and (mem['scale'] == i_mem['scale'] or (mem['scale'] != 1 and i_mem['scale'] != 1))
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
            and (mem['scale'] == i_mem['scale'] or (mem['scale'] != 1 and i_mem['scale'] != 1))
        ):
            return True
        return False
