#!/usr/bin/env python3

import os
import sys
import warnings

from ruamel import yaml

from osaca.semantics import MachineModel


def add_entry_to_db(arch: str, entry):
    """Adds entry to the user database in ~/.osaca/data

    Args:
        arch: string representation of the architecture as abbreviation.
            Database for this architecture must already exist.
        entry: DB entry which will be added. Should consist at best out of
            'name', 'operand(s)' ('register', 'memory', 'immediate', 'identifier', ...),
            'throughput', 'latency', 'port_pressure'.
    """
    # load yaml
    arch = arch.lower()
    filepath = os.path.join(os.path.expanduser('~/.osaca/data/' + arch + '.yml'))
    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        data = yaml.load(f, Loader=yaml.Loader)
    # check parameter of entry
    if 'name' not in entry:
        raise ValueError('No name for instruction specified. No import possible')
    if 'operands' not in entry:
        entry['operands'] = []
    if 'throughput' not in entry:
        entry['throughput'] = None
    if 'latency' not in entry:
        entry['latency'] = None
    if 'port_pressure' not in entry:
        entry['port_pressure'] = None
    if 'uops' not in entry:
        entry['uops'] = None
    data['instruction_forms'].append(entry)
    __dump_data_to_yaml(filepath, data)


def add_entries_to_db(arch: str, entries: list) -> None:
    """Adds entries to the user database in ~/.osaca/data

    Args:
        arch: string representation of the architecture as abbreviation.
            Database for this architecture must already exist.
        entries: :class:`list` of DB entries which will be added. Should consist at best out of
            'name', 'operand(s)' ('register', 'memory', 'immediate', 'identifier', ...),
            'throughput', 'latency', 'port_pressure', 'uops'.
    """
    # load yaml
    arch = arch.lower()
    filepath = os.path.join(os.path.expanduser('~/.osaca/data/' + arch + '.yml'))
    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        data = yaml.load(f, Loader=yaml.Loader)
    # check parameter of entry and append it to list
    for entry in entries:
        if 'name' not in entry:
            print(
                'No name for instruction \n\t{}\nspecified. No import possible'.format(entry),
                file=sys.stderr,
            )
            # remove entry from list
            entries.remove(entry)
            continue
        if 'operands' not in entry:
            entry['operands'] = []
        if 'throughput' not in entry:
            entry['throughput'] = None
        if 'latency' not in entry:
            entry['latency'] = None
        if 'port_pressure' not in entry:
            entry['port_pressure'] = None
        if 'uops' not in entry:
            entry['uops'] = None
        data['instruction_forms'].append(entry)
    __dump_data_to_yaml(filepath, data)


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
        suspicious_instructions,
        duplicate_instr_arch,
        duplicate_instr_isa,
        only_in_isa,
        verbose=verbose,
    )


def _check_sanity_arch_db(arch_mm, isa_mm):
    suspicious_prefixes_x86 = ['vfm', 'fm']
    suspicious_prefixes_arm = ['fml', 'ldp', 'stp', 'str']
    if arch_mm.get_ISA().lower() == 'aarch64':
        suspicious_prefixes = suspicious_prefixes_arm
    if arch_mm.get_ISA().lower() == 'x86':
        suspicious_prefixes = suspicious_prefixes_x86
    port_num = len(arch_mm['ports'])

    # returned lists
    missing_throughput = []
    missing_latency = []
    missing_port_pressure = []
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
        elif len(instr_form['port_pressure']) != port_num:
            warnings.warn(
                'Invalid number of ports:\n  {}'.format(_get_full_instruction_name(instr_form))
            )
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
        suspicious_instructions,
        duplicate_instr_arch,
    )


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
    total, m_tp, m_l, m_pp, suspic_instr, dup_arch, dup_isa, only_isa, verbose=False
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
            total, m_tp, m_l, m_pp, suspic_instr, dup_arch, dup_isa, only_isa
        )


def _print_sanity_report_verbose(
    total, m_tp, m_l, m_pp, suspic_instr, dup_arch, dup_isa, only_isa
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


def _get_full_instruction_name(instruction_form):
    operands = []
    for op in instruction_form['operands']:
        op_attrs = [
            y + ':' + str(op[y])
            for y in list(filter(lambda x: True if x != 'class' else False, op))
        ]
        operands.append('{}({})'.format(op['class'], ','.join(op_attrs)))
    return '{}  {}'.format(instruction_form['name'], ','.join(operands))


def __dump_data_to_yaml(filepath, data):
    # first add 'normal' meta data in the right order (no ordered dict yet)
    meta_data = dict(data)
    del meta_data['instruction_forms']
    del meta_data['port_model_scheme']
    with open(filepath, 'w') as f:
        yaml.dump(meta_data, f, allow_unicode=True)
    with open(filepath, 'a') as f:
        # now add port model scheme in |-scheme for better readability
        yaml.dump(
            {'port_model_scheme': data['port_model_scheme']},
            f,
            allow_unicode=True,
            default_style='|',
        )
        # finally, add instruction forms
        yaml.dump({'instruction_forms': data['instruction_forms']}, f, allow_unicode=True)
