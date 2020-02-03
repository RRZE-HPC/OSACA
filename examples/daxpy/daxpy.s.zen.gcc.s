    # OSACA-BEGIN
.L19:
	vmovups	(%r12,%rax), %xmm12
	vmovups	16(%r12,%rax), %xmm13
	vmovups	32(%r12,%rax), %xmm14
	vmovups	48(%r12,%rax), %xmm15
	vmovups	64(%r12,%rax), %xmm1
	vmovups	80(%r12,%rax), %xmm0
	vmovups	96(%r12,%rax), %xmm4
	vmovups	112(%r12,%rax), %xmm5
	vfmadd213pd	0(%rbp,%rax), %xmm3, %xmm12
	vfmadd213pd	16(%rbp,%rax), %xmm3, %xmm13
	vfmadd213pd	32(%rbp,%rax), %xmm3, %xmm14
	vfmadd213pd	48(%rbp,%rax), %xmm3, %xmm15
	vfmadd213pd	64(%rbp,%rax), %xmm3, %xmm1
	vfmadd213pd	80(%rbp,%rax), %xmm3, %xmm0
	vfmadd213pd	96(%rbp,%rax), %xmm3, %xmm4
	vfmadd213pd	112(%rbp,%rax), %xmm3, %xmm5
	vmovups	%xmm12, 0(%rbp,%rax)
	vmovups	%xmm13, 16(%rbp,%rax)
	vmovups	%xmm14, 32(%rbp,%rax)
	vmovups	%xmm15, 48(%rbp,%rax)
	vmovups	%xmm1, 64(%rbp,%rax)
	vmovups	%xmm0, 80(%rbp,%rax)
	vmovups	%xmm4, 96(%rbp,%rax)
	vmovups	%xmm5, 112(%rbp,%rax)
	subq	$-128, %rax
	cmpq	%r15, %rax
	jne	.L19
    # OSACA-END
