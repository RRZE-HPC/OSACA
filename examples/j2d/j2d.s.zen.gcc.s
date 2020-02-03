    # OSACA-BEGIN
.L28:
	vmovups	(%r10,%rcx), %xmm5
	vmovups	32(%r10,%rax), %xmm13
	vmovups	(%rdi,%rcx), %xmm1
	vmovups	32(%rdi,%rax), %xmm14
	vmovups	48(%rdi,%rax), %xmm9
	vaddpd	(%r8,%rcx), %xmm1, %xmm10
	vaddpd	32(%r8,%rax), %xmm14, %xmm15
	vaddpd	48(%r8,%rax), %xmm9, %xmm1
	vaddpd	%xmm5, %xmm8, %xmm8
	vaddpd	%xmm13, %xmm5, %xmm6
	vmovups	48(%r10,%rax), %xmm5
	vaddpd	%xmm8, %xmm10, %xmm11
	vaddpd	%xmm6, %xmm15, %xmm0
	vmulpd	%xmm2, %xmm11, %xmm12
	vaddpd	%xmm5, %xmm13, %xmm4
	vmulpd	%xmm2, %xmm0, %xmm7
	vaddpd	%xmm4, %xmm1, %xmm10
	vmovups	%xmm12, (%rsi,%rcx)
	vmovups	%xmm7, 32(%rsi,%rax)
	vmulpd	%xmm2, %xmm10, %xmm8
	vmovups	%xmm8, 48(%rsi,%rax)
	addq	$64, %rax
.L21:
	vmovups	(%r10,%rax), %xmm8
	leaq	16(%rax), %rcx
	vmovups	(%rdi,%rax), %xmm9
	vaddpd	(%r8,%rax), %xmm9, %xmm10
	vaddpd	%xmm8, %xmm5, %xmm11
	vaddpd	%xmm11, %xmm10, %xmm12
	vmulpd	%xmm2, %xmm12, %xmm13
	vmovups	%xmm13, (%rsi,%rax)
	cmpq	%rcx, %r14
	jne	.L28
    # OSACA-END
