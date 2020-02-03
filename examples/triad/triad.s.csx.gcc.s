    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L19:
	vmovupd	(%r14,%rsi), %ymm14
	vmovupd	32(%r14,%rsi), %ymm15
	vmovupd	64(%r14,%rsi), %ymm1
	vmovupd	96(%r14,%rsi), %ymm0
	vmovupd	128(%r14,%rsi), %ymm3
	vmovupd	160(%r14,%rsi), %ymm4
	vmovupd	192(%r14,%rsi), %ymm5
	vmovupd	224(%r14,%rsi), %ymm7
	vfmadd213pd	0(%r13,%rsi), %ymm6, %ymm14
	vfmadd213pd	32(%r13,%rsi), %ymm6, %ymm15
	vfmadd213pd	64(%r13,%rsi), %ymm6, %ymm1
	vfmadd213pd	96(%r13,%rsi), %ymm6, %ymm0
	vfmadd213pd	128(%r13,%rsi), %ymm6, %ymm3
	vfmadd213pd	160(%r13,%rsi), %ymm6, %ymm4
	vfmadd213pd	192(%r13,%rsi), %ymm6, %ymm5
	vfmadd213pd	224(%r13,%rsi), %ymm6, %ymm7
	vmovupd	%ymm14, (%r12,%rsi)
	vmovupd	%ymm15, 32(%r12,%rsi)
	vmovupd	%ymm1, 64(%r12,%rsi)
	vmovupd	%ymm0, 96(%r12,%rsi)
	vmovupd	%ymm3, 128(%r12,%rsi)
	vmovupd	%ymm4, 160(%r12,%rsi)
	vmovupd	%ymm5, 192(%r12,%rsi)
	vmovupd	%ymm7, 224(%r12,%rsi)
	addq	$256, %rsi
	cmpq	%rsi, %rcx
	jne	.L19
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
