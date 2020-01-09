#!/usr/bin/env python3
"""
Frontend interface for OSACA. Does everything necessary for printing analysis to the terminal.
"""
import re
from datetime import datetime as dt

from osaca.semantics import INSTR_FLAGS, ArchSemantics, KernelDG, MachineModel


class Frontend(object):
    def __init__(self, filename='', arch=None, path_to_yaml=None):
        """
        Constructor method.

        :param filename: path to the analyzed kernel file for documentation, defaults to ''
        :type filename: str, optional
        :param arch: micro-arch code for getting the machine model, defaults to None
        :type arch: str, optional
        :param path_to_yaml: path to the YAML file for getting the machine model, defaults to None
        :type path_to_yaml: str, optional
        """
        self._filename = filename
        if not arch and not path_to_yaml:
            raise ValueError('Either arch or path_to_yaml required.')
        if arch and path_to_yaml:
            raise ValueError('Only one of arch and path_to_yaml is allowed.')
        self._arch = arch
        if arch:
            self._arch = arch.lower()
            self._machine_model = MachineModel(arch=arch, lazy=True)
        elif path_to_yaml:
            self._machine_model = MachineModel(path_to_yaml=path_to_yaml, lazy=True)
            self._arch = self._machine_model.get_arch()

    def _is_comment(self, instruction_form):
        """
        Checks if instruction form is a comment-only line.

        :param instruction_form: instruction form as dict
        :returns: `True` if comment line, `False` otherwise
        """
        return instruction_form['comment'] is not None and instruction_form['instruction'] is None

    def print_throughput_analysis(self, kernel, show_lineno=False, show_cmnts=True):
        """
        Print throughput analysis only.

        :param kernel: Kernel to print throughput analysis for.
        :type kernel: list
        :param show_lineno: flag for showing the line number of instructions, defaults to `False`
        :type show_lineno: bool, optional
        :param show_cmnts: flag for showing comment-only lines in kernel, defaults to `True`
        :type show_cmnts: bool, optional
        """
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
                self._get_port_pressure(
                    instruction_form['port_pressure'], port_len, separator=sep_list
                ),
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
        tp_sum = ArchSemantics.get_throughput_sum(kernel)
        print(lineno_filler + self._get_port_pressure(tp_sum, port_len, separator=' '))

    def print_latency_analysis(self, cp_kernel, separator='|'):
        """
        Print a list-based CP analysis to the terminal.

        :param cp_kernel: loop kernel containing the CP information for each instruction form
        :type cp_kernel: list
        :separator: separator symbol for the columns, defaults to '|'
        :type separator: str, optional
        """
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
        """
        Print a list-based LCD analysis to the terminal.

        :param dep_dict: dictionary with first instruction in LCD as key and the deps as value
        :type dep_dict: dict
        :separator: separator symbol for the columns, defaults to '|'
        :type separator: str, optional
        """
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
                        [instr_form['latency_lcd'] for instr_form in dep_dict[dep]['dependencies']]
                    ),
                    separator,
                    dep_dict[dep]['root']['line'],
                    separator,
                    [node['line_number'] for node in dep_dict[dep]['dependencies']],
                )
            )

    def print_full_analysis(
        self, kernel, kernel_dg: KernelDG, ignore_unknown=False, verbose=False
    ):
        """
        Prints the full analysis report including header, the symbol map, the combined TP/CP/LCD
        view and the list based LCD view.

        :param kernel: kernel to print
        :type kernel: list
        :param kernel_dg: directed graph containing CP and LCD
        :type kernel_dg: :class:`~osaca.semantics.KernelDG`
        :param ignore_unknown: flag for ignore warning if performance data is missing, defaults to
            `False`
        :type ignore_unknown: boolean, optional
        :param verbose: flag for verbosity level, defaults to False
        :type verbose: boolean, optional
        """
        self._print_header_report()
        self._print_symbol_map()
        self.print_combined_view(
            kernel,
            kernel_dg.get_critical_path(),
            kernel_dg.get_loopcarried_dependencies(),
            ignore_unknown,
        )
        self.print_loopcarried_dependencies(kernel_dg.get_loopcarried_dependencies())

    def print_combined_view(
        self, kernel, cp_kernel: KernelDG, dep_dict, ignore_unknown=False, show_cmnts=True
    ):
        """
        Prints the combined view of the kernel including the port pressure (TP), a CP column and a
        LCD column.

        :param kernel: kernel to print
        :type kernel: list
        :param kernel_dg: directed graph containing CP and LCD
        :type kernel_dg: :class:`~osaca.semantics.KernelDG`
        :param dep_dict: dictionary with first instruction in LCD as key and the deps as value
        :type dep_dict: dict
        :param ignore_unknown: flag for showing result despite of missing instructions, defaults to
            `False`
        :type ignore_unknown: bool, optional
        :param show_cmnts: flag for showing comment-only lines in kernel, defaults to `True`
        :type show_cmnts: bool, optional
        """
        print('\n\nCombined Analysis Report\n' + '------------------------')
        lineno_filler = '     '
        port_len = self._get_max_port_len(kernel)
        # Separator for ports
        separator = '-' * sum([x + 3 for x in port_len]) + '-'
        # ... for line numbers
        separator += '--' + len(str(kernel[-1]['line_number'])) * '-'
        col_sep = '|'
        # for LCD/CP column
        separator += '-' * (2 * 6 + len(col_sep)) + '-' * len(col_sep)
        sep_list = self._get_separator_list(col_sep)
        headline = 'Port pressure in cycles'
        headline_str = '{{:^{}}}'.format(len(separator))
        # Prepare CP/LCD variable
        cp_lines = [x['line_number'] for x in cp_kernel]
        sums = {}
        for dep in dep_dict:
            sums[dep] = sum(
                [instr_form['latency_lcd'] for instr_form in dep_dict[dep]['dependencies']]
            )
        lcd_sum = max(sums.values()) if len(sums) > 0 else 0.0
        lcd_lines = []
        if len(dep_dict) > 0:
            longest_lcd = [line_no for line_no in sums if sums[line_no] == lcd_sum][0]
            lcd_lines = [d['line_number'] for d in dep_dict[longest_lcd]['dependencies']]

        print(headline_str.format(headline))
        print(
            lineno_filler
            + self._get_port_number_line(port_len, separator=col_sep)
            + '{}{:^6}{}{:^6}{}'.format(col_sep, 'CP', col_sep, 'LCD', col_sep)
        )
        print(separator)
        for instruction_form in kernel:
            if show_cmnts is False and self._is_comment(instruction_form):
                continue
            line_number = instruction_form['line_number']
            used_ports = [list(uops[1]) for uops in instruction_form['port_uops']]
            used_ports = list(set([p for uops_ports in used_ports for p in uops_ports]))
            line = '{:4d} {}{} {} {}'.format(
                line_number,
                self._get_port_pressure(
                    instruction_form['port_pressure'], port_len, used_ports, sep_list
                ),
                self._get_lcd_cp_ports(
                    instruction_form['line_number'],
                    cp_kernel if line_number in cp_lines else None,
                    dep_dict[longest_lcd] if line_number in lcd_lines else None,
                ),
                self._get_flag_symbols(instruction_form['flags'])
                if instruction_form['instruction'] is not None
                else ' ',
                instruction_form['line'].strip(),
            )
            print(line)
        print()
        # check for unknown instructions and throw warning if called without --ignore-unknown
        if not ignore_unknown and INSTR_FLAGS.TP_UNKWN in [
            flag for instr in kernel for flag in instr['flags']
        ]:
            num_missing = len(
                [instr['flags'] for instr in kernel if INSTR_FLAGS.TP_UNKWN in instr['flags']]
            )
            self._print_missing_instruction_error(num_missing)
        else:
            # lcd_sum already calculated before
            tp_sum = ArchSemantics.get_throughput_sum(kernel)
            cp_sum = sum([x['latency_cp'] for x in cp_kernel])
            print(
                lineno_filler
                + self._get_port_pressure(tp_sum, port_len, separator=' ')
                + ' {:^6} {:^6}'.format(cp_sum, lcd_sum)
            )

    ####################
    # HELPER FUNCTIONS
    ####################

    def _print_missing_instruction_error(self, amount):
        print(
            (
                '------------------ WARNING: The performance data for {} instructions is missing.'
                '------------------\n'
                '                     No final analysis is given. If you want to ignore this\n'
                '                     warning and run the analysis anyway, start osaca with\n'
                '                                       --ignore_unknown flag.\n'
                '--------------------------------------------------------------------------------'
                '----------------{}'
            ).format(amount, '-' * len(str(amount)))
        )

    def _get_separator_list(self, separator, separator_2=' '):
        """Creates column view for seperators in the TP/combined view."""
        separator_list = []
        for i in range(len(self._machine_model.get_ports()) - 1):
            match_1 = re.search(r'\d+', self._machine_model.get_ports()[i])
            match_2 = re.search(r'\d+', self._machine_model.get_ports()[i + 1])
            if match_1 is not None and match_2 is not None and match_1.group() == match_2.group():
                separator_list.append(separator_2)
            else:
                separator_list.append(separator)
        separator_list.append(separator)
        return separator_list

    def _get_flag_symbols(self, flag_obj):
        """Returns flags for a flag object of an instruction"""
        string_result = ''
        string_result += '*' if INSTR_FLAGS.NOT_BOUND in flag_obj else ''
        string_result += 'X' if INSTR_FLAGS.TP_UNKWN in flag_obj else ''
        string_result += 'P' if INSTR_FLAGS.HIDDEN_LD in flag_obj else ''
        # TODO add other flags
        string_result += ' ' if len(string_result) == 0 else ''
        return string_result

    def _get_port_pressure(self, ports, port_len, used_ports=[], separator='|'):
        """Returns line of port pressure for an instruction."""
        if not isinstance(separator, list):
            separator = [separator for x in ports]
        string_result = '{} '.format(separator[-1])
        for i in range(len(ports)):
            if float(ports[i]) == 0.0 and self._machine_model.get_ports()[i] not in used_ports:
                string_result += port_len[i] * ' ' + ' {} '.format(separator[i])
                continue
            left_len = len(str(float(ports[i])).split('.')[0])
            substr = '{:' + str(left_len) + '.' + str(max(port_len[i] - left_len - 1, 0)) + 'f}'
            string_result += substr.format(ports[i]) + ' {} '.format(separator[i])
        return string_result[:-1]

    def _get_node_by_lineno(self, lineno, kernel):
        """Returns instruction form from kernel by its line number."""
        nodes = [instr for instr in kernel if instr['line_number'] == lineno]
        return nodes[0] if len(nodes) > 0 else None

    def _get_lcd_cp_ports(self, line_number, cp_dg, dependency, separator='|'):
        """Returns the CP and LCD line for one instruction."""
        lat_cp = lat_lcd = ''
        if cp_dg:
            lat_cp = float(self._get_node_by_lineno(line_number, cp_dg)['latency_cp'])
        if dependency:
            lat_lcd = float(
                self._get_node_by_lineno(line_number, dependency['dependencies'])['latency_lcd']
            )
        return '{} {:>4} {} {:>4} {}'.format(separator, lat_cp, separator, lat_lcd, separator)

    def _get_max_port_len(self, kernel):
        """Returns the maximal length needed to print all throughputs of the kernel."""
        port_len = [4 for x in self._machine_model.get_ports()]
        for instruction_form in kernel:
            for i, port in enumerate(instruction_form['port_pressure']):
                if len('{:.2f}'.format(port)) > port_len[i]:
                    port_len[i] = len('{:.2f}'.format(port))
        return port_len

    def _get_port_number_line(self, port_len, separator='|'):
        """Returns column view of port identificators of machine_model."""
        string_result = separator
        separator_list = self._get_separator_list(separator, '-')
        for i, length in enumerate(port_len):
            substr = '{:^' + str(length + 2) + 's}'
            string_result += substr.format(self._machine_model.get_ports()[i]) + separator_list[i]
        return string_result

    def _print_header_report(self):
        """Prints header information"""
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
        """Prints instruction flag map."""
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
