    # OSACA-BEGIN
.L19:
	vaddpd	(%r10), %xmm3, %xmm1
	subq	$-128, %r10
	vaddpd	-112(%r10), %xmm1, %xmm4
	vaddpd	-96(%r10), %xmm4, %xmm5
	vaddpd	-80(%r10), %xmm5, %xmm6
	vaddpd	-64(%r10), %xmm6, %xmm8
	vaddpd	-48(%r10), %xmm8, %xmm9
	vaddpd	-32(%r10), %xmm9, %xmm10
	vaddpd	-16(%r10), %xmm10, %xmm3
	cmpq	%r10, %r14
	jne	.L19
    # OSACA-END
