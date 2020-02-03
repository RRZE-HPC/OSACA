    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L21:
	vmovupd	(%r8,%rax), %ymm11
	vmovupd	(%rsi,%rax), %ymm13
	vaddpd	(%r9,%rax), %ymm11, %ymm12
	vaddpd	(%rdi,%rax), %ymm13, %ymm14
	vmovupd	32(%r8,%rax), %ymm1
	vmovupd	32(%rsi,%rax), %ymm2
	vaddpd	%ymm14, %ymm12, %ymm15
	vaddpd	32(%r9,%rax), %ymm1, %ymm5
	vaddpd	32(%rdi,%rax), %ymm2, %ymm7
	vmulpd	%ymm8, %ymm15, %ymm0
	vmovupd	64(%r8,%rax), %ymm10
	vaddpd	%ymm7, %ymm5, %ymm6
	vmovupd	64(%rsi,%rax), %ymm12
	vmovupd	96(%rsi,%rax), %ymm5
	vmovupd	%ymm0, (%rdx,%rax)
	vmovupd	96(%r8,%rax), %ymm0
	vaddpd	64(%r9,%rax), %ymm10, %ymm11
	vaddpd	64(%rdi,%rax), %ymm12, %ymm13
	vaddpd	96(%r9,%rax), %ymm0, %ymm1
	vaddpd	96(%rdi,%rax), %ymm5, %ymm2
	vaddpd	%ymm13, %ymm11, %ymm14
	vmulpd	%ymm8, %ymm6, %ymm9
	vaddpd	%ymm2, %ymm1, %ymm7
	vmulpd	%ymm8, %ymm14, %ymm15
	vmulpd	%ymm8, %ymm7, %ymm6
	vmovupd	%ymm9, 32(%rdx,%rax)
	vmovupd	%ymm15, 64(%rdx,%rax)
	vmovupd	%ymm6, 96(%rdx,%rax)
	subq	$-128, %rax
	cmpq	%rax, %r15
	jne	.L21
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
