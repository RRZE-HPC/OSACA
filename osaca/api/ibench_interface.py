#!/usr/bin/env python3

import os

from jinja2 import Template


class IbenchAPI(object):
    def __init__(self, isa):
        # TODO
        self.isa = isa.lower()

    def create_ubenchmark(self):
        # TODO
        if self.isa == 'aarch64':
            self.create_ubench_aarch64()
        elif self.isa == 'x86':
            self.create_ubench_x86()

    def import_ibench_output(self, filepath):
        # TODO
        assert os.path.exists(filepath)
        raise NotImplementedError

    def create_ubench_aarch(self):
        # TODO
        raise NotImplementedError

    def create_ubench_x86(self):
        # TODO
        raise NotImplementedError


# TODO
# template_x86 = Template()
template_aarch64 = Template(
    '''
#define INSTR {{ instr }}
#define NINST {{ ninst }}
#define N x0

.globl ninst
.data
ninst:
.long NINST
{% if imd %}
IMD:
.long  0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9
{% endif %}
.text
.globl latency
.type latency, @function
.align 32
latency:

{% if vector_regs %}
    # push callee-save registers onto stack
    sub     sp, sp, #64
    st1     {v8.4s, v9.4s, v10.4s, v11.4s}, [sp]
    sub     sp, sp, #64
    st1     {v12.4s, v13.4s, v14.4s, v15.4s}, [sp]
    mov     x4, N
    fmov    v0.2d, #1.00000000
    fmov    v1.2d, #1.00000000
    fmov    v2.2d, #1.00000000
    fmov    v3.2d, #1.00000000
    fmov    v4.2d, #1.00000000
    fmov    v5.2d, #1.00000000
    fmov    v6.2d, #1.00000000
    fmov    v7.2d, #1.00000000
    fmov    v8.2d, #1.00000000
    fmov    v9.2d, #1.00000000
    fmov    v10.2d, #1.00000000
    fmov    v11.2d, #1.00000000
    fmov    v12.2d, #1.00000000
    fmov    v13.2d, #1.00000000
    fmov    v14.2d, #1.00000000
    fmov    v15.2d, #1.00000000
{% endif %}
{% if gp_regs %}
{% endif %}

loop:
{{ loop_kernel }}
    subs    x4, x4, #1
    bne     loop
done:

{% if vector_regs %}
    # pop callee-save registers from stack
    ld1     {v12.4s, v13.4s, v14.4s, v15.4s}, [sp]
    add     sp, sp, #64
    ld1     {v8.4s, v9.4s, v10.4s, v11.4s}, [sp]
    add     sp, sp, #64
{% endif %}
{% if gp_regs %}
{% endif %}

    ret
.size latency, .-latency
'''
)
