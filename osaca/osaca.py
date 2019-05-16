#!/usr/bin/env python3

import argparse
import collections
import filecmp
import sys
import os
import io
import re
import subprocess
from datetime import datetime
from pprint import pprint

import pandas as pd
import numpy as np

from osaca.param import Register, MemAddr, Parameter
from osaca.eu_sched import Scheduler
from osaca.testcase import Testcase

#from param import Register, MemAddr, Parameter
#from eu_sched import Scheduler
#from testcase import Testcase


DATA_DIR = os.path.expanduser('~') + '/.osaca/'
MODULE_DATA_DIR = os.path.join((os.path.split(__file__)[0]), 'data')

# Matches every variation of the IACA start marker
IACA_START_MARKER = re.compile(r'\s*movl?[ \t]+\$(?:111|0x6f)[ \t]*,[ \t]*%ebx.*\n\s*'
                               r'(?:\.byte[ \t]+100.*((,[ \t]*103.*((,[ \t]*144)|'
                               r'(\n\s*\.byte[ \t]+144)))|'
                               r'(\n\s*\.byte[ \t]+103.*((,[ \t]*144)|'
                               r'(\n\s*\.byte[ \t]+144))))|(?:fs addr32 )?nop)')
# Matches every variation of the IACA end marker
IACA_END_MARKER = re.compile(r'\s*movl?[ \t]+\$(?:222|0x1f3)[ \t]*,[ \t]*%ebx.*\n\s*'
                             r'(?:\.byte[ \t]+100.*((,[ \t]*103.*((,[ \t]*144)|'
                             r'(\n\s*\.byte[ \t]+144)))|'
                             r'(\n\s*\.byte[ \t]+103.*((,[ \t]*144)|'
                             r'(\n\s*\.byte[ \t]+144))))|(?:fs addr32 )?nop)')


def flatten(l):
    """
    Flatten a nested list of strings.

    Parameters
    ----------
    l : [[...[str]]]
        Nested list of strings

    Returns
    -------
    [str]
        List of strings
    """
    if not l:
        return l
    if isinstance(l[0], list):
        return flatten(l[0]) + flatten(l[1:])
    return l[:1] + flatten(l[1:])


def get_assembly_from_binary(bin_path):
    """
    Disassemble binary with llvm-objdump and transform into a canonical from.

    Replace jump and call target offsets with labels.
    
    :param bin_path: path to binary file to disassemble

    :return assembly string
    """
    asm_lines = subprocess.run(
        ['objdump', '-d', '--no-show-raw-insn', bin_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).stdout.decode('utf-8').split('\n')

    asm = []

    # Separate label, offsets and instructions
    # Store offset with each label (thus iterate in reverse)
    label_offsets = {}
    for l in reversed(asm_lines):
        m = re.match(r'^(?:(?P<label>[0-9a-zA-Z_\.]+):|'
                     r'\s*(?P<offset>[0-9a-fA-F]+):(?:\s*(?P<instr>.*)))$', l)
        if m:
            d = m.groupdict()
            if d['offset'] is not None:
                d['offset'] = int(d['offset'], base=16)
                last_offset = d['offset']
            else:
                label_offsets[d['label']] = last_offset

            # insert at front to preserve order
            asm.insert(0, d)

    # Find all jump locations and replace with labels
    new_labels = {}
    for a in asm:
        if a['instr'] is not None:
            m = re.search(r'[\-]?[0-9a-fA-F]+ <(?P<label>[0-9a-zA-Z_\.]+)'
                          r'(?:\+(?P<offset>0x[0-9a-fA-F]+))?>',
                          a['instr'])
            if m and m.group('label') in label_offsets:
                target = label_offsets[m.group('label')]
                label_name = m.group('label')
                if m.group('offset') is not None:
                    # Need to create new label at target + offset
                    target += int(m.group('offset'), base=16)
                    label_name += '_'+str(m.group('offset'))
                    new_labels[label_name] = target

                # replace reference with new name
                a['instr'] = (a['instr'][:m.start()] +
                              '{}'.format(label_name) +
                              a['instr'][m.end():])

    # Find instruction at target and insert label before
    for label, target in new_labels.items():
        for i, a in enumerate(asm):
            if target == a['offset']:
                break
        asm.insert(i, {'label': label, 'offset': None, 'instr': None})

    # Remove trailing suffixes (lqwb) from instructions
    # FIXME this falsely removed b from jb and potentially others as well
    for a in asm:
        if a['instr'] is not None:
            m = re.match(r'^(?P<instr>[^j][a-z0-9]+)[lqwb](?P<tail>\s+.+|$)', a['instr'])
            if m:
                a['instr'] = m.group('instr') + m.group('tail')

    # Return instructions and labels in canonical assembly
    assembly = ''
    for a in asm:
        if a['label'] is not None:
            assembly += a['label'] + ':\n'
        elif a['instr'] is not None:
            assembly += a['instr'] + '\n'

    # Replace all hexadecimals with decimals
    m = True
    while m:
        m = re.search(r'0x[0-9a-fA-F]+', assembly)
        if m:
            assembly = assembly[:m.start()] + str(int(m.group(0), base=16)) + assembly[m.end():]

    # Remove trailing ",1)" from offsets
    assembly.replace(',1)', ')')

    return assembly


def create_sequences(end=101):
    """
    Create list of integers from 1 to end and list of their reciprocals.

    Parameters
    ----------
    end : int
        End value for list of integers (default 101)

    Returns
    -------
    [int]
        cyc_list of integers
    [float]
        reci_list of floats
    """
    cyc_list = []
    reci_list = []
    for i in range(1, end):
        cyc_list.append(i)
        reci_list.append(1 / i)
    return cyc_list, reci_list


def validate_val(clk_cyc, instr, is_tp, cyc_list, reci_list):
    """
    Validate given clock cycle clk_cyc and return rounded value in case of
    success.

    A succeeded validation means the clock cycle clk_cyc is only 5% higher or
    lower than an integer value from cyc_list or - if clk_cyc is a throughput
    value - 5% higher or lower than a reciprocal from the reci_list.

    Parameters
    ----------
    clk_cyc : float
        Clock cycle to validate
    instr : str
        Instruction for warning output
    is_tp : bool
        True if a throughput value is to check, False for a latency value
    cyc_list : [int]
        Cycle list for validating
    reci_list : [float]
        Reciprocal cycle list for validating

    Returns
    -------
    float
        Clock cycle, either rounded to an integer or its reciprocal or the
        given clk_cyc parameter
    """
    column = 'LT'
    if is_tp:
        column = 'TP'
    for i in range(0, len(cyc_list)):
        if cyc_list[i] * 1.05 > float(clk_cyc) > cyc_list[i] * 0.95:
            # Value is probably correct, so round it to the estimated value
            return cyc_list[i]
        # Check reciprocal only if it is a throughput value
        elif is_tp and reci_list[i] * 1.05 > float(clk_cyc) > reci_list[i] * 0.95:
            # Value is probably correct, so round it to the estimated value
            return reci_list[i]
    # No value close to an integer or its reciprocal found, we assume the
    # measurement is incorrect
    raise ValueError('Your measurement for {} ({}) is probably wrong. '
                     'Please inspect your benchmark!'.format(instr, column))
    return clk_cyc


def include_ibench(arch, ibench_output):
    """
    Read ibench output and include it in the architecture specific csv file.
    """
    df = read_csv(arch)
    # Create sequence of numbers and their reciprocals for validate the measurements
    cyc_list, reci_list = create_sequences()

    new_data = []
    added_vals = 0
    with open(ibench_output) as f:
        source = f.readline()
    for line in source:
        if 'Using frequency' in line or len(line) == 0:
            continue
        column = 'LT'
        instr = line.split()[0][:-1]
        if 'TP' in line:
            # We found a command with a throughput value. Get instruction and the number of
            # clock cycles and remove the '-TP' suffix.
            column = 'TP'
            instr = instr[:-3]
        # Otherwise it is a latency value. Nothing to do.
        clk_cyc = float(line.split()[1])
        clk_cyc = validate_val(clk_cyc, instr, True if (column == 'TP') else False,
                               cyc_list, reci_list)
        val = -2
        new = False
        try:
            entry = df.loc[lambda df, inst=instr: df.instr == inst, column]
            val = entry.values[0]
            # If val is -1 (= not filled with a valid value) add it immediately
            if val == -1:
                df.set_value(entry.index[0], column, clk_cyc)
                added_vals += 1
                continue
        except IndexError:
            # Instruction not in database yet --> add it
            new = True
            # First check if LT or TP value has already been added before
            for i, item in enumerate(new_data):
                if instr in item:
                    if column == 'TP':
                        new_data[i][1] = clk_cyc
                    elif column == 'LT':
                        new_data[i][2] = clk_cyc
                    new = False
                    break
            if new and column == 'TP':
                new_data.append([instr, clk_cyc, '-1', (-1,)])
            elif new and column == 'LT':
                new_data.append([instr, '-1', clk_cyc, (-1,)])
            new = True
            added_vals += 1
        if not new and abs((val / np.float64(clk_cyc)) - 1) > 0.05:
            raise ValueError(
                "Different measurement for {} ({}): {}(old) vs. {}(new)\n"
                "Please check for correctness "
                "(no changes were made).".format(instr, column, val, clk_cyc))
    # Now merge the DataFrames and write new csv file
    df = df.append(pd.DataFrame(new_data, columns=['instr', 'TP', 'LT', 'ports']),
                   ignore_index=True)
    write_csv(arch, df)
    return added_vals


def extract_marked_section(assembly):
    """
    Return the assembly section marked with IACA markers.

    Raise ValueError if none or only one marker was found.
    """
    m_start = re.search(IACA_START_MARKER, assembly)
    m_end = re.search(IACA_END_MARKER, assembly)

    if not m_start or not m_end:
        raise ValueError("Could not find start and end markers.")

    return assembly[m_start.end():m_end.start()]


def strip_assembly(assembly):
    """
    Remove comments and unnecessary whitespaces from assembly.

    :param assembly: assembly string
    :return: assembly string without comments nor any unnecessary whitespaces
    """
    asm_lines = assembly.split('\n')

    for i, line in enumerate(asm_lines):
        # find and remove comment
        c = line.find('#')
        if c != -1:
            line = line[:c]
        # strip leading and trailing whitespaces
        asm_lines[i] = line.strip()
    # remove blank lines
    asm_lines = [l for l in asm_lines if l]
    return '\n'.join(asm_lines)


# TODO replacement for instr_forms entries in OSACA
# class InstructionForm:
#     def __init__(self, mnemonic, parameters, line=None):
#         self.mnemonic = mnemonic
#         self.parameters = parameters
#         self.line = line
#
#     @classmethod
#     def from_assembly(cls, line):
#         # Skip clang padding bytes
#         while line.startswith('data32 '):
#             line = line[7:]
#
#         line_split = line.split()
#         mnemonic = line_split[0]
#         if len(line_split) > 1:
#             parameters = line_split[1:]
#         else:
#             parameters = None
#
#         return cls(mnemonic, parameters, line)
#
#     def __str__(self):
#         return line
#
#     def __repr__(self):
#         return '{}({!r}, {!r}, {!r})'.format(
#             self.__class__.__name__, self.mnemonic, self.parameters, self.line)


class OSACA(object):
    """
    A single OSACA analysis.
    """
    srcCode = None
    tp_list = False
    # Variables for checking lines
    numSeps = 0
    indentChar = ''
    sem = 0

    # Variables for creating output
    longestInstr = 30
    machine_readable = False

    VALID_ARCHS = Scheduler.arch_dict

    def __init__(self, arch, assembly, extract_with_markers=True):
        """
        Create and run analysis on assembly for architecture.

        :param arch: architecture abbreviation
        :param assembly: assembly code as string
        :param extract_with_markers: if True, use markers to isolate relavent section
        """
        # Check architecture
        if arch not in self.VALID_ARCHS:
            raise ValueError("Invalid architecture ({!r}), must be one of {}.".format(
                arch, self.VALID_ARCHS))
        self.arch = arch
        if extract_with_markers:
            assembly = extract_marked_section(assembly)
        self.assembly = strip_assembly(assembly).split('\n')

        self.instr_forms = []
        # Check if data files are already in usr dir, otherwise create them
        if not os.path.isdir(os.path.join(DATA_DIR, 'data')):
            #print('Copying files in user directory...', file=self.file_output, end='')
            os.makedirs(os.path.join(DATA_DIR, 'data'))
            subprocess.call(['cp', '-r',
                             MODULE_DATA_DIR,
                             DATA_DIR])
            #print(' Done!', file=self.file_output)
        else:
            # Compare and warn if files in DATA_DIR are different
            dircmp = filecmp.dircmp(os.path.join(DATA_DIR, 'data'), MODULE_DATA_DIR)
            if dircmp.left_list != dircmp.same_files:
                print("WARNING: data in {0} differs from {1}. Check or delete {1}.".format(
                    MODULE_DATA_DIR,
                    DATA_DIR
                ), file=sys.stderr)

        # Check for database for the chosen architecture
        self.df = read_csv(arch)

        # Run analysis and populate instr_forms
        self.inspect()

        # Create schedule
        self.schedule = Scheduler(self.arch, self.instr_forms)

    def inspect(self):
        """
        Run analysis.
        """
        for line in self.assembly:
            # TODO potential replacement for instr_forms entries in OSACA
            # InstructionForm.from_assembly(line)

            # Ignore labels
            if re.match(r'^[a-zA-Z0-9\_\.]+:$', line):
                continue
            # Ignore .loc
            if re.match(r'^\.loc\s+', line):
                continue
            self.check_instr(line)

    def check_instr(self, instr):
        """
        Inspect instruction for its parameters and add it to the instruction forms
        pool instr_form.

        Parameters
        ----------
        instr : str
            Instruction as string
        """
        # Check for strange clang padding bytes
        while instr.startswith('data32'):
            instr = instr[7:]
        # Separate mnemonic and operands
        mnemonic = instr.split()[0]
        params = instr.split()[1:]
        # Check if line is not only a byte
        empty_byte = re.compile(r'[0-9a-f]{2}')
        if re.match(empty_byte, mnemonic) and len(mnemonic) == 2:
            return
        # Check if there's one or more operands and store all in a list
        param_list = flatten(self._separate_params(params))
        param_list_types = list(param_list)
        # Check if line contains a directive and if so, add as a workaround with
        # marker in mnemonic
        directive = re.compile(r'^\.[a-zA-Z0-9]+$')
        if re.match(directive, mnemonic):
            instr = instr.rstrip()
            instr_form = ['DIRECTIVE'] + list() + [instr]
            self.instr_forms.append(instr_form)
            return
        # Check operands and separate them by IMMEDIATE (IMD), REGISTER (REG),
        # MEMORY (MEM) or LABEL(LBL)
        for i, op in enumerate(param_list):
            if len(op) <= 0:
                op = Parameter('NONE')
            elif op[0] == '$':
                op = Parameter('IMD')
            elif op[0] == '%' and '(' not in op:
                j = len(op)
                opmask = False
                if '{' in op:
                    j = op.index('{')
                    opmask = True
                op = Register(op[1:j].strip(" ,"), opmask)
            elif '<' in op or re.match(r'^([a-zA-Z\._]+[a-zA-Z0-9_\.]*)+$', op):
                op = Parameter('LBL')
            else:
                op = MemAddr(op)
            param_list[i] = str(op)
            param_list_types[i] = op
        # Add to list
        instr = instr.rstrip()
        if len(instr) > self.longestInstr:
            self.longestInstr = len(instr)
        instr_form = [mnemonic] + list(reversed(param_list_types)) + [instr]
        self.instr_forms.append(instr_form)
        # If flag is set, create testcase for instruction form
        # Do this in reversed param list order, du to the fact it's intel syntax
        # Only create benchmark if no label (LBL) is part of the operands
        if 'LBL' in param_list or '' in param_list:
            return
        tc = Testcase(mnemonic, list(reversed(param_list_types)), '32')
        # Only write a testcase if it not already exists or already in data file
        writeTP, writeLT = tc.is_in_dir()
        inDB = len(self.df.loc[lambda df: df.instr == tc.get_entryname()])
        if inDB == 0:
            tc.write_testcase(not writeTP, not writeLT)

    def _separate_params(self, params):
        """
        Delete comments, separates parameters and return them as a list.

        Parameters
        ----------
        params : str
            Splitted line after mnemonic

        Returns
        -------
        [[...[str]]]
            Nested list of strings. The number of nest levels depend on the
            number of parametes given.
        """
        param_list = [params]
        if ',' in params:
            if ')' in params:
                if params.index(')') < len(params) - 1 and params[params.index(')') + 1] == ',':
                    i = params.index(')') + 1
                elif params.index('(') < params.index(','):
                    return param_list
                else:
                    i = params.index(',')
            else:
                i = params.index(',')
            param_list = [params[:i], self._separate_params(params[i + 1:])]
        elif '#' in params:
            i = params.index('#')
            param_list = [params[:i]]
        return param_list

    def create_output(self, tp_list=False, pr_sched=True, machine_readable=False):
        """
        Creates output of analysed file including a time stamp.

        Used to interface with Kerncraft.

        Parameters
        ----------
        tp_list : bool
            Boolean for indicating the need for the throughput list as output
            (default False)
        pr_sched : bool
            Boolean for indicating the need for predicting a scheduling
            (default True)

        Returns
        -------
        str
            OSACA output
        """
        # Check the output alignment depending on the longest instruction
        if self.longestInstr > 70:
            self.longestInstr = 70
        horiz_line = self.create_horiz_sep()
        # Write general information about the benchmark
        output = '--{}\n| Architecture:\t\t{}\n|\n'.format(
            horiz_line, self.arch)
        if tp_list:
            output += self.create_tp_list(horiz_line)
        if pr_sched:
            output += '\n\n'
            sched_output, port_binding = self.schedule.new_schedule(machine_readable)
            # if machine_readable, we're already done here
            if machine_readable:
                return sched_output
            binding = self.schedule.get_port_binding(port_binding)
            output += self.schedule.get_report_info() + '\n' + binding + '\n\n' + sched_output
            block_tp = round(max(port_binding), 2)
            output += 'Total number of estimated throughput: {}\n'.format(block_tp)

        return output

    def get_port_occupation_cycles(self):
        """
        Build dict with port names and cycles they are occupied during one block execution

        Used to interface with Kerncraft.

        :return: dictionary of ports and cycles
        """
        sched_output, port_binding = self.schedule.new_schedule()
        return collections.OrderedDict([
            (port_name, port_binding[i])
            for i, port_name in enumerate(self.schedule.get_port_naming())])

    def get_unmatched_instruction_ratio(self):
        """
        Calculate ratio of unmatched vs total instructions

        :return: float
        """
        sched_output, port_binding = self.schedule.new_schedule()
        return sched_output.count('| X ') / len(self.instr_forms)

    def get_total_throughput(self):
        """
        Return total cycles estimated per block execution. Including (potential) penalties.

        Used to interface with Kerncraft.

        :return: float of cycles
        """
        return max(self.get_port_occupation_cycles().values())

    def create_horiz_sep(self):
        """
        Calculate and return horizontal separator line.

        Returns
        -------
        str
            Horizontal separator line
        """
        return '-' * (self.longestInstr + 8)

    def create_tp_list(self, horiz_line):
        """
        Create list of instruction forms with the proper throughput value.

        Parameter
        ---------
        horiz_line : str
            Calculated horizontal line for nice alignement

        Returns
        -------
        str
            Throughput list output for printing
        """
        warning = False
        ws = ' ' * (len(horiz_line) - 23)

        output = '\n| INSTRUCTION{}CLOCK CYCLES\n| {}\n|\n'.format(ws, horiz_line)
        # Check for the throughput data in CSV
        for elem in self.instr_forms:
            op_ext = []
            for i in range(1, len(elem) - 1):
                if isinstance(elem[i], Register) and elem[i].reg_type == 'GPR':
                    optmp = 'r' + str(elem[i].size)
                elif isinstance(elem[i], MemAddr):
                    optmp = 'mem'
                else:
                    optmp = str(elem[i]).lower()
                op_ext.append(optmp)
            operands = '_'.join(op_ext)
            # Now look up the value in the dataframe
            # Check if there is a stored throughput value in database
            import warnings
            warnings.filterwarnings("ignore", 'This pattern has match groups')
            series = self.df['instr'].str.contains(elem[0] + '-' + operands)
            if True in series.values:
                # It's a match!
                not_found = False
                try:
                    tp = self.df[self.df.instr == elem[0] + '-' + operands].TP.values[0]
                except IndexError:
                    # Something went wrong
                    #print('Error while fetching data from data file', file=self.file_output)
                    continue
            # Did not found the exact instruction form.
            # Try to find the instruction form for register operands only
            else:
                op_ext_regs = []
                for operand in op_ext:
                    try:
                        # regTmp = Register(operand)
                        # Create Register only to see if it is one
                        Register(operand)
                        op_ext_regs.append(True)
                    except KeyError:
                        op_ext_regs.append(False)
                if True not in op_ext_regs:
                    # No register in whole instr form. How can I find out what regsize we need?
                    #print('Feature not included yet: ', end='', file=self.file_output)
                    #print(elem[0] + ' for ' + operands, file=self.file_output)
                    tp = 0
                    warning = True
                    num_whitespaces = self.longestInstr - len(elem[-1])
                    ws = ' ' * num_whitespaces + '|  '
                    n_f = ' ' * (5 - len(str(tp))) + '*'
                    data = '| ' + elem[-1] + ws + str(tp) + n_f + '\n'
                    output += data
                    continue
                if op_ext_regs[0] is False:
                    # Instruction stores result in memory. Check for storing in register instead.
                    if len(op_ext) > 1:
                        if op_ext_regs[1] is True:
                            op_ext[0] = op_ext[1]
                        elif len(op_ext) > 2:
                            if op_ext_regs[2] is True:
                                op_ext[0] = op_ext[2]
                if len(op_ext_regs) == 2 and op_ext_regs[1] is False:
                    # Instruction loads value from memory and has only two operands. Check for
                    # loading from register instead
                    if op_ext_regs[0] is True:
                        op_ext[1] = op_ext[0]
                if len(op_ext_regs) == 3 and op_ext_regs[2] is False:
                    # Instruction loads value from memory and has three operands. Check for loading
                    # from register instead
                    op_ext[2] = op_ext[0]
                operands = '_'.join(op_ext)
                # Check for register equivalent instruction
                series = self.df['instr'].str.contains(elem[0] + '-' + operands)
                if True in series.values:
                    # It's a match!
                    not_found = False
                    try:
                        tp = self.df[self.df.instr == elem[0] + '-' + operands].TP.values[0]
                    except IndexError:
                        # Something went wrong
                        #print('Error while fetching data from data file', file=self.file_output)
                        continue
                # Did not found the register instruction form. Set warning and go on with
                # throughput 0
                else:
                    tp = 0
                    not_found = True
                    warning = True
            # Check the alignement again
            num_whitespaces = self.longestInstr - len(elem[-1])
            ws = ' ' * num_whitespaces + '|  '
            n_f = ''
            if not_found:
                n_f = ' ' * (5 - len(str(tp))) + '*'
            data = '| ' + elem[-1] + ws + '{:3.2f}'.format(tp) + n_f + '\n'
            output += data
        # Finally end the list of  throughput values
        output += '| ' + horiz_line + '\n'
        if warning:
            output += ('\n\n* There was no throughput value found  for the specific instruction '
                       'form.\n  Please create a testcase via the create_testcase-method or add a '
                       'value manually.')
        return output

    def generate_text_output(self):
        """Generate and return an output string showing the analysis results."""
        output = self.create_output(self.tp_list, True, self.machine_readable)
        return output


def read_csv(arch):
    """
    Read architecture dependent CSV from data directory.

    Returns
    -------
    DataFrame
        CSV as DataFrame object
    """
    # curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
    return pd.read_csv(DATA_DIR + 'data/' + arch.lower() + '_data.csv')


def write_csv(arch, df):
    """
    Write architecture DataFrame as CSV into data directory.
    """
    # curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
    csv = df.to_csv(index=False)
    with open(DATA_DIR + 'data/' + arch.lower() + '_data.csv', 'w') as f:
        f.write(csv)


# Stolen from pip
def __read(*names, **kwargs):
    with io.open(
            os.path.join(os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


# Stolen from pip
def __find_version(*file_paths):
    version_file = __read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def main():
    # Parse args
    parser = argparse.ArgumentParser(description='Analyzes a marked innermost loop snippet'
                                                 'for a given architecture type and prints out the '
                                                 'estimated average throughput.')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __find_version('__init__.py'))
    parser.add_argument('--arch', type=str, required=True,
                        help='define architecture (SNB, IVB, HSW, BDW, SKL, ZEN)')
    parser.add_argument('--binary', '-b', action='store_true',
                        help='binary file must be disassembled first')
    parser.add_argument('--tp-list', action='store_true',
                        help='print an additional list of all throughput values for the kernel')
    parser.add_argument('-i', '--include-ibench', action='store_true',
                       help='includes the given values in form of the output of ibench in the'
                            'data file')
    parser.add_argument('--insert-marker', '-m', action='store_true',
                       help='try to find blocks probably corresponding to loops in assembly and'
                            'insert IACA marker')
    parser.add_argument('-l', '--list-output', dest='machine_readable', action='store_true',
                        help='returns output as machine readable list of lists')
    parser.add_argument('filepath', type=str, help='path to object (Binary, ASM, CSV)')

    # Store args in global variables
    args = parser.parse_args()

    # --include-ibench acts stand alone, ignoring everything else
    if args.include_ibench:
        added_values = include_ibench()
        print("Sucessfully adde {} value(s)".format(added_values))
        return

    if args.binary:
        # Read disassembled binary
        assembly = get_assembly_from_binary(args.filepath)
    else:
        # read assembly directly
        with open(args.filepath) as f:
            assembly = f.read()
    
    if args.insert_marker:
        if args.binary:
            raise NotImplementedError("Marker insertion is unsupported for binary input files.")
        # Insert markers using kerncraft
        try:
            from kerncraft import iaca
        except ImportError:
            print("Module kerncraft not installed. Use 'pip install --user "
                  "kerncraft' for installation.\nFor more information see "
                  "https://github.com/RRZE-HPC/kerncraft", file=sys.stderr)
            sys.exit(1)
        # Change due to newer kerncraft version (hopefully temporary)
        # iaca.iaca_instrumentation(input_file=filepath, output_file=filepath,
        #                          block_selection='manual', pointer_increment=1)
        # TODO use io.StringIO here
        unmarked_assembly = io.StringIO(assembly)
        marked_assembly = io.StringIO()
        iaca.iaca_instrumentation(input_file=unmarked_assembly, output_file=marked_assembly,
                                  block_selection='manual', pointer_increment=1)

        marked_assembly.seek(0)
        assembly = marked_assembly.read()

    osaca = OSACA(args.arch, assembly)
    print(osaca.generate_text_output())


if __name__ == '__main__':
    main()
