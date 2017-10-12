#define INSTR vmovsd
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
		INSTR    xmm3, [rip+PI]
		INSTR    xmm4, [rip+PI]
		INSTR    xmm5, [rip+PI]
		INSTR    xmm6, [rip+PI]
		INSTR    xmm7, [rip+PI]
		INSTR    xmm8, [rip+PI]
		INSTR    xmm9, [rip+PI]
		INSTR    xmm10, [rip+PI]
		INSTR    xmm11, [rip+PI]
		INSTR    xmm12, [rip+PI]
		INSTR    xmm13, [rip+PI]
		INSTR    xmm14, [rip+PI]
		INSTR    xmm15, [rip+PI]
		INSTR    xmm3, [rip+PI]
		INSTR    xmm4, [rip+PI]
		INSTR    xmm5, [rip+PI]
		INSTR    xmm6, [rip+PI]
		INSTR    xmm7, [rip+PI]
		INSTR    xmm8, [rip+PI]
		INSTR    xmm9, [rip+PI]
		INSTR    xmm10, [rip+PI]
		INSTR    xmm11, [rip+PI]
		INSTR    xmm12, [rip+PI]
		INSTR    xmm13, [rip+PI]
		INSTR    xmm14, [rip+PI]
		INSTR    xmm15, [rip+PI]
		INSTR    xmm3, [rip+PI]
		INSTR    xmm4, [rip+PI]
		INSTR    xmm5, [rip+PI]
		INSTR    xmm6, [rip+PI]
		INSTR    xmm7, [rip+PI]
		INSTR    xmm8, [rip+PI]
		INSTR    xmm9, [rip+PI]
		INSTR    xmm10, [rip+PI]
		INSTR    xmm11, [rip+PI]
		INSTR    xmm12, [rip+PI]
		INSTR    xmm13, [rip+PI]
		INSTR    xmm14, [rip+PI]
		INSTR    xmm15, [rip+PI]
		INSTR    xmm3, [rip+PI]
		INSTR    xmm4, [rip+PI]
		INSTR    xmm5, [rip+PI]
		INSTR    xmm6, [rip+PI]
		INSTR    xmm7, [rip+PI]
		INSTR    xmm8, [rip+PI]
		INSTR    xmm9, [rip+PI]
		INSTR    xmm10, [rip+PI]
		INSTR    xmm11, [rip+PI]
		INSTR    xmm12, [rip+PI]
		INSTR    xmm13, [rip+PI]
		INSTR    xmm14, [rip+PI]
		INSTR    xmm15, [rip+PI]
		INSTR    xmm3, [rip+PI]
		INSTR    xmm4, [rip+PI]
		INSTR    xmm5, [rip+PI]
		INSTR    xmm6, [rip+PI]
		INSTR    xmm7, [rip+PI]
		INSTR    xmm8, [rip+PI]
		INSTR    xmm9, [rip+PI]
		INSTR    xmm10, [rip+PI]
		INSTR    xmm11, [rip+PI]
		INSTR    xmm12, [rip+PI]
		INSTR    xmm13, [rip+PI]
		INSTR    xmm14, [rip+PI]
		cmp      i, N
		jl       loop
done:
		mov	rsp, rbp
		pop	rbp
		ret
.size latency, .-latency