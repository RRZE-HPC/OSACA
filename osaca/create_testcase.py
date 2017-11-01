#!/usr/bin/env python3

from param import Register, MemAddr, Parameter
from testcase import Testcase

# Choose out of various operands
reg8 = Register('al')
reg16 = Register('ax')
reg32 = Register('eax')
reg64 = Register('rax')
xmm = Register('xmm0')
ymm = Register('ymm0')
zmm = Register('zmm0')
mem0 = MemAddr('(%rax, %esi, 4)')
imd1 = Parameter('IMD')


# -----------------------------------------------
# -USER INPUT------------------------------------
# -----------------------------------------------
#  Enter your mnemonic
mnemonic = 'add'

# Define your operands. If you don't need it, just type in None
dst = mem0
op1 = imd1
op2 = None

# Define the number of instructions per loop (default: 12)
per_loop = '32'

# -----------------------------------------------
# -----------------------------------------------

# Start
operands = [x for x in [dst, op1, op2] if x is not None]
opListStr = ', '.join([str(x) for x in operands])
print('Create Testcase for {} {}'.format(mnemonic, opListStr), end='')
tc = Testcase(mnemonic, operands, per_loop)
tc.write_testcase()
print('  --------> SUCCEEDED')
