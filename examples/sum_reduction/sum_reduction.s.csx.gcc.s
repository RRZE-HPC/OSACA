    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L19:
	vaddpd	(%rcx), %ymm3, %ymm4
	addq	$256, %rcx
	vaddpd	-224(%rcx), %ymm4, %ymm5
	vaddpd	-192(%rcx), %ymm5, %ymm6
	vaddpd	-160(%rcx), %ymm6, %ymm8
	vaddpd	-128(%rcx), %ymm8, %ymm9
	vaddpd	-96(%rcx), %ymm9, %ymm10
	vaddpd	-64(%rcx), %ymm10, %ymm11
	vaddpd	-32(%rcx), %ymm11, %ymm3
	cmpq	%rcx, %r15
	jne	.L19
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
