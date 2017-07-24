#!/apps/python/3.5-anaconda/bin/python

import argparse
import sys
import subprocess 
import os
import re
from  Params import *
import pandas as pd
from datetime import datetime
import numpy as np

#----------Global variables--------------
arch = ''
archList = ['SNB','IVB','HSW', 'BDW', 'SKL']
filepath = ''
srcCode = ''
marker = r'//STARTLOOP'
asm_line = re.compile(r'\s[0-9a-f]+[:]')
numSeps = 0
sem = 0
firstAppearance = True
instrForms = list()
df = ''
output = ''
horizontalSeparator = ''
total_tp = 0
longestInstr = 30
cycList = []
reciList = []
#---------------------------------------

# Check if the architecture arg is valid
def check_arch():
    if(arch in archList):
        return True
    else:
        return False

# Check if the given filepath exists and if the format is the needed elf64
def check_elffile():
    if(os.path.isfile(filepath)):
        create_elffile()
        if('file format elf64' in srcCode[1]):
            return True
    return False

# Check if the given filepath exists
def check_file():
    if(os.path.isfile(filepath)):
        get_file()
        return True
    return False

# Load binary file in variable srcCode and separate by line
def create_elffile():
    global srcCode
    srcCode = subprocess.run(['objdump', '--source', filepath], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')

# Load arbitrary file in variable srcCode and separate by line
def get_file():
    global srcCode
    try:
        f = open(filepath, 'r')
    except IOError:
        print('IOError: file \'{}\' not found'.format(filepath))
    for line in f:
        srcCode += line
    f.close()
    srcCode = srcCode.split('\n')


def check_line(line):
    global numSeps
    global sem
    global firstAppearance
# Check if marker is in line
    if(marker in line):
# First, check if high level code in indented with whitespaces or tabs
        if(firstAppearance):
            set_char_counter(line)
            firstAppearance = False
# Now count the number of whitespaces
        numSeps = (re.split(marker, line)[0]).count(cntChar)
        sem = 2
    elif(sem > 0):
# We're in the marked code snippet
# Check if the line is ASM code and - if not - check if we're still in the loop
        match = re.search(asm_line, line)
        if(match):
# Further analysis of instructions
# Check if there are comments in line
            if(r'//' in line):
                return
            check_instr(''.join(re.split(r'\t', line)[-1:]))
        elif((re.split(r'\S', line)[0]).count(cntChar) <= numSeps):
# Not in the loop anymore - or yet. We decrement the semaphore
            sem = sem-1
    

# Check if separators are either tabulators or whitespaces
def set_char_counter(line):
    global cntChar
    numSpaces = (re.split(marker, line)[0]).count(' ')
    numTabs = (re.split(marker, line)[0]).count('\t')
    if(numSpaces != 0 and numTabs == 0):
        cntChar = ' '
    elif(numSpaces == 0 and numTabs != 0):
        cntChar = '\t'
    else:
        raise NotImplementedError('Indentation of code is only supported for whitespaces and tabs.')


def check_instr(instr):
    global instrForms
    global longestInstr
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
    param_list = flatten(separate_params(params))
    param_list_types = list(param_list)
# check operands and separate them by IMMEDIATE (IMD), REGISTER (REG). MEMORY (MEM) or LABEL(LBL)
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
        elif('<' in op):
            op = Parameter('LBL')
        else:
            op = MemAddr(op)
        param_list[i] = op.print()
        param_list_types[i] = op
#Add to list
    if(len(instr) > longestInstr):
        longestInstr = len(instr)
    instrForm = [mnemonic]+list(reversed(param_list_types))+[instr]
    instrForms.append(instrForm)

def separate_params(params):
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
        param_list = [params[:i],separate_params(params[i+1:])]
    elif('#' in params):
        i = params.index('#')
        param_list = [params[:i]]
    return param_list

def flatten(l):
    if l == []:
        return l
    if(isinstance(l[0], list)):
        return flatten(l[0]) + flatten(l[1:])
    return l[:1] + flatten(l[1:])

def read_csv():
    global df
    currDir = os.path.realpath(__file__)[:-8]
    df = pd.read_csv(currDir+'data/'+arch.lower()+'_throughput.csv')

def create_horiz_sep():
    global horizontalSeparator
    horizontalSeparator = '-'*(longestInstr+8)

def create_output():
    global total_tp
    global output
    global longestInstr
    warning = False
    
#Check the output alignment depending on the longest instruction
    if(longestInstr > 70):
        longestInstr = 70
    create_horiz_sep()
    ws = ' '*(len(horizontalSeparator)-23)
# Write general information about the benchmark
    output = (  '--'+horizontalSeparator+'\n'
                '| Analyzing of file:\t'+os.getcwd()+'/'+filepath+'\n'
                '| Architecture:\t\t'+arch+'\n'
                '| Timestamp:\t\t'+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n'
                '|\n| INSTRUCTION'+ws+'CLOCK CYCLES\n'
                '| '+horizontalSeparator+'\n|\n')
# Check for the throughput data in CSV
# First determine if we're searching for the SSE, AVX or AVX512 type of instruction
    for elem in instrForms:
        extension = ''
        avx = False
        avx512 = False
        opExt = []
        for i in range(1, len(elem)-1):
            optmp = ''
            if(isinstance(elem[i], Register) and elem[i].reg_type == 'GPR'):
                optmp = 'r'+str(elem[i].size)
            elif(isinstance(elem[i], MemAddr)):
                optmp = 'mem'
            else:
                optmp = elem[i].print().lower()
            opExt.append(optmp)
# Due to the fact we store the explicit operands, we don't need anyu avx/avx512 extension
#        for op in elem[1:-1]:
#            if(isinstance(op,Register) and op.reg_type == 'YMM'):
#                avx = True
#            elif(isinstance(op,Register) and op.reg_type == 'ZMM'):
#                avx512 = True
#                break
#        if(avx512):
#            extension = '-avx512'
#        elif(avx):
#            extension = '-avx'
        operands = '_'.join(opExt)
# Now look up the value in the dataframe
# Check if there is a stored throughput value in database
#        print(elem[0]+'-'+operands+'-TP')
        #operands = operands.replace(r'(',r'\(')
        #operands = operands.replace(r')', r'\)')
        import warnings
        warnings.filterwarnings("ignore", 'This pattern has match groups')
        series = df['instr'].str.contains(elem[0]+'-'+operands+'-TP')
        if( True in series.values):
# It's a match!
            notFound = False
            try:
                tp = df[df.instr == elem[0]+'-'+operands+'-TP'].clock_cycles.values[0]
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
# No register in whole instruction form. How can I found out what regsize we need?
                print('Feature not included yet: ', end='')
                print(elem[0]+' for '+operands)
                tp = 0
                notFound = True
                warning = True

                numWhitespaces = longestInstr-len(elem[-1])
                ws = ' '*numWhitespaces+'|  '
                n_f = ' '*(5-len(str(tp)))+'*'
                data = '| '+elem[-1]+ws+str(tp)+n_f+'\n'
                output += data
                continue
            if(opExtRegs[0] == False):
# Instruction stores result in memory. Check for storing in register instead
                if(len(opExt) > 1):
                    if(opExtRegs[1] == True):
                        opExt[0] = opExt[1]
                    elif(len(optExt > 2)):
                        if(opExtRegs[2] == True):
                            opExt[0] = opExt[2]
            if(len(opExtRegs) == 2 and opExtRegs[1] == False):
# Instruction loads value from memory and has only two operands. Check for loading from register instead
                if(opExtRegs[0] == True):
                    opExt[1] = opExt[0]
            if(len(opExtRegs) == 3 and opExtRegs[2] == False):
# Instruction loads value from memorz and has three operands. Check for loading from register instead
                opExt[2] = opExt[0]
            operands = '_'.join(opExt)
# Check for register equivalent instruction
            series = df['instr'].str.contains(elem[0]+'-'+operands+'-TP')
            if( True in series.values):
# It's a match!
                notFound = False
                try:
                    tp = df[df.instr == elem[0]+'-'+operands+'-TP'].clock_cycles.values[0]
# TODO: Add throughput estimation out of register equivalent and load/store instruction
#                    ...
#                    ...
# end TODO
                except IndexError:
# Something went wrong
                    print('Error while fetching data from database')
                    continue
# Did not found the register instruction form. Set warning and go on with throughput 0
            else:
                tp = 0
                notFound = True
                warning = True
# Add it to the overall throughput
        total_tp += tp
# Check the alignement again
        numWhitespaces = longestInstr-len(elem[-1])
        ws = ' '*numWhitespaces+'|  '
        n_f = ''
        if(notFound):
            n_f = ' '*(5-len(str(tp)))+'*'
        data = '| '+elem[-1]+ws+'{:3.2f}'.format(tp)+n_f+'\n'
        output += data
# Finally write the total throughput
    numWhitespaces = longestInstr-27
    ws = '  '+' '*numWhitespaces
    output += ( '| '+horizontalSeparator+'\n'
                '| TOTAL ESTIMATED THROUGHPUT:'+ws+str(np.ceil(total_tp)))
    if(warning):
        output += ('\n\n* There was no throughput value found '
                    'for the specific instruction form.'
                    '\n  Please create a testcase via the create_testcase-method '
                    'or add a value manually.')

def create_sequences():
    global cycList
    global reciList

    for i in range(1, 101):
        cycList.append(i)
        reciList.append(1/i)

def validate_TP(clkC, instr):
    for i in range(0, 100):
        if(cycList[i]*1.05 > float(clkC) and cycList[i]*0.95 < float(clkC)):
# Value is probably correct, so round it to the estimated value
            return cycList[i]
        elif(reciList[i]*1.05 > float(clkC) and reciList[i]*0.95 < float(clkC)):
# Value is probably correct, so round it to the estimated value
            return reciList[i]
# No value close to an integer or its reciprokal found, we assume the measurement is incorrect
    print('Your measurement for {} is probably wrong. Please inspect your benchmark!'.format(instr))
    print('The program will continue with the given value')
    return clkC

def write_csv(csv):
    try:
        f = open('data/'+arch.lower()+'_throughput.csv', 'w')
    except IOError:
        print('IOError: file \'{}\' not found in ./data'.format(arch.lower()+'_throughput.csv'))
    f.write(csv)
    f.close()

##---------------main functions depending on arguments----------------------

#reads ibench output and includes it in the architecture specific csv file
def include_ibench():
    global df

# Check args and exit program if something's wrong
    if(not check_arch()):
        print('Invalid microarchitecture.')
        sys.exit()
    if(not check_file()):
        print('Invalid file path or file format.')
        sys.exit()
# Check for database for the chosen architecture
    read_csv()
# Create sequence of numbers and their reciprokals for validate the measurements
    create_sequences()
    
    print('Everything seems fine! Let\'s start checking!')
    newData = []
    addedValues = 0
    for line in srcCode:
        if('TP' in line):
# We found a command with a throughput value. Get instruction and the number of clock cycles
            instr = line.split()[0][:-1]
            clkC = line.split()[1]
            clkC_tmp = clkC
            clkC = validate_TP(clkC, instr)
            txtOutput = True if (clkC_tmp == clkC) else False
            tp = -1
            new = False
            try:
                tp = df.loc[lambda df: df.instr == instr,'clock_cycles'].values[0]
            except IndexError:
# Instruction not in database yet --> add it
                newData.append([instr,clkC])
                new = True
                addedValues += 1
                pass
            if(not new and abs((tp/np.float64(clkC))-1) > 0.05):
                print('Different measurement for {}: {}(old) vs. {}(new)\nPlease check for correctness (no changes were made).'.format(instr, tp, clkC))
                txtOutput = True
            if(txtOutput):
                print()
                txtOutput = False
# Now merge the DataFrames and write new csv file
    df = df.append(pd.DataFrame(newData, columns=['instr','clock_cycles']), ignore_index=True)
    csv = df.to_csv(index=False)
    write_csv(csv)
    print('ibench output {} successfully in database included.'.format(filepath.split('/')[-1]))
    print('{} values were added.'.format(addedValues))

                
# main function of the tool
def inspect_binary():
# Check args and exit program if something's wrong
    if(not check_arch()):
        print('Invalid microarchitecture.')
        sys.exit()
    if(not check_elffile()):
        print('Invalid file path or file format.')
        sys.exit()
# Finally check for database for the chosen architecture
    read_csv()

    print('Everything seems fine! Let\'s start checking!')
    for line in srcCode:
        check_line(line)
    create_output()
    print(output)

##------------------------------------------------------------------------------
##------------Main method--------------
def main():
    global inp
    global arch
    global filepath
# Parse args
    parser = argparse.ArgumentParser(description='Analyzes a marked innermost loop snippet for a given architecture type and prints out the estimated average throughput')
    parser.add_argument('--version', '-V', action='version', version='%(prog)s 0.1')
    parser.add_argument('--arch', dest='arch', type=str, help='define architecture')
    parser.add_argument('filepath', type=str, help='path to object (Binary, CSV)')
    parser.add_argument('--include-ibench', '-i', dest='incl', action='store_true', help='includes the given values in form of the output of ibench in the database')

# Store args in global variables
    inp = parser.parse_args()
    if(inp.arch is None):
        raise ValueError('Please specify an architecture')
    arch = inp.arch.upper()
    filepath = inp.filepath
    inclIbench = inp.incl
    
    if(inclIbench):
        include_ibench()
    else:
        inspect_binary()


##------------Main method--------------
if __name__ == '__main__':
    main()
