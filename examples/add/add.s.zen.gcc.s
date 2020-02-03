    # OSACA-BEGIN
.L19:
	vmovups	0(%r13,%rax), %xmm0
	vmovups	16(%r13,%rax), %xmm3
	vmovups	32(%r13,%rax), %xmm4
	vmovups	48(%r13,%rax), %xmm6
	vmovups	64(%r13,%rax), %xmm9
	vmovups	80(%r13,%rax), %xmm11
	vmovups	96(%r13,%rax), %xmm13
	vmovups	112(%r13,%rax), %xmm15
	vaddpd	(%r12,%rax), %xmm0, %xmm7
	vaddpd	16(%r12,%rax), %xmm3, %xmm2
	vaddpd	32(%r12,%rax), %xmm4, %xmm5
	vaddpd	48(%r12,%rax), %xmm6, %xmm8
	vaddpd	64(%r12,%rax), %xmm9, %xmm10
	vaddpd	80(%r12,%rax), %xmm11, %xmm12
	vaddpd	96(%r12,%rax), %xmm13, %xmm14
	vaddpd	112(%r12,%rax), %xmm15, %xmm1
	vmovups	%xmm7, 0(%rbp,%rax)
	vmovups	%xmm2, 16(%rbp,%rax)
	vmovups	%xmm5, 32(%rbp,%rax)
	vmovups	%xmm8, 48(%rbp,%rax)
	vmovups	%xmm10, 64(%rbp,%rax)
	vmovups	%xmm12, 80(%rbp,%rax)
	vmovups	%xmm14, 96(%rbp,%rax)
	vmovups	%xmm1, 112(%rbp,%rax)
	subq	$-128, %rax
	cmpq	%rbx, %rax
	jne	.L19
    # OSACA-END
