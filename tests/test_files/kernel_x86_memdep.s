# OSACA-BEGIN
.L4:
	vmovsd %xmm0, 8(%rax)
	addq $8, %rax
	vmovsd %xmm0, 8(%rax,%rcx,8)
	vaddsd (%rax), %xmm0, %xmm0  # depends on line 3, 8(%rax) == (%rax+8)
	subq $-8, %rax
	vaddsd -8(%rax), %xmm0, %xmm0  # depends on line 3, 8(%rax) == -8(%rax+16)
	dec %rcx
	vaddsd 8(%rax,%rcx,8), %xmm0, %xmm0  # depends on line 5, 8(%rax,%rdx,8) == 8(%rax+8,%rdx-1,8)
	movq %rcx, %rdx
	vaddsd 8(%rax,%rdx,8), %xmm0, %xmm0  # depends on line 5, 8(%rax,%rdx,8) == 8(%rax+8,%rdx-1,8)
	vmulsd %xmm1, %xmm0, %xmm0
	addq $8, %rax
	cmpq %rsi, %rax
	jne .L4
# OSACA-END
