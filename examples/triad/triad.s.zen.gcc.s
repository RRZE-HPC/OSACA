    # OSACA-BEGIN
.L19:
	vmovups	0(%r13,%rax), %xmm12
	vmovups	16(%r13,%rax), %xmm13
	vmovups	32(%r13,%rax), %xmm14
	vmovups	48(%r13,%rax), %xmm15
	vmovups	64(%r13,%rax), %xmm1
	vmovups	80(%r13,%rax), %xmm0
	vmovups	96(%r13,%rax), %xmm4
	vmovups	112(%r13,%rax), %xmm5
	vfmadd213pd	(%r12,%rax), %xmm3, %xmm12
	vfmadd213pd	16(%r12,%rax), %xmm3, %xmm13
	vfmadd213pd	32(%r12,%rax), %xmm3, %xmm14
	vfmadd213pd	48(%r12,%rax), %xmm3, %xmm15
	vfmadd213pd	64(%r12,%rax), %xmm3, %xmm1
	vfmadd213pd	80(%r12,%rax), %xmm3, %xmm0
	vfmadd213pd	96(%r12,%rax), %xmm3, %xmm4
	vfmadd213pd	112(%r12,%rax), %xmm3, %xmm5
	vmovups	%xmm12, 0(%rbp,%rax)
	vmovups	%xmm13, 16(%rbp,%rax)
	vmovups	%xmm14, 32(%rbp,%rax)
	vmovups	%xmm15, 48(%rbp,%rax)
	vmovups	%xmm1, 64(%rbp,%rax)
	vmovups	%xmm0, 80(%rbp,%rax)
	vmovups	%xmm4, 96(%rbp,%rax)
	vmovups	%xmm5, 112(%rbp,%rax)
	subq	$-128, %rax
	cmpq	%rbx, %rax
	jne	.L19
    # OSACA-END
