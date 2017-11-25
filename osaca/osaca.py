#!/usr/bin/env python3

import argparse
import sys
import os
import io
import re
import subprocess
from datetime import datetime

import pandas as pd
import numpy as np

from osaca.param import Register, MemAddr, Parameter
from osaca.eu_sched import Scheduler
from osaca.testcase import Testcase


class Osaca(object):
    arch = None
    filepath = None
    srcCode = None
    df = None
    instr_forms = None
    tp_list = False
    file_output = ''
    osaca_dir = os.path.expanduser('~') + '/.osaca/'
    # Variables for checking lines
    numSeps = 0
    indentChar = ''
    sem = 0
    marker = r'//STARTLOOP'

    # Variables for creating output
    longestInstr = 30
    # Constants
    ASM_LINE = re.compile(r'\s[0-9a-f]+[:]')
    # Matches every variation of the IACA start marker
    IACA_SM = re.compile(r'\s*movl[ \t]+\$111[ \t]*,[ \t]*%ebx.*\n\s*\.byte[ \t]+100.*'
                         + r'((,[ \t]*103.*((,[ \t]*144)|(\n\s*\.byte[ \t]+144)))|(\n\s*\.byte'
                         + r'[ \t]+103.*((,[ \t]*144)|(\n\s*\.byte[ \t]+144))))')
    # Matches every variation of the IACA end marker
    IACA_EM = re.compile(r'\s*movl[ \t]+\$222[ \t]*,[ \t]*%ebx.*\n\s*\.byte[ \t]+100.*'
                         + r'((,[ \t]*103.*((,[ \t]*144)|(\n\s*\.byte[ \t]+144)))|(\n\s*\.byte'
                         + r'[ \t]+103.*((,[ \t]*144)|(\n\s*\.byte[ \t]+144))))')

    def __init__(self, _arch, _filepath, output=sys.stdout):
        self.arch = _arch
        self.filepath = _filepath
        self.instr_forms = []
        self.file_output = output
        # Check if data files are already in usr dir, otherwise create them
        if(not os.path.isdir(self.osaca_dir + 'data')):
            print('Copying files in user directory...', file=self.file_output, end='')
            subprocess.call(['mkdir', '-p', self.osaca_dir])
            subprocess.call(['cp', '-r', 
                             '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/data',
                             self.osaca_dir])
            print('Done!', file=self.file_output)

    # -----------------main functions depending on arguments--------------------
    def include_ibench(self):
        """
        Reads ibench output and includes it in the architecture specific csv
        file.
        """
        # Check args and exit program if something's wrong
        if(not self.check_arch()):
            print('Invalid microarchitecture.', file=sys.stderr)
            sys.exit(1)
        if(not self.check_file()):
            print('Invalid file path or file format.', file=sys.stderr)
            sys.exit(1)
        # Check for database for the chosen architecture
        self.df = self.read_csv()
        # Create sequence of numbers and their reciprokals for validate the measurements
        cyc_list, reci_list = self.create_sequences()
        print('Everything seems fine! Let\'s start!', file=self.file_output)
        new_data = []
        added_vals = 0
        for line in self.srcCode:
            if('Using frequency' in line or len(line) == 0):
                continue
            clmn = 'LT'
            instr = line.split()[0][:-1]
            if('TP' in line):
                # We found a command with a throughput value. Get instruction and the number of
                # clock cycles and remove the '-TP' suffix.
                clmn = 'TP'
                instr = instr[:-3]
            # Otherwise it is a latency value. Nothing to do.
            clk_cyc = line.split()[1]
            clk_cyc_tmp = clk_cyc
            clk_cyc = self.validate_val(clk_cyc, instr, True if (clmn == 'TP') else False,
                                        cyc_list, reci_list)
            txt_output = True if (clk_cyc_tmp == clk_cyc) else False
            val = -2
            new = False
            try:
                entry = self.df.loc[lambda df, inst=instr: df.instr == inst, clmn]
                val = entry.values[0]
            except IndexError:
                # Instruction not in database yet --> add it
                new = True
                # First check if LT or TP value has already been added before
                for i, item in enumerate(new_data):
                    if(instr in item):
                        if(clmn == 'TP'):
                            new_data[i][1] = clk_cyc
                        elif(clmn == 'LT'):
                            new_data[i][2] = clk_cyc
                        new = False
                        break
                if(new and clmn == 'TP'):
                    new_data.append([instr, clk_cyc, '-1', (-1,)])
                elif(new and clmn == 'LT'):
                    new_data.append([instr, '-1', clk_cyc, (-1,)])
                new = True
                added_vals += 1
            # If val is -1 (= not filled with a valid value) add it immediately
            if(val == -1):
                self.df.set_value(entry.index[0], clmn, clk_cyc)
                added_vals += 1
                continue
            if(not new and abs((val/np.float64(clk_cyc))-1) > 0.05):
                print('Different measurement for {} ({}): {}(old) vs. '.format(instr, clmn, val)
                      + '{}(new)\nPlease check for correctness '.format(clk_cyc)
                      + '(no changes were made).', file=self.file_output)
                txt_output = True
            if(txt_output):
                print('', file=self.file_output)
                txt_output = False
        # Now merge the DataFrames and write new csv file
        self.df = self.df.append(pd.DataFrame(new_data, columns=['instr', 'TP', 'LT', 'ports']),
                                 ignore_index=True)
        csv = self.df.to_csv(index=False)
        self.write_csv(csv)
        print('ibench output {} '.format(self.filepath.split('/')[-1])
              + 'successfully in data file included.', file=self.file_output)
        print('{} values were added.'.format(added_vals), file=self.file_output)

    def inspect_binary(self):
        """
        Main function of OSACA. Inspect binary file and create analysis.
        """
        # Check args and exit program if something's wrong
        if(not self.check_arch()):
            print('Invalid microarchitecture.', file=sys.stderr)
            sys.exit(1)
        if(not self.check_elffile()):
            print('Invalid file path or file format. Not an ELF file.', file=sys.stderr)
            sys.exit(1)
        # Finally check for database for the chosen architecture
        self.df = self.read_csv()

        print('Everything seems fine! Let\'s start checking!', file=self.file_output)
        for i, line in enumerate(self.srcCode):
            if(i == 0):
                self.check_line(line, True)
            else:
                self.check_line(line)
        output = self.create_output(self.tp_list)
        print(output, file=self.file_output)

    def inspect_with_iaca(self):
        """
        Main function of OSACA with IACA markers instead of OSACA marker.
        Inspect binary file and create analysis.
        """
        # Check args and exit program if something's wrong
        if(not self.check_arch()):
            print('Invalid microarchitecture.', file=sys.stderr)
            sys.exit()
        # Check if input file is a binary or assembly file
        binary_file = True
        if(not self.check_elffile()):
            binary_file = False
            if(not self.check_file(True)):
                print('Invalid file path or file format.', file=sys.stderr)
                sys.exit(1)
        # Finally check for database for the chosen architecture
        self.df = self.read_csv()

        print('Everything seems fine! Let\'s start checking!', file=self.file_output)
        if(binary_file):
            self.iaca_bin()
        else:
            self.iaca_asm()
        output = self.create_output(self.tp_list)
        print(output, file=self.file_output)

    # --------------------------------------------------------------------------

    def check_arch(self):
        """
        Check if the architecture is valid.

        Returns
        -------
        bool
            True    if arch is supported
            False   if arch is not supported

        """
        arch_list = ['SNB', 'IVB', 'HSW', 'BDW', 'SKL']
        if(self.arch in arch_list):
            return True
        else:
            return False

    def check_elffile(self):
        """
        Check if the given filepath exists, if the format is the needed elf64
        and store file data in attribute srcCode.

        Returns
        -------
        bool
            True    if file is expected elf64 file
            False   if file does not exist or is not an elf64 file

        """
        if(os.path.isfile(self.filepath)):
            self.store_src_code_elf()
            try:
                if('file format elf64' in self.srcCode[1].lower()):
                    return True
            except(IndexError):
                return False
        return False

    def check_file(self, iaca_flag=False):
        """
        Check if the given filepath exists and store file data in attribute
        srcCode.

        Parameters
        ----------
        iaca_flag : bool
            store file data as a string in attribute srcCode if True,
            store it as a list of strings (lines) if False (default False)

        Returns
        -------
        bool
            True    if file exists
            False   if file does not exist

        """
        if(os.path.isfile(self.filepath)):
            self.store_src_code(iaca_flag)
            return True
        return False

    def store_src_code_elf(self):
        """
        Load binary file compiled with '-g' in class attribute srcCode and
        separate by line.
        """
        self.srcCode = (subprocess.run(['objdump', '--source', self.filepath],
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE).stdout.decode('utf-8').split('\n'))

    def store_src_code(self, iaca_flag=False):
        """
        Load arbitrary file in class attribute srcCode.

        Parameters
        ----------
        iaca_flag : bool
                store file data as a string in attribute srcCode if True,
                store it as a list of strings (lines) if False (default False)
        """
        try:
            f = open(self.filepath, 'r')
        except IOError:
            print('IOError: file \'{}\' not found'.format(self.filepath), file=self.file_output)
        self.srcCode = ''
        for line in f:
            self.srcCode += line
        f.close()
        if(iaca_flag):
            return
        self.srcCode = self.srcCode.split('\n')

    def read_csv(self):
        """
        Reads architecture dependent CSV from data directory.

        Returns
        -------
        DataFrame
            CSV as DataFrame object
        """
        #curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        df = pd.read_csv(self.osaca_dir+'data/'+self.arch.lower()+'_data.csv')
        return df

    def write_csv(self, csv):
        """
        Writes architecture dependent CSV into data directory.

        Parameters
        ----------
        csv : str
            CSV data as string
        """
        #curr_dir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        try:
            f = open(self.osaca_dir+'data/'+self.arch.lower()+'_data.csv', 'w')
        except IOError:
            print('IOError: file \'{}\' not found in $HOME/.osaca/data'.format(self.arch.lower()
                  + '_data.csv'), file=self.file_output)
        f.write(csv)
        f.close()

    def create_sequences(self, end=101):
        """
        Creates list of integers from 1 to end and list of their reciprocals.

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
            reci_list.append(1/i)
        return cyc_list, reci_list

    def validate_val(self, clk_cyc, instr, is_tp, cyc_list, reci_list):
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
        clmn = 'LT'
        if(is_tp):
            clmn = 'TP'
        for i in range(0, len(cyc_list)):
            if(cyc_list[i]*1.05 > float(clk_cyc) and cyc_list[i]*0.95 < float(clk_cyc)):
                # Value is probably correct, so round it to the estimated value
                return cyc_list[i]
            # Check reciprocal only if it is a throughput value
            elif(is_tp and reci_list[i]*1.05 > float(clk_cyc)
                 and reci_list[i]*0.95 < float(clk_cyc)):
                # Value is probably correct, so round it to the estimated value
                return reci_list[i]
        # No value close to an integer or its reciprocal found, we assume the
        # measurement is incorrect
        print('Your measurement for {} ({}) is probably wrong. '.format(instr, clmn)
              + 'Please inspect your benchmark!', file=self.file_output)
        print('The program will continue with the given value', file=self.file_output)
        return clk_cyc

    def check_line(self, line, first_appearance=False):
        """
        Inspect line of source code and process it if inside the marked snippet.

        Parameter
        ---------
        line : str
            Line of source code
        first_appearance : bool
            Necessary for setting indenting character (default False)
        """
        # Check if marker is in line
        if(self.marker in line):
            # First, check if high level code in indented with whitespaces or tabs
            if(first_appearance):
                self.indentChar = self.get_indent_chars(line)
            # Now count the number of whitespaces
            self.numSeps = (re.split(self.marker, line)[0]).count(self.indentChar)
            self.sem = 3
        elif(self.sem > 0):
            # We're in the marked code snippet
            # Check if the line is ASM code and - if not - check if we're still in the loop
            match = re.search(self.ASM_LINE, line)
            if(match):
                # Further analysis of instructions
                # Check if there are comments in line
                if(r'//' in line):
                    return
                self.check_instr(''.join(re.split(r'\t', line)[-1:]))
            elif((re.split(r'\S', line)[0]).count(self.indentChar) <= self.numSeps):
                # Not in the loop anymore - or yet. We decrement the semaphore
                self.sem = self.sem-1

    def get_indent_chars(self, line):
        """
        Check if indentation characters are either tabulators or whitespaces

        Parameters
        ----------
        line : str
            Line with start marker in it

        Returns
        -------
        str
            Indentation character as string
        """
        num_spaces = (re.split(self.marker, line)[0]).count(' ')
        num_tabs = (re.split(self.marker, line)[0]).count('\t')
        if(num_spaces != 0 and num_tabs == 0):
            return ' '
        elif(num_spaces == 0 and num_tabs != 0):
            return '\t'
        else:
            err_msg = 'Indentation of code is only supported for whitespaces and tabs.'
            raise NotImplementedError(err_msg)

    def iaca_bin(self):
        """
        Extract instruction forms out of binary file using IACA markers.
        """
        self.marker = r'fs addr32 nop'
        part1 = re.compile(r'64\s+fs')
        part2 = re.compile(r'67 90\s+addr32 nop')
        is_2_lines = False
        for line in self.srcCode:
            # Check if marker is in line
            if(self.marker in line):
                self.sem += 1
            elif(re.search(part1, line) or re.search(part2, line)):
                self.sem += 0.5
                is_2_lines = True
            elif(self.sem == 1):
                # We're in the marked code snippet
                # Check if the line is ASM code
                match = re.search(self.ASM_LINE, line)
                if(match):
                    # Further analysis of instructions
                    # Check if there are comments in line
                    if(r'//' in line):
                        continue
                    # Do the same instruction check as for the OSACA marker line check
                    self.check_instr(''.join(re.split(r'\t', line)[-1:]))
            elif(self.sem == 2):
                # Not in the loop anymore. Due to the fact it's the IACA marker we can stop here
                # After removing the last line which belongs to the IACA marker
                del self.instr_forms[-1:]
                #if(is_2_lines):
                    # The marker is splitted into two lines, therefore delete another line
                #    del self.instr_forms[-1:]
                return

    def iaca_asm(self):
        """
        Extract instruction forms out of assembly file using IACA markers.
        """
        # Extract the code snippet surround by the IACA markers
        code = self.srcCode
        # Search for the start marker
        match = re.match(self.IACA_SM, code)
        while(not match):
            code = code.split('\n', 1)[1]
            match = re.match(self.IACA_SM, code)
        # Search for the end marker
        code = (code.split('144', 1)[1]).split('\n', 1)[1]
        res = ''
        match = re.match(self.IACA_EM, code)
        while(not match):
            res += code.split('\n', 1)[0]+'\n'
            code = code.split('\n', 1)[1]
            match = re.match(self.IACA_EM, code)
        # Split the result by line go on like with OSACA markers
        res = res.split('\n')
        for line in res:
            line = line.split('#')[0]
            line = line.lstrip()
            if(len(line) == 0 or '//' in line or line.startswith('..')):
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
        while(instr.startswith('data32')):
            instr = instr[7:]
        # Separate mnemonic and operands
        mnemonic = instr.split()[0]
        params = ''.join(instr.split()[1:])
        # Check if line is not only a byte
        empty_byte = re.compile(r'[0-9a-f]{2}')
        if(re.match(empty_byte, mnemonic) and len(mnemonic) == 2):
            return
        # Check if there's one or more operands and store all in a list
        param_list = self.flatten(self.separate_params(params))
        param_list_types = list(param_list)
        # Check operands and separate them by IMMEDIATE (IMD), REGISTER (REG),
        # MEMORY (MEM) or LABEL(LBL)
        for i in range(len(param_list)):
            op = param_list[i]
            if(len(op) <= 0):
                op = Parameter('NONE')
            elif(op[0] == '$'):
                op = Parameter('IMD')
            elif(op[0] == '%' and '(' not in op):
                j = len(op)
                opmask = False
                if('{' in op):
                    j = op.index('{')
                    opmask = True
                op = Register(op[1:j], opmask)
            elif('<' in op or op.startswith('.')):
                op = Parameter('LBL')
            else:
                op = MemAddr(op)
            param_list[i] = str(op)
            param_list_types[i] = op
        # Add to list
        instr = instr.rstrip()
        if(len(instr) > self.longestInstr):
            self.longestInstr = len(instr)
        instr_form = [mnemonic]+list(reversed(param_list_types))+[instr]
        self.instr_forms.append(instr_form)
        # If flag is set, create testcase for instruction form
        # Do this in reversed param list order, du to the fact it's intel syntax
        # Only create benchmark if no label (LBL) is part of the operands
        if('LBL' in param_list or '' in param_list):
            return
        tc = Testcase(mnemonic, list(reversed(param_list_types)), '32')
        # Only write a testcase if it not already exists or already in data file
        writeTP, writeLT = tc.is_in_dir()
        inDB = len(self.df.loc[lambda df: df.instr == tc.get_entryname()])
        if(inDB == 0):
            tc.write_testcase(not writeTP, not writeLT)

    def separate_params(self, params):
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
        if(',' in params):
            if(')' in params):
                if(params.index(')') < len(params)-1 and params[params.index(')')+1] == ','):
                    i = params.index(')')+1
                elif(params.index('(') < params.index(',')):
                    return param_list
                else:
                    i = params.index(',')
            else:
                i = params.index(',')
            param_list = [params[:i], self.separate_params(params[i+1:])]
        elif('#' in params):
            i = params.index('#')
            param_list = [params[:i]]
        return param_list

    def flatten(self, l):
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
        if l == []:
            return l
        if(isinstance(l[0], list)):
            return self.flatten(l[0]) + self.flatten(l[1:])
        return l[:1] + self.flatten(l[1:])

    def create_output(self, tp_list=False, pr_sched=True):
        """
        Creates output of analysed file including a time stamp.

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
        if(self.longestInstr > 70):
            self.longestInstr = 70
        horiz_line = self.create_horiz_sep()
        # Write general information about the benchmark
        output = ('--' + horiz_line + '\n'
                  + '| Analyzing of file:\t' + os.path.abspath(self.filepath) + '\n'
                  + '| Architecture:\t\t' + self.arch + '\n'
                  + '| Timestamp:\t\t' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
        if(tp_list):
            output += self.create_tp_list(horiz_line)
        if(pr_sched):
            output += '\n\n'
            sched = Scheduler(self.arch, self.instr_forms)
            sched_output, port_binding = sched.new_schedule()
            binding = sched.get_port_binding(port_binding)
            output += sched.get_report_info() + '\n' + binding + '\n\n' + sched_output
            block_tp = round(max(port_binding), 2)
            output += 'Total number of estimated throughput: ' + str(block_tp)
        return output

    def create_horiz_sep(self):
        """
        Calculate and return horizontal separator line.

        Returns
        -------
        str
            Horizontal separator line
        """
        return '-'*(self.longestInstr+8)

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
        ws = ' '*(len(horiz_line)-23)

        output = ('\n| INSTRUCTION' + ws + 'CLOCK CYCLES\n'
                  + '| ' + horiz_line + '\n|\n')
        # Check for the throughput data in CSV
        for elem in self.instr_forms:
            op_ext = []
            for i in range(1, len(elem)-1):
                optmp = ''
                if(isinstance(elem[i], Register) and elem[i].reg_type == 'GPR'):
                    optmp = 'r'+str(elem[i].size)
                elif(isinstance(elem[i], MemAddr)):
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
            if(True in series.values):
                # It's a match!
                not_found = False
                try:
                    tp = self.df[self.df.instr == elem[0] + '-' + operands].TP.values[0]
                except IndexError:
                    # Something went wrong
                    print('Error while fetching data from data file', file=self.file_output)
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
                if(True not in op_ext_regs):
                    # No register in whole instr form. How can I find out what regsize we need?
                    print('Feature not included yet: ', end='', file=self.file_output)
                    print(elem[0]+' for '+operands, file=self.file_output)
                    tp = 0
                    not_found = True
                    warning = True
                    num_whitespaces = self.longestInstr-len(elem[-1])
                    ws = ' ' * num_whitespaces + '|  '
                    n_f = ' ' * (5 - len(str(tp))) + '*'
                    data = '| ' + elem[-1] + ws + str(tp) + n_f + '\n'
                    output += data
                    continue
                if(op_ext_regs[0] is False):
                    # Instruction stores result in memory. Check for storing in register instead.
                    if(len(op_ext) > 1):
                        if(op_ext_regs[1] is True):
                            op_ext[0] = op_ext[1]
                        elif(len(op_ext > 2)):
                            if(op_ext_regs[2] is True):
                                op_ext[0] = op_ext[2]
                if(len(op_ext_regs) == 2 and op_ext_regs[1] is False):
                    # Instruction loads value from memory and has only two operands. Check for
                    # loading from register instead
                    if(op_ext_regs[0] is True):
                        op_ext[1] = op_ext[0]
                if(len(op_ext_regs) == 3 and op_ext_regs[2] is False):
                    # Instruction loads value from memory and has three operands. Check for loading
                    # from register instead
                    op_ext[2] = op_ext[0]
                operands = '_'.join(op_ext)
                # Check for register equivalent instruction
                series = self.df['instr'].str.contains(elem[0]+'-'+operands)
                if(True in series.values):
                    # It's a match!
                    not_found = False
                    try:
                        tp = self.df[self.df.instr == elem[0]+'-'+operands].TP.values[0]
                    except IndexError:
                        # Something went wrong
                        print('Error while fetching data from data file', file=self.file_output)
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
            if(not_found):
                n_f = ' ' * (5 - len(str(tp))) + '*'
            data = '| ' + elem[-1] + ws + '{:3.2f}'.format(tp) + n_f + '\n'
            output += data
        # Finally end the list of  throughput values
        num_whitespaces = self.longestInstr - 27
        ws = '  ' + ' ' * num_whitespaces
        output += '| ' + horiz_line + '\n'
        if(warning):
            output += ('\n\n* There was no throughput value found '
                       'for the specific instruction form.'
                       '\n  Please create a testcase via the create_testcase-method '
                       'or add a value manually.')
        return output


# ------------------------------------------------------------------------------
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


# ------------Main method--------------
def main():
    # Parse args
    parser = argparse.ArgumentParser(description='Analyzes a marked innermost loop snippet'
                                     + 'for a given architecture type and prints out the estimated'
                                     + 'average throughput.')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s '
                        + __find_version('__init__.py'))
    parser.add_argument('--arch', dest='arch', type=str, help='define architecture '
                                                              + '(SNB, IVB, HSW, BDW, SKL)')
    parser.add_argument('--tp-list', dest='tp_list', action='store_true',
                        help='print an additional list of all throughput values for the kernel')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-i', '--include-ibench', dest='incl', action='store_true',
                       help='includes the given values in form of the output of ibench in the'
                            + 'data file')
    group.add_argument('--iaca', dest='iaca', action='store_true',
                       help='search for IACA markers instead the OSACA marker')
    group.add_argument('-m', '--insert-marker', dest='insert_marker', action='store_true',
                       help='try to find blocks probably corresponding to loops in assembly and'
                       + 'insert IACA marker')
    parser.add_argument('filepath', type=str, help='path to object (Binary, ASM, CSV)')

    # Store args in global variables
    inp = parser.parse_args()
    if(inp.arch is None and inp.insert_marker is None):
        raise ValueError('Please specify an architecture.', file=sys.stderr)
    if(inp.arch is not None):
        arch = inp.arch.upper()
    filepath = inp.filepath
    incl_ibench = inp.incl
    iaca_flag = inp.iaca
    insert_m = inp.insert_marker

    # Create Osaca object
    if(inp.arch is not None):
        osaca = Osaca(arch, filepath)
    if(inp.tp_list):
        osaca.tp_list = True

    if(incl_ibench):
        try:
            osaca.include_ibench()
        except UnboundLocalError:
            print('Please specify an architecture.', file=sys.stderr)
    elif(iaca_flag):
        try:
            osaca.inspect_with_iaca()
        except UnboundLocalError:
            print('Please specify an architecture.', file=sys.stderr)
    elif(insert_m):
        try:
            from kerncraft import iaca
        except ImportError:
            print('ImportError: Module kerncraft not installed. Use '
                  + '\'pip install --user kerncraft\' for installation.\nFor more information see '
                  + 'https://github.com/RRZE-HPC/kerncraft', file=sys.stderr)
            sys.exit(1)
        iaca.iaca_instrumentation(input_file=filepath, output_file=filepath,
                                  block_selection='manual', pointer_increment=1)
    else:
        osaca.inspect_binary()


# ------------Main method--------------
if __name__ == '__main__':
    main()
