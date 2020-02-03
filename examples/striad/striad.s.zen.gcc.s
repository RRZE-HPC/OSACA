    # OSACA-BEGIN
.L19:
	vmovups	(%r14,%rax), %xmm0
	vmovups	(%r12,%rax), %xmm5
	vmovups	16(%r14,%rax), %xmm3
	vmovups	16(%r12,%rax), %xmm6
	vmovups	32(%r14,%rax), %xmm4
	vmovups	32(%r12,%rax), %xmm7
	vmovups	48(%r14,%rax), %xmm8
	vmovups	48(%r12,%rax), %xmm9
	vmovups	64(%r14,%rax), %xmm10
	vmovups	64(%r12,%rax), %xmm11
	vmovups	80(%r14,%rax), %xmm12
	vmovups	80(%r12,%rax), %xmm13
	vmovups	96(%r14,%rax), %xmm14
	vmovups	96(%r12,%rax), %xmm15
	vmovups	112(%r14,%rax), %xmm2
	vmovups	112(%r12,%rax), %xmm1
	vfmadd132pd	0(%r13,%rax), %xmm5, %xmm0
	vfmadd132pd	16(%r13,%rax), %xmm6, %xmm3
	vfmadd132pd	32(%r13,%rax), %xmm7, %xmm4
	vfmadd132pd	48(%r13,%rax), %xmm9, %xmm8
	vfmadd132pd	64(%r13,%rax), %xmm11, %xmm10
	vfmadd132pd	80(%r13,%rax), %xmm13, %xmm12
	vfmadd132pd	96(%r13,%rax), %xmm15, %xmm14
	vfmadd132pd	112(%r13,%rax), %xmm1, %xmm2
	vmovups	%xmm0, 0(%rbp,%rax)
	vmovups	%xmm3, 16(%rbp,%rax)
	vmovups	%xmm4, 32(%rbp,%rax)
	vmovups	%xmm8, 48(%rbp,%rax)
	vmovups	%xmm10, 64(%rbp,%rax)
	vmovups	%xmm12, 80(%rbp,%rax)
	vmovups	%xmm14, 96(%rbp,%rax)
	vmovups	%xmm2, 112(%rbp,%rax)
	subq	$-128, %rax
	cmpq	%rcx, %rax
	jne	.L19
    # OSACA-END
