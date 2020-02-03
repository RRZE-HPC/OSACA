    # OSACA-BEGIN
.L19:
	vmovsd	(%r10), %xmm8
	vmovsd	8(%r10), %xmm10
	subq	$-128, %r10
	vmovsd	-112(%r10), %xmm12
	vmovsd	-104(%r10), %xmm14
	vmovsd	-96(%r10), %xmm1
	vmovsd	-88(%r10), %xmm2
	vmovsd	-80(%r10), %xmm3
	vmovsd	-72(%r10), %xmm6
	vaddsd	%xmm8, %xmm7, %xmm9
	vmovsd	-64(%r10), %xmm8
	vaddsd	%xmm9, %xmm10, %xmm11
	vmovsd	-56(%r10), %xmm10
	vaddsd	%xmm12, %xmm11, %xmm13
	vmovsd	-48(%r10), %xmm12
	vaddsd	%xmm13, %xmm14, %xmm15
	vmovsd	-40(%r10), %xmm14
	vaddsd	%xmm1, %xmm15, %xmm4
	vmovsd	-32(%r10), %xmm1
	vaddsd	%xmm4, %xmm2, %xmm0
	vmovsd	-24(%r10), %xmm2
	vaddsd	%xmm3, %xmm0, %xmm5
	vmovsd	-16(%r10), %xmm3
	vaddsd	%xmm5, %xmm6, %xmm7
	vmovsd	-8(%r10), %xmm6
	vaddsd	%xmm8, %xmm7, %xmm9
	vaddsd	%xmm9, %xmm10, %xmm11
	vaddsd	%xmm12, %xmm11, %xmm13
	vaddsd	%xmm13, %xmm14, %xmm15
	vaddsd	%xmm1, %xmm15, %xmm4
	vaddsd	%xmm4, %xmm2, %xmm0
	vaddsd	%xmm3, %xmm0, %xmm5
	vaddsd	%xmm5, %xmm6, %xmm7
	cmpq	%r10, %r14
	jne	.L19
    # OSACA-END
