    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L19:
	vmovupd	(%r14,%rax), %ymm3
	vmovupd	32(%r14,%rax), %ymm4
	vmovupd	64(%r14,%rax), %ymm6
	vmovupd	96(%r14,%rax), %ymm9
	vmovupd	128(%r14,%rax), %ymm11
	vmovupd	160(%r14,%rax), %ymm13
	vmovupd	192(%r14,%rax), %ymm15
	vmovupd	224(%r14,%rax), %ymm0
	vaddpd	0(%r13,%rax), %ymm3, %ymm7
	vaddpd	32(%r13,%rax), %ymm4, %ymm5
	vaddpd	64(%r13,%rax), %ymm6, %ymm8
	vaddpd	96(%r13,%rax), %ymm9, %ymm10
	vaddpd	128(%r13,%rax), %ymm11, %ymm12
	vaddpd	160(%r13,%rax), %ymm13, %ymm14
	vaddpd	192(%r13,%rax), %ymm15, %ymm1
	vaddpd	224(%r13,%rax), %ymm0, %ymm2
	vmovupd	%ymm7, (%r12,%rax)
	vmovupd	%ymm5, 32(%r12,%rax)
	vmovupd	%ymm8, 64(%r12,%rax)
	vmovupd	%ymm10, 96(%r12,%rax)
	vmovupd	%ymm12, 128(%r12,%rax)
	vmovupd	%ymm14, 160(%r12,%rax)
	vmovupd	%ymm1, 192(%r12,%rax)
	vmovupd	%ymm2, 224(%r12,%rax)
	addq	$256, %rax
	cmpq	%rax, %rcx
	jne	.L19
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
