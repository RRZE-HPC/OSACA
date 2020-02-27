        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L31:
	vmovsd	(%rax,%rsi,8), %xmm7
	vaddsd	(%rax,%rcx,8), %xmm8, %xmm11
	vaddsd	8(%rax), %xmm7, %xmm10
	leaq	8(%rax), %rdx
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, (%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	vaddsd	16(%rax), %xmm14, %xmm15
	leaq	16(%rax), %rdx
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm3
	vmovsd	%xmm3, 8(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm2
	vaddsd	(%rdx,%rcx,8), %xmm3, %xmm5
	vaddsd	24(%rax), %xmm2, %xmm4
	leaq	24(%rax), %rdx
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, 16(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm7
	vaddsd	(%rdx,%rcx,8), %xmm8, %xmm11
	vaddsd	32(%rax), %xmm7, %xmm10
	leaq	32(%rax), %rdx
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, 24(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	vaddsd	40(%rax), %xmm14, %xmm15
	leaq	40(%rax), %rdx
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm3
	vmovsd	%xmm3, 32(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm2
	vaddsd	(%rdx,%rcx,8), %xmm3, %xmm5
	vaddsd	48(%rax), %xmm2, %xmm4
	leaq	48(%rax), %rdx
	vaddsd	%xmm5, %xmm4, %xmm6
	vmulsd	%xmm9, %xmm6, %xmm8
	vmovsd	%xmm8, 40(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm7
	vaddsd	(%rdx,%rcx,8), %xmm8, %xmm11
	vaddsd	56(%rax), %xmm7, %xmm10
	leaq	56(%rax), %rdx
	addq	$64, %rax
	vaddsd	%xmm11, %xmm10, %xmm12
	vmulsd	%xmm9, %xmm12, %xmm13
	vmovsd	%xmm13, -16(%rax)
	vmovsd	(%rdx,%rsi,8), %xmm14
	vaddsd	(%rdx,%rcx,8), %xmm13, %xmm1
	vaddsd	(%rax), %xmm14, %xmm15
	vaddsd	%xmm1, %xmm15, %xmm0
	vmulsd	%xmm9, %xmm0, %xmm8
	vmovsd	%xmm8, -8(%rax)
	cmpq	%r8, %rax
	jne	.L31
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
