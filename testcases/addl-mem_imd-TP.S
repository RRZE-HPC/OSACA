#define INSTR addl
#define NINST 64
#define N edi
#define i r8d


.intel_syntax noprefix
.globl ninst
.data
ninst:
.long NINST
.align 32
PI:
.long  0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9, 0xf01b866e, 0x400921f9
.text
.globl latency
.type latency, @function
.align 32
latency:
		push      rbp
		mov       rbp, rsp
		xor       i, i
		test      N, N
		jle       done
		# create DP 1.0
		vpcmpeqw xmm0, xmm0, xmm0		# all ones
		vpsllq xmm0, xmm0, 54			# logical left shift: 11111110..0 (54=64-(10-1))
		vpsrlq xmm0, xmm0, 2			# logical right shift: 1 bit for sign; leading      mantissa bit is zero
loop:
		inc      i
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		INSTR    [rip+PI], 2
		INSTR    [rip+PI], 13
		INSTR    [rip+PI], 1
		cmp      i, N
		jl       loop
done:
		mov	rsp, rbp
		pop	rbp
		ret
.size latency, .-latency