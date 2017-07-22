#!/apps/python/3.5-anaconda/bin/python
import sys
import re
from Testcase import *

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
    regList = list(param_list)
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
        regList[i] = op
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
        is_Reg = True
        for par in regList:
#            print(par.print()+" is Register: "+str(isinstance(par, Register)))
            if(not isinstance(par, Register)):
                is_Reg = False
        if(is_Reg):
            #print(mnemonic)
#            print("create testcase for "+mnemonic+" with params:")
#            for p in regList:
#                print(p.print(),end=", ")
#            print()
#Create testcase with reversed param list, due to the fact its intel syntax!
#            create_testcase(mnemonic, list(reversed(regList)))  
            tc = Testcase(mnemonic, list(reversed(regList)), '12')
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




class Parameter(object):
    type_list = ["REG", "MEM", "IMD", "LBL", "NONE"]
    def __init__(self, ptype, name=""):
        self.ptype = ptype.upper()
        if(self.ptype not in self.type_list):
            raise NameError("Type not supported: "+ptype)
    
    def print(self):
        if(self.ptype == "NONE"):
            return ""
        else:
            return self.ptype

class MemAddr(Parameter):
    segment_regs = ["CS", "DS", "SS", "ES", "FS", "GS"]
    scales = [1, 2, 4, 8]
    def __init__(self, name):
        self.sreg = False
        self.offset = False
        self.base = False
        self.index = False
        self.scale = False
        if(':' in name):
            if(name[1:name.index(':')].upper() not in self.segment_regs):
                raise NameError("Type not supported: "+name)
            self.sreg = True
            self.offset = True
        if('(' not in name or ('(' in name and name.index('(') != 0)):
            self.offset = True
        if('(' in name):
            self.parentheses = name[name.index('(')+1:-1]
            self.commacnt = self.parentheses.count(',')
            if(self.commacnt == 0):
                self.base = True
            elif(self.commacnt == 2 and int(self.parentheses[-1:]) in self.scales):
                self.base = True
                self.index = True
                self.scale = True
            else:
                raise NameError("Type not supported: "+name)
    
    def print(self):
        self.mem_format = "MEM("
        if(self.sreg):
            self.mem_format += "sreg:"
        if(self.offset):
            self.mem_format += "offset"
        if(self.base and not self.index):
            self.mem_format += "(base)"
        elif(self.base and self.index and self.scale):
            self.mem_format += "(base, index, scale)"
        self.mem_format += ")"
        return self.mem_format
        


class Register(Parameter):
    sizes = {
#General Purpose Registers
    "AH":(8,"GPR"), "AL":(8,"GPR"), "BH":(8,"GPR"), "BL":(8,"GPR"), "CH":(8,"GPR"), "CL":(8,"GPR"), "DH":(8,"GPR"), "DL":(8,"GPR"), "BPL":(8,"GPR"), "SIL":(8,"GPR"), "DIL":(8,"GPR"), "SPL":(8,"GPR"), "R8L":(8,"GPR"), "R9L":(8,"GPR"), "R10L":(8,"GPR"), "R11L":(8,"GPR"), "R12L":(8,"GPR"), "R13L":(8,"GPR"), "R14L":(8,"GPR"), "R15L":(8,"GPR"),
    "R8B":(8,"GPR"),"R9B":(8,"GPR"),"R10B":(8,"GPR"),"R11B":(8,"GPR"),"R12B":(8,"GPR"),"R13B":(8,"GPR"),"R14B":(8,"GPR"),"R15B":(8,"GPR"),
    "AX":(16,"GPR"), "BC":(16,"GPR"), "CX":(16,"GPR"), "DX":(16,"GPR"), "BP":(16,"GPR"), "SI":(16,"GPR"), "DI":(16,"GPR"), "SP":(16,"GPR"), "R8W":(16,"GPR"), "R9W":(16,"GPR"), "R10W":(16,"GPR"), "R11W":(16,"GPR"), "R12W":(16,"GPR"), "R13W":(16,"GPR"), "R14W":(16,"GPR"), "R15W":(16,"GPR"),
    "EAX":(32,"GPR"), "EBX":(32,"GPR"), "ECX":(32,"GPR"), "EDX":(32,"GPR"), "EBP":(32,"GPR"), "ESI":(32,"GPR"), "EDI":(32,"GPR"), "ESP":(32,"GPR"), "R8D":(32,"GPR"), "R9D":(32,"GPR"), "R10D":(32,"GPR"), "R11D":(32,"GPR"), "R12D":(32,"GPR"), "R13D":(32,"GPR"), "R14D":(32,"GPR"), "R15D":(32,"GPR"),
    "RAX":(64,"GPR"), "RBX":(64,"GPR"), "RCX":(64,"GPR"), "RDX":(64,"GPR"), "RBP":(64,"GPR"), "RSI":(64,"GPR"), "RDI":(64,"GPR"), "RSP":(64,"GPR"), "R8":(64,"GPR"), "R9":(64,"GPR"), "R10":(64,"GPR"), "R11":(64,"GPR"), "R12":(64,"GPR"), "R13":(64,"GPR"), "R14":(64,"GPR"), "R15":(64,"GPR"),
    "CS":(16,"GPR"), "DS":(16,"GPR"), "SS":(16,"GPR"), "ES":(16,"GPR"), "FS":(16,"GPR"), "GS":(16,"GPR"),
    "EFLAGS":(32,"GPR"), "RFLAGS":(64,"GPR"), "EIP":(32,"GPR"), "RIP":(64,"GPR"),
#FPU Registers
    "ST0":(80,"FPU"),"ST1":(80,"FPU"),"ST2":(80,"FPU"),"ST3":(80,"FPU"),"ST4":(80,"FPU"),"ST5":(80,"FPU"),"ST6":(80,"FPU"),"ST7":(80,"FPU"),
#MMX Registers
    "MM0":(64,"MMX"),"MM1":(64,"MMX"),"MM2":(64,"MMX"),"MM3":(64,"MMX"),"MM4":(64,"MMX"),"MM5":(64,"MMX"),"MM6":(64,"MMX"),"MM7":(64,"MMX"),
#XMM Registers
    "XMM0":(128,"XMM"),"XMM1":(128,"XMM"),"XMM2":(128,"XMM"),"XMM3":(128,"XMM"),"XMM4":(128,"XMM"),"XMM5":(128,"XMM"),"XMM6":(128,"XMM"),"XMM7":(128,"XMM"), "XMM8":(128,"XMM"), "XMM9":(128,"XMM"), "XMM10":(128,"XMM"), "XMM11":(128,"XMM"), "XMM12":(128,"XMM"), "XMM13":(128,"XMM"), "XMM14":(128,"XMM"), "XMM15":(128,"XMM"), "XMM16":(128,"XMM"), "XMM17":(128,"XMM"), "XMM18":(128,"XMM"), "XMM19":(128,"XMM"), "XMM20":(128,"XMM"), "XMM21":(128,"XMM"), "XMM22":(128,"XMM"), "XMM23":(128,"XMM"), "XMM24":(128,"XMM"), "XMM25":(128,"XMM"), "XMM26":(128,"XMM"), "XMM27":(128,"XMM"), "XMM28":(128,"XMM"), "XMM29":(128,"XMM"), "XMM30":(128,"XMM"), "XMM31":(128,"XMM"),
#YMM Registers
    "YMM0":(256,"YMM"),"YMM1":(256,"YMM"),"YMM2":(256,"YMM"),"YMM3":(256,"YMM"),"YMM4":(256,"YMM"),"YMM5":(256,"YMM"),"YMM6":(256,"YMM"),"YMM7":(256,"YMM"), "YMM8":(256,"YMM"), "YMM9":(256,"YMM"), "YMM10":(256,"YMM"), "YMM11":(256,"YMM"), "YMM12":(256,"YMM"), "YMM13":(256,"YMM"), "YMM14":(256,"YMM"), "YMM15":(256,"YMM"), "YMM16":(256,"YMM"), "YMM17":(256,"YMM"), "YMM18":(256,"YMM"), "YMM19":(256,"YMM"), "YMM20":(256,"YMM"), "YMM21":(256,"YMM"), "YMM22":(256,"YMM"), "YMM23":(256,"YMM"), "YMM24":(256,"YMM"), "YMM25":(256,"YMM"), "YMM26":(256,"YMM"), "YMM27":(256,"YMM"), "YMM28":(256,"YMM"), "YMM29":(256,"YMM"), "YMM30":(256,"YMM"), "YMM31":(256,"YMM"),
#ZMM Registers
    "ZMM0":(512,"ZMM"),"ZMM1":(512,"ZMM"),"ZMM2":(512,"ZMM"),"ZMM3":(512,"ZMM"),"ZMM4":(512,"ZMM"),"ZMM5":(512,"ZMM"),"ZMM6":(512,"ZMM"),"ZMM7":(512,"ZMM"), "ZMM8":(512,"ZMM"), "ZMM9":(512,"ZMM"), "ZMM10":(512,"ZMM"), "ZMM11":(512,"ZMM"), "ZMM12":(512,"ZMM"), "ZMM13":(512,"ZMM"), "ZMM14":(512,"ZMM"), "ZMM15":(512,"ZMM"), "ZMM16":(512,"ZMM"), "ZMM17":(512,"ZMM"), "ZMM18":(512,"ZMM"), "ZMM19":(512,"ZMM"), "ZMM20":(512,"ZMM"), "ZMM21":(512,"ZMM"), "ZMM22":(512,"ZMM"), "ZMM23":(512,"ZMM"), "ZMM24":(512,"ZMM"), "ZMM25":(512,"ZMM"), "ZMM26":(512,"ZMM"), "ZMM27":(512,"ZMM"), "ZMM28":(512,"ZMM"), "ZMM29":(512,"ZMM"), "ZMM30":(512,"ZMM"), "ZMM31":(512,"ZMM"),
#Opmask Register
    "K0":(64,"K"), "K1":(64,"K"), "K2":(64,"K"), "K3":(64,"K"), "K4":(64,"K"), "K5":(64,"K"), "K6":(64,"K"), "K7":(64,"K"), 
#Bounds Registers
    "BND0":(128,"BND"),"BND1":(128,"BND"),"BND2":(128,"BND"),"BND3":(128,"BND")
    }

    def __init__(self,name,mask=False):
        self.name = name.upper()
        self.mask = mask
#        try:
        if[name in self.sizes]:
            self.size = self.sizes[self.name][0]
            self.reg_type = self.sizes[self.name][1]
        else:
            print(lncnt)
            raise NameError("Register name not in dictionary: "+self.name)
#        except KeyError:
#            print(lncnt)
	
    def print(self):
        opmask = ""
        if(self.mask):
            opmask = "{opmask}"
        return(self.reg_type+str(self.size)+opmask)



if __name__ == "__main__":
#    load_db()
    r0 = Register("ymm0")
    r1 = Register("xmm0")
    r2 = Register("rax")
    mem0 = MemAddr('(%rax, %esi, 4)')
#    Testcase("ADD", [mem0,r1])
#    create_testcase("VADDPD", [r0, r0, r0])
    if(len(sys.argv) > 1):
        for i in range(1,len(sys.argv)):
            extract_instr(sys.argv[i])
    print_sorted_db()
    
#    save_db()
