#define INSTR vaddpd
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
		# copy DP 1.0
		vmovaps xmm0, xmm0
		vmovaps xmm1, xmm0
		# Create DP 2.0
		vaddpd xmm1, xmm1, xmm1
		# Create DP 0.5
		vdivpd xmm2, xmm0, xmm1
loop:
		inc      i
		INSTR    xmm3, xmm0, xmm0
		INSTR    xmm4, xmm1, xmm1
		INSTR    xmm5, xmm2, xmm2
		INSTR    xmm6, xmm0, xmm0
		INSTR    xmm7, xmm1, xmm1
		INSTR    xmm8, xmm2, xmm2
		INSTR    xmm9, xmm0, xmm0
		INSTR    xmm10, xmm1, xmm1
		INSTR    xmm11, xmm2, xmm2
		INSTR    xmm12, xmm0, xmm0
		INSTR    xmm13, xmm1, xmm1
		INSTR    xmm14, xmm2, xmm2
		INSTR    xmm15, xmm0, xmm0
		INSTR    xmm3, xmm1, xmm1
		INSTR    xmm4, xmm2, xmm2
		INSTR    xmm5, xmm0, xmm0
		INSTR    xmm6, xmm1, xmm1
		INSTR    xmm7, xmm2, xmm2
		INSTR    xmm8, xmm0, xmm0
		INSTR    xmm9, xmm1, xmm1
		INSTR    xmm10, xmm2, xmm2
		INSTR    xmm11, xmm0, xmm0
		INSTR    xmm12, xmm1, xmm1
		INSTR    xmm13, xmm2, xmm2
		INSTR    xmm14, xmm0, xmm0
		INSTR    xmm15, xmm1, xmm1
		INSTR    xmm3, xmm2, xmm2
		INSTR    xmm4, xmm0, xmm0
		INSTR    xmm5, xmm1, xmm1
		INSTR    xmm6, xmm2, xmm2
		INSTR    xmm7, xmm0, xmm0
		INSTR    xmm8, xmm1, xmm1
		INSTR    xmm9, xmm2, xmm2
		INSTR    xmm10, xmm0, xmm0
		INSTR    xmm11, xmm1, xmm1
		INSTR    xmm12, xmm2, xmm2
		INSTR    xmm13, xmm0, xmm0
		INSTR    xmm14, xmm1, xmm1
		INSTR    xmm15, xmm2, xmm2
		INSTR    xmm3, xmm0, xmm0
		INSTR    xmm4, xmm1, xmm1
		INSTR    xmm5, xmm2, xmm2
		INSTR    xmm6, xmm0, xmm0
		INSTR    xmm7, xmm1, xmm1
		INSTR    xmm8, xmm2, xmm2
		INSTR    xmm9, xmm0, xmm0
		INSTR    xmm10, xmm1, xmm1
		INSTR    xmm11, xmm2, xmm2
		INSTR    xmm12, xmm0, xmm0
		INSTR    xmm13, xmm1, xmm1
		INSTR    xmm14, xmm2, xmm2
		INSTR    xmm15, xmm0, xmm0
		INSTR    xmm3, xmm1, xmm1
		INSTR    xmm4, xmm2, xmm2
		INSTR    xmm5, xmm0, xmm0
		INSTR    xmm6, xmm1, xmm1
		INSTR    xmm7, xmm2, xmm2
		INSTR    xmm8, xmm0, xmm0
		INSTR    xmm9, xmm1, xmm1
		INSTR    xmm10, xmm2, xmm2
		INSTR    xmm11, xmm0, xmm0
		INSTR    xmm12, xmm1, xmm1
		INSTR    xmm13, xmm2, xmm2
		INSTR    xmm14, xmm0, xmm0
		cmp      i, N
		jl       loop
done:
		mov	rsp, rbp
		pop	rbp
		ret
.size latency, .-latency