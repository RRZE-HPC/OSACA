#define INSTR vmulpd
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
		# expand from SSE to AVX
		vinsertf128 ymm0, ymm0, xmm0, 0x1
		# copy DP 1.0
		vmovaps ymm0, ymm0
		vmovaps ymm1, ymm0
		# Create DP 2.0
		vaddpd ymm1, ymm1, ymm1
		# Create DP 0.5
		vdivpd ymm2, ymm0, ymm1
loop:
		inc      i
		INSTR    ymm3, ymm0, ymm0
		INSTR    ymm4, ymm1, ymm1
		INSTR    ymm5, ymm2, ymm2
		INSTR    ymm6, ymm0, ymm0
		INSTR    ymm7, ymm1, ymm1
		INSTR    ymm8, ymm2, ymm2
		INSTR    ymm9, ymm0, ymm0
		INSTR    ymm10, ymm1, ymm1
		INSTR    ymm11, ymm2, ymm2
		INSTR    ymm12, ymm0, ymm0
		INSTR    ymm13, ymm1, ymm1
		INSTR    ymm14, ymm2, ymm2
		INSTR    ymm15, ymm0, ymm0
		INSTR    ymm3, ymm1, ymm1
		INSTR    ymm4, ymm2, ymm2
		INSTR    ymm5, ymm0, ymm0
		INSTR    ymm6, ymm1, ymm1
		INSTR    ymm7, ymm2, ymm2
		INSTR    ymm8, ymm0, ymm0
		INSTR    ymm9, ymm1, ymm1
		INSTR    ymm10, ymm2, ymm2
		INSTR    ymm11, ymm0, ymm0
		INSTR    ymm12, ymm1, ymm1
		INSTR    ymm13, ymm2, ymm2
		INSTR    ymm14, ymm0, ymm0
		INSTR    ymm15, ymm1, ymm1
		INSTR    ymm3, ymm2, ymm2
		INSTR    ymm4, ymm0, ymm0
		INSTR    ymm5, ymm1, ymm1
		INSTR    ymm6, ymm2, ymm2
		INSTR    ymm7, ymm0, ymm0
		INSTR    ymm8, ymm1, ymm1
		INSTR    ymm9, ymm2, ymm2
		INSTR    ymm10, ymm0, ymm0
		INSTR    ymm11, ymm1, ymm1
		INSTR    ymm12, ymm2, ymm2
		INSTR    ymm13, ymm0, ymm0
		INSTR    ymm14, ymm1, ymm1
		INSTR    ymm15, ymm2, ymm2
		INSTR    ymm3, ymm0, ymm0
		INSTR    ymm4, ymm1, ymm1
		INSTR    ymm5, ymm2, ymm2
		INSTR    ymm6, ymm0, ymm0
		INSTR    ymm7, ymm1, ymm1
		INSTR    ymm8, ymm2, ymm2
		INSTR    ymm9, ymm0, ymm0
		INSTR    ymm10, ymm1, ymm1
		INSTR    ymm11, ymm2, ymm2
		INSTR    ymm12, ymm0, ymm0
		INSTR    ymm13, ymm1, ymm1
		INSTR    ymm14, ymm2, ymm2
		INSTR    ymm15, ymm0, ymm0
		INSTR    ymm3, ymm1, ymm1
		INSTR    ymm4, ymm2, ymm2
		INSTR    ymm5, ymm0, ymm0
		INSTR    ymm6, ymm1, ymm1
		INSTR    ymm7, ymm2, ymm2
		INSTR    ymm8, ymm0, ymm0
		INSTR    ymm9, ymm1, ymm1
		INSTR    ymm10, ymm2, ymm2
		INSTR    ymm11, ymm0, ymm0
		INSTR    ymm12, ymm1, ymm1
		INSTR    ymm13, ymm2, ymm2
		INSTR    ymm14, ymm0, ymm0
		cmp      i, N
		jl       loop
done:
		mov	rsp, rbp
		pop	rbp
		ret
.size latency, .-latency