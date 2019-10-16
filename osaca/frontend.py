#!/usr/bin/env python3

import os
import re
from datetime import datetime as dt

from ruamel import yaml

from osaca import utils
from osaca.semantics import INSTR_FLAGS, KernelDG, SemanticsAppender


class Frontend(object):
    def __init__(self, filename='', arch=None, path_to_yaml=None):
        self._filename = filename
        if not arch and not path_to_yaml:
            raise ValueError('Either arch or path_to_yaml required.')
        if arch and path_to_yaml:
            raise ValueError('Only one of arch and path_to_yaml is allowed.')
        self._arch = arch
        if arch:
            self._arch = arch.lower()
            with open(utils.find_file(self._arch + '.yml'), 'r') as f:
                self._data = yaml.load(f, Loader=yaml.Loader)
        elif path_to_yaml:
            with open(path_to_yaml, 'r') as f:
                self._data = yaml.load(f, Loader=yaml.Loader)

    def _is_comment(self, instruction_form):
        return instruction_form['comment'] is not None and instruction_form['instruction'] is None

    def print_throughput_analysis(self, kernel, show_lineno=False, show_cmnts=True):
        lineno_filler = '     ' if show_lineno else ''
        port_len = self._get_max_port_len(kernel)
        separator = '-' * sum([x + 3 for x in port_len]) + '-'
        separator += '--' + len(str(kernel[-1]['line_number'])) * '-' if show_lineno else ''
        col_sep = '|'
        sep_list = self._get_separator_list(col_sep)
        headline = 'Port pressure in cycles'
        headline_str = '{{:^{}}}'.format(len(separator))

        print('\n\nThroughput Analysis Report\n' + '--------------------------')
        print(headline_str.format(headline))
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
        tp_sum = SemanticsAppender.get_throughput_sum(kernel)
        print(lineno_filler + self._get_port_pressure(tp_sum, port_len, ' '))

    def _get_separator_list(self, separator, separator_2=' '):
        separator_list = []
        for i in range(len(self._data['ports']) - 1):
            match_1 = re.search(r'\d+', self._data['ports'][i])
            match_2 = re.search(r'\d+', self._data['ports'][i + 1])
            if match_1 is not None and match_2 is not None and match_1.group() == match_2.group():
                separator_list.append(separator_2)
            else:
                separator_list.append(separator)
        separator_list.append(separator)
        return separator_list

    def _get_flag_symbols(self, flag_obj):
        string_result = ''
        string_result += '*' if INSTR_FLAGS.NOT_BOUND in flag_obj else ''
        string_result += 'X' if INSTR_FLAGS.TP_UNKWN in flag_obj else ''
        string_result += 'P' if INSTR_FLAGS.HIDDEN_LD in flag_obj else ''
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
        print('\n\nLatency Analysis Report\n' + '-----------------------')
        for instruction_form in cp_kernel:
            print(
                '{:4d} {} {:4.1f} {}{}{} {}'.format(
                    instruction_form['line_number'],
                    separator,
                    instruction_form['latency_cp'],
                    separator,
                    'X' if INSTR_FLAGS.LT_UNKWN in instruction_form['flags'] else ' ',
                    separator,
                    instruction_form['line'],
                )
            )
        print(
            '\n{:4} {} {:4.1f}'.format(
                ' ' * max([len(str(instr_form['line_number'])) for instr_form in cp_kernel]),
                ' ' * len(separator),
                sum([instr_form['latency_cp'] for instr_form in cp_kernel]),
            )
        )

    def print_loopcarried_dependencies(self, dep_dict, separator='|'):
        print(
            '\n\nLoop-Carried Dependencies Analysis Report\n'
            + '-----------------------------------------'
        )
        # TODO find a way to overcome padding for different tab-lengths
        for dep in dep_dict:
            print(
                '{:4d} {} {:4.1f} {} {:36}{} {}'.format(
                    dep,
                    separator,
                    sum(
                        [
                            instr_form['latency_lcd']
                            for instr_form in dep_dict[dep]['dependencies']
                        ]
                    ),
                    separator,
                    dep_dict[dep]['root']['line'],
                    separator,
                    [node['line_number'] for node in dep_dict[dep]['dependencies']],
                )
            )

    def _print_header_report(self):
        version = 'v0.3'
        adjust = 20
        header = ''
        header += 'Open Source Architecture Code Analyzer (OSACA) - {}\n'.format(version)
        header += 'Analyzed file:'.ljust(adjust) + '{}\n'.format(self._filename)
        header += 'Architecture:'.ljust(adjust) + '{}\n'.format(self._arch)
        header += 'Timestamp:'.ljust(adjust) + '{}\n'.format(
            dt.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
        print(header)

    def _print_symbol_map(self):
        symbol_dict = {
            INSTR_FLAGS.NOT_BOUND: 'Instruction micro-ops not bound to a port',
            INSTR_FLAGS.TP_UNKWN: 'No throughput/latency information for this instruction in '
            + 'data file',
            INSTR_FLAGS.HIDDEN_LD: 'Throughput of LOAD operation can be hidden behind a past '
            + 'or future STORE instruction',
        }
        symbol_map = ''
        for flag in sorted(symbol_dict.keys()):
            symbol_map += ' {} - {}\n'.format(self._get_flag_symbols([flag]), symbol_dict[flag])

        print(symbol_map, end='')

    def _print_port_binding_summary(self):
        raise NotImplementedError

    def print_full_analysis(self, kernel, kernel_dg: KernelDG, verbose=False):
        self._print_header_report()
        self._print_symbol_map()
        self.print_throughput_analysis(kernel, show_lineno=True)
        self.print_latency_analysis(kernel_dg.get_critical_path())
        self.print_loopcarried_dependencies(kernel_dg.get_loopcarried_dependencies())
