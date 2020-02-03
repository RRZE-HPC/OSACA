    # OSACA-BEGIN
.L19:
	vmulpd	(%r10), %xmm3, %xmm11
	subq	$-128, %r10
	vmulpd	-112(%r10), %xmm3, %xmm12
	vmulpd	-96(%r10), %xmm3, %xmm13
	vmulpd	-80(%r10), %xmm3, %xmm14
	vmulpd	-64(%r10), %xmm3, %xmm15
	vmulpd	-48(%r10), %xmm3, %xmm0
	vmovups	%xmm11, -128(%r10)
	vmulpd	-32(%r10), %xmm3, %xmm7
	vmovups	%xmm12, -112(%r10)
	vmulpd	-16(%r10), %xmm3, %xmm1
	vmovups	%xmm13, -96(%r10)
	vmovups	%xmm14, -80(%r10)
	vmovups	%xmm15, -64(%r10)
	vmovups	%xmm0, -48(%r10)
	vmovups	%xmm7, -32(%r10)
	vmovups	%xmm1, -16(%r10)
	cmpq	%r10, %r14
	jne	.L19
    # OSACA-END
