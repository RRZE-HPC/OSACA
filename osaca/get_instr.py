#!/usr/bin/env python3
import os
import re
import argparse

from osaca.testcase import Testcase
from osaca.param import Register, MemAddr, Parameter
#from testcase import Testcase
#from param import Register, MemAddr, Parameter


class InstrExtractor(object):
    filepaths = []
    # Variables for checking lines
    numSeps = 0
    sem = 0
    db = {}
    sorted_db = []
    lncnt = 1
    cntChar = ''
    first = True
    # Constant variables
    MARKER = r'//STARTLOOP'
    ASM_LINE = re.compile(r'\s[0-9a-f]+[:]')

    def __init__(self, filepath):
        self.filepaths = filepath

    def check_all(self):
        for i in range(0, len(self.filepaths)):
            self.extract_instr(self.filepaths[i])

    def is_elffile(self, filepath):
        if os.path.isfile(filepath):
            with open(filepath) as f:
                src = f.read()
            if 'format elf64' in src:
                return True
            return False

    def extract_instr(self, asm_file):
        # Check if parameter is in the correct file format
        if not self.is_elffile(asm_file):
            print('Invalid argument')
            return
        # Open file
        f = open(asm_file, 'r')
        # Analyse code line by line and check the instructions
        self.lncnt = 1
        for line in f:
            self.check_line(line)
            self.lncnt += 1
        f.close()

    def check_line(self, line):
        # Check if MARKER is in line and count the number of whitespaces if so
        if self.MARKER in line:
            # But first, check if high level code ist indented with whitespaces or tabs
            if self.first:
                self.set_counter_char(line)
                self.first = False
            self.numSeps = (re.split(self.MARKER, line)[0]).count(self.cntChar)
            self.sem = 2
        elif self.sem > 0:
            # We're in the marked code snipped
            # Check if the line is ASM code and - if not - check if we're still in the loop
            match = re.search(self.ASM_LINE, line)
            if match:
                # Further analysis of instructions
                # Check if there are commetns in line
                if r'//' in line:
                    return
                self.check_instr(''.join(re.split(r'\t', line)[-1:]))
            elif (re.split(r'\S', line)[0]).count(self.cntChar) <= self.numSeps:
                # Not in the loop anymore - or yet - so we decrement the semaphore
                self.sem = self.sem - 1

    # Check if seperator is either tabulator or whitespace
    def set_counter_char(self, line):
        num_spaces = (re.split(self.MARKER, line)[0]).count(' ')
        num_tabs = (re.split(self.MARKER, line)[0]).count('\t')
        if num_spaces != 0 and num_tabs == 0:
            self.cntChar = ' '
        elif num_spaces == 0 and num_tabs != 0:
            self.cntChar = '\t'
        else:
            err_msg = 'Indentation of code is only supported for whitespaces and tabs.'
            raise NotImplementedError(err_msg)

    def check_instr(self, instr):
        # Check for strange clang padding bytes
        while instr.startswith('data32'):
            instr = instr[7:]
        # Seperate mnemonic and operands
        mnemonic = instr.split()[0]
        params = ''.join(instr.split()[1:])
        # Check if line is not only a byte
        empty_byte = re.compile(r'[0-9a-f]{2}')
        if re.match(empty_byte, mnemonic) and len(mnemonic) == 2:
            return
        # Check if there's one or more operand and store all in a list
        param_list = self.flatten(self.separate_params(params))
        op_list = list(param_list)
        # Check operands and seperate them by IMMEDIATE (IMD), REGISTER (REG), MEMORY (MEM) or
        # LABEL (LBL)
        for i in range(len(param_list)):
            op = param_list[i]
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
                op = Register(op[1:j], opmask)
            elif '<' in op:
                op = Parameter('LBL')
            else:
                op = MemAddr(op)
            param_list[i] = str(op) if (type(op) is not Register) else str(op) + str(op.size)
            op_list[i] = op
        # Join mnemonic and operand(s) to an instruction form
        if len(mnemonic) > 7:
            tabs = '\t'
        else:
            tabs = '\t\t'
        instr_form = mnemonic + tabs + ('  '.join(param_list))
        # Check in data file for instruction form and increment the counter
        if instr_form in self.db:
            self.db[instr_form] = self.db[instr_form] + 1
        else:
            self.db[instr_form] = 1
            # Create testcase for instruction form, since it is the first appearance of it
            # Only create benchmark if no label (LBL) is part of the operands
            do_bench = True
            for par in op_list:
                if str(par) == 'LBL' or str(par) == '':
                    do_bench = False
            if do_bench:
                # Create testcase with reversed param list, due to the fact its intel syntax!
                tc = Testcase(mnemonic, list(reversed(op_list)), '64')
                tc.write_testcase()

    def separate_params(self, params):
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
            param_list = [params[:i], self.separate_params(params[i + 1:])]
        elif '#' in params:
            i = params.index('#')
            param_list = [params[:i]]
        return param_list

    def sort_db(self):
        self.sorted_db = sorted(self.db.items(), key=lambda x: x[1], reverse=True)

    def print_sorted_db(self):
        self.sort_db()
        total = 0
        print('Number of\tmnemonic')
        print('calls\n')
        for i in range(len(self.sorted_db)):
            print(str(self.sorted_db[i][1]) + '\t\t' + self.sorted_db[i][0])
            total += self.sorted_db[i][1]
        print('\nCumulated number of instructions: ' + str(total))

    def save_db(self):
        file = open('.cnt_asm_ops.db', 'w')
        for i in self.db.items():
            file.write(i[0] + '\t' + str(i[1]) + '\n')
        file.close()

    def load_db(self):
        try:
            file = open('.cnt_asm_ops.db', 'r')
        except FileNotFoundError:
            print('no data file found in current directory')
            return
        for line in file:
            mnemonic = line.split('\t')[0]
            # Join mnemonic and operand(s) to an instruction form
            if len(mnemonic) > 7:
                tabs = '\t'
                params = line.split('\t')[1]
                num_calls = line.split('\t')[2][:-1]
            else:
                tabs = '\t\t'
                params = line.split('\t')[2]
                num_calls = line.split('\t')[3][:-1]
            instr_form = mnemonic + tabs + params
            self.db[instr_form] = int(num_calls)
        file.close()

    def flatten(self, l):
        if not l:
            return l
        if isinstance(l[0], list):
            return self.flatten(l[0]) + self.flatten(l[1:])
        return l[:1] + self.flatten(l[1:])


def main():
    # Parse args
    parser = argparse.ArgumentParser(description='Returns a list of all instruction forms in the '
                                                 'given files sorted by their number of '
                                                 'occurrences.')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.2')
    parser.add_argument('filepath', nargs='+', help='path to objdump(s)')
    parser.add_argument('-l', '--load', dest='load', action='store_true',
                        help='load data file before checking new files')
    parser.add_argument('-s', '--store', dest='store', action='store_true',
                        help='store data file before checking new files')

    # Create object and store arguments as attribute
    inp = parser.parse_args()
    ie = InstrExtractor(inp.filepath)

    # Do work
    if inp.load:
        ie.load_db()
    ie.check_all()
    ie.print_sorted_db()
    if inp.store:
        ie.save_db()


# ---------main method----------
if __name__ == '__main__':
    main()
