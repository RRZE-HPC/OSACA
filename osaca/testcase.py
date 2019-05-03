#!/usr/bin/env python3

import os
from subprocess import call
from math import ceil

from osaca.param import Register, MemAddr, Parameter
#from param import Register, MemAddr, Parameter


class Testcase(object):
    # ------------------Constant variables--------------------------
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
            'xmm10', 'xmm11', 'xmm12', 'xmm13', 'xmm14', 'xmm15']
    ymms = ['ymm0', 'ymm1', 'ymm2', 'ymm3', 'ymm4', 'ymm5', 'ymm6', 'ymm7', 'ymm8', 'ymm9',
            'ymm10', 'ymm11', 'ymm12', 'ymm13', 'ymm14', 'ymm15']
    zmms = ['zmm0', 'zmm1', 'zmm2', 'zmm3', 'zmm4', 'zmm5', 'zmm6', 'zmm7', 'zmm8', 'zmm9',
            'zmm10', 'zmm11', 'zmm12', 'zmm13', 'zmm14', 'zmm15']
    # Lookup table for memory
    mems = ['[rip+PI]', '[rip+PI]', '[rip+PI]', '[rip+PI]', '[rip+PI]', '[rip+PI]', '[rip+PI]',
            '[rip+PI]']
    # Lookup table for immediates
    imds = ['1', '2', '13', '22', '8', '78', '159', '222', '3', '9', '5', '55', '173', '317',
            '254', '255']
    # TODO Differentiate between AVX512 (with additional xmm16-31) and the rest
    #       ...
    #       ...
    # end TODO

    ops = {'gpr64': gprs64, 'gpr32': gprs32, 'gpr16': gprs16, 'gpr8': gprs8, 'fpu': fpus,
           'mmx': mmxs, 'k': ks, 'bnd': bnds, 'xmm': xmms, 'ymm': ymms, 'zmm': zmms, 'mem': mems,
           'imd': imds}

    # Create Single Precision 1.0
    sp1 = ('\t\t# create SP 1.0\n'
           '\t\tvpcmpeqw xmm0, xmm0, xmm0\n'
           '\t\tvpslld xmm0, xmm0, 25\t\t\t# logical left shift: 11111110..0 (25=32-(8-1))\n'
           '\t\tvpsrld xmm0, xmm0, 2\t\t\t# logical right shift: 1 bit for sign; leading '
           'mantissa bit is zero\n'
           '\t\t# copy SP 1.0\n')
    # Create Double Precision 1.0
    dp1 = ('\t\t# create DP 1.0\n'
           '\t\tvpcmpeqw xmm0, xmm0, xmm0\t\t# all ones\n'
           '\t\tvpsllq xmm0, xmm0, 54\t\t\t# logical left shift: 11111110..0 (54=64-(10-1))\n'
           '\t\tvpsrlq xmm0, xmm0, 2\t\t\t# logical right shift: 1 bit for sign; leading '
           'mantissa bit is zero\n')
    # Create epilogue
    done = ('done:\n'
            '\t\tmov\trsp, rbp\n'
            '\t\tpop\trbp\n'
            '\t\tret\n'
            '.size latency, .-latency')
    # ----------------------------------------------------------------

    # Constructor
    def __init__(self, _mnemonic, _param_list, _num_instr='32'):
        self.instr = _mnemonic.lower()
        self.param_list = _param_list
        # num_instr must be an even number
        self.num_instr = str(ceil(int(_num_instr)/2)*2)
        # Check for the number of operands and initialise the GPRs if necessary
        self.op_a, self.op_b, self.op_c, self.gprPush, self.gprPop, self.zeroGPR, self.copy = \
            self.__define_operands()
        self.num_operands = len(self.param_list)

        # Create asm header
        self.def_instr, self.ninstr, self.init, self.expand = self.__define_header()
        # Create latency and throughput loop
        self.loop_lat = self.__define_loop_lat()
        self.loop_thrpt = self.__define_loop_thrpt()
        # Create extension for testcase name
        sep0 = '-' if (self.num_operands > 0) else ''
        sep1 = '_' if (self.num_operands > 1) else ''
        sep2 = '_' if (self.num_operands > 2) else ''
        self.extension = (sep0 + (self.op_a if ('gpr' not in self.op_a) else 'r' + self.op_a[3:])
                          + sep1 + (self.op_b if ('gpr' not in self.op_b) else 'r' + self.op_b[3:])
                          + sep2 + (self.op_c if ('gpr' not in self.op_c) else 'r' + self.op_c[3:]))

    def write_testcase(self, tp=True, lt=True):
        """
        Write testcase for class attributes in a file.

        Parameters
        ----------
        tp : bool
            Controls if throughput testcase should be written
            (default True)

        lt : bool
            Controls if latency testcase should be written
            (default True)
        """
        osaca_dir = os.path.expanduser('~') + '/.osaca/'
        if lt:
            # Write latency file
            call(['mkdir', '-p', osaca_dir + 'benchmarks'])
            f = open(osaca_dir + 'benchmarks/'+self.instr+self.extension+'.S', 'w')
            data = (self.def_instr + self.ninstr + self.init + self.dp1 + self.expand + self.gprPush
                    + self.zeroGPR + self.copy + self.loop_lat + self.gprPop + self.done)
            f.write(data)
            f.close()
        if tp:
            # Write throughput file
            call(['mkdir', '-p', osaca_dir + 'benchmarks'])
            f = open(osaca_dir + 'benchmarks/' + self.instr + self.extension
                     + '-TP.S', 'w')
            data = (self.def_instr + self.ninstr + self.init + self.dp1 + self.expand + self.gprPush
                    + self.zeroGPR + self.copy + self.loop_thrpt + self.gprPop + self.done)
            f.write(data)
            f.close()

    # Check operands
    def __define_operands(self):
        """
        Check for the number of operands and initialise the GPRs if necessary.

        Returns
        -------
        (str, str, str, str, str, str)
            String tuple containing types of operands and if needed push/pop operations, the
            initialisation of general purpose regs and the copy if registers.
        """
        operands = self.param_list
        op_a, op_b, op_c = ('', '', '')
        gpr_push, gpr_pop, zero_gpr = ('', '', '')
        if len(operands) > 0:
            if isinstance(operands[0], Register):
                op_a = operands[0].reg_type.lower()
            elif isinstance(operands[0], MemAddr):
                op_a = 'mem'
            elif isinstance(operands[0], Parameter) and str(operands[0]) == 'IMD':
                op_a = 'imd'
            if op_a == 'gpr':
                gpr_push, gpr_pop, zero_gpr = self.__initialise_gprs()
                op_a += str(operands[0].size)
        if len(operands) > 1:
            if isinstance(operands[1], Register):
                op_b = operands[1].reg_type.lower()
            elif isinstance(operands[1], MemAddr):
                op_b = 'mem'
            elif isinstance(operands[1], Parameter) and str(operands[1]) == 'IMD':
                op_b = 'imd'
            if op_b == 'gpr':
                op_b += str(operands[1].size)
                if 'gpr' not in op_a:
                    gpr_push, gpr_pop, zero_gpr = self.__initialise_gprs()
        if len(operands) == 3:
            if isinstance(operands[2], Register):
                op_c = operands[2].reg_type.lower()
            elif isinstance(operands[2], MemAddr):
                op_c = 'mem'
            elif isinstance(operands[2], Parameter) and str(operands[2]) == 'IMD':
                op_c = 'imd'
            if op_c == 'gpr':
                op_c += str(operands[2].size)
                if ('gpr' not in op_a) and ('gpr' not in op_b):
                    gpr_push, gpr_pop, zero_gpr = self.__initialise_gprs()
        if len(operands) == 1 and isinstance(operands[0], Register):
            copy = self.__copy_regs(operands[0])
        elif len(operands) > 1 and isinstance(operands[1], Register):
            copy = self.__copy_regs(operands[1])
        elif len(operands) > 2 and isinstance(operands[2], Register):
            copy = self.__copy_regs(operands[1])
        else:
            copy = ''
        return op_a, op_b, op_c, gpr_push, gpr_pop, zero_gpr, copy

    def __initialise_gprs(self):
        """
        Initialize eleven general purpose registers and set them to zero.

        Returns
        -------
        (str, str, str)
            String tuple for push, pop and initalisation operations
        """

        gpr_push = ''
        gpr_pop = ''
        zero_gpr = ''
        for reg in self.gprs64:
            gpr_push += '\t\tpush    {}\n'.format(reg)
        for reg in reversed(self.gprs64):
            gpr_pop += '\t\tpop     {}\n'.format(reg)
        for reg in self.gprs64:
            zero_gpr += '\t\txor     {}, {}\n'.format(reg, reg)
        return gpr_push, gpr_pop, zero_gpr


    # Copy created values in specific register
    def __copy_regs(self, reg):
        """
        Copy created values in specific register.

        Parameters
        ----------
        reg : Register
            Register for copying the value

        Returns
        -------
        str
            String containing the copy instructions
        """
        copy = '\t\t# copy DP 1.0\n'
        # Different handling for GPR, MMX and SSE/AVX registers
        if reg.reg_type == 'GPR':
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][0])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][1])
            copy += '\t\t# Create DP 2.0\n'
            copy += '\t\tadd {}, {}\n'.format(self.ops['gpr64'][1], self.ops['gpr64'][0])
            copy += '\t\t# Create DP 0.5\n'
            copy += '\t\tdiv {}\n'.format(self.ops['gpr64'][0])
            copy += '\t\tmovq {}, {}\n'.format(self.ops['gpr64'][2], self.ops['gpr64'][0])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][0])
        elif reg.reg_type == 'MMX':
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['mmx'][0])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['mmx'][1])
            copy += '\t\tvmovq {}, xmm0\n'.format(self.ops['gpr64'][0])
            copy += '\t\t# Create DP 2.0\n'
            copy += '\t\tadd {}, {}\n'.format(self.ops['mmx'][1], self.ops['mmx'][0])
            copy += '\t\t# Create DP 0.5\n'
            copy += '\t\tdiv {}\n'.format(self.ops['gpr64'][0])
            copy += '\t\tmovq {}, {}\n'.format(self.ops['mmx'][2], self.ops['gpr64'][0])
        elif reg.reg_type == 'XMM' or reg.reg_type == 'YMM' or reg.reg_type == 'ZMM':
            key = reg.reg_type.lower()
            copy += '\t\tvmovaps {}, {}\n'.format(self.ops[key][0], self.ops[key][0])
            copy += '\t\tvmovaps {}, {}\n'.format(self.ops[key][1], self.ops[key][0])
            copy += '\t\t# Create DP 2.0\n'
            copy += '\t\tvaddpd {}, {}, {}\n'.format(self.ops[key][1], self.ops[key][1],
                                                     self.ops[key][1])
            copy += '\t\t# Create DP 0.5\n'
            copy += '\t\tvdivpd {}, {}, {}\n'.format(self.ops[key][2], self.ops[key][0],
                                                     self.ops[key][1])
        else:
            copy = ''
        return copy

    def __define_header(self):
        """
        Define header.

        Returns
        -------
        (str, str, str, str)
            String tuple containing the header, value initalisations and extensions
        """
        def_instr = '#define INSTR '+self.instr+'\n'
        ninstr = '#define NINST '+self.num_instr+'\n'
        pi = ('PI:\n'
              '.long  0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, '   # 128 bit
              '0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, '          # 256 bit
              '0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, '          # 384 bit
              '0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9\n')         # 512 bit
        init = ('#define N edi\n'
                '#define i r8d\n\n\n'
                '.intel_syntax noprefix\n'
                '.globl ninst\n'
                '.data\n'
                'ninst:\n'
                '.long NINST\n'
                '.align 32\n'
                + pi +
                '.text\n'
                '.globl latency\n'
                '.type latency, @function\n'
                '.align 32\n'
                'latency:\n'
                '\t\tpush      rbp\n'
                '\t\tmov       rbp, rsp\n'
                '\t\txor       i, i\n'
                '\t\ttest      N, N\n'
                '\t\tjle       done\n')
        # Expand to AVX(512) if necessary
        expand = ''
        if self.op_a == 'ymm' or self.op_b == 'ymm' or self.op_c == 'ymm':
            expand = ('\t\t# expand from SSE to AVX\n'
                      '\t\tvinsertf128 ymm0, ymm0, xmm0, 0x1\n')
        if self.op_a == 'zmm' or self.op_b == 'zmm' or self.op_c == 'zmm':
            expand = ('\t\t# expand from SSE to AVX\n'
                      '\t\tvinsertf128 ymm0, ymm0, xmm0, 0x1\n'
                      '\t\t# expand from AVX to AVX512\n'
                      '\t\tvinsert64x4 zmm0, zmm0, ymm0, 0x1\n')
        return def_instr, ninstr, init, expand

    def __define_loop_lat(self):
        """
        Create latency loop.

        Returns
        -------
        str
            Latency loop as string
        """
        loop_lat = ('loop:\n'
                    '\t\tinc      i\n')
        if self.num_operands == 0:
            for i in range(0, int(self.num_instr)):
                loop_lat += '\t\tINSTR\n'
        if self.num_operands == 1:
            for i in range(0, int(self.num_instr)):
                loop_lat += '\t\tINSTR    {}\n'.format(self.ops[self.op_a][0])
        elif self.num_operands == 2 and self.op_a == self.op_b:
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.op_a][0],
                                                           self.ops[self.op_b][1])
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.op_b][1],
                                                           self.ops[self.op_b][0])
        elif self.num_operands == 2 and self.op_a != self.op_b:
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.op_a][0],
                                                           self.ops[self.op_b][0])
                loop_lat += '\t\tINSTR    {}, {}\n'.format(self.ops[self.op_a][0],
                                                           self.ops[self.op_b][0])
        elif self.num_operands == 3 and self.op_a == self.op_b:
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.op_a][0],
                                                               self.ops[self.op_b][1],
                                                               self.ops[self.op_c][0])
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.op_a][1],
                                                               self.ops[self.op_b][0],
                                                               self.ops[self.op_c][0])
        elif self.num_operands == 3 and self.op_a == self.op_c:
            for i in range(0, int(self.num_instr), 2):
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.op_a][0],
                                                               self.ops[self.op_b][0],
                                                               self.ops[self.op_c][0])
                loop_lat += '\t\tINSTR    {}, {}, {}\n'.format(self.ops[self.op_a][1],
                                                               self.ops[self.op_b][0],
                                                               self.ops[self.op_c][0])
        loop_lat += ('\t\tcmp      i, N\n'
                     '\t\tjl       loop\n')
        return loop_lat

    def __define_loop_thrpt(self):
        """
        Create throughput loop.

        Returns
        -------
        str
            Throughput loop as string
        """
        loop_thrpt = ('loop:\n'
                      '\t\tinc      i\n')
        ext = ''
        ext1 = False
        ext2 = False
        if self.num_operands == 2:
            ext1 = True
        if self.num_operands == 3:
            ext1 = True
            ext2 = True
        for i in range(0, int(self.num_instr)):
            if self.num_operands == 0:
                loop_thrpt += '\t\tINSTR\n'
                continue
            if ext1:
                ext = ', {}'.format(self.ops[self.op_b][i % 3])
            if ext2:
                ext += ', {}'.format(self.ops[self.op_c][i % 3])
            reg_num = (i % (len(self.ops[self.op_a]) - 3)) + 3
            loop_thrpt += '\t\tINSTR    {}{}\n'.format(self.ops[self.op_a][reg_num], ext)
        loop_thrpt += ('\t\tcmp      i, N\n'
                       '\t\tjl       loop\n')
        return loop_thrpt

    def is_in_dir(self):
        """
        Check if testcases with the same name already exist in testcase
        directory.

        Returns
        -------
        (bool, bool)
            True    if file is in directory
            False   if file is not in directory
            While the first value stands for the throughput testcase
            and the second value stands for the latency testcase
        """
        tp = False
        lt = False
        name = self.instr+self.extension
        for root, dirs, files in os.walk(os.path.dirname(__file__)+'/benchmarks'):
            if (name + '-tp.S') in files:
                tp = True
            if name+'.S' in files:
                lt = True
        return tp, lt

    def get_entryname(self):
        """
        Return the name of the entry the instruction form would be the data file

        Returns
        -------
        str
            The composited string out of instruction mnemonic and operands
        """
        name = self.instr+self.extension
        return name
