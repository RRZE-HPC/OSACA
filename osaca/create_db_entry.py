#!/usr/bin/env python3

import os
import sys

from ruamel import yaml


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
    filepath = os.path.join(os.path.expanduser('~/.osaca/data/', arch + '.yml'))
    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        data = yaml.load(f, Loader=yaml.Loader)
    # check parameter of entry
    if 'name' not in entry:
        raise ValueError('No name for instruction specified. No import possible')
    if 'operands' not in entry:
        entry['operands'] = None
    if 'throughput' not in entry:
        entry['throughput'] = None
    if 'latency' not in entry:
        entry['latency'] = None
    if 'port_pressure' not in entry:
        entry['port_pressure'] = None
    data['instruction_forms'].append(entry)
    __dump_data_to_yaml(filepath, data)


def add_entries_to_db(arch: str, entries: list) -> None:
    """Adds entries to the user database in ~/.osaca/data

    Args:
        arch: string representation of the architecture as abbreviation.
            Database for this architecture must already exist.
        entries: :class:`list` of DB entries which will be added. Should consist at best out of
            'name', 'operand(s)' ('register', 'memory', 'immediate', 'identifier', ...),
            'throughput', 'latency', 'port_pressure'.
    """
    # load yaml
    arch = arch.lower()
    filepath = os.path.join(os.path.expanduser('~/.osaca/data/', arch + '.yml'))
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
            entry['operands'] = None
        if 'throughput' not in entry:
            entry['throughput'] = None
        if 'latency' not in entry:
            entry['latency'] = None
        if 'port_pressure' not in entry:
            entry['port_pressure'] = None
        data['instruction_forms'].append(entry)
    __dump_data_to_yaml(filepath, data)


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
