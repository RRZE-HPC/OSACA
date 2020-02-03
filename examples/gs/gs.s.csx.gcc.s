	.file	"gs.f90"
	.text
	.section	.rodata.str1.1,"aMS",@progbits,1
.LC0:
	.string	"gs.f90"
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align 8
.LC1:
	.string	"Integer overflow when calculating the amount of memory to allocate"
	.align 8
.LC2:
	.string	"Allocation would exceed memory limit"
	.section	.rodata.str1.1
.LC8:
	.string	"# Iterations: "
.LC9:
	.string	" Performance: "
.LC11:
	.string	" MLUPs"
	.text
	.p2align 4
	.type	MAIN__, @function
MAIN__:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movabsq	$21474836608, %rax
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	pushq	%r15
	pushq	%r14
	.cfi_offset 15, -24
	.cfi_offset 14, -32
	movq	$-1, %r14
	pushq	%r13
	pushq	%r12
	pushq	%rbx
	.cfi_offset 13, -40
	.cfi_offset 12, -48
	.cfi_offset 3, -56
	movq	%r14, %rbx
	subq	$696, %rsp
	leaq	160(%rsp), %rdi
	movq	%rax, 160(%rsp)
	movq	$.LC0, 168(%rsp)
	movl	$12, 176(%rsp)
	call	_gfortran_st_read
	movl	$4, %edx
	leaq	112(%rsp), %rsi
	leaq	160(%rsp), %rdi
	call	_gfortran_transfer_integer
	movl	$4, %edx
	leaq	116(%rsp), %rsi
	leaq	160(%rsp), %rdi
	call	_gfortran_transfer_integer
	leaq	160(%rsp), %rdi
	call	_gfortran_st_read_done
	movslq	112(%rsp), %r15
	movslq	116(%rsp), %rdi
	testq	%r15, %r15
	cmovns	%r15, %rbx
	movabsq	$4611686018427387904, %rcx
	incq	%rbx
	testq	%rdi, %rdi
	cmovns	%rdi, %r14
	movabsq	$2305843009213693951, %rsi
	incq	%r14
	imulq	%rbx, %r14
	xorl	%edx, %edx
	movl	%r15d, 88(%rsp)
	cmpq	%rcx, %r14
	leaq	(%r14,%r14), %r13
	sete	%dl
	cmpq	%rsi, %r13
	setg	%r8b
	movzbl	%r8b, %r9d
	movq	%rdi, 56(%rsp)
	movq	%rdi, %r12
	addl	%r9d, %edx
	testq	%r15, %r15
	js	.L36
	testq	%rdi, %rdi
	js	.L36
	movq	%r14, %r10
	salq	$4, %r10
.L2:
	testl	%edx, %edx
	jne	.L286
	testq	%r10, %r10
	movl	$1, %edi
	cmovne	%r10, %rdi
	call	malloc
	movq	%rax, %rdx
	testq	%rax, %rax
	je	.L287
	movl	88(%rsp), %r11d
	cmpl	$1, %r12d
	jle	.L5
	cmpl	$1, %r11d
	jle	.L6
	movl	%r11d, %r9d
	subl	$2, %r11d
	movq	%r11, %rcx
	addq	%rbx, %r11
	leaq	16(%rax,%r11,8), %r10
	leaq	0(,%rbx,8), %rdi
	leal	-1(%r9), %r11d
	leaq	8(%rax,%rdi), %rsi
	movq	%rdi, 8(%rsp)
	movl	%r11d, %edi
	leaq	0(,%r14,8), %rax
	movl	%r11d, 52(%rsp)
	shrl	$2, %edi
	andl	$-4, %r11d
	movq	%r10, 80(%rsp)
	movq	%rax, (%rsp)
	leal	2(%r11), %r10d
	leal	3(%r11), %eax
	salq	$5, %rdi
	movq	%r13, %r8
	movq	%rdi, 64(%rsp)
	movl	%r10d, 48(%rsp)
	movq	%r10, 24(%rsp)
	movl	%eax, 20(%rsp)
	movq	%rax, 40(%rsp)
	movl	$1, 72(%rsp)
	leal	1(%r11), %r9d
	subq	%r14, %r8
	movq	%r9, 32(%rsp)
	addq	%rbx, %r8
	movq	%rbx, %r9
	vxorpd	%xmm0, %xmm0, %xmm0
.L14:
	leaq	3(%r8), %rdi
	cmpq	%rdi, %r9
	leaq	3(%r9), %rax
	setg	%r10b
	cmpq	%rax, %r8
	setg	%dil
	orb	%dil, %r10b
	je	.L39
	movq	(%rsp), %rax
	cmpl	$2, %ecx
	seta	%r10b
	leaq	(%rsi,%rax), %rdi
	xorl	%eax, %eax
	testb	%r10b, %r10b
	je	.L39
	movq	64(%rsp), %r10
	subq	$32, %r10
	shrq	$5, %r10
	incq	%r10
	andl	$7, %r10d
	je	.L13
	cmpq	$1, %r10
	je	.L177
	cmpq	$2, %r10
	je	.L178
	cmpq	$3, %r10
	je	.L179
	cmpq	$4, %r10
	je	.L180
	cmpq	$5, %r10
	je	.L181
	cmpq	$6, %r10
	je	.L182
	vmovupd	%ymm0, (%rsi)
	movl	$32, %eax
	vmovupd	%ymm0, (%rdi)
.L182:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	addq	$32, %rax
.L181:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	addq	$32, %rax
.L180:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	addq	$32, %rax
.L179:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	addq	$32, %rax
.L178:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	addq	$32, %rax
.L177:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	addq	$32, %rax
	cmpq	64(%rsp), %rax
	je	.L156
.L13:
	vmovupd	%ymm0, (%rsi,%rax)
	vmovupd	%ymm0, (%rdi,%rax)
	vmovupd	%ymm0, 32(%rax,%rsi)
	vmovupd	%ymm0, 32(%rdi,%rax)
	vmovupd	%ymm0, 64(%rax,%rsi)
	vmovupd	%ymm0, 64(%rdi,%rax)
	vmovupd	%ymm0, 96(%rax,%rsi)
	vmovupd	%ymm0, 96(%rdi,%rax)
	vmovupd	%ymm0, 128(%rax,%rsi)
	vmovupd	%ymm0, 128(%rdi,%rax)
	vmovupd	%ymm0, 160(%rax,%rsi)
	vmovupd	%ymm0, 160(%rdi,%rax)
	vmovupd	%ymm0, 192(%rax,%rsi)
	vmovupd	%ymm0, 192(%rdi,%rax)
	vmovupd	%ymm0, 224(%rax,%rsi)
	vmovupd	%ymm0, 224(%rdi,%rax)
	addq	$256, %rax
	cmpq	64(%rsp), %rax
	jne	.L13
.L156:
	cmpl	%r11d, 52(%rsp)
	je	.L16
	movq	32(%rsp), %rdi
	leaq	(%r9,%rdi), %r10
	movq	$0x000000000, (%rdx,%r10,8)
	leaq	(%r8,%rdi), %rax
	movl	48(%rsp), %r10d
	movl	88(%rsp), %edi
	movq	$0x000000000, (%rdx,%rax,8)
	cmpl	%r10d, %edi
	jle	.L16
	movq	24(%rsp), %r10
	leaq	(%r9,%r10), %rax
	movq	$0x000000000, (%rdx,%rax,8)
	movl	20(%rsp), %eax
	leaq	(%r8,%r10), %r10
	movq	$0x000000000, (%rdx,%r10,8)
	cmpl	%eax, %edi
	jle	.L16
	movq	40(%rsp), %rdi
	leaq	(%r9,%rdi), %r10
	leaq	(%r8,%rdi), %rax
	movq	$0x000000000, (%rdx,%r10,8)
	movq	$0x000000000, (%rdx,%rax,8)
.L16:
	incl	72(%rsp)
	movq	8(%rsp), %rdi
	addq	%rbx, %r9
	addq	%rdi, 80(%rsp)
	movl	72(%rsp), %r10d
	addq	%rbx, %r8
	addq	%rdi, %rsi
	cmpl	%r10d, %r12d
	jne	.L14
.L11:
	movq	56(%rsp), %r10
	movl	88(%rsp), %r8d
	imulq	%rbx, %r10
	movl	$0, %r11d
	testl	%r8d, %r8d
	movq	%r10, %rax
	cmovns	%r8d, %r11d
	leaq	3(%r10), %rsi
	subq	%r14, %rax
	movq	%r13, %r9
	addq	%r13, %rax
	subq	%r14, %r9
	cmpq	$6, %rsi
	seta	%dil
	cmpl	$2, %r11d
	leaq	3(%rax), %r8
	movq	%rsi, 80(%rsp)
	seta	%sil
	andl	%esi, %edi
	cmpq	$6, %r8
	movq	%r9, 72(%rsp)
	seta	%sil
	leaq	3(%r9), %r9
	andl	%edi, %esi
	cmpq	$6, %r9
	seta	%dil
	andl	%esi, %edi
	cmpq	%rax, 80(%rsp)
	setl	%sil
	cmpq	%r8, %r10
	setg	64(%rsp)
	orb	64(%rsp), %sil
	andl	%esi, %edi
	cmpq	%rax, %r9
	setl	%sil
	movb	%dil, 64(%rsp)
	cmpq	72(%rsp), %r8
	setl	%r8b
	orl	%r8d, %esi
	testb	%sil, 64(%rsp)
	je	.L19
	movq	72(%rsp), %rdi
	cmpq	%r9, %r10
	setg	%r9b
	cmpq	%rdi, 80(%rsp)
	setl	%sil
	orb	%sil, %r9b
	je	.L19
	incl	%r11d
	movl	%r11d, %r9d
	shrl	$2, %r9d
	salq	$5, %r9
	movq	%r9, 80(%rsp)
	subq	$32, %r9
	shrq	$5, %r9
	incq	%r9
	leaq	(%rdx,%rax,8), %rdi
	vmovapd	.LC4(%rip), %ymm1
	leaq	(%rdx,%r10,8), %r8
	leaq	(%rdx,%r14,8), %rsi
	xorl	%eax, %eax
	vxorpd	%xmm2, %xmm2, %xmm2
	andl	$7, %r9d
	je	.L21
	cmpq	$1, %r9
	je	.L189
	cmpq	$2, %r9
	je	.L190
	cmpq	$3, %r9
	je	.L191
	cmpq	$4, %r9
	je	.L192
	cmpq	$5, %r9
	je	.L193
	cmpq	$6, %r9
	je	.L194
	vmovupd	%ymm1, (%r8)
	movl	$32, %eax
	vmovupd	%ymm1, (%rdi)
	vmovupd	%ymm2, (%rdx)
	vmovupd	%ymm2, (%rsi)
.L194:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	addq	$32, %rax
.L193:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	addq	$32, %rax
.L192:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	addq	$32, %rax
.L191:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	addq	$32, %rax
.L190:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	addq	$32, %rax
.L189:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	addq	$32, %rax
	cmpq	80(%rsp), %rax
	je	.L114
.L21:
	vmovupd	%ymm1, (%r8,%rax)
	vmovupd	%ymm1, (%rdi,%rax)
	vmovupd	%ymm2, (%rdx,%rax)
	vmovupd	%ymm2, (%rsi,%rax)
	vmovupd	%ymm1, 32(%r8,%rax)
	vmovupd	%ymm1, 32(%rdi,%rax)
	vmovupd	%ymm2, 32(%rdx,%rax)
	vmovupd	%ymm2, 32(%rsi,%rax)
	vmovupd	%ymm1, 64(%r8,%rax)
	vmovupd	%ymm1, 64(%rdi,%rax)
	vmovupd	%ymm2, 64(%rdx,%rax)
	vmovupd	%ymm2, 64(%rsi,%rax)
	vmovupd	%ymm1, 96(%r8,%rax)
	vmovupd	%ymm1, 96(%rdi,%rax)
	vmovupd	%ymm2, 96(%rdx,%rax)
	vmovupd	%ymm2, 96(%rsi,%rax)
	vmovupd	%ymm1, 128(%r8,%rax)
	vmovupd	%ymm1, 128(%rdi,%rax)
	vmovupd	%ymm2, 128(%rdx,%rax)
	vmovupd	%ymm2, 128(%rsi,%rax)
	vmovupd	%ymm1, 160(%r8,%rax)
	vmovupd	%ymm1, 160(%rdi,%rax)
	vmovupd	%ymm2, 160(%rdx,%rax)
	vmovupd	%ymm2, 160(%rsi,%rax)
	vmovupd	%ymm1, 192(%r8,%rax)
	vmovupd	%ymm1, 192(%rdi,%rax)
	vmovupd	%ymm2, 192(%rdx,%rax)
	vmovupd	%ymm2, 192(%rsi,%rax)
	vmovupd	%ymm1, 224(%r8,%rax)
	vmovupd	%ymm1, 224(%rdi,%rax)
	vmovupd	%ymm2, 224(%rdx,%rax)
	vmovupd	%ymm2, 224(%rsi,%rax)
	addq	$256, %rax
	cmpq	80(%rsp), %rax
	jne	.L21
.L114:
	movl	%r11d, %eax
	andl	$-4, %eax
	testb	$3, %r11b
	je	.L282
	movslq	%eax, %r8
	vmovsd	.LC5(%rip), %xmm3
	leaq	(%r10,%r8), %rsi
	movq	%r8, %rdi
	vmovsd	%xmm3, (%rdx,%rsi,8)
	subq	%r14, %rdi
	addq	%r14, %rsi
	movl	88(%rsp), %r9d
	vmovsd	%xmm3, (%rdx,%rsi,8)
	addq	%r13, %rdi
	movq	$0x000000000, (%rdx,%r8,8)
	leal	1(%rax), %r8d
	movq	$0x000000000, (%rdx,%rdi,8)
	cmpl	%r8d, %r9d
	jl	.L282
	movslq	%r8d, %rsi
	movq	%rsi, %r8
	leaq	(%r10,%rsi), %rdi
	subq	%r14, %r8
	vmovsd	%xmm3, (%rdx,%rdi,8)
	addq	%r13, %r8
	addq	%r14, %rdi
	addl	$2, %eax
	vmovsd	%xmm3, (%rdx,%rdi,8)
	movq	$0x000000000, (%rdx,%rsi,8)
	movq	$0x000000000, (%rdx,%r8,8)
	cmpl	%eax, %r9d
	jl	.L282
	cltq
	movq	%rax, %r9
	leaq	(%r10,%rax), %r10
	subq	%r14, %r9
	vmovsd	%xmm3, (%rdx,%r10,8)
	addq	%r13, %r9
	addq	%r14, %r10
	vmovsd	%xmm3, (%rdx,%r10,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rdx,%r9,8)
	vzeroupper
.L10:
	testl	%r12d, %r12d
	js	.L17
.L18:
	vxorpd	%xmm5, %xmm5, %xmm5
	vcvtsi2sdl	%r11d, %xmm5, %xmm6
	vcvtsi2sdl	88(%rsp), %xmm5, %xmm7
	movq	%r15, %r11
	subq	%r14, %r11
	leaq	0(%r13,%r11), %rdi
	vdivsd	%xmm7, %xmm6, %xmm8
	subq	%r14, %r13
	leaq	0(,%rbx,8), %rsi
	movl	%r12d, %r14d
	andl	$7, %r14d
	movl	$1, %r9d
	leaq	(%rdx,%rsi), %rax
	vmovsd	%xmm8, (%rdx)
	vmovsd	%xmm8, (%rdx,%r13,8)
	vmovsd	%xmm8, (%rdx,%r15,8)
	vmovsd	%xmm8, (%rdx,%rdi,8)
	cmpl	$1, %r12d
	jl	.L17
	testl	%r14d, %r14d
	je	.L26
	cmpl	$1, %r14d
	je	.L201
	cmpl	$2, %r14d
	je	.L202
	cmpl	$3, %r14d
	je	.L203
	cmpl	$4, %r14d
	je	.L204
	cmpl	$5, %r14d
	je	.L205
	cmpl	$6, %r14d
	je	.L206
	vmovsd	%xmm8, (%rax)
	movl	$2, %r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
.L206:
	vmovsd	%xmm8, (%rax)
	incl	%r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
.L205:
	vmovsd	%xmm8, (%rax)
	incl	%r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
.L204:
	vmovsd	%xmm8, (%rax)
	incl	%r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
.L203:
	vmovsd	%xmm8, (%rax)
	incl	%r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
.L202:
	vmovsd	%xmm8, (%rax)
	incl	%r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
.L201:
	incl	%r9d
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	cmpl	%r9d, %r12d
	jl	.L17
.L26:
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	addl	$8, %r9d
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rdi,8)
	addq	%rsi, %rax
	cmpl	%r9d, %r12d
	jge	.L26
.L17:
	movl	%ecx, %ecx
	leaq	0(,%rbx,8), %r13
	addq	%rbx, %rcx
	leaq	8(%rdx,%r13), %r15
	leaq	(%rbx,%rbx), %r10
	leaq	16(%rdx,%rcx,8), %r8
	movq	%r15, 64(%rsp)
	movq	%r10, 72(%rsp)
	movq	%r8, 56(%rsp)
	movl	$10, 80(%rsp)
.L25:
	leaq	128(%rsp), %rsi
	leaq	144(%rsp), %rdi
	sall	80(%rsp)
	call	timing_
	movq	.LC6(%rip), %r11
	xorl	%r15d, %r15d
	vmovq	%r11, %xmm9
	.p2align 4,,10
	.p2align 3
.L29:
	cmpl	$1, %r12d
	jle	.L32
	cmpl	$1, 88(%rsp)
	jle	.L32
	movq	56(%rsp), %r8
	movq	72(%rsp), %r14
	movq	64(%rsp), %rdi
	movq	%rbx, %r9
	xorl	%r11d, %r11d
	movl	$1, %r10d
	.p2align 4,,10
	.p2align 3
.L33:
	movq	%r8, %rdx
	subq	%rdi, %rdx
	subq	$8, %rdx
	shrq	$3, %rdx
	movq	%r11, %rsi
	movq	%r14, %rcx
	incq	%rdx
	vmovsd	-8(%rdi), %xmm8
	incl	%r10d
	movq	%rdi, %rax
	subq	%r9, %rsi
	subq	%r9, %rcx
	andl	$7, %edx
	je	.L31
	cmpq	$1, %rdx
	je	.L195
	cmpq	$2, %rdx
	je	.L196
	cmpq	$3, %rdx
	je	.L197
	cmpq	$4, %rdx
	je	.L198
	cmpq	$5, %rdx
	je	.L199
	cmpq	$6, %rdx
	je	.L200
	vmovsd	(%rdi,%rsi,8), %xmm10
	vaddsd	(%rdi,%rcx,8), %xmm8, %xmm12
	vaddsd	8(%rdi), %xmm10, %xmm11
	leaq	8(%rdi), %rax
	vaddsd	%xmm12, %xmm11, %xmm13
	vmulsd	%xmm9, %xmm13, %xmm8
	vmovsd	%xmm8, (%rdi)
.L200:
	vmovsd	(%rax,%rsi,8), %xmm14
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm0
	vaddsd	8(%rax), %xmm14, %xmm15
	addq	$8, %rax
	vaddsd	%xmm0, %xmm15, %xmm1
	vmulsd	%xmm9, %xmm1, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L199:
	vmovsd	(%rax,%rsi,8), %xmm2
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm4
	vaddsd	8(%rax), %xmm2, %xmm3
	addq	$8, %rax
	vaddsd	%xmm4, %xmm3, %xmm5
	vmulsd	%xmm9, %xmm5, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L198:
	vmovsd	(%rax,%rsi,8), %xmm6
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm8
	vaddsd	8(%rax), %xmm6, %xmm7
	addq	$8, %rax
	vaddsd	%xmm8, %xmm7, %xmm10
	vmulsd	%xmm9, %xmm10, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L197:
	vmovsd	(%rax,%rsi,8), %xmm11
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm13
	vaddsd	8(%rax), %xmm11, %xmm12
	addq	$8, %rax
	vaddsd	%xmm13, %xmm12, %xmm14
	vmulsd	%xmm9, %xmm14, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L196:
	vmovsd	(%rax,%rsi,8), %xmm15
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm0
	vaddsd	8(%rax), %xmm15, %xmm1
	addq	$8, %rax
	vaddsd	%xmm0, %xmm1, %xmm2
	vmulsd	%xmm9, %xmm2, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L195:
	vmovsd	(%rax,%rsi,8), %xmm3
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm5
	vaddsd	8(%rax), %xmm3, %xmm4
	addq	$8, %rax
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, -8(%rax)
	cmpq	%r8, %rax
	je	.L267
        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L31:
	vmovsd	(%rax,%rsi,8), %xmm7
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm11
	vaddsd	8(%rax), %xmm7, %xmm10
	leaq	8(%rax), %rdx
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, (%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	vaddsd	16(%rax), %xmm14, %xmm15
	leaq	16(%rax), %rdx
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm3
	vmovsd	%xmm3, 8(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm2
	vaddsd	(%rdx,%rcx,8), %xmm3, %xmm5
	vaddsd	24(%rax), %xmm2, %xmm4
	leaq	24(%rax), %rdx
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, 16(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm7
	vaddsd	(%rdx,%rcx,8), %xmm8, %xmm11
	vaddsd	32(%rax), %xmm7, %xmm10
	leaq	32(%rax), %rdx
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, 24(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	vaddsd	40(%rax), %xmm14, %xmm15
	leaq	40(%rax), %rdx
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm3
	vmovsd	%xmm3, 32(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm2
	vaddsd	(%rdx,%rcx,8), %xmm3, %xmm5
	vaddsd	48(%rax), %xmm2, %xmm4
	leaq	48(%rax), %rdx
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, 40(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm7
	vaddsd	(%rdx,%rcx,8), %xmm8, %xmm11
	vaddsd	56(%rax), %xmm7, %xmm10
	leaq	56(%rax), %rdx
	addq	$64, %rax
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, -16(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	vaddsd	(%rax), %xmm14, %xmm15
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm8
	vmovsd	%xmm8, -8(%rax)
	cmpq	%r8, %rax
	jne	.L31
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L267:
	addq	%r13, %rdi
	addq	%rbx, %r11
	addq	%rbx, %r9
	addq	%rbx, %r14
	addq	%r13, %r8
	cmpl	%r10d, %r12d
	jne	.L33
.L32:
	leal	1(%r15), %r8d
	cmpl	80(%rsp), %r8d
	je	.L28
	movl	%r8d, %r15d
	jmp	.L29
.L39:
	movq	80(%rsp), %r10
	movq	%r8, %rdi
	subq	%rsi, %r10
	subq	$8, %r10
	shrq	$3, %r10
	incq	%r10
	movq	%rsi, %rax
	subq	%r9, %rdi
	andl	$7, %r10d
	je	.L9
	cmpq	$1, %r10
	je	.L183
	cmpq	$2, %r10
	je	.L184
	cmpq	$3, %r10
	je	.L185
	cmpq	$4, %r10
	je	.L186
	cmpq	$5, %r10
	je	.L187
	cmpq	$6, %r10
	je	.L188
	movq	$0x000000000, (%rsi)
	movq	$0x000000000, (%rsi,%rdi,8)
	leaq	8(%rsi), %rax
.L188:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	addq	$8, %rax
.L187:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	addq	$8, %rax
.L186:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	addq	$8, %rax
.L185:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	addq	$8, %rax
.L184:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	addq	$8, %rax
.L183:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	addq	$8, %rax
	cmpq	80(%rsp), %rax
	je	.L16
.L9:
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rax,%rdi,8)
	movq	$0x000000000, 8(%rax)
	movq	$0x000000000, 8(%rax,%rdi,8)
	movq	$0x000000000, 16(%rax)
	movq	$0x000000000, 16(%rax,%rdi,8)
	movq	$0x000000000, 24(%rax)
	movq	$0x000000000, 24(%rax,%rdi,8)
	movq	$0x000000000, 32(%rax)
	movq	$0x000000000, 32(%rax,%rdi,8)
	movq	$0x000000000, 40(%rax)
	movq	$0x000000000, 40(%rax,%rdi,8)
	movq	$0x000000000, 48(%rax)
	movq	$0x000000000, 48(%rax,%rdi,8)
	movq	$0x000000000, 56(%rax)
	movq	$0x000000000, 56(%rax,%rdi,8)
	addq	$64, %rax
	cmpq	80(%rsp), %rax
	jne	.L9
	jmp	.L16
.L36:
	xorl	%r10d, %r10d
	jmp	.L2
	.p2align 4,,10
	.p2align 3
.L28:
	addl	$2, %r15d
	leaq	120(%rsp), %rsi
	leaq	136(%rsp), %rdi
	movl	%r15d, 108(%rsp)
	call	timing_
	vmovsd	136(%rsp), %xmm9
	vsubsd	144(%rsp), %xmm9, %xmm3
	vcomisd	.LC7(%rip), %xmm3
	jnb	.L40
	cmpl	$999999999, 80(%rsp)
	jle	.L25
.L40:
	movl	80(%rsp), %ebx
	cmpl	%ebx, %r15d
	jle	.L35
	movl	%ebx, 108(%rsp)
.L35:
	leaq	160(%rsp), %rdi
	movabsq	$25769803904, %r13
	vmovsd	%xmm3, 88(%rsp)
	movq	$.LC0, 168(%rsp)
	movl	$72, 176(%rsp)
	movq	%r13, 160(%rsp)
	call	_gfortran_st_write
	movl	$14, %edx
	movl	$.LC8, %esi
	leaq	160(%rsp), %rdi
	call	_gfortran_transfer_character_write
	movl	$4, %edx
	leaq	108(%rsp), %rsi
	leaq	160(%rsp), %rdi
	call	_gfortran_transfer_integer_write
	movl	$14, %edx
	movl	$.LC9, %esi
	leaq	160(%rsp), %rdi
	call	_gfortran_transfer_character_write
	decl	%r12d
	vxorpd	%xmm2, %xmm2, %xmm2
	vcvtsi2sdl	52(%rsp), %xmm2, %xmm4
	vcvtsi2sdl	%r12d, %xmm2, %xmm5
	vcvtsi2sdl	108(%rsp), %xmm2, %xmm8
	vmovsd	88(%rsp), %xmm11
	movl	$8, %edx
	vmulsd	%xmm5, %xmm4, %xmm6
	vmulsd	.LC10(%rip), %xmm8, %xmm7
	leaq	152(%rsp), %rsi
	leaq	160(%rsp), %rdi
	vmulsd	%xmm7, %xmm6, %xmm10
	vdivsd	%xmm11, %xmm10, %xmm12
	vmovsd	%xmm12, 152(%rsp)
	call	_gfortran_transfer_real_write
	movl	$6, %edx
	movl	$.LC11, %esi
	leaq	160(%rsp), %rdi
	call	_gfortran_transfer_character_write
	leaq	160(%rsp), %rdi
	call	_gfortran_st_write_done
	xorl	%edx, %edx
	xorl	%esi, %esi
	xorl	%edi, %edi
	call	_gfortran_stop_string
.L282:
	vzeroupper
	jmp	.L10
.L5:
	testl	%r11d, %r11d
	js	.L37
.L284:
	leal	-2(%r11), %ecx
	decl	%r11d
	movl	%r11d, 52(%rsp)
	jmp	.L11
.L6:
	cmpl	$0, 88(%rsp)
	jns	.L288
	movl	88(%rsp), %eax
	xorl	%r11d, %r11d
	leal	-2(%rax), %ecx
	decl	%eax
	movl	%eax, 52(%rsp)
	jmp	.L18
.L19:
	imulq	$-8, %r14, %rax
	leaq	(%rdx,%r10,8), %r8
	addq	%r13, %r10
	leaq	(%rax,%r10,8), %rdi
	movl	88(%rsp), %r10d
	vmovsd	.LC5(%rip), %xmm4
	leaq	(%rax,%r13,8), %rsi
	movl	%r10d, %r9d
	addq	%rdx, %rdi
	addq	%rdx, %rsi
	andl	$7, %r9d
	decl	%r10d
	vmovsd	%xmm4, (%r8)
	movl	$1, %eax
	vmovsd	%xmm4, (%rdi)
	movq	$0x000000000, (%rdx)
	movq	$0x000000000, (%rsi)
	jl	.L45
	testl	%r9d, %r9d
	je	.L24
	cmpl	$1, %r9d
	je	.L207
	cmpl	$2, %r9d
	je	.L208
	cmpl	$3, %r9d
	je	.L209
	cmpl	$4, %r9d
	je	.L210
	cmpl	$5, %r9d
	je	.L211
	cmpl	$6, %r9d
	je	.L212
	vmovsd	%xmm4, 8(%r8)
	vmovsd	%xmm4, 8(%rdi)
	movq	$0x000000000, 8(%rdx)
	movq	$0x000000000, 8(%rsi)
	movl	$2, %eax
.L212:
	vmovsd	%xmm4, (%r8,%rax,8)
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	incq	%rax
.L211:
	vmovsd	%xmm4, (%r8,%rax,8)
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	incq	%rax
.L210:
	vmovsd	%xmm4, (%r8,%rax,8)
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	incq	%rax
.L209:
	vmovsd	%xmm4, (%r8,%rax,8)
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	incq	%rax
.L208:
	vmovsd	%xmm4, (%r8,%rax,8)
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	incq	%rax
.L207:
	vmovsd	%xmm4, (%r8,%rax,8)
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	incq	%rax
	cmpl	%eax, 88(%rsp)
	jl	.L45
.L24:
	leaq	1(%rax), %r10
	vmovsd	%xmm4, (%r8,%rax,8)
	leaq	2(%rax), %r9
	vmovsd	%xmm4, (%rdi,%rax,8)
	movq	$0x000000000, (%rdx,%rax,8)
	movq	$0x000000000, (%rsi,%rax,8)
	vmovsd	%xmm4, (%r8,%r10,8)
	vmovsd	%xmm4, (%rdi,%r10,8)
	movq	$0x000000000, (%rdx,%r10,8)
	movq	$0x000000000, (%rsi,%r10,8)
	leaq	3(%rax), %r10
	vmovsd	%xmm4, (%r8,%r9,8)
	vmovsd	%xmm4, (%rdi,%r9,8)
	movq	$0x000000000, (%rdx,%r9,8)
	movq	$0x000000000, (%rsi,%r9,8)
	vmovsd	%xmm4, (%r8,%r10,8)
	leaq	4(%rax), %r9
	vmovsd	%xmm4, (%rdi,%r10,8)
	movq	$0x000000000, (%rdx,%r10,8)
	movq	$0x000000000, (%rsi,%r10,8)
	leaq	5(%rax), %r10
	vmovsd	%xmm4, (%r8,%r9,8)
	vmovsd	%xmm4, (%rdi,%r9,8)
	movq	$0x000000000, (%rdx,%r9,8)
	movq	$0x000000000, (%rsi,%r9,8)
	vmovsd	%xmm4, (%r8,%r10,8)
	leaq	6(%rax), %r9
	vmovsd	%xmm4, (%rdi,%r10,8)
	movq	$0x000000000, (%rdx,%r10,8)
	movq	$0x000000000, (%rsi,%r10,8)
	leaq	7(%rax), %r10
	addq	$8, %rax
	vmovsd	%xmm4, (%r8,%r9,8)
	vmovsd	%xmm4, (%rdi,%r9,8)
	movq	$0x000000000, (%rdx,%r9,8)
	movq	$0x000000000, (%rsi,%r9,8)
	vmovsd	%xmm4, (%r8,%r10,8)
	vmovsd	%xmm4, (%rdi,%r10,8)
	movq	$0x000000000, (%rdx,%r10,8)
	movq	$0x000000000, (%rsi,%r10,8)
	cmpl	%eax, 88(%rsp)
	jge	.L24
.L45:
	incl	%r11d
	vzeroupper
	jmp	.L10
.L37:
	movl	88(%rsp), %r8d
	xorl	%r11d, %r11d
	leal	-2(%r8), %ecx
	decl	%r8d
	movl	%r8d, 52(%rsp)
	jmp	.L10
.L287:
	movl	$.LC2, %edi
	call	_gfortran_os_error
.L286:
	movl	$.LC1, %edi
	xorl	%eax, %eax
	call	_gfortran_runtime_error
.L288:
	movl	88(%rsp), %r11d
	jmp	.L284
	.cfi_endproc
.LFE0:
	.size	MAIN__, .-MAIN__
	.section	.text.startup,"ax",@progbits
	.p2align 4
	.globl	main
	.type	main, @function
main:
.LFB1:
	.cfi_startproc
	subq	$8, %rsp
	.cfi_def_cfa_offset 16
	call	_gfortran_set_args
	movl	$options.9.4008, %esi
	movl	$7, %edi
	call	_gfortran_set_options
	call	MAIN__
	.cfi_endproc
.LFE1:
	.size	main, .-main
	.section	.rodata
	.align 16
	.type	options.9.4008, @object
	.size	options.9.4008, 28
options.9.4008:
	.long	2116
	.long	4095
	.long	0
	.long	1
	.long	1
	.long	0
	.long	31
	.section	.rodata.cst32,"aM",@progbits,32
	.align 32
.LC4:
	.long	0
	.long	1072693248
	.long	0
	.long	1072693248
	.long	0
	.long	1072693248
	.long	0
	.long	1072693248
	.section	.rodata.cst8,"aM",@progbits,8
	.align 8
.LC5:
	.long	0
	.long	1072693248
	.align 8
.LC6:
	.long	0
	.long	1070596096
	.align 8
.LC7:
	.long	2576980378
	.long	1070176665
	.align 8
.LC10:
	.long	2696277389
	.long	1051772663
	.ident	"GCC: (GNU) 9.1.0"
	.section	.note.GNU-stack,"",@progbits
