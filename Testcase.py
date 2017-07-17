#!/apps/python/3.5-anaconda/bin/python

import os
from subprocess import call
from math import ceil
from Params import Register

class Testcase(object):
    
##------------------Constant variables--------------------------
# Lookup tables for regs
    gprs64 = ['rax', 'rbx', 'rcx', 'rdx', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
    gprs32 = ['eax', 'ebx', 'ecx', 'edx', 'r9d', 'r10d', 'r11d', 'r12d', 'r13d', 'r14d', 'r15d']
    gprs16 = ['ax', 'bx', 'cx', 'dx', 'r9w', 'r10w', 'r11w', 'r12w', 'r13w', 'r14w', 'r15w']
    gprs8 = ['al', 'bl', 'cl', 'dl', 'r9l', 'r10l', 'r11l', 'r12l', 'r13l', 'r14l', 'r15l']
    fpus = ['st0', 'st1', 'st2', 'st3', 'st4', 'st5', 'st6', 'st7']
    mmxs = ['mm0', 'mm1', 'mm2', 'mm3', 'mm4', 'mm5', 'mm6', 'mm7']
    ks = ['k0', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7']
    bnds = ['bnd0', 'bnd1', 'bnd2', 'bnd3', 'bnd4', 'bnd5', 'bnd6', 'bnd7']
    xmms = ['xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 'xmm5', 'xmm6', 'xmm7', 'xmm8', 'xmm9',
    'xmm10', 'xmm11', 'xmm12', 'xmm13', 'xmm14', 'xmm15', 'xmm16', 'xmm17', 'xmm18', 'xmm19',
    'xmm20', 'xmm21', 'xmm22', 'xmm23', 'xmm24', 'xmm25', 'xmm26', 'xmm27', 'xmm28', 'xmm29',
    'xmm30', 'xmm31']
    ymms = ['ymm0', 'ymm1', 'ymm2', 'ymm3', 'ymm4', 'ymm5', 'ymm6', 'ymm7', 'ymm8', 'ymm9',
    'ymm10', 'ymm11', 'ymm12', 'ymm13', 'ymm14', 'ymm15', 'ymm16', 'ymm17', 'ymm18', 'ymm19',
    'ymm20', 'ymm21', 'ymm22', 'ymm23', 'ymm24', 'ymm25', 'ymm26', 'ymm27', 'ymm28', 'ymm29',
    'ymm30', 'ymm31']
    zmms = ['zmm0', 'zmm1', 'zmm2', 'zmm3', 'zmm4', 'zmm5', 'zmm6', 'zmm7', 'zmm8', 'zmm9',
    'zmm10', 'zmm11', 'zmm12', 'zmm13', 'zmm14', 'zmm15', 'zmm16', 'zmm17', 'zmm18', 'zmm19',
    'zmm20', 'zmm21', 'zmm22', 'zmm23', 'zmm24', 'zmm25', 'zmm26', 'zmm27', 'zmm28', 'zmm29',
    'zmm30', 'zmm31']

    ops = {'gpr64':gprs64, 'gpr32':gprs32, 'gpr16':gprs16, 'gpr8':gprs8, 'fpu':fpus, 'mmx':mmxs,  'k':ks, 'bnd':bnds, 'xmm':xmms, 'ymm':ymms, 'zmm':zmms}

# Create Single Precision 1.0
    sp1 =  '\t\t# create SP 1.0\n'
    sp1 += '\t\tvpcmpeqw xmm0, xmm0, xmm0\n'
    sp1 += '\t\tvpslld xmm0, xmm0, 25\t\t\t# logical left shift: 11111110..0 (25=32-(8-1))\n'
    sp1 += '\t\tvpsrld xmm0, xmm0, 2\t\t\t# logical right shift: 1 bit for sign; leading      mantissa bit is zero\n'
    sp1 += '\t\t# copy SP 1.0\n'
# Create Double Precision 1.0
    dp1 =  '\t\t# create DP 1.0\n'
    dp1 += '\t\tvpcmpeqw xmm0, xmm0, xmm0\t\t# all ones\n'
    dp1 += '\t\tvpsllq xmm0, xmm0, 54\t\t\t# logical left shift: 11111110..0 (54=64-(10-1))\n'
    dp1 += '\t\tvpsrlq xmm0, xmm0, 2\t\t\t# logical right shift: 1 bit for sign; leading      mantissa bit is zero\n'
# Create epilogue
    done = ('done:\n'
            '\t\tmov\trsp, rbp\n'
            '\t\tpop\trbp\n'
            '\t\tret\n'
            '.size latency, .-latency')
##----------------------------------------------------------------

# Constructor
    def __init__(self, _mnemonic, _param_list, _num_instr='12'):
        self.instr = _mnemonic.lower()
        self.param_list = _param_list
# num_instr must be an even number
        self.num_instr = str(ceil(int(_num_instr)/2)*2)
# Check for the number of operands and initialise the GPRs if necessary
        self.reg_a, self.reg_b, self.reg_c, self.gprPush, self.gprPop, self.zeroGPR, self.copy = self.__define_regs()
        self.num_regs = len(self.param_list)

# Create asm header 
        self.def_instr, self.ninstr, self.init, self.expand = self.__define_header()
# Create latency and throughput loop
        self.loop_lat = self.__define_loop_lat()
        self.loop_thrpt = self.__define_loop_thrpt()


    def write_testcase(self):
        regs = self.param_list
        extension = ''
# Add operands
        extension += ('-'+(self.reg_a if ('gpr' not in self.reg_a) else 'r'+self.reg_a[3:]) + ('_') +
                     (self.reg_b if ('gpr' not in self.reg_b) else 'r'+self.reg_b[3:]) + ('_') + 
                     (self.reg_c if ('gpr' not in self.reg_c) else 'r'+self.reg_c[3:]))
# Write latency file
        call(['mkdir', '-p', 'testcases'])
        f = open('./testcases/'+self.instr+extension+'.S', 'w')
        data = (self.def_instr+self.ninstr+self.init+self.dp1+self.expand+self.gprPush+self.zeroGPR+self.copy+self.loop_lat+self.gprPop+self.done)
        f.write(data)
        f.close()
# Write throughput file
        f = open('./testcases/'+self.instr+extension+'-TP.S', 'w')
        data = (self.def_instr+self.ninstr+self.init+self.dp1+self.expand+self.gprPush+self.zeroGPR+self.copy+self.loop_thrpt+self.gprPop+self.done)
        f.write(data)
        f.close()


# Check register
    def __define_regs(self):
        regs = self.param_list
        reg_a, reg_b, reg_c = ('', '', '')
        gprPush, gprPop, zeroGPR = ('', '', '')
        reg_a = regs[0].reg_type.lower()
        if(reg_a == 'gpr'):
            gprPush, gprPop, zeroGPR = self.__initialise_gprs()
            reg_a += str(regs[0].size)
        if(len(regs) > 1):
            reg_b = regs[1].reg_type.lower()
            if(reg_b == 'gpr'):
                reg_b += str(regs[1].size)
                if('gpr' not in reg_a):
                    gprPush, gprPop, zeroGPR = self.__initialise_gprs()
        if(len(regs) == 3):
            reg_c = regs[2].reg_type.lower()
            if(reg_c == 'gpr'):
                reg_c += str(regs[2].size)
                if(('gpr' not in reg_a) and ('gpr'not in reg_b)):
                    gprPush, gprPop, zeroGPR = self.__initialise_gprs()
        if(len(regs) == 1):
            copy = self.__copy_regs(regs[0])
        else:
            copy = self.__copy_regs(regs[1])
        return (reg_a, reg_b, reg_c, gprPush, gprPop, zeroGPR, copy)


# Initialise 11 general purpose registers and set them to zero
    def __initialise_gprs(self):
        gprPush = ''
        gprPop = ''
        zeroGPR = ''
        for reg in self.gprs64:
            gprPush += '\t\tpush    {}\n'.format(reg)
        for reg in reversed(self.gprs64):
            gprPop +=  '\t\tpop     {}\n'.format(reg)
        for reg in self.gprs64:
            zeroGPR += '\t\txor     {}, {}\n'.format(reg, reg)
        return (gprPush, gprPop, zeroGPR)


# Copy created values in specific register
    def __copy_regs(self, reg):
        copy = '\t\t# copy DP 1.0\n'
# Different handling for GPR, MMX and SSE/AVX registers
        if(reg.reg_type == 'GPR'):
            copy +=  '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][0])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][1])
            copy += '\t\t# Create DP 2.0\n'
            copy += '\t\tadd {}, {}\n'.format(self.ops['gpr64'][1], self.ops['gpr64'][0])
            copy += '\t\t# Create DP 0.5\n'
            copy += '\t\tdiv {}\n'.format(self.ops['gpr64'][0])
            copy += '\t\tmovq {}, {}\n'.format(self.ops['gpr64'][2], self.ops['gpr64'][0])
            copy +=  '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][0])
        elif(reg.reg_type == 'MMX'):
            copy +=  '\t\tvmovq {}, xmm0\n'.format(self.ops['mmx'][0])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['mmx'][1])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][0])
            copy += '\t\t# Create DP 2.0\n'
            copy += '\t\tadd {}, {}\n'.format(ops['mmx'][1], ops['mmx'][0])
            copy += '\t\t# Create DP 0.5\n'
            copy += '\t\tdiv {}\n'.format(self.ops['gpr64'][0])
            copy += '\t\tmovq {}, {}\n'.format(self.ops['mmx'][2], self.ops['gpr64'][0])
        elif(reg.reg_type == 'XMM' or reg.reg_type == 'YMM' or reg.reg_type == 'ZMM'):
            key = reg.reg_type.lower()
            copy +=  '\t\tvmovaps {}, {}\n'.format(self.ops[key][0], self.ops[key][0])
            copy += '\t\tvmovaps {}, {}\n'.format(self.ops[key][1], self.ops[key][0])
            copy += '\t\t# Create DP 2.0\n'
            copy += '\t\tvaddpd {}, {}, {}\n'.format(self.ops[key][1], self.ops[key][1], self.ops[key][1])
            copy += '\t\t# Create DP 0.5\n'
            copy += '\t\tvdivpd {}, {}, {}\n'.format(self.ops[key][2], self.ops[key][0], self.ops[key][1])
        else:
            copy = ''
        return copy


    def __define_header(self):
        def_instr = '#define INSTR '+self.instr+'\n'
        ninstr = '#define NINST '+self.num_instr+'\n'
        init = ('#define N edi\n' \
               '#define i r8d\n\n\n'
               '.intel_syntax noprefix\n'
               '.globl ninst\n'
               '.data\n'
               'ninst:\n'
               '.long NINST\n'
               '.text\n'
               '.globl latency\n'
               '.type latency, @function\n'
               '.align 32\n'
               'latency:\n'
               '\t\tpush\trbp\n'
               '\t\tmov\trbp, rsp\n'
               '\t\txor\ti, i\n'
               '\t\ttest\tN, N\n'
               '\t\tjle\tdone\n')
# Expand to AVX(512) if necessary
        expand = ''
        if(self.reg_a == 'ymm' or self.reg_b == 'ymm' or self.reg_c == 'ymm'):
            expand = ('\t\t# expand from SSE to AVX\n'
                      '\t\tvinsertf128 ymm0, ymm0, xmm0, 0x1\n')
        if(self.reg_a == 'zmm' or self.reg_b == 'zmm' or self.reg_c == 'zmm'):
            expand = ('\t\t# expand from SSE to AVX\n'
                      '\t\tvinsertf128 ymm0, ymm0, xmm0, 0x1\n'
                      '\t\t# expand from AVX to AVX512\n'
                      '\t\tvinsert64x4 zmm0, zmm0, ymm0, 0x1\n')
        return (def_instr, ninstr, init, expand)

# Create latency loop
    def __define_loop_lat(self):
        loop_lat = ('loop:\n'
                    '\t\tinc      i\n')
        if(self.num_regs == 1):
            for i in range(0, int(self.num_instr)):
                loop_lat += '\t\tINSTR    {}\n'.format(self.ops[self.reg_a][0])
        elif(self.num_regs == 2 and self.reg_a == self.reg_b):
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.reg_a][0], self.ops[self.reg_b][1])
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.reg_b][1], self.ops[self.reg_b][0])
        elif(self.num_regs == 2 and self.reg_a != self.reg_b):
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.reg_a][0], self.ops[self.reg_b][0])
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.reg_a][0], self.ops[self.reg_b][0])
        elif(self.num_regs == 3 and self.reg_a == self.reg_b):
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.reg_a][0], self.ops[self.reg_b][1],      self.ops[self.reg_c][0])
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.reg_a][1], self.ops[self.reg_b][0],      self.ops[self.reg_c][0])
        elif(self.num_regs == 3 and self.reg_a == self.reg_c):
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.reg_a][0], self.ops[self.reg_b][0],      self.ops[self.reg_c][0])
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.reg_a][1], self.ops[self.reg_b][0],      self.ops[self.reg_c][0])
        loop_lat += ('\t\tcmp      i, N\n'
                     '\t\tjl       loop\n')
        return loop_lat

# Create throughput loop
    def __define_loop_thrpt(self):
        loop_thrpt = ('loop:\n'
                      '\t\tinc      i\n')
        ext = ''
        ext1 = False
        ext2 = False
        if(self.num_regs == 2):
            ext1 = True
        if(self.num_regs == 3):
            ext1 = True
            ext2 = True
        for i in range(0, int(self.num_instr)):
            if(ext1):
                ext = ', {}'.format(self.ops[self.reg_b][i%3])
            if(ext2):
                ext += ', {}'.format(self.ops[self.reg_c][i%3])
            regNum = i%len(self.ops[self.reg_a]) if (i > 2) else (i+3)%len(self.ops[self.reg_a])
            loop_thrpt += '\t\tINSTR    {}{}\n'.format(self.ops[self.reg_a][regNum], ext)
        loop_thrpt += ('\t\tcmp      i, N\n'
                        '\t\tjl       loop\n')
        return loop_thrpt


    def __is_in_dir(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return True
        return False
