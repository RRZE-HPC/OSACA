#define INSTR vcvtsi2ss
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
		xor     rax, rax
		xor     rbx, rbx
		xor     rcx, rcx
		xor     rdx, rdx
		xor     r9, r9
		xor     r10, r10
		xor     r11, r11
		xor     r12, r12
		xor     r13, r13
		xor     r14, r14
		xor     r15, r15
		# copy DP 1.0
		vmovaps xmm0, xmm0
		vmovaps xmm1, xmm0
		# Create DP 2.0
		vaddpd xmm1, xmm1, xmm1
		# Create DP 0.5
		vdivpd xmm2, xmm0, xmm1
loop:
		inc      i
		INSTR    xmm3, xmm0, eax
		INSTR    xmm4, xmm1, ebx
		INSTR    xmm5, xmm2, ecx
		INSTR    xmm6, xmm0, eax
		INSTR    xmm7, xmm1, ebx
		INSTR    xmm8, xmm2, ecx
		INSTR    xmm9, xmm0, eax
		INSTR    xmm10, xmm1, ebx
		INSTR    xmm11, xmm2, ecx
		INSTR    xmm12, xmm0, eax
		INSTR    xmm13, xmm1, ebx
		INSTR    xmm14, xmm2, ecx
		INSTR    xmm15, xmm0, eax
		INSTR    xmm3, xmm1, ebx
		INSTR    xmm4, xmm2, ecx
		INSTR    xmm5, xmm0, eax
		INSTR    xmm6, xmm1, ebx
		INSTR    xmm7, xmm2, ecx
		INSTR    xmm8, xmm0, eax
		INSTR    xmm9, xmm1, ebx
		INSTR    xmm10, xmm2, ecx
		INSTR    xmm11, xmm0, eax
		INSTR    xmm12, xmm1, ebx
		INSTR    xmm13, xmm2, ecx
		INSTR    xmm14, xmm0, eax
		INSTR    xmm15, xmm1, ebx
		INSTR    xmm3, xmm2, ecx
		INSTR    xmm4, xmm0, eax
		INSTR    xmm5, xmm1, ebx
		INSTR    xmm6, xmm2, ecx
		INSTR    xmm7, xmm0, eax
		INSTR    xmm8, xmm1, ebx
		INSTR    xmm9, xmm2, ecx
		INSTR    xmm10, xmm0, eax
		INSTR    xmm11, xmm1, ebx
		INSTR    xmm12, xmm2, ecx
		INSTR    xmm13, xmm0, eax
		INSTR    xmm14, xmm1, ebx
		INSTR    xmm15, xmm2, ecx
		INSTR    xmm3, xmm0, eax
		INSTR    xmm4, xmm1, ebx
		INSTR    xmm5, xmm2, ecx
		INSTR    xmm6, xmm0, eax
		INSTR    xmm7, xmm1, ebx
		INSTR    xmm8, xmm2, ecx
		INSTR    xmm9, xmm0, eax
		INSTR    xmm10, xmm1, ebx
		INSTR    xmm11, xmm2, ecx
		INSTR    xmm12, xmm0, eax
		INSTR    xmm13, xmm1, ebx
		INSTR    xmm14, xmm2, ecx
		INSTR    xmm15, xmm0, eax
		INSTR    xmm3, xmm1, ebx
		INSTR    xmm4, xmm2, ecx
		INSTR    xmm5, xmm0, eax
		INSTR    xmm6, xmm1, ebx
		INSTR    xmm7, xmm2, ecx
		INSTR    xmm8, xmm0, eax
		INSTR    xmm9, xmm1, ebx
		INSTR    xmm10, xmm2, ecx
		INSTR    xmm11, xmm0, eax
		INSTR    xmm12, xmm1, ebx
		INSTR    xmm13, xmm2, ecx
		INSTR    xmm14, xmm0, eax
		cmp      i, N
		jl       loop
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
done:
		mov	rsp, rbp
		pop	rbp
		ret
.size latency, .-latency