	.file	"triad.c"
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align 8
.LC9:
	.string	"%12.1f | %9.8f | %9.3f | %7.1f | %7.1f | %7d | %4d \n"
	.text
	.p2align 4,,15
	.globl	triad
	.type	triad, @function
triad:
.LFB24:
	.cfi_startproc
	pushq	%r13
	.cfi_def_cfa_offset 16
	.cfi_offset 13, -16
	movslq	%edi, %rax
	movl	$64, %edi
	leaq	16(%rsp), %r13
	.cfi_def_cfa 13, 0
	andq	$-32, %rsp
	pushq	-8(%r13)
	pushq	%rbp
	.cfi_escape 0x10,0x6,0x2,0x76,0
	movq	%rsp, %rbp
	pushq	%r15
	.cfi_escape 0x10,0xf,0x2,0x76,0x78
	leaq	0(,%rax,8), %r15
	pushq	%r14
	movq	%r15, %rsi
	pushq	%r13
	.cfi_escape 0xf,0x3,0x76,0x68,0x6
	.cfi_escape 0x10,0xe,0x2,0x76,0x70
	pushq	%r12
	pushq	%rbx
	.cfi_escape 0x10,0xc,0x2,0x76,0x60
	.cfi_escape 0x10,0x3,0x2,0x76,0x58
	movq	%rax, %rbx
	subq	$72, %rsp
	call	aligned_alloc
	movq	%r15, %rsi
	movl	$64, %edi
	movq	%rax, %r14
	call	aligned_alloc
	movq	%r15, %rsi
	movl	$64, %edi
	movq	%rax, %r12
	call	aligned_alloc
	movq	%r15, %rsi
	movl	$64, %edi
	movq	%rax, %r13
	call	aligned_alloc
	movq	%rax, %r15
	leal	-1(%rbx), %eax
	movl	%eax, -96(%rbp)
	testl	%ebx, %ebx
	jle	.L2
	cmpl	$2, %eax
	jbe	.L14
	movl	%ebx, %esi
	vmovapd	.LC0(%rip), %ymm0
	xorl	%eax, %eax
	xorl	%ecx, %ecx
	shrl	$2, %esi
	.p2align 4,,10
	.p2align 3
.L4:
	addl	$1, %ecx
	vmovapd	%ymm0, (%r15,%rax)
	vmovapd	%ymm0, 0(%r13,%rax)
	vmovapd	%ymm0, (%r12,%rax)
	vmovapd	%ymm0, (%r14,%rax)
	addq	$32, %rax
	cmpl	%ecx, %esi
	ja	.L4
	movl	%ebx, %eax
	andl	$-4, %eax
	cmpl	%eax, %ebx
	je	.L26
	vzeroupper
.L3:
	vmovsd	.LC1(%rip), %xmm0
	movslq	%eax, %rcx
	vmovsd	%xmm0, (%r15,%rcx,8)
	vmovsd	%xmm0, 0(%r13,%rcx,8)
	vmovsd	%xmm0, (%r12,%rcx,8)
	vmovsd	%xmm0, (%r14,%rcx,8)
	leal	1(%rax), %ecx
	cmpl	%ecx, %ebx
	jle	.L2
	movslq	%ecx, %rcx
	addl	$2, %eax
	vmovsd	%xmm0, (%r15,%rcx,8)
	vmovsd	%xmm0, 0(%r13,%rcx,8)
	vmovsd	%xmm0, (%r12,%rcx,8)
	vmovsd	%xmm0, (%r14,%rcx,8)
	cmpl	%eax, %ebx
	jle	.L2
	cltq
	vmovsd	%xmm0, (%r15,%rax,8)
	vmovsd	%xmm0, 0(%r13,%rax,8)
	vmovsd	%xmm0, (%r12,%rax,8)
	vmovsd	%xmm0, (%r14,%rax,8)
.L2:
	movl	%ebx, %eax
	movl	$1, -84(%rbp)
	movl	%ebx, %r10d
	andl	$-4, %eax
	shrl	$2, %r10d
	movl	%eax, -100(%rbp)
	.p2align 4,,10
	.p2align 3
.L13:
	leaq	-56(%rbp), %rsi
	leaq	-72(%rbp), %rdi
	movl	%r10d, -88(%rbp)
	call	timing
	movl	-88(%rbp), %r10d
	xorl	%r11d, %r11d
	.p2align 4,,10
	.p2align 3
.L12:
	vmovsd	(%r14), %xmm0
	vxorpd	%xmm7, %xmm7, %xmm7
	vucomisd	%xmm7, %xmm0
	jbe	.L6
	movq	%r14, %rdi
	movl	%r11d, -92(%rbp)
	movl	%r10d, -88(%rbp)
	vzeroupper
	call	dummy
	movl	-92(%rbp), %r11d
	movl	-88(%rbp), %r10d
.L6:
	testl	%ebx, %ebx
	jle	.L8
	cmpl	$2, -96(%rbp)
	jbe	.L15
	xorl	%eax, %eax
	xorl	%ecx, %ecx
	.p2align 4,,10
	.p2align 3
.L10:
	vmovapd	(%r15,%rax), %ymm0
	vmovapd	(%r12,%rax), %ymm3
	addl	$1, %ecx
	vfmadd132pd	0(%r13,%rax), %ymm3, %ymm0
	vmovapd	%ymm0, (%r14,%rax)
	addq	$32, %rax
	cmpl	%ecx, %r10d
	ja	.L10
	movl	-100(%rbp), %eax
	cmpl	%ebx, %eax
	je	.L8
.L9:
	movslq	%eax, %rcx
	vmovsd	0(%r13,%rcx,8), %xmm0
	vmovsd	(%r12,%rcx,8), %xmm5
	vfmadd132sd	(%r15,%rcx,8), %xmm5, %xmm0
	vmovsd	%xmm0, (%r14,%rcx,8)
	leal	1(%rax), %ecx
	cmpl	%ebx, %ecx
	jge	.L8
	movslq	%ecx, %rcx
	addl	$2, %eax
	vmovsd	0(%r13,%rcx,8), %xmm0
	vmovsd	(%r12,%rcx,8), %xmm6
	vfmadd132sd	(%r15,%rcx,8), %xmm6, %xmm0
	vmovsd	%xmm0, (%r14,%rcx,8)
	cmpl	%eax, %ebx
	jle	.L8
	cltq
	vmovsd	(%r15,%rax,8), %xmm0
	vmovsd	(%r12,%rax,8), %xmm4
	vfmadd132sd	0(%r13,%rax,8), %xmm4, %xmm0
	vmovsd	%xmm0, (%r14,%rax,8)
.L8:
	addl	$1, %r11d
	cmpl	-84(%rbp), %r11d
	jne	.L12
	leaq	-56(%rbp), %rsi
	leaq	-64(%rbp), %rdi
	movl	%r11d, -84(%rbp)
	movl	%r10d, -88(%rbp)
	vzeroupper
	call	timing
	vmovsd	-64(%rbp), %xmm1
	vsubsd	-72(%rbp), %xmm1, %xmm1
	vmovsd	.LC3(%rip), %xmm2
	movl	-84(%rbp), %r11d
	movl	-88(%rbp), %r10d
	vucomisd	%xmm1, %xmm2
	leal	(%r11,%r11), %eax
	movl	%eax, -84(%rbp)
	ja	.L13
	movl	%eax, %esi
	vxorpd	%xmm6, %xmm6, %xmm6
	vxorpd	%xmm0, %xmm0, %xmm0
	movl	%ebx, %edx
	sarl	%esi
	vcvtsi2sd	%ebx, %xmm0, %xmm0
	movl	$.LC9, %edi
	movl	$5, %eax
	vcvtsi2sd	%esi, %xmm6, %xmm6
	vmulsd	.LC5(%rip), %xmm6, %xmm2
	vmovsd	.LC4(%rip), %xmm5
	vmovsd	.LC6(%rip), %xmm7
	vmulsd	%xmm0, %xmm6, %xmm4
	vmulsd	%xmm0, %xmm2, %xmm2
	vdivsd	%xmm1, %xmm4, %xmm4
	vdivsd	%xmm1, %xmm2, %xmm2
	vdivsd	%xmm5, %xmm4, %xmm4
	vmulsd	%xmm7, %xmm2, %xmm3
	vaddsd	%xmm0, %xmm0, %xmm2
	vmulsd	.LC8(%rip), %xmm0, %xmm0
	vmulsd	%xmm6, %xmm2, %xmm2
	vmulsd	.LC7(%rip), %xmm2, %xmm2
	vmulsd	%xmm7, %xmm3, %xmm3
	vdivsd	%xmm5, %xmm0, %xmm0
	vdivsd	%xmm5, %xmm4, %xmm4
	vdivsd	%xmm1, %xmm2, %xmm2
	call	printf
	movq	%r14, %rdi
	call	free
	movq	%r12, %rdi
	call	free
	movq	%r13, %rdi
	call	free
	addq	$72, %rsp
	movq	%r15, %rdi
	popq	%rbx
	popq	%r12
	popq	%r13
	.cfi_remember_state
	.cfi_def_cfa 13, 0
	popq	%r14
	popq	%r15
	popq	%rbp
	leaq	-16(%r13), %rsp
	.cfi_def_cfa 7, 16
	popq	%r13
	.cfi_def_cfa_offset 8
	jmp	free
	.p2align 4,,10
	.p2align 3
.L15:
	.cfi_restore_state
	xorl	%eax, %eax
	jmp	.L9
.L26:
	vzeroupper
	jmp	.L2
.L14:
	xorl	%eax, %eax
	jmp	.L3
	.cfi_endproc
.LFE24:
	.size	triad, .-triad
	.section	.rodata.str1.8
	.align 8
.LC10:
	.string	"TRIAD a[i] = b[i]+c[i]*d[i], 32 byte/it, 2 Flop/it"
	.align 8
.LC11:
	.string	"Size (KByte) |   runtime  |  MFlop/s  |  MB/s   |  MLUP/s | repeat | size"
	.section	.text.startup,"ax",@progbits
	.p2align 4,,15
	.globl	main
	.type	main, @function
main:
.LFB25:
	.cfi_startproc
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset 3, -16
	movl	$.LC10, %edi
	movl	$20, %ebx
	call	puts
	movl	$.LC11, %edi
	call	puts
	.p2align 4,,10
	.p2align 3
.L28:
	vxorpd	%xmm1, %xmm1, %xmm1
	movq	.LC12(%rip), %rax
	vcvtsi2sd	%ebx, %xmm1, %xmm1
	addl	$1, %ebx
	vmovq	%rax, %xmm0
	call	pow
	vcvttsd2si	%xmm0, %edi
	call	triad
	cmpl	$36, %ebx
	jne	.L28
	xorl	%eax, %eax
	popq	%rbx
	.cfi_def_cfa_offset 8
	ret
	.cfi_endproc
.LFE25:
	.size	main, .-main
	.section	.rodata.cst32,"aM",@progbits,32
	.align 32
.LC0:
	.long	1907715710
	.long	1048610426
	.long	1907715710
	.long	1048610426
	.long	1907715710
	.long	1048610426
	.long	1907715710
	.long	1048610426
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC1:
	.long	1907715710
	.long	1048610426
	.align 8
.LC3:
	.long	2576980378
	.long	1070176665
	.align 8
.LC4:
	.long	0
	.long	1083129856
	.align 8
.LC5:
	.long	0
	.long	1077936128
	.align 8
.LC6:
	.long	0
	.long	1062207488
	.align 8
.LC7:
	.long	2696277389
	.long	1051772663
	.align 8
.LC8:
	.long	0
	.long	1075838976
	.align 8
.LC12:
	.long	3435973837
	.long	1073007820
	.ident	"GCC: (GNU) 7.2.0"
	.section	.note.GNU-stack,"",@progbits
