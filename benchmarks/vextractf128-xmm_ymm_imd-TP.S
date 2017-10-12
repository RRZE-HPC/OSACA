#define INSTR vextractf128
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
		INSTR    xmm3, ymm0, 1
		INSTR    xmm4, ymm1, 2
		INSTR    xmm5, ymm2, 13
		INSTR    xmm6, ymm0, 1
		INSTR    xmm7, ymm1, 2
		INSTR    xmm8, ymm2, 13
		INSTR    xmm9, ymm0, 1
		INSTR    xmm10, ymm1, 2
		INSTR    xmm11, ymm2, 13
		INSTR    xmm12, ymm0, 1
		INSTR    xmm13, ymm1, 2
		INSTR    xmm14, ymm2, 13
		INSTR    xmm15, ymm0, 1
		INSTR    xmm3, ymm1, 2
		INSTR    xmm4, ymm2, 13
		INSTR    xmm5, ymm0, 1
		INSTR    xmm6, ymm1, 2
		INSTR    xmm7, ymm2, 13
		INSTR    xmm8, ymm0, 1
		INSTR    xmm9, ymm1, 2
		INSTR    xmm10, ymm2, 13
		INSTR    xmm11, ymm0, 1
		INSTR    xmm12, ymm1, 2
		INSTR    xmm13, ymm2, 13
		INSTR    xmm14, ymm0, 1
		INSTR    xmm15, ymm1, 2
		INSTR    xmm3, ymm2, 13
		INSTR    xmm4, ymm0, 1
		INSTR    xmm5, ymm1, 2
		INSTR    xmm6, ymm2, 13
		INSTR    xmm7, ymm0, 1
		INSTR    xmm8, ymm1, 2
		INSTR    xmm9, ymm2, 13
		INSTR    xmm10, ymm0, 1
		INSTR    xmm11, ymm1, 2
		INSTR    xmm12, ymm2, 13
		INSTR    xmm13, ymm0, 1
		INSTR    xmm14, ymm1, 2
		INSTR    xmm15, ymm2, 13
		INSTR    xmm3, ymm0, 1
		INSTR    xmm4, ymm1, 2
		INSTR    xmm5, ymm2, 13
		INSTR    xmm6, ymm0, 1
		INSTR    xmm7, ymm1, 2
		INSTR    xmm8, ymm2, 13
		INSTR    xmm9, ymm0, 1
		INSTR    xmm10, ymm1, 2
		INSTR    xmm11, ymm2, 13
		INSTR    xmm12, ymm0, 1
		INSTR    xmm13, ymm1, 2
		INSTR    xmm14, ymm2, 13
		INSTR    xmm15, ymm0, 1
		INSTR    xmm3, ymm1, 2
		INSTR    xmm4, ymm2, 13
		INSTR    xmm5, ymm0, 1
		INSTR    xmm6, ymm1, 2
		INSTR    xmm7, ymm2, 13
		INSTR    xmm8, ymm0, 1
		INSTR    xmm9, ymm1, 2
		INSTR    xmm10, ymm2, 13
		INSTR    xmm11, ymm0, 1
		INSTR    xmm12, ymm1, 2
		INSTR    xmm13, ymm2, 13
		INSTR    xmm14, ymm0, 1
		cmp      i, N
		jl       loop
done:
		mov	rsp, rbp
		pop	rbp
		ret
.size latency, .-latency