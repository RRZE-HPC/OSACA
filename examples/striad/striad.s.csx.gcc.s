    movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
.L19:
	vmovupd	(%r15,%rax), %ymm5
	vmovupd	0(%r13,%rax), %ymm6
	vmovupd	32(%r15,%rax), %ymm8
	vmovupd	32(%r13,%rax), %ymm7
	vmovupd	64(%r15,%rax), %ymm9
	vmovupd	64(%r13,%rax), %ymm10
	vmovupd	96(%r15,%rax), %ymm11
	vmovupd	96(%r13,%rax), %ymm12
	vmovupd	128(%r15,%rax), %ymm13
	vmovupd	128(%r13,%rax), %ymm14
	vmovupd	160(%r15,%rax), %ymm15
	vmovupd	160(%r13,%rax), %ymm2
	vmovupd	192(%r15,%rax), %ymm0
	vmovupd	192(%r13,%rax), %ymm1
	vmovupd	224(%r15,%rax), %ymm3
	vmovupd	224(%r13,%rax), %ymm4
	vfmadd132pd	(%r14,%rax), %ymm6, %ymm5
	vfmadd132pd	32(%r14,%rax), %ymm7, %ymm8
	vfmadd132pd	64(%r14,%rax), %ymm10, %ymm9
	vfmadd132pd	96(%r14,%rax), %ymm12, %ymm11
	vfmadd132pd	128(%r14,%rax), %ymm14, %ymm13
	vfmadd132pd	160(%r14,%rax), %ymm2, %ymm15
	vfmadd132pd	192(%r14,%rax), %ymm1, %ymm0
	vfmadd132pd	224(%r14,%rax), %ymm4, %ymm3
	vmovupd	%ymm5, (%r12,%rax)
	vmovupd	%ymm8, 32(%r12,%rax)
	vmovupd	%ymm9, 64(%r12,%rax)
	vmovupd	%ymm11, 96(%r12,%rax)
	vmovupd	%ymm13, 128(%r12,%rax)
	vmovupd	%ymm15, 160(%r12,%rax)
	vmovupd	%ymm0, 192(%r12,%rax)
	vmovupd	%ymm3, 224(%r12,%rax)
	addq	$256, %rax
	cmpq	%rax, %r8
	jne	.L19
    movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
    .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
