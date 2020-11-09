#!/usr/bin/env python3

import os
import pickle
import re
import string
from copy import deepcopy
from itertools import product
import hashlib
from pathlib import Path
from collections import defaultdict

import ruamel.yaml
from ruamel.yaml.compat import StringIO

from osaca import __version__, utils
from osaca.parser import ParserX86ATT


class MachineModel(object):
    WILDCARD = '*'
    INTERNAL_VERSION = 1  # increase whenever self._data format changes to invalidate cache!

    def __init__(self, arch=None, path_to_yaml=None, isa=None, lazy=False):
        if not arch and not path_to_yaml:
            if not isa:
                raise ValueError('One of arch, path_to_yaml and isa must be specified')
            self._data = {
                'osaca_version': str(__version__),
                'micro_architecture': None,
                'arch_code': None,
                'isa': isa,
                'ROB_size': None,
                'retired_uOps_per_cycle': None,
                'scheduler_size': None,
                'hidden_loads': None,
                'load_latency': {},
                'load_throughput': [
                    {'base': b, 'index': i, 'offset': o, 'scale': s, 'port_pressure': []}
                    for b, i, o, s in product(['gpr'], ['gpr', None], ['imd', None], [1, 8])
                ],
                'load_throughput_default': [],
                'ports': [],
                'port_model_scheme': None,
                'instruction_forms': []
            }
        else:
            if arch and path_to_yaml:
                raise ValueError('Only one of arch and path_to_yaml is allowed.')
            self._path = path_to_yaml
            self._arch = arch
            yaml = self._create_yaml_object()
            if arch:
                self._arch = arch.lower()
                self._path = utils.find_datafile(self._arch + '.yml')
            # check if file is cached
            cached = self._get_cached(self._path) if not lazy else False
            if cached:
                self._data = cached
            else:
                # otherwise load
                with open(self._path, 'r') as f:
                    if not lazy:
                        self._data = yaml.load(f)
                    else:
                        file_content = ''
                        line = f.readline()
                        while 'instruction_forms:' not in line:
                            file_content += line
                            line = f.readline()
                        self._data = yaml.load(file_content)
                        self._data['instruction_forms'] = []
                # separate multi-alias instruction forms
                for entry in [x for x in self._data['instruction_forms']
                              if isinstance(x['name'], list)]:
                    for name in entry['name']:
                        new_entry = {'name': name}
                        for k in [x for x in entry.keys() if x != 'name']:
                            new_entry[k] = entry[k]
                        self._data['instruction_forms'].append(new_entry)
                    # remove old entry
                    self._data['instruction_forms'].remove(entry)
                # Normalize instruction_form names (to UPPERCASE) and build dict for faster access:
                self._data['instruction_forms_dict'] = defaultdict(list)
                for iform in self._data['instruction_forms']:
                    iform['name'] = iform['name'].upper()
                    self._data['instruction_forms_dict'][iform['name']].append(iform)
                self._data['internal_version'] = self.INTERNAL_VERSION

                if not lazy:
                    # cache internal representation for future use
                    self._write_in_cache(self._path)

    def __getitem__(self, key):
        """Return configuration entry."""
        return self._data[key]

    def __contains__(self, key):
        """Return true if configuration key is present."""
        return key in self._data

    ######################################################

    def get_instruction(self, name, operands):
        """Find and return instruction data from name and operands."""
        # For use with dict instead of list as DB
        if name is None:
            return None
        name_matched_iforms = self._data['instruction_forms_dict'].get(name.upper(), [])
        try:
            return next(
                instruction_form
                for instruction_form in name_matched_iforms if self._match_operands(
                    instruction_form['operands'] if 'operands' in instruction_form else [],
                    operands))
        except StopIteration:
            return None
        except TypeError as e:
            print('\nname: {}\noperands: {}'.format(name, operands))
            raise TypeError from e

    def average_port_pressure(self, port_pressure):
        """Construct average port pressure list from instruction data."""
        port_list = self._data['ports']
        average_pressure = [0.0] * len(port_list)
        for cycles, ports in port_pressure:
            for p in ports:
                average_pressure[port_list.index(p)] += cycles / len(ports)
        return average_pressure

    def set_instruction(
        self, name, operands=None, latency=None, port_pressure=None, throughput=None, uops=None
    ):
        """Import instruction form information."""
        # If it already exists. Overwrite information.
        instr_data = self.get_instruction(name, operands)
        if instr_data is None:
            instr_data = {}
            self._data['instruction_forms'].append(instr_data)

        instr_data['name'] = name
        instr_data['operands'] = operands
        instr_data['latency'] = latency
        instr_data['port_pressure'] = port_pressure
        instr_data['throughput'] = throughput
        instr_data['uops'] = uops

    def set_instruction_entry(self, entry):
        """Import instruction as entry object form information."""
        self.set_instruction(
            entry['name'],
            entry['operands'] if 'operands' in entry else None,
            entry['latency'] if 'latency' in entry else None,
            entry['port_pressure'] if 'port_pressure' in entry else None,
            entry['throughput'] if 'throughput' in entry else None,
            entry['uops'] if 'uops' in entry else None,
        )

    def add_port(self, port):
        """Add port in port model of current machine model."""
        if port not in self._data['ports']:
            self._data['ports'].append(port)

    def get_ISA(self):
        """Return ISA of :class:`MachineModel`."""
        return self._data['isa'].lower()

    def get_arch(self):
        """Return micro-architecture code of :class:`MachineModel`."""
        return self._data['arch_code'].lower()

    def get_ports(self):
        """Return port model of :class:`MachineModel`."""
        return self._data['ports']

    def has_hidden_loads(self):
        """Return if model has hidden loads."""
        if 'hidden_loads' in self._data:
            return self._data['hidden_loads']
        return False

    def get_load_latency(self, reg_type):
        """Return load latency for given register type."""
        return self._data['load_latency'][reg_type]

    def get_load_throughput(self, memory):
        """Return load thorughput for given register type."""
        ld_tp = [m for m in self._data['load_throughput'] if self._match_mem_entries(memory, m)]
        if len(ld_tp) > 0:
            return ld_tp[0]['port_pressure']
        return self._data['load_throughput_default']

    def get_store_latency(self, reg_type):
        """Return store latency for given register type."""
        # assume 0 for now, since load-store-dependencies currently not detectable
        return 0

    def get_store_throughput(self, memory):
        """Return store throughput for given register type."""
        st_tp = [m for m in self._data['store_throughput'] if self._match_mem_entries(memory, m)]
        if len(st_tp) > 0:
            return st_tp[0]['port_pressure']
        return self._data['store_throughput_default']

    def _match_mem_entries(self, mem, i_mem):
        """Check if memory addressing ``mem`` and ``i_mem`` are of the same type."""
        if self._data['isa'].lower() == 'aarch64':
            return self._is_AArch64_mem_type(i_mem, mem)
        if self._data['isa'].lower() == 'x86':
            return self._is_x86_mem_type(i_mem, mem)

    def get_data_ports(self):
        """Return all data ports (i.e., ports with D-suffix) of current model."""
        data_port = re.compile(r'^[0-9]+D$')
        data_ports = [x for x in filter(data_port.match, self._data['ports'])]
        return data_ports

    @staticmethod
    def get_full_instruction_name(instruction_form):
        """Get one instruction name string including the mnemonic and all operands."""
        operands = []
        for op in instruction_form['operands']:
            op_attrs = [
                y + ':' + str(op[y])
                for y in list(filter(lambda x: True if x != 'class' else False, op))
            ]
            operands.append('{}({})'.format(op['class'], ','.join(op_attrs)))
        return '{}  {}'.format(instruction_form['name'].lower(), ','.join(operands))

    @staticmethod
    def get_isa_for_arch(arch):
        """Return ISA for given micro-arch ``arch``."""
        arch_dict = {
            'a64fx': 'aarch64',
            'tx2': 'aarch64',
            'n1': 'aarch64',
            'zen1': 'x86',
            'zen+': 'x86',
            'zen2': 'x86',
            'con': 'x86',  # Intel Conroe
            'wol': 'x86',  # Intel Wolfdale
            'snb': 'x86',
            'ivb': 'x86',
            'hsw': 'x86',
            'bdw': 'x86',
            'skl': 'x86',
            'skx': 'x86',
            'csx': 'x86',
            'wsm': 'x86',
            'nhm': 'x86',
            'kbl': 'x86',
            'cnl': 'x86',
            'cfl': 'x86',
            'icl': 'x86',
        }
        arch = arch.lower()
        if arch in arch_dict:
            return arch_dict[arch].lower()
        else:
            raise ValueError("Unknown architecture {!r}.".format(arch))

    def dump(self, stream=None):
        """Dump machine model to stream or return it as a ``str`` if no stream is given."""
        # Replace instruction form's port_pressure with styled version for RoundtripDumper
        formatted_instruction_forms = deepcopy(self._data['instruction_forms'])
        for instruction_form in formatted_instruction_forms:
            if instruction_form['port_pressure'] is not None:
                cs = ruamel.yaml.comments.CommentedSeq(instruction_form['port_pressure'])
                cs.fa.set_flow_style()
                instruction_form['port_pressure'] = cs

        # Replace load_throughput with styled version for RoundtripDumper
        formatted_load_throughput = []
        for lt in self._data['load_throughput']:
            cm = ruamel.yaml.comments.CommentedMap(lt)
            cm.fa.set_flow_style()
            formatted_load_throughput.append(cm)

        # Create YAML object
        yaml = self._create_yaml_object()
        if not stream:
            stream = StringIO()

        yaml.dump(
            {
                k: v
                for k, v in self._data.items()
                if k not in ['instruction_forms', 'instruction_forms_dict', 'load_throughput',
                             'internal_version']
            },
            stream,
        )
        yaml.dump({'load_throughput': formatted_load_throughput}, stream)
        yaml.dump({'instruction_forms': formatted_instruction_forms}, stream)

        if isinstance(stream, StringIO):
            return stream.getvalue()

    ######################################################

    def _get_cached(self, filepath):
        """
        Check if machine model is cached and if so, load it.

        :param filepath: path to check for cached machine model
        :type filepath: str
        :returns: cached DB if existing, `False` otherwise
        """
        p = Path(filepath)
        hexhash = hashlib.sha256(p.read_bytes()).hexdigest()

        # 1. companion cachefile: same location, with '.<name>_<sha512hash>.pickle'
        companion_cachefile = p.with_name('.' + p.stem + '_' + hexhash).with_suffix('.pickle')
        if companion_cachefile.exists():
            # companion file (must be up-to-date, due to equal hash)
            with companion_cachefile.open('rb') as f:
                data = pickle.load(f)
            if data.get('internal_version') == self.INTERNAL_VERSION:
                return data

        # 2. home cachefile: ~/.osaca/cache/<name>_<sha512hash>.pickle
        home_cachefile = (Path(utils.CACHE_DIR) / (p.stem + '_' + hexhash)).with_suffix('.pickle')
        if home_cachefile.exists():
            # home file (must be up-to-date, due to equal hash)
            with home_cachefile.open('rb') as f:
                data = pickle.load(f)
            if data.get('internal_version') == self.INTERNAL_VERSION:
                return data
        return False

    def _write_in_cache(self, filepath):
        """
        Write machine model to cache

        :param filepath: path to store DB
        :type filepath: str
        """
        p = Path(filepath)
        hexhash = hashlib.sha256(p.read_bytes()).hexdigest()
        # 1. companion cachefile: same location, with '.<name>_<sha512hash>.pickle'
        companion_cachefile = p.with_name('.' + p.stem + '_' + hexhash).with_suffix('.pickle')
        if os.access(str(companion_cachefile.parent), os.W_OK):
            with companion_cachefile.open('wb') as f:
                pickle.dump(self._data, f)
                return

        # 2. home cachefile: ~/.osaca/cache/<name>_<sha512hash>.pickle
        cache_dir = Path(utils.CACHE_DIR)
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except OSError:
            return
        home_cachefile = (cache_dir / (p.stem + '_' + hexhash)).with_suffix('.pickle')
        if os.access(str(home_cachefile.parent), os.W_OK):
            with home_cachefile.open('wb') as f:
                pickle.dump(self._data, f)

    def _get_key(self, name, operands):
        """Get unique instruction form key for dict DB."""
        key_string = name.lower() + '-'
        if operands is None:
            return key_string[:-1]
        key_string += '_'.join([self._get_operand_hash(op) for op in operands])
        return key_string

    def _get_operand_hash(self, operand):
        """Get unique key for operand for dict DB"""
        operand_string = ''
        if 'class' in operand:
            # DB entry
            opclass = operand['class']
        else:
            # parsed instruction
            opclass = list(operand.keys())[0]
            operand = operand[opclass]
        if opclass == 'immediate':
            # Immediate
            operand_string += 'i'
        elif opclass == 'register':
            # Register
            if 'prefix' in operand:
                operand_string += operand['prefix']
                operand_string += operand['shape'] if 'shape' in operand else ''
            elif 'name' in operand:
                operand_string += 'r' if operand['name'] == 'gpr' else operand['name'][0]
        elif opclass == 'memory':
            # Memory
            operand_string += 'm'
            operand_string += 'b' if operand['base'] is not None else ''
            operand_string += 'o' if operand['offset'] is not None else ''
            operand_string += 'i' if operand['index'] is not None else ''
            operand_string += (
                's' if operand['scale'] == self.WILDCARD or operand['scale'] > 1 else ''
            )
            if 'pre-indexed' in operand:
                operand_string += 'r' if operand['pre-indexed'] else ''
                operand_string += 'p' if operand['post-indexed'] else ''
        return operand_string

    def _create_db_operand_aarch64(self, operand):
        """Create instruction form operand for DB out of operand string."""
        if operand == 'i':
            return {'class': 'immediate', 'imd': 'int'}
        elif operand in 'wxbhsdq':
            return {'class': 'register', 'prefix': operand}
        elif operand.startswith('v'):
            return {'class': 'register', 'prefix': 'v', 'shape': operand[1:2]}
        elif operand.startswith('m'):
            return {
                'class': 'memory',
                'base': 'x' if 'b' in operand else None,
                'offset': 'imd' if 'o' in operand else None,
                'index': 'gpr' if 'i' in operand else None,
                'scale': 8 if 's' in operand else 1,
                'pre-indexed': True if 'r' in operand else False,
                'post-indexed': True if 'p' in operand else False,
            }
        else:
            raise ValueError('Parameter {} is not a valid operand code'.format(operand))

    def _create_db_operand_x86(self, operand):
        """Create instruction form operand for DB out of operand string."""
        if operand == 'r':
            return {'class': 'register', 'name': 'gpr'}
        elif operand in 'xyz':
            return {'class': 'register', 'name': operand + 'mm'}
        elif operand == 'i':
            return {'class': 'immediate', 'imd': 'int'}
        elif operand.startswith('m'):
            return {
                'class': 'memory',
                'base': 'gpr' if 'b' in operand else None,
                'offset': 'imd' if 'o' in operand else None,
                'index': 'gpr' if 'i' in operand else None,
                'scale': 8 if 's' in operand else 1,
            }
        else:
            raise ValueError('Parameter {} is not a valid operand code'.format(operand))

    def _check_for_duplicate(self, name, operands):
        """
        Check if instruction form exists at least twice in DB.

        :param str name: mnemonic of instruction form
        :param list operands: instruction form operands

        :returns: `True`, if duplicate exists, `False` otherwise
        """
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
        """Check if all operand types of ``i_operands`` and ``operands`` match."""
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

    def _check_operands(self, i_operand, operand):
        """Check if the types of operand ``i_operand`` and ``operand`` match."""
        # check for wildcard
        if self.WILDCARD in operand:
            if (
                'class' in i_operand
                and i_operand['class'] == 'register'
                or 'register' in i_operand
            ):
                return True
            else:
                return False
        if self._data['isa'].lower() == 'aarch64':
            return self._check_AArch64_operands(i_operand, operand)
        if self._data['isa'].lower() == 'x86':
            return self._check_x86_operands(i_operand, operand)

    def _check_AArch64_operands(self, i_operand, operand):
        """Check if the types of operand ``i_operand`` and ``operand`` match."""
        if 'class' in operand:
            # compare two DB entries
            return self._compare_db_entries(i_operand, operand)
        # TODO support class wildcards
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
        # TODO support wildcards
        if 'value' in operand or ('immediate' in operand and 'value' in operand['immediate']):
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'int'
        if 'float' in operand or ('immediate' in operand and 'float' in operand['immediate']):
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'float'
        if 'double' in operand or ('immediate' in operand and 'double' in operand['immediate']):
            return i_operand['class'] == 'immediate' and i_operand['imd'] == 'double'
        # identifier
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
        """Check if the types of operand ``i_operand`` and ``operand`` match."""
        if 'class' in operand:
            # compare two DB entries
            return self._compare_db_entries(i_operand, operand)
        # register
        if 'register' in operand:
            if i_operand['class'] != 'register':
                return False
            return self._is_x86_reg_type(i_operand, operand['register'], consider_masking=True)
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
        """Check if operand types in DB format (i.e., not parsed) match."""
        operand_attributes = list(
            filter(lambda x: True if x != 'source' and x != 'destination' else False, operand_1)
        )
        for key in operand_attributes:
            try:
                if operand_1[key] != operand_2[key] and not any(
                    [x == self.WILDCARD for x in [operand_1[key], operand_2[key]]]
                ):
                    return False
            except KeyError:
                return False
        return True

    def _is_AArch64_reg_type(self, i_reg, reg):
        """Check if register type match."""
        # check for wildcards
        if reg['prefix'] == self.WILDCARD or i_reg['prefix'] == self.WILDCARD:
            if 'shape' in reg:
                if 'shape' in i_reg and (
                    reg['shape'] == i_reg['shape']
                    or self.WILDCARD in (reg['shape'] + i_reg['shape'])
                ):
                    return True
                return False
            return True
        # check for prefix and shape
        if reg['prefix'] != i_reg['prefix']:
            return False
        if 'shape' in reg:
            if 'shape' in i_reg and reg['shape'] == i_reg['shape']:
                return True
            return False
        return True

    def _is_x86_reg_type(self, i_reg, reg, consider_masking=False):
        """Check if register type match."""
        i_reg_name = i_reg['name'] if i_reg and 'name' in i_reg else i_reg
        if reg is None:
            if i_reg is None:
                return True
            return False
        # check for wildcards
        if i_reg_name == self.WILDCARD or reg['name'] == self.WILDCARD:
            return True
        # differentiate between vector registers (mm, xmm, ymm, zmm) and others (gpr)
        parser_x86 = ParserX86ATT()
        if parser_x86.is_vector_register(reg):
            if reg['name'].rstrip(string.digits).lower() == i_reg_name:
                # Consider masking and zeroing for AVX512
                if consider_masking:
                    mask_ok = zero_ok = True
                    if 'mask' in reg or 'mask' in i_reg:
                        # one instruction is missing the masking while the other has it
                        mask_ok = False
                        # check for wildcard
                        if (
                            (
                                'mask' in reg
                                and reg['mask'].rstrip(string.digits).lower() == i_reg.get('mask')
                            )
                            or reg.get('mask') == self.WILDCARD
                            or i_reg.get('mask') == self.WILDCARD
                        ):
                            mask_ok = True
                        if bool('zeroing' in reg) ^ bool('zeroing' in i_reg):
                            # one instruction is missing zeroing while the other has it
                            zero_ok = False
                            # check for wildcard
                            if (
                                i_reg.get('zeroing') == self.WILDCARD
                                or reg.get('zeroing') == self.WILDCARD
                            ):
                                zero_ok = True
                        if not mask_ok or not zero_ok:
                            return False
                return True
        else:
            if i_reg_name == 'gpr':
                return True
        return False

    def _is_AArch64_mem_type(self, i_mem, mem):
        """Check if memory addressing type match."""
        if (
            # check base
            (
                (mem['base'] is None and i_mem['base'] is None)
                or i_mem['base'] == self.WILDCARD
                or mem['base']['prefix'] == i_mem['base']
            )
            # check offset
            and (
                mem['offset'] == i_mem['offset']
                or i_mem['offset'] == self.WILDCARD
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
                or i_mem['index'] == self.WILDCARD
                or (
                    mem['index'] is not None
                    and 'prefix' in mem['index']
                    and mem['index']['prefix'] == i_mem['index']
                )
            )
            # check scale
            and (
                mem['scale'] == i_mem['scale']
                or i_mem['scale'] == self.WILDCARD
                or (mem['scale'] != 1 and i_mem['scale'] != 1)
            )
            # check pre-indexing
            and (
                i_mem['pre-indexed'] == self.WILDCARD
                or ('pre_indexed' in mem) == (i_mem['pre-indexed'])
            )
            # check post-indexing
            and (
                i_mem['post-indexed'] == self.WILDCARD
                or ('post_indexed' in mem) == (i_mem['post-indexed'])
            )
        ):
            return True
        return False

    def _is_x86_mem_type(self, i_mem, mem):
        """Check if memory addressing type match."""
        if (
            # check base
            (
                (mem['base'] is None and i_mem['base'] is None)
                or i_mem['base'] == self.WILDCARD
                or self._is_x86_reg_type(i_mem['base'], mem['base'])
            )
            # check offset
            and (
                mem['offset'] == i_mem['offset']
                or i_mem['offset'] == self.WILDCARD
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
                or (
                    mem['offset'] is not None
                    and 'identifier' in mem['offset']
                    and i_mem['offset'] == 'id'
                )
            )
            # check index
            and (
                mem['index'] == i_mem['index']
                or i_mem['index'] == self.WILDCARD
                or (
                    mem['index'] is not None
                    and 'name' in mem['index']
                    and self._is_x86_reg_type(i_mem['index'], mem['index'])
                )
            )
            # check scale
            and (
                mem['scale'] == i_mem['scale']
                or i_mem['scale'] == self.WILDCARD
                or (mem['scale'] != 1 and i_mem['scale'] != 1)
            )
        ):
            return True
        return False

    def _create_yaml_object(self):
        """Create YAML object for parsing and dumping DB"""
        yaml_obj = ruamel.yaml.YAML()
        yaml_obj.representer.add_representer(type(None), self.__represent_none)
        yaml_obj.default_flow_style = None
        yaml_obj.width = 120
        yaml_obj.representer.ignore_aliases = lambda *args: True
        return yaml_obj

    def __represent_none(self, yaml_obj, data):
        """YAML representation for `None`"""
        return yaml_obj.represent_scalar(u'tag:yaml.org,2002:null', u'~')
