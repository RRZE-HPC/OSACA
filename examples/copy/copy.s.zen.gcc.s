    # OSACA-BEGIN
.L19:
	vmovups	0(%rbp,%r10), %xmm9
	vmovups	16(%rbp,%r10), %xmm10
	vmovups	32(%rbp,%r10), %xmm11
	vmovups	48(%rbp,%r10), %xmm12
	vmovups	64(%rbp,%r10), %xmm13
	vmovups	80(%rbp,%r10), %xmm14
	vmovups	96(%rbp,%r10), %xmm15
	vmovups	112(%rbp,%r10), %xmm0
	vmovups	%xmm9, (%r12,%r10)
	vmovups	%xmm10, 16(%r12,%r10)
	vmovups	%xmm11, 32(%r12,%r10)
	vmovups	%xmm12, 48(%r12,%r10)
	vmovups	%xmm13, 64(%r12,%r10)
	vmovups	%xmm14, 80(%r12,%r10)
	vmovups	%xmm15, 96(%r12,%r10)
	vmovups	%xmm0, 112(%r12,%r10)
	subq	$-128, %r10
	cmpq	%r10, %r15
	jne	.L19
    # OSACA-END
