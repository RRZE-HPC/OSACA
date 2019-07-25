#!/usr/bin/env python3

import os
import re
from functools import reduce

from ruamel import yaml

from osaca.semantics import INSTR_FLAGS


class Frontend(object):
    def __init__(self, arch=None, path_to_yaml=None):
        if not arch and not path_to_yaml:
            raise ValueError('Either arch or path_to_yaml required.')
        if arch and path_to_yaml:
            raise ValueError('Only one of arch and path_to_yaml is allowed.')
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
                with open(path_to_yaml, 'r') as f:
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

    def _is_comment(self, instruction_form):
        return instruction_form['comment'] is not None and instruction_form['instruction'] is None

    def print_throughput_analysis(self, kernel, show_lineno=False, show_cmnts=True):
        print()
        lineno_filler = '     ' if show_lineno else ''
        port_len = self._get_max_port_len(kernel)
        separator = '-' * sum([x + 3 for x in port_len]) + '-'
        separator += '--' + len(str(kernel[-1]['line_number'])) * '-' if show_lineno else ''
        col_sep = '|'
        sep_list = self._get_separator_list(col_sep)
        print(lineno_filler + self._get_port_number_line(port_len))
        print(separator)
        for instruction_form in kernel:
            line = '{:4d} {} {} {}'.format(
                instruction_form['line_number'],
                self._get_port_pressure(instruction_form['port_pressure'], port_len, sep_list),
                self._get_flag_symbols(instruction_form['flags'])
                if instruction_form['instruction'] is not None
                else ' ',
                instruction_form['line'].strip(),
            )
            line = line if show_lineno else col_sep + col_sep.join(line.split(col_sep)[1:])
            if show_cmnts is False and self._is_comment(instruction_form):
                continue
            print(line)
        print()
        tp_sum = self._get_throughput_sum(kernel)
        print(lineno_filler + self._get_port_pressure(tp_sum, port_len, ' '))

    def _get_throughput_sum(self, kernel):
        tp_sum = reduce(
            (lambda x, y: [sum(z) for z in zip(x, y)]),
            [instr['port_pressure'] for instr in kernel],
        )
        tp_sum = [round(x, 2) for x in tp_sum]
        return tp_sum

    def _get_separator_list(self, separator, separator_2=' '):
        separator_list = []
        for i in range(len(self._data['ports']) - 1):
            if (
                re.search(r'\d+', self._data['ports'][i]).group()
                == re.search(r'\d+', self._data['ports'][i + 1]).group()
            ):
                separator_list.append(separator_2)
            else:
                separator_list.append(separator)
        separator_list.append(separator)
        return separator_list

    def _get_flag_symbols(self, flag_obj):
        string_result = ''
        string_result += '*' if INSTR_FLAGS.NOT_BOUND in flag_obj else ''
        string_result += 'X' if INSTR_FLAGS.TP_UNKWN in flag_obj else ''
        # TODO add other flags
        string_result += ' ' if len(string_result) == 0 else ''
        return string_result

    def _get_port_pressure(self, ports, port_len, separator='|'):
        if not isinstance(separator, list):
            separator = [separator for x in ports]
        string_result = '{} '.format(separator[-1])
        for i in range(len(ports)):
            if float(ports[i]) == 0.0:
                string_result += port_len[i] * ' ' + ' {} '.format(separator[i])
                continue
            left_len = len(str(float(ports[i])).split('.')[0])
            substr = '{:' + str(left_len) + '.' + str(max(port_len[i] - left_len - 1, 0)) + 'f}'
            string_result += substr.format(ports[i]) + ' {} '.format(separator[i])
        return string_result[:-1]

    def _get_max_port_len(self, kernel):
        port_len = [4 for x in self._data['ports']]
        for instruction_form in kernel:
            for i, port in enumerate(instruction_form['port_pressure']):
                if len('{:.2f}'.format(port)) > port_len[i]:
                    port_len[i] = len('{:.2f}'.format(port))
        return port_len

    def _get_port_number_line(self, port_len, separator='|'):
        string_result = separator
        separator_list = self._get_separator_list(separator, '-')
        for i, length in enumerate(port_len):
            substr = '{:^' + str(length + 2) + 's}'
            string_result += substr.format(self._data['ports'][i]) + separator_list[i]
        return string_result

    def print_latency_analysis(self, cp_kernel, separator='|'):
        print('\n\n------------------------')
        for instruction_form in cp_kernel:
            print(
                '{} {} {} {}{}{} {}'.format(
                    instruction_form['line_number'],
                    separator,
                    instruction_form['latency'],
                    separator,
                    'X' if INSTR_FLAGS.LT_UNKWN in instruction_form['flags'] else ' ',
                    separator,
                    instruction_form['line'],
                )
            )

    def print_list_summary(self):
        raise NotImplementedError

    def _print_header_throughput_report(self):
        raise NotImplementedError

    def _print_port_binding_summary(self):
        raise NotImplementedError
