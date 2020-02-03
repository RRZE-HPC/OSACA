    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L28:
	movupd	16(%r8,%rax), %xmm11
	movupd	16(%rdi,%rax), %xmm12
	movupd	16(%rsi,%rax), %xmm13
	addpd	%xmm11, %xmm15
	addpd	%xmm13, %xmm12
	movupd	32(%rdi,%rax), %xmm14
	movupd	32(%rsi,%rax), %xmm0
	addpd	%xmm15, %xmm12
	movupd	32(%r8,%rax), %xmm15
	addpd	%xmm0, %xmm14
	addpd	%xmm15, %xmm11
	movupd	48(%rdi,%rax), %xmm1
	movupd	48(%rsi,%rax), %xmm7
	addpd	%xmm11, %xmm14
	addpd	%xmm7, %xmm1
	mulpd	%xmm2, %xmm12
	mulpd	%xmm2, %xmm14
	movups	%xmm12, 16(%rcx,%rax)
	movups	%xmm14, 32(%rcx,%rax)
	movupd	48(%r8,%rax), %xmm14
	addpd	%xmm14, %xmm15
	addpd	%xmm15, %xmm1
	mulpd	%xmm2, %xmm1
	movups	%xmm1, 48(%rcx,%rax)
	addq	$64, %rax
.L21:
	movupd	(%r8,%rax), %xmm15
	movupd	(%rdi,%rax), %xmm0
	movupd	(%rsi,%rax), %xmm1
	addpd	%xmm15, %xmm14
	addpd	%xmm1, %xmm0
	leaq	16(%rax), %r10
	addpd	%xmm0, %xmm14
	mulpd	%xmm2, %xmm14
	movups	%xmm14, (%rcx,%rax)
	cmpq	%r10, %r14
	jne	.L28
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
