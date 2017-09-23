#!/apps/python/3.5-anaconda/bin/python

import argparse
import sys
import subprocess 
import os
import re
from  param import *
from eu_sched import *
from testcase import *
import pandas as pd
from datetime import datetime
import numpy as np


class Osaca(object):
    arch = None
    filepath = None
    srcCode = None
    df = None
    instrForms = None
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
    IACA_SM = re.compile(r'\s*movl[ \t]+\$111[ \t]*,[ \t]*%ebx[ \t]*\n\s*\.byte[ \t]+100[ \t]*((,[ \t]*103[ \t]*((,[ \t]*144)|(\n\s*\.byte[ \t]+144)))|(\n\s*\.byte[ \t]+103[ \t]*((,[ \t]*144)|(\n\s*\.byte[ \t]+144))))')
# Matches every variation of the IACA end marker
    IACA_EM = re.compile(r'\s*movl[ \t]+\$222[ \t]*,[ \t]*%ebx[ \t]*\n\s*\.byte[ \t]+100[ \t]*((,[ \t]*103[ \t]*((,[ \t]*144)|(\n\s*\.byte[ \t]+144)))|(\n\s*\.byte[ \t]+103[ \t]*((,[ \t]*144)|(\n\s*\.byte[ \t]+144))))')

    def __init__(self, _arch, _filepath):
        self.arch = _arch
        self.filepath = _filepath
        self.instrForms = []


##-------------------main functions depending on arguments----------------------
    def include_ibench(self):
        """
        Reads ibench output and includes it in the architecture specific csv 
        file.
        """
# Check args and exit program if something's wrong
        if(not self.check_arch()):
            print('Invalid microarchitecture.')
            sys.exit()
        if(not self.check_file()):
            print('Invalid file path or file format.')
            sys.exit()
# Check for database for the chosen architecture
        self.df = self.read_csv()
# Create sequence of numbers and their reciprokals for validate the measurements
        cycList,reciList = self.create_sequences() 
        print('Everything seems fine! Let\'s start!')
        newData = []
        addedValues = 0
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
            clkC = line.split()[1]
            clkC_tmp = clkC
            clkC = self.validate_val(clkC, instr, True if (clmn == 'TP') else False, cycList, reciList)
            txtOutput = True if (clkC_tmp == clkC) else False
            val = -2
            new = False
            try:
                entry = self.df.loc[lambda df: df.instr == instr,clmn]
                val = entry.values[0]
            except IndexError:
# Instruction not in database yet --> add it
                new = True
# First check if LT or TP value has already been added before
                for i,item in enumerate(newData):
                    if(instr in item):
                        if(clmn == 'TP'):
                            newData[i][1] = clkC
                        elif(clmn == 'LT'):
                            newData[i][2] = clkC
                        new = False
                        break
                if(new and clmn == 'TP'):
                    newData.append([instr,clkC,'-1',((-1,),)])
                elif(new and clmn == 'LT'):
                    newData.append([instr,'-1',clkC,((-1,),)])              
                new = True
                addedValues += 1
                pass
# If val is -1 (= not filled with a valid value) add it immediately
            if(val == -1):
                self.df.set_value(entry.index[0], clmn, clkC)
                addedValues += 1
                continue
            if(not new and abs((val/np.float64(clkC))-1) > 0.05):
                print('Different measurement for {} ({}): {}(old) vs. {}(new)\nPlease check for correctness (no changes were made).'.format(instr, clmn, val, clkC))
                txtOutput = True
            if(txtOutput):
                print()
                txtOutput = False
# Now merge the DataFrames and write new csv file
        self.df = self.df.append(pd.DataFrame(newData, columns=['instr','TP','LT','ports']), ignore_index=True)
        csv = self.df.to_csv(index=False)
        self.write_csv(csv)
        print('ibench output {} successfully in database included.'.format(self.filepath.split('/')[-1]))
        print('{} values were added.'.format(addedValues))


    def inspect_binary(self):
        """
        Main function of OSACA. Inspect binary file and create analysis.
        """
# Check args and exit program if something's wrong
        if(not self.check_arch()):
            print('Invalid microarchitecture.')
            sys.exit()
        if(not self.check_elffile()):
            print('Invalid file path or file format.')
            sys.exit()
# Finally check for database for the chosen architecture
        self.read_csv()
    
        print('Everything seems fine! Let\'s start checking!')
        for i,line in enumerate(self.srcCode):
            if(i == 0):
                self.check_line(line, True)
            else:
                self.check_line(line)
        output = self.create_output()
        print(output)
    

    def inspect_with_iaca(self):
        """
        Main function of OSACA with IACA markers instead of OSACA marker.
        Inspect binary file and create analysis.
        """
# Check args and exit program if something's wrong
        if(not self.check_arch()):
            print('Invalid microarchitecture.')
            sys.exit()
# Check if input file is a binary or assembly file
        try:
            binaryFile = True
            if(not self.check_elffile()):
                print('Invalid file path or file format.')
                sys.exit()
        except (TypeError,IndexError):
            binaryFile = False
            if(not self.check_file(True)):
                print('Invalid file path or file format.')
                sys.exit()       
# Finally check for database for the chosen architecture
        self.read_csv()
    
        print('Everything seems fine! Let\'s start checking!')
        if(binaryFile):
            self.iaca_bin()
        else:
            self.iaca_asm()
        output = self.create_output()
        print(output)
    
##------------------------------------------------------------------------------

    def check_arch(self):
        """
        Check if the architecture is valid.

        Returns
        -------
        bool
            True    if arch is supported
            False   if arch is not supported
    
        """
        archList = ['SNB','IVB','HSW', 'BDW', 'SKL']
        if(self.arch in archList):
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
            self.store_srcCode_elf()
            if('file format elf64' in self.srcCode[1]):
                return True
        return False


    def check_file(self,iacaFlag=False):
        """
        Check if the given filepath exists and store file data in attribute
        srcCode.
        
        Parameters
        ----------
        iacaFlag : bool 
            store file data as a string in attribute srcCode if True,
            store it as a list of strings (lines) if False (default False)
    
        Returns
        -------
        bool
            True    if file exists
            False   if file does not exist
    
        """
        if(os.path.isfile(self.filepath)):
            self.store_srcCode(iacaFlag)
            return True
        return False
    
    def store_srcCode_elf(self):
        """
        Load binary file compiled with '-g' in class attribute srcCode and
        separate by line.
        """
        self.srcCode = subprocess.run(['objdump', '--source', self.filepath], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    
    
    def store_srcCode(self,iacaFlag=False):
        """
        Load arbitrary file in class attribute srcCode.
    
        Parameters
        ----------
        iacaFlag : bool 
                store file data as a string in attribute srcCode if True,
                store it as a list of strings (lines) if False (default False)
        """    
        try:
            f = open(self.filepath, 'r')
        except IOError:
            print('IOError: file \'{}\' not found'.format(self.filepath))
        self.srcCode = ''
        for line in f:
            self.srcCode += line
        f.close()
        if(iacaFlag):
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
        currDir = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        df = pd.read_csv(currDir+'/data/'+self.arch.lower()+'_data.csv')
        return df


    def write_csv(self,csv):
        """
        Writes architecture dependent CSV into data directory.
    
        Parameters
        ----------
        csv : str
            CSV data as string
        """
        try:
            f = open('data/'+self.arch.lower()+'_data.csv', 'w')
        except IOError:
            print('IOError: file \'{}\' not found in ./data'.format(self.arch.lower()+'_data.csv'))
        f.write(csv)
        f.close()
    


    def create_sequences(self,end=101):
        """
        Creates list of integers from 1 to end and list of their reciprocals.
    
        Parameters
        ----------
        end : int 
            End value for list of integers (default 101)
    
        Returns
        -------
        [int]
            cycList of integers
        [float]
            reciList of floats
        """
        cycList = []
        reciList = []
        for i in range(1, end):
            cycList.append(i)
            reciList.append(1/i)
        return cycList,reciList


    def validate_val(self,clkC, instr, isTP, cycList, reciList):
        """
        Validate given clock cycle clkC and return rounded value in case of
        success.
    
        A succeeded validation means the clock cycle clkC is only 5% higher or
        lower than an integer value from cycList or - if clkC is a throughput
        value - 5% higher or lower than a reciprocal from the reciList.
    
        Parameters
        ----------
        clkC : float
            Clock cycle to validate
        instr : str
            Instruction for warning output
        isTP : bool
            True if a throughput value is to check, False for a latency value
        cycList : [int]
            Cycle list for validating
        reciList : [float]
            Reciprocal cycle list for validating
    
        Returns
        -------
        float
            Clock cycle, either rounded to an integer or its reciprocal or the 
            given clkC parameter
        """
        clmn = 'LT'
        if(isTP):
            clmn = 'TP'
        for i in range(0, len(cycList)):
            if(cycList[i]*1.05 > float(clkC) and cycList[i]*0.95 < float(clkC)):
# Value is probably correct, so round it to the estimated value
                return cycList[i]
# Check reciprocal only if it is a throughput value
            elif(isTP and reciList[i]*1.05 > float(clkC) and reciList[i]*0.95 < float(clkC)):
# Value is probably correct, so round it to the estimated value
                return reciList[i]
# No value close to an integer or its reciprocal found, we assume the
# measurement is incorrect
        print('Your measurement for {} ({}) is probably wrong. Please inspect your benchmark!'.format(instr, clmn))
        print('The program will continue with the given value')
        return clkC


    def check_line(self,line,firstAppearance=False):
        """
        Inspect line of source code and process it if inside the marked snippet.
        
        Parameter
        ---------
        line : str
            Line of source code
        firstAppearance : bool
            Necessary for setting indenting character (default False)
        """
# Check if marker is in line
        if(self.marker in line):
# First, check if high level code in indented with whitespaces or tabs
            if(firstAppearance):
                self.indentChar = self.get_indent_chars(line)
# Now count the number of whitespaces
            self.numSeps = (re.split(self.marker, line)[0]).count(self.indentChar)
            self.sem = 2
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
        

    def get_indent_chars(self,line):
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
        numSpaces = (re.split(self.marker, line)[0]).count(' ')
        numTabs = (re.split(self.marker, line)[0]).count('\t')
        if(numSpaces != 0 and numTabs == 0):
            return ' '
        elif(numSpaces == 0 and numTabs != 0):
            return '\t'
        else:
            raise NotImplementedError('Indentation of code is only supported for whitespaces and tabs.')
    
   
    def iaca_bin(self):
        """
        Extract instruction forms out of binary file using IACA markers.
        """
        self.marker = r'fs addr32 nop'
        for line in self.srcCode:
# Check if marker is in line
            if(self.marker in line):
                self.sem += 1
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
                del self.instrForms[-1:]
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
            code = code.split('\n',1)[1]
            match = re.match(self.IACA_SM, code)
# Search for the end marker
        code = (code.split('144',1)[1]).split('\n',1)[1]
        res = ''
        match = re.match(self.IACA_EM, code)
        while(not match):
            res += code.split('\n',1)[0]+'\n'
            code = code.split('\n',1)[1]
            match = re.match(self.IACA_EM, code)
# Split the result by line go on like with OSACA markers
        res = res.split('\n')
        for line in res:
            line = line.split('#')[0]
            line = line.lstrip()
            if(len(line) == 0 or '//' in line or line.startswith('..')):
                continue
            self.check_instr(line)
    

    def check_instr(self,instr):
        """
        Inspect instruction for its parameters and add it to the instruction forms 
        pool instrForm.
    
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
        if(len(instr) > self.longestInstr):
            self.longestInstr = len(instr)
        instrForm = [mnemonic]+list(reversed(param_list_types))+[instr]
        self.instrForms.append(instrForm)
# If flag is set, create testcase for instruction form
# Do this in reversed param list order, du to the fact it's intel syntax
# Only create benchmark if no label (LBL) is part of the operands
        if('LBL' in param_list or '' in param_list):
            return 
        tc = Testcase(mnemonic, list(reversed(param_list_types)), '64')
# Only write a testcase if it not already exists
        writeTP, writeLT = tc._Testcase__is_in_dir()
        tc.write_testcase(not writeTP, not writeLT)
    

    def separate_params(self,params):
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
            param_list = [params[:i],self.separate_params(params[i+1:])]
        elif('#' in params):
            i = params.index('#')
            param_list = [params[:i]]
        return param_list
    
    def flatten(self,l):
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
    
   
    def create_output(self,tp_list=False,pr_sched=True):    
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
        horizLine = self.create_horiz_sep()
        ws = ' '*(len(horizLine)-23)
# Write general information about the benchmark
        output = (  '--'+horizLine+'\n'
                    '| Analyzing of file:\t'+os.path.abspath(self.filepath)+'\n'
                    '| Architecture:\t\t'+self.arch+'\n'
                    '| Timestamp:\t\t'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n')
    
        if(tp_list):
            output += self.create_TP_list(horizLine)
        if(pr_sched):
            output += '\n\n'
            sched = Scheduler(self.arch, self.instrForms) 
            schedOutput,portBinding = sched.schedule()
            binding = sched.get_port_binding(portBinding)
            output += sched.get_report_info()+'\n'+binding+'\n\n'+schedOutput
            blockTP = round(max(portBinding), 2)
            output += 'Total number of estimated throughput: '+str(blockTP)
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
    
    
    def create_TP_list(self,horizLine):        
        """
        Create list of instruction forms with the proper throughput value.
    
        Parameter
        ---------
        horizLine : str
            Calculated horizontal line for nice alignement
    
        Returns
        -------
        str
            Throughput list output for printing
        """
        warning = False
        ws = ' '*(len(horizLine)-23)
    
        output =   ('\n| INSTRUCTION'+ws+'CLOCK CYCLES\n'
                    '| '+horizLine+'\n|\n')
# Check for the throughput data in CSV
        for elem in self.instrForms:
            extension = ''
            opExt = []
            for i in range(1, len(elem)-1):
                optmp = ''
                if(isinstance(elem[i], Register) and elem[i].reg_type == 'GPR'):
                    optmp = 'r'+str(elem[i].size)
                elif(isinstance(elem[i], MemAddr)):
                    optmp = 'mem'
                else:
                    optmp = str(elem[i]).lower()
                opExt.append(optmp)
            operands = '_'.join(opExt)
# Now look up the value in the dataframe
# Check if there is a stored throughput value in database
            import warnings
            warnings.filterwarnings("ignore", 'This pattern has match groups')
            series = self.df['instr'].str.contains(elem[0]+'-'+operands)
            if( True in series.values):
# It's a match!
                notFound = False
                try:
                    tp = self.df[self.df.instr == elem[0]+'-'+operands].TP.values[0]
                except IndexError:
# Something went wrong
                    print('Error while fetching data from database')
                    continue
# Did not found the exact instruction form.
# Try to find the instruction form for register operands only
            else:
                opExtRegs = []
                for operand in opExt:
                    try:
                        regTmp = Register(operand)
                        opExtRegs.append(True)
                    except KeyError:
                        opExtRegs.append(False)
                        pass
                if(not True in opExtRegs):
# No register in whole instruction form. How can I find out what regsize we need?
                    print('Feature not included yet: ', end='')
                    print(elem[0]+' for '+operands)
                    tp = 0
                    notFound = True
                    warning = True
    
                    numWhitespaces = self.longestInstr-len(elem[-1])
                    ws = ' '*numWhitespaces+'|  '
                    n_f = ' '*(5-len(str(tp)))+'*'
                    data = '| '+elem[-1]+ws+str(tp)+n_f+'\n'
                    output += data
                    continue
                if(opExtRegs[0] == False):
# Instruction stores result in memory. Check for storing in register instead.
                    if(len(opExt) > 1):
                        if(opExtRegs[1] == True):
                            opExt[0] = opExt[1]
                        elif(len(optExt > 2)):
                            if(opExtRegs[2] == True):
                                opExt[0] = opExt[2]
                if(len(opExtRegs) == 2 and opExtRegs[1] == False):
# Instruction loads value from memory and has only two operands. Check for
# loading from register instead
                    if(opExtRegs[0] == True):
                        opExt[1] = opExt[0]
                if(len(opExtRegs) == 3 and opExtRegs[2] == False):
# Instruction loads value from memory and has three operands. Check for loading
# from register instead
                    opExt[2] = opExt[0]
                operands = '_'.join(opExt)
# Check for register equivalent instruction
                series = self.df['instr'].str.contains(elem[0]+'-'+operands)
                if( True in series.values):
# It's a match!
                    notFound = False
                    try:
                        tp = self.df[self.df.instr == elem[0]+'-'+operands].TP.values[0]
    
                    except IndexError:
# Something went wrong
                        print('Error while fetching data from database')
                        continue
# Did not found the register instruction form. Set warning and go on with
# throughput 0
                else:
                    tp = 0
                    notFound = True
                    warning = True
# Check the alignement again
            numWhitespaces = self.longestInstr-len(elem[-1])
            ws = ' '*numWhitespaces+'|  '
            n_f = ''
            if(notFound):
                n_f = ' '*(5-len(str(tp)))+'*'
            data = '| '+elem[-1]+ws+'{:3.2f}'.format(tp)+n_f+'\n'
            output += data
# Finally end the list of  throughput values
        numWhitespaces = self.longestInstr-27
        ws = '  '+' '*numWhitespaces
        output += '| '+horizLine+'\n'
        if(warning):
            output += ('\n\n* There was no throughput value found '
                       'for the specific instruction form.'
                       '\n  Please create a testcase via the create_testcase-method '
                       'or add a value manually.')
        return output
    

##------------------------------------------------------------------------------
##------------Main method--------------
def main():
# Parse args
    parser = argparse.ArgumentParser(description='Analyzes a marked innermost loop snippet for a given architecture type and prints out the estimated average throughput')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--arch', dest='arch', type=str, help='define architecture (SNB, IVB, HSW, BDW, SKL)')
    parser.add_argument('filepath', type=str, help='path to object (Binary, ASM, CSV)')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-i', '--include-ibench', dest='incl', action='store_true', help='includes the given values in form of the output of ibench in the database')
    group.add_argument('--iaca', dest='iaca', action='store_true', help='search for IACA markers instead the OSACA marker')
    group.add_argument('-m', '--insert-marker', dest='insert_marker', action='store_true', help='try to find blocks probably corresponding to loops in assembly and insert IACA marker')

# Store args in global variables
    inp = parser.parse_args()
    if(inp.arch is None and inp.insert_marker is None):
        raise ValueError('Please specify an architecture')
    if(inp.arch is not None):
        arch = inp.arch.upper()
    filepath = inp.filepath
    inclIbench = inp.incl
    iacaFlag = inp.iaca
    insert_m = inp.insert_marker

# Create Osaca object
    if(inp.arch is not None):
        osaca = Osaca(arch, filepath)
    
    if(inclIbench):
        osaca.include_ibench()
    elif(iacaFlag):
        osaca.inspect_with_iaca()
    elif(insert_m):
        try:
            from kerncraft import iaca
        except ImportError:
           print('ImportError: Module kerncraft not installed. Use \'pip install --user kerncraft\' for installation.\nFor more information see https://github.com/RRZE-HPC/kerncraft')
           sys.exit()
        iaca.iaca_instrumentation(input_file=filepath, output_file=filepath,
                                  block_selection='manual', pointer_increment=1)
    else:
        osaca.inspect_binary()


##------------Main method--------------
if __name__ == '__main__':
    main()
