#!/apps/python/3.5-anaconda/bin/python
import sys
import re
from Testcase import *
from Params import *

marker = r'//STARTLOOP'
asm_line = re.compile(r'\s[0-9a-f]+[:]')
numSeps = 0
sem = 0
db = {}
sorted_db = []
lncnt = 1
#cnt=0
fname = ""
cntChar = ''
first = True

def extract_instr(asmFile):
    global once
    global lncnt
    global fname
    fname = asmFile
#Check if parameter is in the correct file format
    if(asmFile[-4:] != ".log"):
        print("Invalid argument")
        sys.exit()
#Open file
    try:
        f=open(asmFile, "r")
    except IOError:
        print("IOError: File not found")
#Analyse code line by line and check the instructions
    lncnt = 1
    for line in f:
        check_line(line)
        lncnt += 1
    f.close()


def check_line(line):
    global numSeps
    global sem
    global first
#Check if marker is in line and count the number of whitespaces if so
    if(marker in line):
#But first, check if high level code ist indented with whitespaces or tabs
        if(first):
            set_counter_char(line)
            first = False
        numSeps = (re.split(marker,line)[0]).count(cntChar)
        sem = 2;
    elif(sem > 0):
#We're in the marked code snipped
#Check if the line is ASM code and - if not - check if we're still in the loop
        match = re.search(asm_line, line)
        if(match):
#Further analysis of instructions
#            print("".join(re.split(r'\t',line)[-1:]),end="")
#Check if there are commetns in line
            if(r'//' in line):
                return
            check_instr("".join(re.split(r'\t',line)[-1:]))
        elif((re.split(r'\S',line)[0]).count(cntChar) <= numSeps):
#Not in the loop anymore - or yet - so we decrement the semaphore
            sem = sem-1

#Check if seperator is either tabulator or whitespace 
def set_counter_char(line):
    global cntChar
    numSpaces = (re.split(marker,line)[0]).count(" ")
    numTabs = (re.split(marker,line)[0]).count("\t")
    if(numSpaces != 0 and numTabs == 0):
        cntChar = ' '
    elif(numSpaces == 0 and numTabs != 0):
        cntChar = '\t'
    else:
       raise NotImplementedError("Indentation of code is only supported for whitespaces and tabs.")


def check_instr(instr):
    global db
    global lncnt
    global cnt
    global fname
#Check for strange clang padding bytes
    while(instr.startswith("data32")):
        instr = instr[7:]
#Seperate mnemonic and operands
    mnemonic = instr.split()[0]
    params = "".join(instr.split()[1:])
#Check if line is not only a byte
    empty_byte = re.compile(r'[0-9a-f]{2}')
    if(re.match(empty_byte, mnemonic) and len(mnemonic) == 2):
        return
#Check if there's one or more operand and store all in a list
    param_list = flatten(separate_params(params))
    opList = list(param_list)
#Check operands and seperate them by IMMEDIATE (IMD), REGISTER (REG), MEMORY (MEM) or LABEL (LBL)
    for i in range(len(param_list)):
        op = param_list[i]
        if(len(op) <= 0):
            op = Parameter("NONE")
        elif(op[0] == '$'):
            op = Parameter("IMD")
        elif(op[0] == '%' and '(' not in op):
            j = len(op)
            opmask = False
            if('{' in op):
                j = op.index('{')
                opmask = True
            op = Register(op[1:j], opmask)
        elif('<' in op):
            op = Parameter("LBL")
        else:
            op = MemAddr(op)
        param_list[i] = op.print()
        opList[i] = op
#Join mnemonic and operand(s) to an instruction form
    if(len(mnemonic) > 7):
        tabs = "\t"
    else:
        tabs = "\t\t"
    instr_form = mnemonic+tabs+("  ".join(param_list))
#Check in database for instruction form and increment the counter
    if(instr_form in db):
        db[instr_form] = db[instr_form]+1
    else:
        db[instr_form] = 1
#Create testcase for instruction form, since it is the first appearance of it
#But (as far as now) only for instr forms with only registers as operands
#        is_Reg = True
#        for par in opList:
#            print(par.print()+" is Register: "+str(isinstance(par, Register)))
#            if(not isinstance(par, Register)):
#                is_Reg = False
#        if(is_Reg):
            #print(mnemonic)
#            print("create testcase for "+mnemonic+" with params:")
#            for p in opList:
#                print(p.print(),end=", ")
#            print()


#Only create benchmark if no label (LBL) is part of the operands
        do_bench = True
        for par in opList:
            if(par.print() == 'LBL'):
                do_bench = False
        if(do_bench):
#Create testcase with reversed param list, due to the fact its intel syntax!
#            create_testcase(mnemonic, list(reversed(opList))) 
#            print('menmonic: '+mnemonic+' ops: '+str(list(reversed(opList))))
            tc = Testcase(mnemonic, list(reversed(opList)), '64')
            tc.write_testcase()
#        print("-----------")

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
   

def sort_db():
    global sorted_db
    sorted_db=sorted(db.items(), key=lambda x:x[1], reverse=True)


def print_sorted_db():
    sort_db()
    sum = 0
    print("Number of\tmnemonic")
    print("calls\n")
    for i in range(len(sorted_db)):
        print(str(sorted_db[i][1])+"\t\t"+sorted_db[i][0])
        sum += sorted_db[i][1]
    print("\nCumulated number of instructions: "+str(sum))


def save_db():
    global db
    file = open(".cnt_asm_ops.db","w")
    for i in db.items():
        file.write(i[0]+"\t"+str(i[1])+"\n")
    file.close()


def load_db():
    global db
    try:
        file = open(".cnt_asm_ops.db", "r")
    except FileNotFoundError:
        print("no database found in current directory")
        return
    for line in file:
        mnemonic = line.split('\t')[0]
#Join mnemonic and operand(s) to an instruction form
        if(len(mnemonic) > 7):
            tabs = "\t"
            params = line.split('\t')[1]
            numCalls = line.split("\t")[2][:-1]
        else:
            tabs = "\t\t"
            params = line.split('\t')[2]
            numCalls = line.split("\t")[3][:-1]
        instr_form = mnemonic+tabs+params
        db[instr_form] = int(numCalls)
    file.close()


def flatten(l):
    if l == []:
        return l
    if(isinstance(l[0], list)):
        return flatten(l[0]) + flatten(l[1:])
    return l[:1] + flatten(l[1:])


if __name__ == "__main__":
#    load_db()
#    r0 = Register("ymm0")
#    r1 = Register("xmm0")
#    r64 = Register("rax")
#    r32 = Register("eax")
#    mem0 = MemAddr('(%rax, %esi, 4)')
#    tc = Testcase("XOR", [r32, r32], '64')
#    tc.write_testcase()
#    create_testcase("VADDPD", [r0, r0, r0])
    if(len(sys.argv) > 1):
        for i in range(1,len(sys.argv)):
            extract_instr(sys.argv[i])
    print_sorted_db()
    
#    save_db()
