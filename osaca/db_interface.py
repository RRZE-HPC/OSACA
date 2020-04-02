#!/usr/bin/env python3

import math
import os
import re
import sys
import warnings
from collections import OrderedDict

import ruamel.yaml

from osaca.semantics import MachineModel


def sanity_check(arch: str, verbose=False, internet_check=False, output_file=sys.stdout):
    """
    Checks the database for missing TP/LT values, instructions might missing int the ISA DB and
    duplicate instructions.

    :param arch: micro-arch key to define DB to check
    :type arch: str
    :param verbose: verbose output flag, defaults to `False`
    :type verbose: bool, optional
    :param internet_check: indicates if OSACA should try to look up the src/dst distribution in the internet, defaults to False
    :type internet_check: boolean, optional
    :param output_file: output stream specifying where to write output, defaults to :class:`sys.stdout`
    :type output_file: stream, optional

    """
    # load arch machine model
    arch_mm = MachineModel(arch=arch)
    data = arch_mm['instruction_forms']
    # load isa machine model
    isa = arch_mm.get_ISA()
    isa_mm = MachineModel(arch='isa/{}'.format(isa))
    num_of_instr = len(data)

    # check arch DB entries
    (
        missing_throughput,
        missing_latency,
        missing_port_pressure,
        suspicious_instructions,
        duplicate_instr_arch,
    ) = _check_sanity_arch_db(arch_mm, isa_mm, internet_check=internet_check)
    # check ISA DB entries
    duplicate_instr_isa, only_in_isa = _check_sanity_isa_db(arch_mm, isa_mm)

    report = _get_sanity_report(
        num_of_instr,
        missing_throughput,
        missing_latency,
        missing_port_pressure,
        suspicious_instructions,
        duplicate_instr_arch,
        duplicate_instr_isa,
        only_in_isa,
        verbose=verbose,
        colors=True if output_file == sys.stdout else False,
    )
    print(report, file=output_file)


def import_benchmark_output(arch, bench_type, filepath, output=sys.stdout):
    """
    Import benchmark results from micro-benchmarks.

    :param arch: target architecture key
    :type arch: str
    :param bench_type: key for defining type of benchmark output
    :type bench_type: str
    :param filepath: filepath to the output file
    :type filepath: str
    :param output: output stream to dump, defaults to sys.stdout
    :type output: stream
    """
    supported_bench_outputs = ['ibench', 'asmbench']
    assert os.path.exists(filepath)
    if bench_type not in supported_bench_outputs:
        raise ValueError('Benchmark type is not supported.')
    with open(filepath, 'r') as f:
        input_data = f.readlines()
    db_entries = None
    mm = MachineModel(arch)
    if bench_type == 'ibench':
        db_entries = _get_ibench_output(input_data, mm.get_ISA())
    elif bench_type == 'asmbench':
        db_entries = _get_asmbench_output(input_data, mm.get_ISA())
    # write entries to DB
    for entry in db_entries:
        mm.set_instruction_entry(db_entries[entry])
    if output is None:
        print(mm.dump())
    else:
        mm.dump(stream=output)


##################
# HELPERS IBENCH #
##################


def _get_asmbench_output(input_data, isa):
    """
    Parse asmbench output in the format

    1 MNEMONIC[-OP1[_OP2][...]]
    2 Latency: X cycles
    3 Throughput: Y cycles
    4

    and creates per 4 lines in the input_data one entry in the database.

    :param str input_data: content of asmbench output file
    :param str isa: ISA of target architecture (x86, AArch64, ...)
    : return: dictionary with all new db_entries
    """
    db_entries = {}
    for i in range(0, len(input_data), 4):
        if input_data[i + 3].strip() != '':
            print('asmbench output not in the correct format! Format must be: ', file=sys.stderr)
            print(
                '-------------\nMNEMONIC[-OP1[_OP2][...]]\nLatency: X cycles\n'
                'Throughput: Y cycles\n\n-------------',
                file=sys.stderr,
            )
            print(
                'Entry {} and all further entries won\'t be added.'.format((i / 4) + 1),
                file=sys.stderr,
            )
            break
        else:
            i_form = input_data[i].strip()
            mnemonic = i_form.split('-')[0]
            operands = i_form.split('-')[1].split('_')
            operands = [_create_db_operand(op, isa) for op in operands]
            entry = {
                'name': mnemonic,
                'operands': operands,
                'throughput': _validate_measurement(float(input_data[i + 2].split()[1]), 'tp'),
                'latency': _validate_measurement(float(input_data[i + 1].split()[1]), 'lt'),
                'port_pressure': None,
            }
            if not entry['throughput'] or not entry['latency']:
                warnings.warn(
                    'Your measurement for {} looks suspicious'.format(i_form)
                    + ' and was not added. Please inspect your benchmark.'
                )
            db_entries[i_form] = entry
    return db_entries


def _get_ibench_output(input_data, isa):
    """Parse the standard output of ibench and add instructions to DB."""
    db_entries = {}
    for line in input_data:
        if 'Using frequency' in line or len(line) == 0:
            continue
        instruction = line.split(':')[0]
        key = '-'.join(instruction.split('-')[:2])
        if key in db_entries:
            # add only TP/LT value
            entry = db_entries[key]
        else:
            mnemonic = instruction.split('-')[0]
            operands = instruction.split('-')[1].split('_')
            operands = [_create_db_operand(op, isa) for op in operands]
            entry = {
                'name': mnemonic,
                'operands': operands,
                'throughput': None,
                'latency': None,
                'port_pressure': None,
            }
        if 'TP' in instruction:
            entry['throughput'] = _validate_measurement(float(line.split()[1]), 'tp')
            if not entry['throughput']:
                warnings.warn(
                    'Your THROUGHPUT measurement for {} looks suspicious'.format(key)
                    + ' and was not added. Please inspect your benchmark.'
                )
        elif 'LT' in instruction:
            entry['latency'] = _validate_measurement(float(line.split()[1]), 'lt')
            if not entry['latency']:
                warnings.warn(
                    'Your LATENCY measurement for {} looks suspicious'.format(key)
                    + ' and was not added. Please inspect your benchmark.'
                )
        db_entries[key] = entry
    return db_entries


def _validate_measurement(measurement, mode):
    """
    Check if latency has a maximum deviation of 0.05% and throughput is a reciprocal of a
    an integer number.
    """
    if mode == 'lt':
        if (
            math.floor(measurement) * 1.05 >= measurement
            or math.ceil(measurement) * 0.95 <= measurement
        ):
            # Value is probably correct, so round it to the estimated value
            return float(round(measurement))
        # Check reciprocal only if it is a throughput value
    elif mode == 'tp':
        reciprocals = [1 / x for x in range(1, 11)]
        for reci in reciprocals:
            if reci * 0.95 <= measurement <= reci * 1.05:
                # Value is probably correct, so round it to the estimated value
                return round(reci, 5)
    # No value close to an integer or its reciprocal found, we assume the
    # measurement is incorrect
    return None


def _create_db_operand(operand, isa):
    """Get DB operand by input string and ISA."""
    if isa == 'aarch64':
        return _create_db_operand_aarch64(operand)
    elif isa == 'x86':
        return _create_db_operand_x86(operand)


def _create_db_operand_aarch64(operand):
    """Get DB operand for AArch64 by operand string."""
    if operand == 'i':
        return {'class': 'immediate', 'imd': 'int'}
    elif operand in 'wxbhsdq':
        return {'class': 'register', 'prefix': operand}
    elif operand.startswith('v'):
        return {
            'class': 'register',
            'prefix': 'v',
            'shape': operand[1:2] if operand[1:2] != '' else 'd',
        }
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


def _create_db_operand_x86(operand):
    """Get DB operand for AArch64 by operand string."""
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


########################
# HELPERS SANITY CHECK #
########################


def _scrape_from_felixcloutier(mnemonic):
    """Scrape src/dst information from felixcloutier website and return information for user."""
    import requests

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print(
            'Module BeautifulSoup not installed. Fetching instruction form information '
            'online requires BeautifulSoup.\nUse \'pip install bs4\' for installation.',
            file=sys.stderr,
        )
        sys.exit(1)

    index = 'https://www.felixcloutier.com/x86/index.html'
    base_url = 'https://www.felixcloutier.com/x86/'
    url = base_url + mnemonic.lower()

    suspicious = True
    operands = []

    # GET website
    r = requests.get(url=url)
    if r.status_code == 200:
        # Found result
        operand_enc = BeautifulSoup(r.text, 'html.parser').find(
            'h2', attrs={'id': 'instruction-operand-encoding'}
        )
        if operand_enc:
            # operand encoding found, otherwise, no need to mark as suspicous
            table = operand_enc.findNextSibling()
            operands = _get_src_dst_from_table(table)
    elif r.status_code == 404:
        # Check for alternative href
        index = BeautifulSoup(requests.get(url=index).text, 'html.parser')
        alternatives = [ref for ref in index.findAll('a') if ref.text == mnemonic.upper()]
        if len(alternatives) > 0:
            # alternative(s) found, take first one
            url = base_url + alternatives[0].attrs['href'][2:]
            operand_enc = BeautifulSoup(requests.get(url=url).text, 'html.parser').find(
                'h2', attrs={'id': 'instruction-operand-encoding'}
            )
            if operand_enc:
                # operand encoding found, otherwise, no need to mark as suspicous
                table = (
                    operand_enc.findNextSibling()
                )
                operands = _get_src_dst_from_table(table)
    if operands:
        # Found src/dst assignment for NUM_OPERANDS
        if not any(['r' in x and 'w' in x for x in operands]):
            suspicious = False
    return (suspicious, ' '.join(operands))


def _get_src_dst_from_table(table, num_operands=2):
    """Prettify bs4 table object to string for user"""
    # Parse table
    header = [''.join(x.string.lower().split()) for x in table.find('tr').findAll('td')]
    data = table.findAll('tr')[1:]
    data_dict = OrderedDict()
    for i, row in enumerate(data):
        data_dict[i] = {}
        for j, col in enumerate(row.findAll('td')):
            if col.string != 'NA':
                data_dict[i][header[j]] = col.string
    # Get only the instruction forms with 2 operands
    num_ops = [_get_number_of_operands(row) for _, row in data_dict.items()]
    if num_operands in num_ops:
        row = data_dict[num_ops.index(num_operands)]
        reads_writes = []
        for i in range(1, num_operands + 1):
            m = re.search(r'(\([^\(\)]+\))', row['operand{}'.format(i)])
            if not m:
                # no parentheses (probably immediate operand), assume READ
                reads_writes.append('(r)')
                continue
            reads_writes.append(''.join(m.group(0).split()))
        # reverse reads_writes for AT&T syntax
        reads_writes.reverse()
        return reads_writes
    return []


def _get_number_of_operands(data_dict_row):
    """Return the number of `Operand [X]` attributes in row"""
    num = 0
    for i in range(1, 5):
        if 'operand{}'.format(i) in [''.join(x.split()).lower() for x in data_dict_row]:
            num += 1
    return num


def _check_sanity_arch_db(arch_mm, isa_mm, internet_check=True):
    """Do sanity check for ArchDB by given ISA."""
    # prefixes of instruction forms which we assume to have non-default operands
    suspicious_prefixes_x86 = ['vfm', 'fm']
    suspicious_prefixes_arm = ['fml', 'ldp', 'stp', 'str']
    # already known to be default-operand instruction forms with 2 operands
    if arch_mm.get_ISA().lower() == 'aarch64':
        suspicious_prefixes = suspicious_prefixes_arm
    if arch_mm.get_ISA().lower() == 'x86':
        suspicious_prefixes = suspicious_prefixes_x86

    # returned lists
    missing_throughput = []
    missing_latency = []
    missing_port_pressure = []
    suspicious_instructions = []
    duplicate_instr_arch = []
    duplicate_strings = []

    for instr_form in arch_mm['instruction_forms']:
        # check value in DB entry
        if instr_form['throughput'] is None:
            missing_throughput.append(instr_form)
        if instr_form['latency'] is None:
            missing_latency.append(instr_form)
        if instr_form['port_pressure'] is None:
            missing_port_pressure.append(instr_form)
        # check entry against ISA DB
        for prefix in suspicious_prefixes:
            if instr_form['name'].lower().startswith(prefix):
                # check if instruction in ISA DB
                if isa_mm.get_instruction(instr_form['name'], instr_form['operands']) is None:
                    # if not, mark them as suspicious and print it on the screen
                    suspicious_instructions.append(instr_form)
        # instr forms with less than 3 operands might need an ISA DB entry due to src_reg operands
        if (
            len(instr_form['operands']) < 3
            and len(instr_form['operands']) > 1
            and 'mov' not in instr_form['name'].lower()
            and not instr_form['name'].lower().startswith('j')
            and instr_form not in suspicious_instructions
            and isa_mm.get_instruction(instr_form['name'], instr_form['operands']) is None
        ):
            # validate with data from internet if connected flag is set
            if internet_check:
                is_susp, info_string = _scrape_from_felixcloutier(instr_form['name'])
                if is_susp:
                    instr_form['note'] = info_string
                    suspicious_instructions.append(instr_form)
            else:
                suspicious_instructions.append(instr_form)
        # check for duplicates in DB
        if arch_mm._check_for_duplicate(instr_form['name'], instr_form['operands']):
            duplicate_instr_arch.append(instr_form)
    # every entry exists twice --> uniquify
    tmp_list = []
    for _ in range(0, len(duplicate_instr_arch)):
        tmp = duplicate_instr_arch.pop()
        if _get_full_instruction_name(tmp).lower() not in duplicate_strings:
            duplicate_strings.append(_get_full_instruction_name(tmp).lower())
            tmp_list.append(tmp)
    duplicate_instr_arch = tmp_list
    return (
        missing_throughput,
        missing_latency,
        missing_port_pressure,
        suspicious_instructions,
        duplicate_instr_arch,
    )


def _check_sanity_isa_db(arch_mm, isa_mm):
    """Do sanity check for an ISA DB."""
    # returned lists
    duplicate_instr_isa = []
    only_in_isa = []

    for instr_form in isa_mm['instruction_forms']:
        # check if instr is missing in arch DB
        if arch_mm.get_instruction(instr_form['name'], instr_form['operands']) is None:
            only_in_isa.append(instr_form)
        # check for duplicates
        if isa_mm._check_for_duplicate(instr_form['name'], instr_form['operands']):
            duplicate_instr_isa.append(instr_form)
    # every entry exists twice --> uniquify
    tmp_list = []
    for i in range(0, len(duplicate_instr_isa)):
        tmp = duplicate_instr_isa.pop()
        if tmp not in duplicate_instr_isa:
            tmp_list.append(tmp)
    duplicate_instr_isa = tmp_list

    return duplicate_instr_isa, only_in_isa


def _get_sanity_report(
    total, m_tp, m_l, m_pp, suspic_instr, dup_arch, dup_isa, only_isa, verbose=False, colors=False
):
    """Get sanity summary report."""
    s = ''
    # non-verbose summary
    s += 'SUMMARY\n----------------------\n'
    s += '{}% ({}/{}) of instruction forms have no throughput value.\n'.format(
        round(100 * len(m_tp) / total), len(m_tp), total
    )
    s += '{}% ({}/{}) of instruction forms have no latency value.\n'.format(
        round(100 * len(m_l) / total), len(m_l), total
    )
    s += '{}% ({}/{}) of instruction forms have no port pressure assignment.\n'.format(
        round(100 * len(m_pp) / total), len(m_pp), total
    )
    s += '{}% ({}/{}) of instruction forms might miss an ISA DB entry.\n'.format(
        round(100 * len(suspic_instr) / total), len(suspic_instr), total
    )
    s += '{} duplicate instruction forms in uarch DB.\n'.format(len(dup_arch))
    s += '{} duplicate instruction forms in ISA DB.\n'.format(len(dup_isa))
    s += (
        '{} instruction forms in ISA DB are not referenced by instruction '.format(len(only_isa))
        + 'forms in uarch DB.\n'
    )
    s += '----------------------\n'
    # verbose version
    if verbose:
        s += _get_sanity_report_verbose(
            total, m_tp, m_l, m_pp, suspic_instr, dup_arch, dup_isa, only_isa, colors=colors
        )
    return s


def _get_sanity_report_verbose(
    total, m_tp, m_l, m_pp, suspic_instr, dup_arch, dup_isa, only_isa, colors=False
):
    """Get the verbose part of the sanity report with all missing instruction forms."""
    BRIGHT_CYAN = '\033[1;36;1m' if colors else ''
    BRIGHT_BLUE = '\033[1;34;1m' if colors else ''
    BRIGHT_RED = '\033[1;31;1m' if colors else ''
    BRIGHT_MAGENTA = '\033[1;35;1m' if colors else ''
    BRIGHT_YELLOW = '\033[1;33;1m' if colors else ''
    CYAN = '\033[36m' if colors else ''
    YELLOW = '\033[33m' if colors else ''
    WHITE = '\033[0m' if colors else ''

    s = ''
    s += 'Instruction forms without throughput value:\n' if len(m_tp) != 0 else ''
    for instr_form in sorted(m_tp, key=lambda i: i['name']):
        s += '{}{}{}\n'.format(BRIGHT_BLUE, _get_full_instruction_name(instr_form), WHITE)
    s += 'Instruction forms without latency value:\n' if len(m_l) != 0 else ''
    for instr_form in sorted(m_l, key=lambda i: i['name']):
        s += '{}{}{}\n'.format(BRIGHT_RED, _get_full_instruction_name(instr_form), WHITE)
    s += 'Instruction forms without port pressure assignment:\n' if len(m_pp) != 0 else ''
    for instr_form in sorted(m_pp, key=lambda i: i['name']):
        s += '{}{}{}\n'.format(BRIGHT_MAGENTA, _get_full_instruction_name(instr_form), WHITE)
    s += 'Instruction forms which might miss an ISA DB entry:\n' if len(suspic_instr) != 0 else ''
    for instr_form in sorted(suspic_instr, key=lambda i: i['name']):
        s += '{}{}{}{}\n'.format(
            BRIGHT_CYAN,
            _get_full_instruction_name(instr_form),
            ' -- ' + instr_form['note'] if 'note' in instr_form else '',
            WHITE,
        )
    s += 'Duplicate instruction forms in uarch DB:\n' if len(dup_arch) != 0 else ''
    for instr_form in sorted(dup_arch, key=lambda i: i['name']):
        s += '{}{}{}\n'.format(YELLOW, _get_full_instruction_name(instr_form), WHITE)
    s += 'Duplicate instruction forms in ISA DB:\n' if len(dup_isa) != 0 else ''
    for instr_form in sorted(dup_isa, key=lambda i: i['name']):
        s += '{}{}{}\n'.format(BRIGHT_YELLOW, _get_full_instruction_name(instr_form), WHITE)
    s += (
        'Instruction forms existing in ISA DB but not in uarch DB:\n' if len(only_isa) != 0 else ''
    )
    for instr_form in sorted(only_isa, key=lambda i: i['name']):
        s += '{}{}{}\n'.format(CYAN, _get_full_instruction_name(instr_form), WHITE)
    return s


###################
# GENERIC HELPERS #
###################


def _get_full_instruction_name(instruction_form):
    """Get full instruction form name/identifier string out of given instruction form."""
    operands = []
    for op in instruction_form['operands']:
        op_attrs = [
            y + ':' + str(op[y])
            for y in list(filter(lambda x: True if x != 'class' else False, op))
        ]
        operands.append('{}({})'.format(op['class'], ','.join(op_attrs)))
    return '{}  {}'.format(instruction_form['name'], ','.join(operands))


def __represent_none(self, data):
    """Get YAML None representation."""
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'~')


def _create_yaml_object():
    """Create YAML module with None representation."""
    yaml_obj = ruamel.yaml.YAML()
    yaml_obj.representer.add_representer(type(None), __represent_none)
    return yaml_obj


def __dump_data_to_yaml(filepath, data):
    """Dump data to YAML file at given filepath."""
    # first add 'normal' meta data in the right order (no ordered dict yet)
    meta_data = dict(data)
    del meta_data['instruction_forms']
    del meta_data['port_model_scheme']
    with open(filepath, 'w') as f:
        ruamel.yaml.dump(meta_data, f, allow_unicode=True)
    with open(filepath, 'a') as f:
        # now add port model scheme in |-scheme for better readability
        ruamel.yaml.dump(
            {'port_model_scheme': data['port_model_scheme']},
            f,
            allow_unicode=True,
            default_style='|',
        )
        # finally, add instruction forms
        ruamel.yaml.dump({'instruction_forms': data['instruction_forms']}, f, allow_unicode=True)
