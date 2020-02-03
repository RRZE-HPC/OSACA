    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L19:
	vmovupd	(%r12,%rcx), %ymm10
	vmovupd	32(%r12,%rcx), %ymm11
	vmovupd	64(%r12,%rcx), %ymm12
	vmovupd	96(%r12,%rcx), %ymm13
	vmovupd	128(%r12,%rcx), %ymm14
	vmovupd	160(%r12,%rcx), %ymm15
	vmovupd	192(%r12,%rcx), %ymm0
	vmovupd	224(%r12,%rcx), %ymm1
	vmovupd	%ymm10, 0(%r13,%rcx)
	vmovupd	%ymm11, 32(%r13,%rcx)
	vmovupd	%ymm12, 64(%r13,%rcx)
	vmovupd	%ymm13, 96(%r13,%rcx)
	vmovupd	%ymm14, 128(%r13,%rcx)
	vmovupd	%ymm15, 160(%r13,%rcx)
	vmovupd	%ymm0, 192(%r13,%rcx)
	vmovupd	%ymm1, 224(%r13,%rcx)
	addq	$256, %rcx
	cmpq	%rcx, %r10
	jne	.L19
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
