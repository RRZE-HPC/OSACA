#movl    $111,%ebx
#.byte   100,103,144
.L10:	
    vmovapd	(%r15,%rax), %ymm0
	vmovapd	(%r12,%rax), %ymm3
	addl	$1, %ecx
	vfmadd132pd	0(%r13,%rax), %ymm3, %ymm0
	vmovapd	%ymm0, (%r14,%rax)
	addq	$32, %rax
	cmpl	%ecx, %r10d
	ja	.L10
#movl    $222,%ebx
#.byte   100,103,144
