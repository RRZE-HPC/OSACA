    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L19:
	vmulpd	(%rcx), %ymm3, %ymm12
	vmulpd	32(%rcx), %ymm3, %ymm13
	vmulpd	64(%rcx), %ymm3, %ymm14
	vmulpd	96(%rcx), %ymm3, %ymm15
	vmulpd	128(%rcx), %ymm3, %ymm0
	vmulpd	160(%rcx), %ymm3, %ymm1
	vmulpd	192(%rcx), %ymm3, %ymm7
	vmulpd	224(%rcx), %ymm3, %ymm4
	vmovupd	%ymm12, (%rcx)
	vmovupd	%ymm13, 32(%rcx)
	vmovupd	%ymm14, 64(%rcx)
	vmovupd	%ymm15, 96(%rcx)
	vmovupd	%ymm0, 128(%rcx)
	vmovupd	%ymm1, 160(%rcx)
	vmovupd	%ymm7, 192(%rcx)
	vmovupd	%ymm4, 224(%rcx)
	addq	$256, %rcx
	cmpq	%r15, %rcx
	jne	.L19
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
