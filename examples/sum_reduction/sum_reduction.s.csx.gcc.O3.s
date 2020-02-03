    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    # LLVM-MCA-BEGIN
.L19:
	vmovupd	(%rcx), %ymm4
	vmovupd	32(%rcx), %ymm13
	vaddsd	%xmm4, %xmm0, %xmm6
	vunpckhpd	%xmm4, %xmm4, %xmm3
	vextractf64x2	$0x1, %ymm4, %xmm8
	vaddsd	%xmm6, %xmm3, %xmm7
	vunpckhpd	%xmm8, %xmm8, %xmm11
	vunpckhpd	%xmm13, %xmm13, %xmm1
	vaddsd	%xmm7, %xmm8, %xmm10
	vextractf64x2	$0x1, %ymm13, %xmm2
	vunpckhpd	%xmm2, %xmm2, %xmm3
	vaddsd	%xmm11, %xmm10, %xmm12
	vmovupd	64(%rcx), %ymm8
	vmovupd	96(%rcx), %ymm5
	vaddsd	%xmm13, %xmm12, %xmm0
	vunpckhpd	%xmm8, %xmm8, %xmm12
	vextractf64x2	$0x1, %ymm8, %xmm14
	vaddsd	%xmm0, %xmm1, %xmm4
	vunpckhpd	%xmm14, %xmm14, %xmm0
	vextractf64x2	$0x1, %ymm5, %xmm9
	vaddsd	%xmm4, %xmm2, %xmm6
	subq	$-128, %rcx
	vaddsd	%xmm3, %xmm6, %xmm7
	vaddsd	%xmm8, %xmm7, %xmm11
	vunpckhpd	%xmm5, %xmm5, %xmm7
	vaddsd	%xmm11, %xmm12, %xmm13
	vunpckhpd	%xmm9, %xmm9, %xmm12
	vaddsd	%xmm13, %xmm14, %xmm1
	vaddsd	%xmm0, %xmm1, %xmm4
	vaddsd	%xmm5, %xmm4, %xmm3
	vaddsd	%xmm3, %xmm7, %xmm8
	vaddsd	%xmm8, %xmm9, %xmm11
	vaddsd	%xmm12, %xmm11, %xmm0
	cmpq	%rcx, %r15
	jne	.L19
    # LLVM-MCA-END
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
