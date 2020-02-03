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
	pushq	%r15
	.cfi_def_cfa_offset 16
	.cfi_offset 15, -16
	pushq	%r14
	.cfi_def_cfa_offset 24
	.cfi_offset 14, -24
	movabsq	$21474836608, %rax
	movq	$-1, %r14
	pushq	%r13
	.cfi_def_cfa_offset 32
	.cfi_offset 13, -32
	pushq	%r12
	.cfi_def_cfa_offset 40
	.cfi_offset 12, -40
	pushq	%rbp
	.cfi_def_cfa_offset 48
	.cfi_offset 6, -48
	pushq	%rbx
	.cfi_def_cfa_offset 56
	.cfi_offset 3, -56
	subq	$664, %rsp
	.cfi_def_cfa_offset 720
	leaq	128(%rsp), %rdi
	movq	%rax, 128(%rsp)
	movq	$.LC0, 136(%rsp)
	movl	$12, 144(%rsp)
	call	_gfortran_st_read
	movl	$4, %edx
	leaq	80(%rsp), %rsi
	leaq	128(%rsp), %rdi
	call	_gfortran_transfer_integer
	movl	$4, %edx
	leaq	84(%rsp), %rsi
	leaq	128(%rsp), %rdi
	call	_gfortran_transfer_integer
	leaq	128(%rsp), %rdi
	call	_gfortran_st_read_done
	movslq	80(%rsp), %rdi
	movabsq	$4611686018427387904, %rcx
	movabsq	$2305843009213693951, %r8
	movslq	84(%rsp), %rsi
	testq	%rdi, %rdi
	movq	%rdi, %r15
	movq	%rdi, %r12
	movq	%rdi, 16(%rsp)
	cmovs	%r14, %r15
	testq	%rsi, %rsi
	movq	%rsi, %rbp
	movq	%rsi, 24(%rsp)
	cmovns	%rsi, %r14
	leaq	1(%r15), %rbx
	xorl	%edx, %edx
	incq	%r14
	imulq	%rbx, %r14
	cmpq	%rcx, %r14
	leaq	(%r14,%r14), %r13
	sete	%dl
	cmpq	%r8, %r13
	setg	%r9b
	movzbl	%r9b, %r10d
	addl	%r10d, %edx
	testq	%rdi, %rdi
	js	.L37
	testq	%rsi, %rsi
	js	.L37
	movq	%r14, %r11
	salq	$4, %r11
.L2:
	testl	%edx, %edx
	jne	.L282
	testq	%r11, %r11
	movl	$1, %edi
	cmovne	%r11, %rdi
	call	malloc
	testq	%rax, %rax
	je	.L283
	cmpl	$1, %ebp
	jle	.L5
	cmpl	$1, %r12d
	jle	.L6
	leal	-1(%r12), %r9d
	movq	%r13, %r10
	leal	-2(%r12), %r11d
	leaq	(%rax,%r14,8), %rdi
	movl	%r9d, %ecx
	movl	%r9d, %r8d
	subq	%r14, %r10
	leaq	8(%rax), %rdx
	shrl	%ecx
	andl	$-2, %r8d
	movl	%r9d, 32(%rsp)
	addq	%rbx, %r10
	salq	$4, %rcx
	movl	%r8d, 36(%rsp)
	addq	$2, %r15
	movq	%rdi, 40(%rsp)
	movq	%rcx, 8(%rsp)
	orl	$1, %r9d
	movl	$1, (%rsp)
	movq	%r11, %r8
	movq	%r11, 48(%rsp)
	movq	%rdx, 56(%rsp)
	vxorps	%xmm0, %xmm0, %xmm0
.L14:
	leaq	-1(%r15), %rcx
	leaq	1(%r10), %rsi
	cmpq	%rcx, %rsi
	setl	%dil
	cmpq	%r15, %r10
	setg	%r11b
	orl	%r11d, %edi
	andl	$1, %edi
	je	.L9
	cmpl	$3, %r8d
	jbe	.L9
	movq	8(%rsp), %r11
	leaq	0(,%r15,8), %rsi
	xorl	%edx, %edx
	leaq	(%rax,%rsi), %rdi
	addq	40(%rsp), %rsi
	subq	$16, %r11
	shrq	$4, %r11
	incq	%r11
	andl	$7, %r11d
	je	.L13
	cmpq	$1, %r11
	je	.L176
	cmpq	$2, %r11
	je	.L177
	cmpq	$3, %r11
	je	.L178
	cmpq	$4, %r11
	je	.L179
	cmpq	$5, %r11
	je	.L180
	cmpq	$6, %r11
	je	.L181
	vmovups	%xmm0, (%rdi)
	movl	$16, %edx
	vmovups	%xmm0, (%rsi)
.L181:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	addq	$16, %rdx
.L180:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	addq	$16, %rdx
.L179:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	addq	$16, %rdx
.L178:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	addq	$16, %rdx
.L177:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	addq	$16, %rdx
.L176:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	addq	$16, %rdx
	cmpq	8(%rsp), %rdx
	je	.L155
.L13:
	vmovups	%xmm0, (%rdi,%rdx)
	vmovups	%xmm0, (%rsi,%rdx)
	vmovups	%xmm0, 16(%rdi,%rdx)
	vmovups	%xmm0, 16(%rsi,%rdx)
	vmovups	%xmm0, 32(%rdi,%rdx)
	vmovups	%xmm0, 32(%rsi,%rdx)
	vmovups	%xmm0, 48(%rdi,%rdx)
	vmovups	%xmm0, 48(%rsi,%rdx)
	vmovups	%xmm0, 64(%rdi,%rdx)
	vmovups	%xmm0, 64(%rsi,%rdx)
	vmovups	%xmm0, 80(%rdi,%rdx)
	vmovups	%xmm0, 80(%rsi,%rdx)
	vmovups	%xmm0, 96(%rdi,%rdx)
	vmovups	%xmm0, 96(%rsi,%rdx)
	vmovups	%xmm0, 112(%rdi,%rdx)
	vmovups	%xmm0, 112(%rsi,%rdx)
	subq	$-128, %rdx
	cmpq	8(%rsp), %rdx
	jne	.L13
.L155:
	movl	36(%rsp), %esi
	cmpl	%esi, 32(%rsp)
	je	.L16
	addq	%r9, %rcx
	movq	$0x000000000, (%rax,%rcx,8)
	leaq	(%r10,%r9), %rcx
	movq	$0x000000000, (%rax,%rcx,8)
.L16:
	incl	(%rsp)
	addq	%rbx, %r10
	addq	%rbx, %r15
	movl	(%rsp), %r11d
	cmpl	%r11d, %ebp
	jne	.L14
.L11:
	movq	24(%rsp), %r11
	movl	$0, %edx
	movq	%r13, %rsi
	imulq	%rbx, %r11
	testl	%r12d, %r12d
	cmovns	%r12d, %edx
	subq	%r14, %rsi
	movq	%r11, %r10
	leaq	1(%r11), %r9
	subq	%r14, %r10
	movq	%r9, (%rsp)
	leaq	(%r10,%r13), %rcx
	leaq	1(%r13,%r10), %r15
	leaq	1(%rsi), %r10
	cmpq	%rcx, %r10
	setl	%r9b
	cmpq	%rsi, %r15
	setl	%dil
	orl	%edi, %r9d
	cmpq	%rcx, (%rsp)
	setl	%dil
	cmpq	%r15, %r11
	setg	8(%rsp)
	orw	8(%rsp), %di
	andl	%edi, %r9d
	cmpq	%r10, %r11
	setg	%dil
	cmpq	%rsi, (%rsp)
	setl	%sil
	orl	%edi, %esi
	andl	%r9d, %esi
	andl	$1, %esi
	je	.L20
	cmpq	$2, %r10
	seta	%r10b
	cmpq	$2, %r15
	seta	%r15b
	andl	%r15d, %r10d
	cmpq	$2, (%rsp)
	seta	%dil
	cmpl	$2, %edx
	seta	%r9b
	andl	%r9d, %edi
	andl	%edi, %r10d
	andl	$1, %r10d
	je	.L20
	incl	%edx
	leaq	(%rax,%rcx,8), %rdi
	xorl	%ecx, %ecx
	vmovaps	.LC4(%rip), %xmm1
	movl	%edx, %r15d
	leaq	(%rax,%r11,8), %r9
	leaq	(%rax,%r14,8), %rsi
	vxorps	%xmm2, %xmm2, %xmm2
	shrl	%r15d
	salq	$4, %r15
	leaq	-16(%r15), %r10
	shrq	$4, %r10
	incq	%r10
	andl	$7, %r10d
	je	.L22
	cmpq	$1, %r10
	je	.L188
	cmpq	$2, %r10
	je	.L189
	cmpq	$3, %r10
	je	.L190
	cmpq	$4, %r10
	je	.L191
	cmpq	$5, %r10
	je	.L192
	cmpq	$6, %r10
	je	.L193
	vmovups	%xmm1, (%r9)
	movl	$16, %ecx
	vmovups	%xmm1, (%rdi)
	vmovups	%xmm2, (%rax)
	vmovups	%xmm2, (%rsi)
.L193:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	addq	$16, %rcx
.L192:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	addq	$16, %rcx
.L191:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	addq	$16, %rcx
.L190:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	addq	$16, %rcx
.L189:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	addq	$16, %rcx
.L188:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	addq	$16, %rcx
	cmpq	%r15, %rcx
	je	.L113
.L22:
	vmovups	%xmm1, (%r9,%rcx)
	vmovups	%xmm1, (%rdi,%rcx)
	vmovups	%xmm2, (%rax,%rcx)
	vmovups	%xmm2, (%rsi,%rcx)
	vmovups	%xmm1, 16(%r9,%rcx)
	vmovups	%xmm1, 16(%rdi,%rcx)
	vmovups	%xmm2, 16(%rax,%rcx)
	vmovups	%xmm2, 16(%rsi,%rcx)
	vmovups	%xmm1, 32(%r9,%rcx)
	vmovups	%xmm1, 32(%rdi,%rcx)
	vmovups	%xmm2, 32(%rax,%rcx)
	vmovups	%xmm2, 32(%rsi,%rcx)
	vmovups	%xmm1, 48(%r9,%rcx)
	vmovups	%xmm1, 48(%rdi,%rcx)
	vmovups	%xmm2, 48(%rax,%rcx)
	vmovups	%xmm2, 48(%rsi,%rcx)
	vmovups	%xmm1, 64(%r9,%rcx)
	vmovups	%xmm1, 64(%rdi,%rcx)
	vmovups	%xmm2, 64(%rax,%rcx)
	vmovups	%xmm2, 64(%rsi,%rcx)
	vmovups	%xmm1, 80(%r9,%rcx)
	vmovups	%xmm1, 80(%rdi,%rcx)
	vmovups	%xmm2, 80(%rax,%rcx)
	vmovups	%xmm2, 80(%rsi,%rcx)
	vmovups	%xmm1, 96(%r9,%rcx)
	vmovups	%xmm1, 96(%rdi,%rcx)
	vmovups	%xmm2, 96(%rax,%rcx)
	vmovups	%xmm2, 96(%rsi,%rcx)
	vmovups	%xmm1, 112(%r9,%rcx)
	vmovups	%xmm1, 112(%rdi,%rcx)
	vmovups	%xmm2, 112(%rax,%rcx)
	vmovups	%xmm2, 112(%rsi,%rcx)
	subq	$-128, %rcx
	cmpq	%r15, %rcx
	jne	.L22
.L113:
	movl	%edx, %r9d
	andl	$-2, %r9d
	testb	$1, %dl
	je	.L10
	vmovsd	.LC5(%rip), %xmm3
	movslq	%r9d, %r15
	movq	%r15, %rdi
	leaq	(%r11,%r15), %r11
	subq	%r14, %rdi
	leaq	0(%r13,%rdi), %rsi
	vmovsd	%xmm3, (%rax,%r11,8)
	addq	%r14, %r11
	vmovsd	%xmm3, (%rax,%r11,8)
	movq	$0x000000000, (%rax,%r15,8)
	movq	$0x000000000, (%rax,%rsi,8)
.L10:
	testl	%ebp, %ebp
	js	.L18
.L19:
	vxorps	%xmm5, %xmm5, %xmm5
	movq	16(%rsp), %r15
	leaq	0(,%rbx,8), %rdi
	movl	$1, %r9d
	vcvtsi2sdl	%edx, %xmm5, %xmm6
	vcvtsi2sdl	%r12d, %xmm5, %xmm7
	vdivsd	%xmm7, %xmm6, %xmm8
	leaq	(%rax,%rdi), %r10
	movq	%r15, %rdx
	subq	%r14, %rdx
	leaq	0(%r13,%rdx), %rcx
	subq	%r14, %r13
	movl	%ebp, %r14d
	andl	$7, %r14d
	vmovsd	%xmm8, (%rax)
	vmovsd	%xmm8, (%rax,%r13,8)
	vmovsd	%xmm8, (%rax,%r15,8)
	vmovsd	%xmm8, (%rax,%rcx,8)
	cmpl	$1, %ebp
	jl	.L18
	testl	%r14d, %r14d
	je	.L27
	cmpl	$1, %r14d
	je	.L200
	cmpl	$2, %r14d
	je	.L201
	cmpl	$3, %r14d
	je	.L202
	cmpl	$4, %r14d
	je	.L203
	cmpl	$5, %r14d
	je	.L204
	cmpl	$6, %r14d
	je	.L205
	vmovsd	%xmm8, (%r10)
	movl	$2, %r9d
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
.L205:
	vmovsd	%xmm8, (%r10)
	incl	%r9d
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
.L204:
	vmovsd	%xmm8, (%r10)
	incl	%r9d
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
.L203:
	vmovsd	%xmm8, (%r10)
	incl	%r9d
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
.L202:
	vmovsd	%xmm8, (%r10)
	incl	%r9d
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
.L201:
	vmovsd	%xmm8, (%r10)
	incl	%r9d
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
.L200:
	incl	%r9d
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	cmpl	%r9d, %ebp
	jl	.L18
.L27:
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	addl	$8, %r9d
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	vmovsd	%xmm8, (%r10)
	vmovsd	%xmm8, (%r10,%r13,8)
	vmovsd	%xmm8, (%r10,%r15,8)
	vmovsd	%xmm8, (%r10,%rcx,8)
	addq	%rdi, %r10
	cmpl	%r9d, %ebp
	jge	.L27
.L18:
	movl	%r8d, %r8d
	leaq	0(,%rbx,8), %r13
	leaq	(%rbx,%rbx), %rsi
	movl	$10, (%rsp)
	addq	%rbx, %r8
	leaq	8(%rax,%r13), %r11
	movq	%rsi, 8(%rsp)
	leaq	16(%rax,%r8,8), %rax
	movq	%r11, 16(%rsp)
	movq	%rax, 24(%rsp)
.L26:
	leaq	96(%rsp), %rsi
	leaq	112(%rsp), %rdi
	xorl	%r15d, %r15d
	sall	(%rsp)
	call	timing_
	movq	.LC6(%rip), %rdx
	vmovq	%rdx, %xmm9
	.p2align 4
	.p2align 3
.L30:
	cmpl	$1, %ebp
	jle	.L33
	cmpl	$1, %r12d
	jle	.L33
	movq	24(%rsp), %r8
	movq	8(%rsp), %r14
	movq	%rbx, %r9
	xorl	%r11d, %r11d
	movq	16(%rsp), %rdi
	movl	$1, %r10d
	.p2align 4
	.p2align 3
.L34:
	movq	%r8, %rdx
	movq	%r11, %rsi
	movq	%r14, %rcx
	incl	%r10d
	subq	%rdi, %rdx
	subq	%r9, %rsi
	subq	%r9, %rcx
	vmovsd	-8(%rdi), %xmm8
	subq	$8, %rdx
	movq	%rdi, %rax
	shrq	$3, %rdx
	incq	%rdx
	andl	$7, %edx
	je	.L32
	cmpq	$1, %rdx
	je	.L194
	cmpq	$2, %rdx
	je	.L195
	cmpq	$3, %rdx
	je	.L196
	cmpq	$4, %rdx
	je	.L197
	cmpq	$5, %rdx
	je	.L198
	cmpq	$6, %rdx
	je	.L199
	vmovsd	(%rdi,%rsi,8), %xmm10
	vaddsd	(%rdi,%rcx,8), %xmm8, %xmm12
	leaq	8(%rdi), %rax
	vaddsd	8(%rdi), %xmm10, %xmm11
	vaddsd	%xmm12, %xmm11, %xmm13
	vmulsd	%xmm9, %xmm13, %xmm8
	vmovsd	%xmm8, (%rdi)
.L199:
	vmovsd	(%rax,%rsi,8), %xmm14
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm0
	vaddsd	8(%rax), %xmm14, %xmm15
	addq	$8, %rax
	vaddsd	%xmm0, %xmm15, %xmm1
	vmulsd	%xmm9, %xmm1, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L198:
	vmovsd	(%rax,%rsi,8), %xmm2
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm4
	vaddsd	8(%rax), %xmm2, %xmm3
	addq	$8, %rax
	vaddsd	%xmm4, %xmm3, %xmm5
	vmulsd	%xmm9, %xmm5, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L197:
	vmovsd	(%rax,%rsi,8), %xmm6
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm8
	vaddsd	8(%rax), %xmm6, %xmm7
	addq	$8, %rax
	vaddsd	%xmm8, %xmm7, %xmm10
	vmulsd	%xmm9, %xmm10, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L196:
	vmovsd	(%rax,%rsi,8), %xmm11
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm13
	vaddsd	8(%rax), %xmm11, %xmm12
	addq	$8, %rax
	vaddsd	%xmm13, %xmm12, %xmm14
	vmulsd	%xmm9, %xmm14, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L195:
	vmovsd	(%rax,%rsi,8), %xmm15
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm0
	vaddsd	8(%rax), %xmm15, %xmm1
	addq	$8, %rax
	vaddsd	%xmm0, %xmm1, %xmm2
	vmulsd	%xmm9, %xmm2, %xmm8
	vmovsd	%xmm8, -8(%rax)
.L194:
	vmovsd	(%rax,%rsi,8), %xmm3
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm5
	vaddsd	8(%rax), %xmm3, %xmm4
	addq	$8, %rax
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, -8(%rax)
	cmpq	%r8, %rax
	je	.L266
# OSACA-BEGIN
.L32:
	vmovsd	(%rax,%rsi,8), %xmm7
	leaq	8(%rax), %rdx
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm11
	vaddsd	8(%rax), %xmm7, %xmm10
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, (%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	leaq	16(%rax), %rdx
	vaddsd	16(%rax), %xmm14, %xmm15
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm3
	vmovsd	%xmm3, 8(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm2
	vaddsd	(%rdx,%rcx,8), %xmm3, %xmm5
	leaq	24(%rax), %rdx
	vaddsd	24(%rax), %xmm2, %xmm4
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, 16(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm7
	vaddsd	(%rdx,%rcx,8), %xmm8, %xmm11
	leaq	32(%rax), %rdx
	vaddsd	32(%rax), %xmm7, %xmm10
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, 24(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	leaq	40(%rax), %rdx
	vaddsd	40(%rax), %xmm14, %xmm15
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm3
	vmovsd	%xmm3, 32(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm2
	vaddsd	(%rdx,%rcx,8), %xmm3, %xmm5
	leaq	48(%rax), %rdx
	vaddsd	48(%rax), %xmm2, %xmm4
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, 40(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm7
	vaddsd	(%rdx,%rcx,8), %xmm8, %xmm11
	leaq	56(%rax), %rdx
	vaddsd	56(%rax), %xmm7, %xmm10
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
	jne	.L32
# OSACA-END
.L266:
	addq	%r13, %rdi
	addq	%rbx, %r11
	addq	%rbx, %r9
	addq	%rbx, %r14
	addq	%r13, %r8
	cmpl	%r10d, %ebp
	jne	.L34
.L33:
	leal	1(%r15), %r8d
	cmpl	(%rsp), %r8d
	je	.L29
	movl	%r8d, %r15d
	jmp	.L30
.L9:
	movq	48(%rsp), %rdi
	movq	56(%rsp), %rsi
	leaq	(%rax,%r15,8), %r11
	leaq	(%rdi,%r15), %rdx
	movq	%r10, %rdi
	leaq	(%rsi,%rdx,8), %rdx
	subq	%rcx, %rdi
	movq	%rdx, %rsi
	movq	%rdi, %rcx
	subq	%r11, %rsi
	subq	$8, %rsi
	shrq	$3, %rsi
	incq	%rsi
	andl	$7, %esi
	je	.L17
	cmpq	$1, %rsi
	je	.L182
	cmpq	$2, %rsi
	je	.L183
	cmpq	$3, %rsi
	je	.L184
	cmpq	$4, %rsi
	je	.L185
	cmpq	$5, %rsi
	je	.L186
	cmpq	$6, %rsi
	je	.L187
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rdi,8)
	addq	$8, %r11
.L187:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	addq	$8, %r11
.L186:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	addq	$8, %r11
.L185:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	addq	$8, %r11
.L184:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	addq	$8, %r11
.L183:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	addq	$8, %r11
.L182:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	addq	$8, %r11
	cmpq	%rdx, %r11
	je	.L16
.L17:
	movq	$0x000000000, (%r11)
	movq	$0x000000000, (%r11,%rcx,8)
	movq	$0x000000000, 8(%r11)
	movq	$0x000000000, 8(%r11,%rcx,8)
	movq	$0x000000000, 16(%r11)
	movq	$0x000000000, 16(%r11,%rcx,8)
	movq	$0x000000000, 24(%r11)
	movq	$0x000000000, 24(%r11,%rcx,8)
	movq	$0x000000000, 32(%r11)
	movq	$0x000000000, 32(%r11,%rcx,8)
	movq	$0x000000000, 40(%r11)
	movq	$0x000000000, 40(%r11,%rcx,8)
	movq	$0x000000000, 48(%r11)
	movq	$0x000000000, 48(%r11,%rcx,8)
	movq	$0x000000000, 56(%r11)
	movq	$0x000000000, 56(%r11,%rcx,8)
	addq	$64, %r11
	cmpq	%rdx, %r11
	jne	.L17
	jmp	.L16
.L37:
	xorl	%r11d, %r11d
	jmp	.L2
	.p2align 4
	.p2align 3
.L29:
	addl	$2, %r15d
	leaq	88(%rsp), %rsi
	leaq	104(%rsp), %rdi
	movl	%r15d, 76(%rsp)
	call	timing_
	vmovsd	104(%rsp), %xmm9
	vsubsd	112(%rsp), %xmm9, %xmm3
	vcomisd	.LC7(%rip), %xmm3
	jnb	.L40
	cmpl	$999999999, (%rsp)
	jle	.L26
.L40:
	movl	(%rsp), %ebx
	cmpl	%ebx, %r15d
	jle	.L36
	movl	%ebx, 76(%rsp)
.L36:
	leaq	128(%rsp), %rdi
	movabsq	$25769803904, %r12
	vmovsd	%xmm3, (%rsp)
	movq	$.LC0, 136(%rsp)
	movl	$72, 144(%rsp)
	movq	%r12, 128(%rsp)
	decl	%ebp
	call	_gfortran_st_write
	movl	$14, %edx
	movl	$.LC8, %esi
	leaq	128(%rsp), %rdi
	call	_gfortran_transfer_character_write
	movl	$4, %edx
	leaq	76(%rsp), %rsi
	leaq	128(%rsp), %rdi
	call	_gfortran_transfer_integer_write
	movl	$14, %edx
	movl	$.LC9, %esi
	leaq	128(%rsp), %rdi
	call	_gfortran_transfer_character_write
	vxorps	%xmm2, %xmm2, %xmm2
	vmovsd	(%rsp), %xmm11
	movl	$8, %edx
	vcvtsi2sdl	76(%rsp), %xmm2, %xmm8
	vmulsd	.LC10(%rip), %xmm8, %xmm7
	vcvtsi2sdl	32(%rsp), %xmm2, %xmm4
	vcvtsi2sdl	%ebp, %xmm2, %xmm5
	vmulsd	%xmm5, %xmm4, %xmm6
	leaq	120(%rsp), %rsi
	leaq	128(%rsp), %rdi
	vmulsd	%xmm7, %xmm6, %xmm10
	vdivsd	%xmm11, %xmm10, %xmm12
	vmovsd	%xmm12, 120(%rsp)
	call	_gfortran_transfer_real_write
	movl	$6, %edx
	movl	$.LC11, %esi
	leaq	128(%rsp), %rdi
	call	_gfortran_transfer_character_write
	leaq	128(%rsp), %rdi
	call	_gfortran_st_write_done
	xorl	%edx, %edx
	xorl	%esi, %esi
	xorl	%edi, %edi
	call	_gfortran_stop_string
.L5:
	testl	%r12d, %r12d
	js	.L38
.L280:
	leal	-1(%r12), %r15d
	leal	-2(%r12), %r8d
	movl	%r15d, 32(%rsp)
	jmp	.L11
.L6:
	testl	%r12d, %r12d
	jns	.L280
	leal	-1(%r12), %esi
	xorl	%edx, %edx
	leal	-2(%r12), %r8d
	movl	%esi, 32(%rsp)
	jmp	.L19
.L20:
	vmovsd	.LC5(%rip), %xmm4
	imulq	$-8, %r14, %r10
	leaq	(%rax,%r11,8), %r9
	addq	%r13, %r11
	movl	$1, %ecx
	leaq	(%r10,%r11,8), %r15
	leaq	(%r10,%r13,8), %rdi
	movl	%r12d, %r11d
	addq	%rax, %r15
	addq	%rax, %rdi
	andl	$7, %r11d
	vmovsd	%xmm4, (%r9)
	vmovsd	%xmm4, (%r15)
	movq	$0x000000000, (%rax)
	movq	$0x000000000, (%rdi)
	cmpl	$1, %r12d
	jl	.L45
	testl	%r11d, %r11d
	je	.L25
	cmpl	$1, %r11d
	je	.L206
	cmpl	$2, %r11d
	je	.L207
	cmpl	$3, %r11d
	je	.L208
	cmpl	$4, %r11d
	je	.L209
	cmpl	$5, %r11d
	je	.L210
	cmpl	$6, %r11d
	je	.L211
	vmovsd	%xmm4, 8(%r9)
	movl	$2, %ecx
	vmovsd	%xmm4, 8(%r15)
	movq	$0x000000000, 8(%rax)
	movq	$0x000000000, 8(%rdi)
.L211:
	vmovsd	%xmm4, (%r9,%rcx,8)
	vmovsd	%xmm4, (%r15,%rcx,8)
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	incq	%rcx
.L210:
	vmovsd	%xmm4, (%r9,%rcx,8)
	vmovsd	%xmm4, (%r15,%rcx,8)
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	incq	%rcx
.L209:
	vmovsd	%xmm4, (%r9,%rcx,8)
	vmovsd	%xmm4, (%r15,%rcx,8)
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	incq	%rcx
.L208:
	vmovsd	%xmm4, (%r9,%rcx,8)
	vmovsd	%xmm4, (%r15,%rcx,8)
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	incq	%rcx
.L207:
	vmovsd	%xmm4, (%r9,%rcx,8)
	vmovsd	%xmm4, (%r15,%rcx,8)
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	incq	%rcx
.L206:
	vmovsd	%xmm4, (%r9,%rcx,8)
	vmovsd	%xmm4, (%r15,%rcx,8)
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	incq	%rcx
	cmpl	%ecx, %r12d
	jl	.L45
.L25:
	leaq	1(%rcx), %rsi
	vmovsd	%xmm4, (%r9,%rcx,8)
	leaq	2(%rcx), %r10
	vmovsd	%xmm4, (%r15,%rcx,8)
	leaq	3(%rcx), %r11
	movq	$0x000000000, (%rax,%rcx,8)
	movq	$0x000000000, (%rdi,%rcx,8)
	vmovsd	%xmm4, (%r9,%rsi,8)
	vmovsd	%xmm4, (%r15,%rsi,8)
	movq	$0x000000000, (%rax,%rsi,8)
	movq	$0x000000000, (%rdi,%rsi,8)
	leaq	4(%rcx), %rsi
	vmovsd	%xmm4, (%r9,%r10,8)
	vmovsd	%xmm4, (%r15,%r10,8)
	movq	$0x000000000, (%rax,%r10,8)
	movq	$0x000000000, (%rdi,%r10,8)
	leaq	5(%rcx), %r10
	vmovsd	%xmm4, (%r9,%r11,8)
	vmovsd	%xmm4, (%r15,%r11,8)
	movq	$0x000000000, (%rax,%r11,8)
	movq	$0x000000000, (%rdi,%r11,8)
	leaq	6(%rcx), %r11
	vmovsd	%xmm4, (%r9,%rsi,8)
	vmovsd	%xmm4, (%r15,%rsi,8)
	movq	$0x000000000, (%rax,%rsi,8)
	movq	$0x000000000, (%rdi,%rsi,8)
	leaq	7(%rcx), %rsi
	addq	$8, %rcx
	vmovsd	%xmm4, (%r9,%r10,8)
	vmovsd	%xmm4, (%r15,%r10,8)
	movq	$0x000000000, (%rax,%r10,8)
	movq	$0x000000000, (%rdi,%r10,8)
	vmovsd	%xmm4, (%r9,%r11,8)
	vmovsd	%xmm4, (%r15,%r11,8)
	movq	$0x000000000, (%rax,%r11,8)
	movq	$0x000000000, (%rdi,%r11,8)
	vmovsd	%xmm4, (%r9,%rsi,8)
	vmovsd	%xmm4, (%r15,%rsi,8)
	movq	$0x000000000, (%rax,%rsi,8)
	movq	$0x000000000, (%rdi,%rsi,8)
	cmpl	%ecx, %r12d
	jge	.L25
.L45:
	incl	%edx
	jmp	.L10
.L282:
	movl	$.LC1, %edi
	xorl	%eax, %eax
	call	_gfortran_runtime_error
.L38:
	leal	-1(%r12), %r8d
	xorl	%edx, %edx
	movl	%r8d, 32(%rsp)
	leal	-2(%r12), %r8d
	jmp	.L10
.L283:
	movl	$.LC2, %edi
	call	_gfortran_os_error
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
	.section	.rodata.cst16,"aM",@progbits,16
	.align 16
.LC4:
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
