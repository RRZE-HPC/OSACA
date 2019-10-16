#!/usr/bin/env python3

import math
import os
import warnings

import ruamel.yaml

from osaca.semantics import MachineModel


def sanity_check(arch: str, verbose=False):
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
        wrong_port,
        suspicious_instructions,
        duplicate_instr_arch,
    ) = _check_sanity_arch_db(arch_mm, isa_mm)
    # check ISA DB entries
    duplicate_instr_isa, only_in_isa = _check_sanity_isa_db(arch_mm, isa_mm)

    _print_sanity_report(
        num_of_instr,
        missing_throughput,
        missing_latency,
        missing_port_pressure,
        wrong_port,
        suspicious_instructions,
        duplicate_instr_arch,
        duplicate_instr_isa,
        only_in_isa,
        verbose=verbose,
    )


def import_benchmark_output(arch, bench_type, filepath):
    supported_bench_outputs = ['ibench', 'asmbench']
    assert os.path.exists(filepath)
    if bench_type not in supported_bench_outputs:
        raise ValueError('Benchmark type is not supported.')
    with open(filepath, 'r') as f:
        input_data = f.readlines()
    db_entries = None
    if bench_type == 'ibench':
        db_entries = _get_ibench_output(input_data)
    elif bench_type == 'asmbench':
        raise NotImplementedError
    # write entries to DB
    mm = MachineModel(arch)
    for entry in db_entries:
        mm.set_instruction_entry(entry)
    with open(filepath, 'w') as f:
        mm.dump(f)

##################
# HELPERS IBENCH #
##################


def _get_ibench_output(input_data):
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
            operands = [_create_db_operand(op) for op in operands]
            entry = {
                'name': mnemonic,
                'operands': operands,
                'throughput': None,
                'latency': None,
                'port_pressure': None,
            }
        if 'TP' in instruction:
            entry['throughput'] = _validate_measurement(float(line.split()[1]), True)
            if not entry['throughput']:
                warnings.warn(
                    'Your THROUGHPUT measurement for {} looks suspicious'.format(key)
                    + ' and was not added. Please inspect your benchmark.'
                )
        elif 'LT' in instruction:
            entry['latency'] = _validate_measurement(float(line.split()[1]), False)
            if not entry['latency']:
                warnings.warn(
                    'Your LATENCY measurement for {} looks suspicious'.format(key)
                    + ' and was not added. Please inspect your benchmark.'
                )
        db_entries[key] = entry
    return db_entries


def _validate_measurement(self, measurement, is_tp):
    if not is_tp:
        if (
            math.floor(measurement) * 1.05 >= measurement
            or math.ceil(measurement) * 0.95 <= measurement
        ):
            # Value is probably correct, so round it to the estimated value
            return float(round(measurement))
        # Check reciprocal only if it is a throughput value
    else:
        reciprocals = [1 / x for x in range(1, 11)]
        for reci in reciprocals:
            if reci * 0.95 <= measurement <= reci * 1.05:
                # Value is probably correct, so round it to the estimated value
                return round(reci, 5)
    # No value close to an integer or its reciprocal found, we assume the
    # measurement is incorrect
    return None


def _create_db_operand(self, operand):
    if self.isa == 'aarch64':
        return self._create_db_operand_aarch64(operand)
    elif self.isa == 'x86':
        return self._create_db_operand_x86(operand)


def _create_db_operand_aarch64(self, operand):
    if operand == 'i':
        return {'class': 'immediate', 'imd': 'int'}
    elif operand in 'wxbhsdq':
        return {'class': 'register', 'prefix': operand}
    elif operand.startswith('v'):
        return {'class': 'register', 'prefix': 'v', 'shape': operand[1:2]}
    elif operand.startswith('m'):
        return {
            'class': 'memory',
            'base': 'gpr' if 'b' in operand else None,
            'offset': 'imd' if 'o' in operand else None,
            'index': 'gpr' if 'i' in operand else None,
            'scale': 8 if 's' in operand else 1,
            'pre-indexed': True if 'r' in operand else False,
            'post-indexed': True if 'p' in operand else False,
        }
    else:
        raise ValueError('Parameter {} is not a valid operand code'.format(operand))


def _create_db_operand_x86(self, operand):
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


def _check_sanity_arch_db(arch_mm, isa_mm):
    suspicious_prefixes_x86 = ['vfm', 'fm']
    suspicious_prefixes_arm = ['fml', 'ldp', 'stp', 'str']
    if arch_mm.get_ISA().lower() == 'aarch64':
        suspicious_prefixes = suspicious_prefixes_arm
    if arch_mm.get_ISA().lower() == 'x86':
        suspicious_prefixes = suspicious_prefixes_x86

    # returned lists
    missing_throughput = []
    missing_latency = []
    missing_port_pressure = []
    wrong_port = []
    suspicious_instructions = []
    duplicate_instr_arch = []

    for instr_form in arch_mm['instruction_forms']:
        # check value in DB entry
        if instr_form['throughput'] is None:
            missing_throughput.append(instr_form)
        if instr_form['latency'] is None:
            missing_latency.append(instr_form)
        if instr_form['port_pressure'] is None:
            missing_port_pressure.append(instr_form)
        else:
            if _check_for_wrong_port(arch_mm['ports'], instr_form):
                wrong_port.append(instr_form)
        # check entry against ISA DB
        for prefix in suspicious_prefixes:
            if instr_form['name'].startswith(prefix):
                # check if instruction in ISA DB
                if isa_mm.get_instruction(instr_form['name'], instr_form['operands']) is None:
                    # if not, mark them as suspicious and print it on the screen
                    suspicious_instructions.append(instr_form)
        # check for duplicates in DB
        if arch_mm._check_for_duplicate(instr_form['name'], instr_form['operands']):
            duplicate_instr_arch.append(instr_form)
    # every entry exists twice --> uniquify
    tmp_list = []
    for i in range(0, len(duplicate_instr_arch)):
        tmp = duplicate_instr_arch.pop()
        if tmp not in duplicate_instr_arch:
            tmp_list.append(tmp)
    duplicate_instr_arch = tmp_list
    return (
        missing_throughput,
        missing_latency,
        missing_port_pressure,
        wrong_port,
        suspicious_instructions,
        duplicate_instr_arch,
    )


def _check_for_wrong_port(port_list, instr_form):
    for cycles, ports in instr_form['port_pressure']:
        for p in ports:
            if p not in port_list:
                return False
    return True


def _check_sanity_isa_db(arch_mm, isa_mm):
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


def _print_sanity_report(
    total, m_tp, m_l, m_pp, wrong_pp, suspic_instr, dup_arch, dup_isa, only_isa, verbose=False
):
    # non-verbose summary
    print('SUMMARY\n----------------------')
    print(
        '{}% ({}/{}) of instruction forms have no throughput value.'.format(
            round(100 * len(m_tp) / total), len(m_tp), total
        )
    )
    print(
        '{}% ({}/{}) of instruction forms have no latency value.'.format(
            round(100 * len(m_l) / total), len(m_l), total
        )
    )
    print(
        '{}% ({}/{}) of instruction forms have no port pressure assignment.'.format(
            round(100 * len(m_pp) / total), len(m_pp), total
        )
    )
    print(
        '{}% ({}/{}) of instruction forms have an invalid port identifier.'.format(
            round(100 * len(wrong_pp) / total), len(wrong_pp), total
        )
    )
    print(
        '{}% ({}/{}) of instruction forms might miss an ISA DB entry.'.format(
            round(100 * len(suspic_instr) / total), len(suspic_instr), total
        )
    )
    print('{} duplicate instruction forms in uarch DB.'.format(len(dup_arch)))
    print('{} duplicate instruction forms in ISA DB.'.format(len(dup_isa)))
    print(
        '{} instruction forms in ISA DB are not referenced by instruction '.format(len(only_isa))
        + 'forms in uarch DB.'
    )
    print('----------------------\n')
    # verbose version
    if verbose:
        _print_sanity_report_verbose(
            total, m_tp, m_l, m_pp, wrong_pp, suspic_instr, dup_arch, dup_isa, only_isa
        )


def _print_sanity_report_verbose(
    total, m_tp, m_l, m_pp, wrong_pp, suspic_instr, dup_arch, dup_isa, only_isa
):
    BRIGHT_CYAN = '\033[1;36;1m'
    BRIGHT_BLUE = '\033[1;34;1m'
    BRIGHT_RED = '\033[1;31;1m'
    BRIGHT_MAGENTA = '\033[1;35;1m'
    BRIGHT_YELLOW = '\033[1;33;1m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    WHITE = '\033[0m'

    print('Instruction forms without throughput value:\n' if len(m_tp) != 0 else '', end='')
    for instr_form in m_tp:
        print('{}{}{}'.format(BRIGHT_BLUE, _get_full_instruction_name(instr_form), WHITE))
    print('Instruction forms without latency value:\n' if len(m_l) != 0 else '', end='')
    for instr_form in m_l:
        print('{}{}{}'.format(BRIGHT_RED, _get_full_instruction_name(instr_form), WHITE))
    print(
        'Instruction forms without port pressure assignment:\n' if len(m_pp) != 0 else '', end=''
    )
    for instr_form in m_pp:
        print('{}{}{}'.format(BRIGHT_MAGENTA, _get_full_instruction_name(instr_form), WHITE))
    print(
        'Instruction forms with invalid port identifiers in port pressure:\n'
        if len(wrong_pp) != 0
        else '',
        end='',
    )
    for instr_form in wrong_pp:
        print('{}{}{}'.format(BRIGHT_MAGENTA, _get_full_instruction_name(instr_form), WHITE))
    print(
        'Instruction forms which might miss an ISA DB entry:\n' if len(suspic_instr) != 0 else '',
        end='',
    )
    for instr_form in suspic_instr:
        print('{}{}{}'.format(BRIGHT_CYAN, _get_full_instruction_name(instr_form), WHITE))
    print('Duplicate instruction forms in uarch DB:\n' if len(dup_arch) != 0 else '', end='')
    for instr_form in dup_arch:
        print('{}{}{}'.format(YELLOW, _get_full_instruction_name(instr_form), WHITE))
    print('Duplicate instruction forms in ISA DB:\n' if len(dup_isa) != 0 else '', end='')
    for instr_form in dup_isa:
        print('{}{}{}'.format(BRIGHT_YELLOW, _get_full_instruction_name(instr_form), WHITE))
    print(
        'Instruction forms existing in ISA DB but not in uarch DB:\n'
        if len(only_isa) != 0
        else '',
        end='',
    )
    for instr_form in only_isa:
        print('{}{}{}'.format(CYAN, _get_full_instruction_name(instr_form), WHITE))


###################
# GENERIC HELPERS #
###################


def _get_full_instruction_name(instruction_form):
    operands = []
    for op in instruction_form['operands']:
        op_attrs = [
            y + ':' + str(op[y])
            for y in list(filter(lambda x: True if x != 'class' else False, op))
        ]
        operands.append('{}({})'.format(op['class'], ','.join(op_attrs)))
    return '{}  {}'.format(instruction_form['name'], ','.join(operands))


def __represent_none(self, data):
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'~')


def _create_yaml_object():
    yaml_obj = ruamel.yaml.YAML()
    yaml_obj.representer.add_representer(type(None), __represent_none)
    return yaml_obj


def __dump_data_to_yaml(filepath, data):
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
