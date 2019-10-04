#!/usr/bin/env python3

import copy
import os

from jinja2 import Template

from osaca.parser import ParserAArch64v81, ParserX86ATT

BENCHMARK_DIR = os.path.expanduser('~/.osaca/benchmarks')


class IbenchAPI(object):
    def __init__(self, isa):
        self.isa = isa.lower()
        self.ibench_dir = os.path.join(BENCHMARK_DIR, 'ibench', self.isa)
        if not os.path.isdir(self.ibench_dir):
            os.makedirs(self.ibench_dir)

    def create_ubenchmark(self, instruction_form):
        if self.isa == 'aarch64':
            self.parser = ParserAArch64v81()
            tp_bench, lt_bench = self._create_ubench_aarch(instruction_form)
        elif self.isa == 'x86':
            self.parser = ParserX86ATT()
            tp_bench, lt_bench = self._create_ubench_x86(instruction_form)
        if tp_bench is None or lt_bench is None:
            return
        self._write_benchmark(self._get_ibench_name(instruction_form) + '-TP.S', tp_bench)
        self._write_benchmark(self._get_ibench_name(instruction_form) + '-LT.S', lt_bench)

    def import_ibench_output(self, filepath):
        # TODO
        assert os.path.exists(filepath)
        raise NotImplementedError

    ##########################################
    ##########################################

    def _write_benchmark(self, filename, content):
        with open(os.path.join(self.ibench_dir, filename), 'w') as f:
            f.write(content)

    def _get_ibench_name(self, instruction_form):
        name = ''
        op_sep = '_'
        name += instruction_form['instruction'].lower() + '-'
        operands = (
            instruction_form['operands']['operand_list']
            if 'operand_list' in instruction_form['operands']
            else instruction_form['operands']
        )
        if self.isa == 'aarch64':
            for op in operands:
                if 'register' in op:
                    name += op['register']['prefix']
                    name += op['register']['shape'] if 'shape' in op['register'] else ''
                elif 'immediate' in op:
                    name += 'i'
                else:
                    raise NotImplementedError
                name += op_sep
        elif self.isa == 'x86':
            for op in operands:
                if 'register' in op:
                    name += (
                        'r' if self.parser.is_gpr(op['register']) else op['register']['name'][0]
                    )
                elif 'immediate' in op:
                    name += 'i'
                name += op_sep
        else:
            raise NotImplementedError(
                'Currently only AArch64 and x86 architectures are supported.'
            )
        return name[:-1]

    def _create_ubench_aarch(self, instruction_form, num_instructions=8):
        loop_kernel_tp = ''
        loop_kernel_lt = ''
        vector_regs = False
        gp_regs = False
        mnemonic = instruction_form['instruction']
        operands = (
            instruction_form['operands']['operand_list']
            if 'operand_list' in instruction_form['operands']
            else instruction_form['operands']
        )
        for op in operands:
            if 'register' in op:
                if self.parser.is_gpr(op['register']):
                    gp_regs = True
                elif self.parser.is_vector_register(op['register']):
                    vector_regs = True
            elif 'memory' in op:
                return None, None
        num_regs = len([x for x in operands if 'register' in x])

        # throughput benchmark
        possible_regs_tp = list(range(5, 16)) + list(range(19, 29))
        i = 0
        while i < num_instructions * num_regs:
            ops = []
            for op in operands:
                name = possible_regs_tp[i % len(possible_regs_tp)]
                ops.append(self._get_aarch_op(op, name))
                i += 1 if 'register' in op else 0
            line = '\tINSTR    {}\n'.format(', '.join(ops))
            loop_kernel_tp += line

        # latency benchmark
        possible_regs_lt = list(range(5, 5 + num_regs))
        operands_lt = copy.deepcopy(operands)
        for i, x in enumerate(operands_lt):
            operands_lt[i] = (
                self._get_aarch_op(x, possible_regs_lt.pop())
                if 'register' in x
                else self._get_aarch_op(x, 0)
            )
        for i in range(0, 6):
            line = '\tINSTR    {}\n'.format(', '.join(operands_lt))
            loop_kernel_lt += line
            operands_lt = self._invert_regs(operands, operands_lt)

        args_tp = {
            'instr': mnemonic,
            'ninst': num_instructions,
            'vector_regs': vector_regs,
            'gp_regs': gp_regs,
            'loop_kernel': loop_kernel_tp,
        }

        args_lt = {
            'instr': mnemonic,
            'ninst': 6,
            'vector_regs': vector_regs,
            'gp_regs': gp_regs,
            'loop_kernel': loop_kernel_lt,
        }
        return template_aarch64.render(**args_tp), template_aarch64.render(**args_lt)

    def _create_ubench_x86(self, instruction_form, num_instructions=8):
        loop_kernel_tp = ''
        loop_kernel_lt = ''
        gp_regs = False
        AVX = False
        AVX512 = False
        mnemonic = instruction_form['instruction']
        operands = list(
            reversed(
                copy.deepcopy(
                    instruction_form['operands']['operand_list']
                    if 'operand_list' in instruction_form['operands']
                    else instruction_form['operands']
                )
            )
        )
        for op in operands:
            if 'register' in op:
                if self.parser.is_gpr(op['register']):
                    gp_regs = True
                elif op['register']['name'][0].lower() == 'y':
                    AVX = True
                elif op['register']['name'][0].lower() == 'z':
                    AVX512 = True
            elif 'memory' in op:
                return None, None
        num_regs = len([x for x in operands if 'register' in x])

        # throughput benchmark
        possible_regs_tp = {
            'gpr': ['ax', 'bx', 'cx', 'dx'] + list(range(9, 16)),
            'vector': list(range(0, 16)),
        }
        gpr_i = 0
        vector_i = 0
        for i in range(num_instructions):
            ops = []
            for op in operands:
                name = 0
                if 'register' in op:
                    if self.parser.is_gpr(op['register']):
                        name = possible_regs_tp['gpr'][gpr_i % len(possible_regs_tp['gpr'])]
                        gpr_i += 1
                    else:
                        name = possible_regs_tp['vector'][
                            vector_i % len(possible_regs_tp['vector'])
                        ]
                        vector_i += 1
                ops.append(self._get_x86_op(op, name))
            line = '\tINSTR    {}\n'.format(', '.join(ops))
            loop_kernel_tp += line

        # latency benchmark
        possible_regs_lt = list(range(9, 9 + num_regs))
        operands_lt = copy.deepcopy(operands)
        for i, x in enumerate(operands_lt):
            operands_lt[i] = (
                self._get_x86_op(x, possible_regs_lt.pop())
                if 'register' in x
                else self._get_x86_op(x, 0)
            )
        for i in range(0, 6):
            line = '\tINSTR    {}\n'.format(', '.join(operands_lt))
            loop_kernel_lt += line
            operands_lt = self._invert_regs(operands, operands_lt)

        args_tp = {
            'instr': mnemonic,
            'ninst': num_instructions,
            'gp_regs': gp_regs,
            'AVX': AVX,
            'AVX512': AVX512,
            'loop_kernel': loop_kernel_tp.rstrip(),
        }
        args_lt = {
            'instr': mnemonic,
            'ninst': num_instructions,
            'gp_regs': gp_regs,
            'AVX': AVX,
            'AVX512': AVX512,
            'loop_kernel': loop_kernel_lt.rstrip(),
        }
        return template_x86.render(**args_tp), template_x86.render(**args_lt)

    def _get_aarch_op(self, operand, name):
        operand = copy.deepcopy(operand)
        if 'register' in operand:
            operand['register']['name'] = name
            return self.parser.get_full_reg_name(operand['register'])
        elif 'immediate' in operand:
            return '#192'
        else:
            raise NotImplementedError('Only immediates and register in benchmark allowed')

    def _get_x86_op(self, operand, name):
        operand = copy.deepcopy(operand)
        if 'register' in operand:
            reg_type = self.parser.get_reg_type(operand['register'])
            reg_type = reg_type[-1] if reg_type.startswith('gp') else reg_type
            operand['register']['name'] = reg_type + str(name)
            return self.parser.get_full_reg_name(operand['register'])
        elif 'immediate' in operand:
            return '192'
        else:
            raise NotImplementedError('Only immediates and register in benchmark allowed')

    def _invert_regs(self, operands, operand_str_list):
        reg_indices = [i for i, op in enumerate(operands) if 'register' in op]
        reg_indices_inverted = list(reversed(reg_indices))
        operands_tmp = [None for x in operand_str_list]
        for i in range(len(operand_str_list)):
            operands_tmp[i] = (
                operand_str_list[reg_indices_inverted[i]]
                if i in reg_indices
                else operand_str_list[i]
            )
        return operands_tmp


template_aarch64 = Template(
    '''#define INSTR {{ instr }}
#define NINST {{ ninst }}
#define N x0

.globl ninst
.data
ninst:
.long NINST
.text
.globl benchmark
.type benchmark, @function
.align 32
benchmark:
{% if vector_regs %}
    # push callee-save registers onto stack
    sub     sp, sp, #64
    st1     {v8.4s, v9.4s, v10.4s, v11.4s}, [sp]
    sub     sp, sp, #64
    st1     {v12.4s, v13.4s, v14.4s, v15.4s}, [sp]
    mov     x4, N
    fmov    v0.2d, #1.20000000
    fmov    v1.2d, #1.23000000
    fmov    v2.2d, #1.23400000
    fmov    v3.2d, #1.23410000
    fmov    v4.2d, #1.23412000
    fmov    v5.2d, #1.23412300
    fmov    v6.2d, #1.23412340
    fmov    v7.2d, #1.23412341
    fmov    v8.2d, #2.34123412
    fmov    v9.2d, #2.34123410
    fmov    v10.2d, #2.34123400
    fmov    v11.2d, #2.34123000
    fmov    v12.2d, #2.34120000
    fmov    v13.2d, #2.34100000
    fmov    v14.2d, #2.34000000
    fmov    v15.2d, #2.30000000
{% endif %}
{% if gp_regs %}
    # push callee-save register onto stack
    push {x19-x28}
{% endif %}

loop:
    subs    x4, x4, #1
{{ loop_kernel }}
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
    pop {x19-x28}
{% endif %}

    ret
.size benchmark, .-benchmark
'''
)

template_x86 = Template(
    '''#define INSTR {{ instr }}
#define NINST {{ ninst }}
#define N edi
#define i r8d


.intel_syntax noprefix
.globl ninst
.data
ninst:
.long NINST
.text
.globl benchmark
.type benchmark, @function
.align 32
benchmark:
    push      rbp
    mov       rbp, rsp
    xor       i, i
    test      N, N
    jle       done
{% if gp_regs %}
    push    rax
    push    rbx
    push    rcx
    push    rdx
    push    r9
    push    r10
    push    r11
    push    r12
    push    r13
    push    r14
    push    r15
    mov     rax, 1
    mov     rbx, 2
    mov     rcx, 3
    mov     rdx, 4
    mov     r9,  5
    mov     r10, 6
    mov     r11, 7
    mov     r12, 8
    mov     r13, 9
    mov     r14, 10
    mov     r15, 11
{% endif %}
    # create SP 1.0
    vpcmpeqw xmm0, xmm0, xmm0   # all ones
    vpslld xmm0, xmm0, 25       # logical left shift: 11111110..0 (25 = 32 - (8 - 1))
    vpsrld xmm0, xmm0, 2        # logical right shift: 1 bit for sign; leading mantissa bit is 0
{% if AVX or AVX512 %}
    # expand from SSE to AVX
    vinsertf128 ymm0, ymm0, xmm0, 0x1
{% endif %}
{% if AVX512 %}
    # expand from AVX to AVX-512
    vinsertf64x4 zmm0, zmm0, ymm0, 0x1
{% endif %}
{% if not AVX and not AVX512 %}
    # create SP 2.0
    vaddps xmm1, xmm0, xmm0
    # create SP 0.5
    vdivps xmm2, xmm0, xmm1
{% endif %}
{% if AVX and not AVX512 %}
    # create SP 2.0
    vaddps ymm1, ymm0, ymm0
    # create SP 0.5
    vdivps ymm2, ymm0, ymm1
{% endif %}
{% if AVX512 %}
    # create AVX-512 DP 2.0
    vaddps zmm1, zmm0, zmm0
    # create AVX-512 DP 0.5
    vdivps zmm2, zmm0, zmm1
{% endif %}
loop:
    inc     i
{{ loop_kernel }}
    cmp     i, N
    jl     loop
done:
{% if gp_regs %}
    pop     r15
    pop     r14
    pop     r13
    pop     r12
    pop     r11
    pop     r10
    pop     r9
    pop     rdx
    pop     rcx
    pop     rbx
    pop     rax
{% endif %}
    mov  rsp, rbp
    pop rbp
    ret
.size benchmark, .-benchmark
'''
)
