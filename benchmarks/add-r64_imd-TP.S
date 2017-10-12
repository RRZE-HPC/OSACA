#define INSTR add
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
loop:
		inc      i
		INSTR    rdx, 1
		INSTR    r9, 2
		INSTR    r10, 13
		INSTR    r11, 1
		INSTR    r12, 2
		INSTR    r13, 13
		INSTR    r14, 1
		INSTR    r15, 2
		INSTR    rdx, 13
		INSTR    r9, 1
		INSTR    r10, 2
		INSTR    r11, 13
		INSTR    r12, 1
		INSTR    r13, 2
		INSTR    r14, 13
		INSTR    r15, 1
		INSTR    rdx, 2
		INSTR    r9, 13
		INSTR    r10, 1
		INSTR    r11, 2
		INSTR    r12, 13
		INSTR    r13, 1
		INSTR    r14, 2
		INSTR    r15, 13
		INSTR    rdx, 1
		INSTR    r9, 2
		INSTR    r10, 13
		INSTR    r11, 1
		INSTR    r12, 2
		INSTR    r13, 13
		INSTR    r14, 1
		INSTR    r15, 2
		INSTR    rdx, 13
		INSTR    r9, 1
		INSTR    r10, 2
		INSTR    r11, 13
		INSTR    r12, 1
		INSTR    r13, 2
		INSTR    r14, 13
		INSTR    r15, 1
		INSTR    rdx, 2
		INSTR    r9, 13
		INSTR    r10, 1
		INSTR    r11, 2
		INSTR    r12, 13
		INSTR    r13, 1
		INSTR    r14, 2
		INSTR    r15, 13
		INSTR    rdx, 1
		INSTR    r9, 2
		INSTR    r10, 13
		INSTR    r11, 1
		INSTR    r12, 2
		INSTR    r13, 13
		INSTR    r14, 1
		INSTR    r15, 2
		INSTR    rdx, 13
		INSTR    r9, 1
		INSTR    r10, 2
		INSTR    r11, 13
		INSTR    r12, 1
		INSTR    r13, 2
		INSTR    r14, 13
		INSTR    r15, 1
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