	.section	__TEXT,__text,regular,pure_instructions
	.macosx_version_min 10, 14
	.globl	_main                   ## -- Begin function main
	.p2align	4, 0x90
_main:                                  ## @main
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	pushq	%r15
	pushq	%r14
	pushq	%r13
	pushq	%r12
	pushq	%rbx
	subq	$408, %rsp              ## imm = 0x198
	.cfi_offset %rbx, -56
	.cfi_offset %r12, -48
	.cfi_offset %r13, -40
	.cfi_offset %r14, -32
	.cfi_offset %r15, -24
	movq	%rsi, %rbx
	movq	16(%rsi), %rdi
	callq	_atoi
	movl	%eax, %r14d
	movq	24(%rbx), %rdi
	callq	_atoi
                                        ## kill: def $eax killed $eax def $rax
	movq	%r14, -96(%rbp)         ## 8-byte Spill
	movl	%r14d, %ecx
	imull	%r14d, %ecx
	movl	%ecx, -88(%rbp)         ## 4-byte Spill
	movq	%rax, -72(%rbp)         ## 8-byte Spill
	imull	%eax, %ecx
	movslq	%ecx, %r13
	shlq	$3, %r13
	leaq	-56(%rbp), %rdi
	movl	$32, %esi
	movq	%r13, %rdx
	callq	_posix_memalign
	testl	%eax, %eax
	je	LBB0_2
## %bb.1:
	movq	$0, -56(%rbp)
	xorl	%ebx, %ebx
	jmp	LBB0_3
LBB0_2:
	movq	-56(%rbp), %rbx
LBB0_3:
	leaq	-56(%rbp), %rdi
	movl	$32, %esi
	movq	%r13, %rdx
	callq	_posix_memalign
	testl	%eax, %eax
	je	LBB0_5
## %bb.4:
	movq	$0, -56(%rbp)
	xorl	%eax, %eax
	jmp	LBB0_6
LBB0_5:
	movq	-56(%rbp), %rax
LBB0_6:
	movq	%rax, -80(%rbp)         ## 8-byte Spill
	movq	-96(%rbp), %r9          ## 8-byte Reload
	movabsq	$4602641980904887326, %rax ## imm = 0x3FDFDE7EEC22D41E
	movq	%rax, -56(%rbp)
	cmpl	$3, -72(%rbp)           ## 4-byte Folded Reload
	jl	LBB0_15
## %bb.7:
	movabsq	$4294967296, %r12       ## imm = 0x100000000
	leal	-1(%r9), %ecx
	movslq	%r9d, %rax
	movslq	-88(%rbp), %rdx         ## 4-byte Folded Reload
	movq	%rdx, -160(%rbp)        ## 8-byte Spill
	movq	-72(%rbp), %rsi         ## 8-byte Reload
	leal	-1(%rsi), %edx
	leaq	8(%rbx,%rax,8), %rsi
	movq	%rsi, -152(%rbp)        ## 8-byte Spill
	movq	-80(%rbp), %rsi         ## 8-byte Reload
	leaq	8(%rsi,%rax,8), %rsi
	movq	%rsi, -144(%rbp)        ## 8-byte Spill
	leaq	(,%rax,8), %rsi
	movq	%rsi, -104(%rbp)        ## 8-byte Spill
	leaq	2(%rax), %rsi
	movq	%rsi, -136(%rbp)        ## 8-byte Spill
	shlq	$32, %rax
	movq	%rax, -184(%rbp)        ## 8-byte Spill
	addq	$-1, %rcx
	movl	%r9d, %eax
	movq	%rax, -176(%rbp)        ## 8-byte Spill
	movl	$1, %eax
	movabsq	$4601149042440805838, %rdi ## imm = 0x3FDA90AD19501DCE
	movq	%rdx, -208(%rbp)        ## 8-byte Spill
	.p2align	4, 0x90
LBB0_8:                                 ## =>This Loop Header: Depth=1
                                        ##     Child Loop BB0_10 Depth 2
                                        ##       Child Loop BB0_11 Depth 3
	cmpl	$2, %r9d
	jle	LBB0_14
## %bb.9:                               ##   in Loop: Header=BB0_8 Depth=1
	movl	%eax, %r14d
	imull	-88(%rbp), %r14d        ## 4-byte Folded Reload
	leaq	1(%rax), %r8
	movq	-160(%rbp), %rdx        ## 8-byte Reload
	movq	%rdx, %rsi
	movq	%r8, -168(%rbp)         ## 8-byte Spill
	imulq	%r8, %rsi
	movq	-152(%rbp), %r10        ## 8-byte Reload
	leaq	(%r10,%rsi,8), %r8
	leaq	-1(%rax), %rsi
	imulq	%rdx, %rsi
	leaq	(%r10,%rsi,8), %r10
	movq	%rax, %rsi
	imulq	%rdx, %rsi
	movq	-144(%rbp), %rdx        ## 8-byte Reload
	leaq	(%rdx,%rsi,8), %r11
	addl	-136(%rbp), %esi        ## 4-byte Folded Reload
	shlq	$32, %rsi
	movl	%r9d, %r15d
	imull	%eax, %r15d
	leal	2(%r15), %r13d
	imull	%r9d, %r13d
	addl	$1, %r13d
	addq	$1, %r14
	addl	$1, %r15d
	imull	%r9d, %r15d
	movl	$1, %eax
	.p2align	4, 0x90
LBB0_10:                                ##   Parent Loop BB0_8 Depth=1
                                        ## =>  This Loop Header: Depth=2
                                        ##       Child Loop BB0_11 Depth 3
	movq	%rax, -112(%rbp)        ## 8-byte Spill
	leaq	1(%rax), %rax
	movq	%rax, -192(%rbp)        ## 8-byte Spill
	movq	%rsi, -120(%rbp)        ## 8-byte Spill
	xorl	%edx, %edx
	.p2align	4, 0x90
LBB0_11:                                ##   Parent Loop BB0_8 Depth=1
                                        ##     Parent Loop BB0_10 Depth=2
                                        ## =>    This Inner Loop Header: Depth=3
	movq	%rdi, (%r11,%rdx,8)
	leal	(%r15,%rdx), %r9d
	movslq	%r9d, %rax
	movq	%rdi, (%rbx,%rax,8)
	movq	%rsi, %rax
	sarq	$29, %rax
	movq	%rdi, (%rbx,%rax)
	leal	(%r14,%rdx), %eax
	cltq
	movq	%rdi, (%rbx,%rax,8)
	leal	(%r13,%rdx), %eax
	cltq
	movq	%rdi, (%rbx,%rax,8)
	movq	%rdi, (%r10,%rdx,8)
	movq	%rdi, (%r8,%rdx,8)
	addq	$1, %rdx
	addq	%r12, %rsi
	cmpq	%rdx, %rcx
	jne	LBB0_11
## %bb.12:                              ##   in Loop: Header=BB0_10 Depth=2
	movq	-104(%rbp), %rax        ## 8-byte Reload
	addq	%rax, %r8
	addq	%rax, %r10
	addq	%rax, %r11
	movq	-120(%rbp), %rsi        ## 8-byte Reload
	addq	-184(%rbp), %rsi        ## 8-byte Folded Reload
	movq	-176(%rbp), %rax        ## 8-byte Reload
	addq	%rax, %r13
	addq	%rax, %r14
	addq	%rax, %r15
	cmpq	%rdx, -112(%rbp)        ## 8-byte Folded Reload
	movq	-192(%rbp), %rax        ## 8-byte Reload
	jne	LBB0_10
## %bb.13:                              ##   in Loop: Header=BB0_8 Depth=1
	movq	-168(%rbp), %rsi        ## 8-byte Reload
	movq	%rsi, %rax
	movq	-96(%rbp), %r9          ## 8-byte Reload
	movq	-208(%rbp), %rdx        ## 8-byte Reload
	cmpq	%rdx, %rsi
	jne	LBB0_8
	jmp	LBB0_15
	.p2align	4, 0x90
LBB0_14:                                ##   in Loop: Header=BB0_8 Depth=1
	addq	$1, %rax
	movq	%rax, %rsi
	cmpq	%rdx, %rsi
	jne	LBB0_8
LBB0_15:
	movq	_var_false@GOTPCREL(%rip), %rax
	cmpl	$0, (%rax)
	je	LBB0_17
## %bb.16:
	movq	%rbx, %rdi
	callq	_dummy
	movq	-80(%rbp), %rdi         ## 8-byte Reload
	callq	_dummy
	leaq	-56(%rbp), %rdi
	callq	_dummy
	movq	-96(%rbp), %r9          ## 8-byte Reload
LBB0_17:
	cmpl	$3, -72(%rbp)           ## 4-byte Folded Reload
	jl	LBB0_59
## %bb.18:
	movabsq	$4294967296, %r14       ## imm = 0x100000000
	leal	-1(%r9), %ecx
	movslq	%r9d, %rsi
	movslq	-88(%rbp), %rax         ## 4-byte Folded Reload
	movq	%rax, -312(%rbp)        ## 8-byte Spill
	movq	-72(%rbp), %rax         ## 8-byte Reload
	addl	$-1, %eax
	movq	%rax, -72(%rbp)         ## 8-byte Spill
	leaq	-1(%rcx), %rax
	leaq	-2(%rcx), %rdi
	movq	%rdi, -424(%rbp)        ## 8-byte Spill
	leaq	1(%rsi), %rdi
	movq	%rdi, -224(%rbp)        ## 8-byte Spill
	leaq	(%rsi,%rcx), %rdi
	movq	%rdi, -304(%rbp)        ## 8-byte Spill
	movl	%r9d, %edi
	movq	%rdi, -256(%rbp)        ## 8-byte Spill
	movq	%rcx, -264(%rbp)        ## 8-byte Spill
	leaq	(%rbx,%rcx,8), %rcx
	addq	$-8, %rcx
	movq	%rcx, -352(%rbp)        ## 8-byte Spill
	leal	6(%r9), %ecx
	andl	$7, %ecx
	movq	%rax, -448(%rbp)        ## 8-byte Spill
	movq	%rcx, -344(%rbp)        ## 8-byte Spill
	subq	%rcx, %rax
	movq	%rsi, %rcx
	shlq	$32, %rcx
	movq	%rcx, -440(%rbp)        ## 8-byte Spill
	leaq	1(%rax), %rcx
	movq	%rcx, -328(%rbp)        ## 8-byte Spill
	movq	%rax, -336(%rbp)        ## 8-byte Spill
	leal	1(%rax), %eax
	movl	%eax, -212(%rbp)        ## 4-byte Spill
	leaq	2(%rsi), %rax
	movq	%rax, -296(%rbp)        ## 8-byte Spill
	movq	-80(%rbp), %rax         ## 8-byte Reload
	leaq	8(%rax,%rsi,8), %rax
	movq	%rax, -288(%rbp)        ## 8-byte Spill
	leaq	(,%rsi,8), %rax
	movq	%rax, -432(%rbp)        ## 8-byte Spill
	movq	%rsi, -200(%rbp)        ## 8-byte Spill
	leaq	(%rbx,%rsi,8), %rax
	addq	$8, %rax
	movq	%rax, -280(%rbp)        ## 8-byte Spill
	movl	$1, %eax
	.p2align	4, 0x90
LBB0_19:                                ## =>This Loop Header: Depth=1
                                        ##     Child Loop BB0_52 Depth 2
                                        ##       Child Loop BB0_37 Depth 3
                                        ##       Child Loop BB0_55 Depth 3
	cmpl	$2, %r9d
	jle	LBB0_58
## %bb.20:                              ##   in Loop: Header=BB0_19 Depth=1
	movq	%rax, %rcx
	movq	%rax, %r12
	movq	-312(%rbp), %r15        ## 8-byte Reload
	imulq	%r15, %r12
	leaq	1(%rax), %rax
	movl	%r9d, %edi
	imull	%ecx, %edi
	leal	1(%rdi), %r8d
	imull	%r9d, %r8d
	addl	$2, %edi
	imull	%r9d, %edi
	movq	%rax, -320(%rbp)        ## 8-byte Spill
	movq	%rax, %r13
	imulq	%r15, %r13
	movq	-224(%rbp), %rdx        ## 8-byte Reload
	leaq	(%rdx,%r13), %rax
	movq	%rax, -408(%rbp)        ## 8-byte Spill
	movq	-304(%rbp), %rsi        ## 8-byte Reload
	leaq	(%rsi,%r13), %rax
	movq	%rax, -400(%rbp)        ## 8-byte Spill
	addq	$-1, %rcx
	imulq	%r15, %rcx
	leaq	(%rdx,%rcx), %rax
	movq	%rax, -392(%rbp)        ## 8-byte Spill
	leaq	(%rsi,%rcx), %rax
	movq	%rax, -384(%rbp)        ## 8-byte Spill
	movq	-296(%rbp), %rax        ## 8-byte Reload
	leal	(%rax,%r12), %eax
	shlq	$32, %rax
	movq	%rax, -104(%rbp)        ## 8-byte Spill
	movq	-280(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%r13,8), %r10
	leaq	(%rax,%rcx,8), %r11
	movl	%r12d, %edx
	addq	$1, %rdx
	movq	-200(%rbp), %rax        ## 8-byte Reload
	addq	%rax, %r13
	movq	%r13, -144(%rbp)        ## 8-byte Spill
	addq	%rax, %rcx
	movq	%rcx, -152(%rbp)        ## 8-byte Spill
	leal	2(%r8), %eax
	movq	%rax, -240(%rbp)        ## 8-byte Spill
	leal	1(%r12), %eax
	movq	%rax, -416(%rbp)        ## 8-byte Spill
	movq	%rdi, %rax
	movq	%rdi, -112(%rbp)        ## 8-byte Spill
	leal	1(%rdi), %r15d
	movq	-224(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%r12), %rcx
	leaq	(%rsi,%r12), %rax
	movq	%rax, -368(%rbp)        ## 8-byte Spill
	movq	-288(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%r12,8), %rsi
	leaq	-8(%rax,%r12,8), %rax
	movq	%rax, -136(%rbp)        ## 8-byte Spill
	movq	%r12, -120(%rbp)        ## 8-byte Spill
	leaq	1(%r12), %rax
	movq	%rax, -360(%rbp)        ## 8-byte Spill
	leal	-1(%r8), %eax
	movl	%eax, -124(%rbp)        ## 4-byte Spill
	movq	%rcx, -376(%rbp)        ## 8-byte Spill
	movq	%rcx, -272(%rbp)        ## 8-byte Spill
	movq	%r8, -248(%rbp)         ## 8-byte Spill
	movq	%r8, %rdi
	movq	%r15, -232(%rbp)        ## 8-byte Spill
	movq	%r15, %r8
	xorl	%r12d, %r12d
	movl	$1, %eax
	jmp	LBB0_52
	.p2align	4, 0x90
LBB0_21:                                ##   in Loop: Header=BB0_52 Depth=2
	movl	%r9d, %edx
	imull	%r12d, %edx
	movq	-248(%rbp), %rax        ## 8-byte Reload
	leal	(%rax,%rdx), %ecx
	movq	-424(%rbp), %rax        ## 8-byte Reload
	leal	(%rcx,%rax), %esi
	cmpl	%ecx, %esi
	jl	LBB0_53
## %bb.22:                              ##   in Loop: Header=BB0_52 Depth=2
	movq	%rax, %rcx
	shrq	$32, %rcx
	jne	LBB0_53
## %bb.23:                              ##   in Loop: Header=BB0_52 Depth=2
	movq	-240(%rbp), %rsi        ## 8-byte Reload
	leal	(%rsi,%rdx), %esi
	leal	(%rsi,%rax), %edi
	cmpl	%esi, %edi
	jl	LBB0_53
## %bb.24:                              ##   in Loop: Header=BB0_52 Depth=2
	testq	%rcx, %rcx
	jne	LBB0_53
## %bb.25:                              ##   in Loop: Header=BB0_52 Depth=2
	movq	-416(%rbp), %rsi        ## 8-byte Reload
	leal	(%rsi,%rdx), %esi
	leal	(%rsi,%rax), %edi
	cmpl	%esi, %edi
	jl	LBB0_53
## %bb.26:                              ##   in Loop: Header=BB0_52 Depth=2
	testq	%rcx, %rcx
	jne	LBB0_53
## %bb.27:                              ##   in Loop: Header=BB0_52 Depth=2
	addl	-232(%rbp), %edx        ## 4-byte Folded Reload
	leal	(%rdx,%rax), %esi
	cmpl	%edx, %esi
	jl	LBB0_53
## %bb.28:                              ##   in Loop: Header=BB0_52 Depth=2
	testq	%rcx, %rcx
	jne	LBB0_53
## %bb.29:                              ##   in Loop: Header=BB0_52 Depth=2
	movq	-192(%rbp), %rdx        ## 8-byte Reload
	movq	%rdx, %rsi
	imulq	-200(%rbp), %rsi        ## 8-byte Folded Reload
	movq	-376(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%rsi), %rdi
	movq	-368(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%rsi), %r13
	movq	-408(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%rsi), %r11
	movq	-400(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%rsi), %rcx
	movq	-392(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%rsi), %r10
	addq	-384(%rbp), %rsi        ## 8-byte Folded Reload
                                        ## kill: def $edx killed $edx killed $rdx def $rdx
	imull	-256(%rbp), %edx        ## 4-byte Folded Reload
	movq	-232(%rbp), %rax        ## 8-byte Reload
	leal	(%rax,%rdx), %r12d
	movq	-360(%rbp), %rax        ## 8-byte Reload
	leal	(%rax,%rdx), %r9d
	movq	-240(%rbp), %rax        ## 8-byte Reload
	leal	(%rax,%rdx), %eax
	movl	%eax, -60(%rbp)         ## 4-byte Spill
	addl	-248(%rbp), %edx        ## 4-byte Folded Reload
	movq	-80(%rbp), %rax         ## 8-byte Reload
	leaq	(%rax,%rdi,8), %rdi
	leaq	(%rbx,%rcx,8), %rcx
	cmpq	%rcx, %rdi
	leaq	(%rax,%r13,8), %rcx
	leaq	(%rbx,%r11,8), %r11
	setb	-45(%rbp)               ## 1-byte Folded Spill
	cmpq	%rcx, %r11
	leaq	(%rbx,%r10,8), %r10
	leaq	(%rbx,%rsi,8), %r11
	movslq	%r12d, %rsi
	setb	-44(%rbp)               ## 1-byte Folded Spill
	cmpq	%r11, %rdi
	setb	%r12b
	cmpq	%rcx, %r10
	leaq	(%rbx,%rsi,8), %r10
	movq	-352(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%rsi,8), %rsi
	movslq	%r9d, %r9
	setb	-43(%rbp)               ## 1-byte Folded Spill
	cmpq	%rsi, %rdi
	setb	%r11b
	cmpq	%rcx, %r10
	leaq	(%rbx,%r9,8), %r10
	leaq	(%rax,%r9,8), %rsi
	movslq	-60(%rbp), %r9          ## 4-byte Folded Reload
	setb	-60(%rbp)               ## 1-byte Folded Spill
	cmpq	%rsi, %rdi
	setb	%r13b
	cmpq	%rcx, %r10
	leaq	(%rbx,%r9,8), %r10
	leaq	(%rax,%r9,8), %rsi
	movslq	%edx, %rdx
	setb	-42(%rbp)               ## 1-byte Folded Spill
	cmpq	%rsi, %rdi
	setb	%r9b
	cmpq	%rcx, %r10
	leaq	(%rax,%rdx,8), %rsi
	setb	-41(%rbp)               ## 1-byte Folded Spill
	cmpq	%rsi, %rdi
	leaq	(%rbx,%rdx,8), %rdx
	setb	%r10b
	cmpq	%rcx, %rdx
	setb	%dl
	leaq	-55(%rbp), %rax
	cmpq	%rdi, %rax
	seta	%dil
	leaq	-56(%rbp), %rax
	cmpq	%rcx, %rax
	setb	%al
	movb	-44(%rbp), %cl          ## 1-byte Reload
	testb	%cl, -45(%rbp)          ## 1-byte Folded Reload
	jne	LBB0_53
## %bb.30:                              ##   in Loop: Header=BB0_52 Depth=2
	andb	-43(%rbp), %r12b        ## 1-byte Folded Reload
	jne	LBB0_53
## %bb.31:                              ##   in Loop: Header=BB0_52 Depth=2
	andb	-60(%rbp), %r11b        ## 1-byte Folded Reload
	jne	LBB0_53
## %bb.32:                              ##   in Loop: Header=BB0_52 Depth=2
	andb	-42(%rbp), %r13b        ## 1-byte Folded Reload
	jne	LBB0_53
## %bb.33:                              ##   in Loop: Header=BB0_52 Depth=2
	andb	-41(%rbp), %r9b         ## 1-byte Folded Reload
	jne	LBB0_53
## %bb.34:                              ##   in Loop: Header=BB0_52 Depth=2
	movl	$1, %r9d
	andb	%dl, %r10b
	jne	LBB0_54
## %bb.35:                              ##   in Loop: Header=BB0_52 Depth=2
	andb	%al, %dil
	jne	LBB0_54
## %bb.36:                              ##   in Loop: Header=BB0_52 Depth=2
	vbroadcastsd	-56(%rbp), %zmm0
	movq	-104(%rbp), %rdx        ## 8-byte Reload
	xorl	%esi, %esi
	movq	-336(%rbp), %r9         ## 8-byte Reload
	movabsq	$34359738368, %rdi      ## imm = 0x800000000
	movq	%rdi, %r10
	movq	-184(%rbp), %r11        ## 8-byte Reload
	movq	-176(%rbp), %r15        ## 8-byte Reload
	movq	-168(%rbp), %r12        ## 8-byte Reload
	movq	-88(%rbp), %rdi         ## 8-byte Reload
	movq	-160(%rbp), %rax        ## 8-byte Reload
	.p2align	4, 0x90
        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
LBB0_37:                                ##   Parent Loop BB0_19 Depth=1
                                        ##     Parent Loop BB0_52 Depth=2
                                        ## =>    This Inner Loop Header: Depth=3
	leal	(%rax,%rsi), %ecx
	movslq	%ecx, %rcx
	vmovupd	(%rbx,%rcx,8), %zmm1
	movq	%rdx, %rcx
	sarq	$29, %rcx
	vaddpd	(%rbx,%rcx), %zmm1, %zmm1
	leal	(%r12,%rsi), %ecx
	movslq	%ecx, %rcx
	vaddpd	(%rbx,%rcx,8), %zmm1, %zmm1
	leal	(%r8,%rsi), %ecx
	movslq	%ecx, %rcx
	vaddpd	(%rbx,%rcx,8), %zmm1, %zmm1
	vaddpd	(%r15,%rsi,8), %zmm1, %zmm1
	vaddpd	(%r11,%rsi,8), %zmm1, %zmm1
	vmulpd	%zmm0, %zmm1, %zmm1
	vmovupd	%zmm1, (%rdi,%rsi,8)
	addq	$8, %rsi
	addq	%r10, %rdx
	cmpq	%rsi, %r9
	jne	LBB0_37
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
## %bb.38:                              ##   in Loop: Header=BB0_52 Depth=2
	movq	-328(%rbp), %r9         ## 8-byte Reload
	movl	-212(%rbp), %eax        ## 4-byte Reload
	movl	%eax, %r15d
	cmpl	$0, -344(%rbp)          ## 4-byte Folded Reload
	jne	LBB0_54
	jmp	LBB0_56
	.p2align	4, 0x90
LBB0_52:                                ##   Parent Loop BB0_19 Depth=1
                                        ## =>  This Loop Header: Depth=2
                                        ##       Child Loop BB0_37 Depth 3
                                        ##       Child Loop BB0_55 Depth 3
	movq	%rdx, -168(%rbp)        ## 8-byte Spill
	addq	$1, %rax
	movl	$1, %r15d
	cmpq	$8, -448(%rbp)          ## 8-byte Folded Reload
	movq	%r10, -184(%rbp)        ## 8-byte Spill
	movq	%r11, -176(%rbp)        ## 8-byte Spill
	movq	%rsi, -88(%rbp)         ## 8-byte Spill
	movq	%rdi, -160(%rbp)        ## 8-byte Spill
	movq	%r12, -192(%rbp)        ## 8-byte Spill
	movq	%rax, -208(%rbp)        ## 8-byte Spill
	jae	LBB0_21
LBB0_53:                                ##   in Loop: Header=BB0_52 Depth=2
	movl	$1, %r9d
LBB0_54:                                ##   in Loop: Header=BB0_52 Depth=2
	movq	-136(%rbp), %rax        ## 8-byte Reload
	leaq	(%rax,%r9,8), %rdx
	movq	-144(%rbp), %rax        ## 8-byte Reload
	leaq	(%r9,%rax), %rcx
	leaq	(%rbx,%rcx,8), %r11
	movq	-152(%rbp), %rax        ## 8-byte Reload
	leaq	(%r9,%rax), %rcx
	leaq	(%rbx,%rcx,8), %r10
	movq	-272(%rbp), %rax        ## 8-byte Reload
	leal	(%r9,%rax), %r12d
	shlq	$32, %r12
	movq	-264(%rbp), %r13        ## 8-byte Reload
	subq	%r9, %r13
	movq	-112(%rbp), %rax        ## 8-byte Reload
	leal	(%r15,%rax), %esi
	movq	-120(%rbp), %rax        ## 8-byte Reload
	leal	(%r15,%rax), %edi
	addl	-124(%rbp), %r15d       ## 4-byte Folded Reload
	xorl	%ecx, %ecx
	.p2align	4, 0x90
LBB0_55:                                ##   Parent Loop BB0_19 Depth=1
                                        ##     Parent Loop BB0_52 Depth=2
                                        ## =>    This Inner Loop Header: Depth=3
	leal	(%r15,%rcx), %eax
	cltq
	vmovsd	(%rbx,%rax,8), %xmm0    ## xmm0 = mem[0],zero
	movq	%r12, %rax
	sarq	$29, %rax
	vaddsd	(%rbx,%rax), %xmm0, %xmm0
	leal	(%rdi,%rcx), %eax
	cltq
	vaddsd	(%rbx,%rax,8), %xmm0, %xmm0
	leal	(%rsi,%rcx), %eax
	cltq
	vaddsd	(%rbx,%rax,8), %xmm0, %xmm0
	vaddsd	(%r10,%rcx,8), %xmm0, %xmm0
	vaddsd	(%r11,%rcx,8), %xmm0, %xmm0
	vmulsd	-56(%rbp), %xmm0, %xmm0
	vmovsd	%xmm0, (%rdx,%rcx,8)
	addq	$1, %rcx
	addq	%r14, %r12
	cmpq	%rcx, %r13
	jne	LBB0_55
LBB0_56:                                ##   in Loop: Header=BB0_52 Depth=2
	movq	-192(%rbp), %r12        ## 8-byte Reload
	addq	$1, %r12
	movq	-104(%rbp), %rax        ## 8-byte Reload
	addq	-440(%rbp), %rax        ## 8-byte Folded Reload
	movq	%rax, -104(%rbp)        ## 8-byte Spill
	movq	-432(%rbp), %rcx        ## 8-byte Reload
	movq	-88(%rbp), %rsi         ## 8-byte Reload
	addq	%rcx, %rsi
	movq	-184(%rbp), %r10        ## 8-byte Reload
	addq	%rcx, %r10
	movq	-176(%rbp), %r11        ## 8-byte Reload
	addq	%rcx, %r11
	movq	-256(%rbp), %rax        ## 8-byte Reload
	addq	%rax, %r8
	movq	-168(%rbp), %rdx        ## 8-byte Reload
	addq	%rax, %rdx
	movq	-160(%rbp), %rdi        ## 8-byte Reload
	addq	%rax, %rdi
	addq	%rcx, -136(%rbp)        ## 8-byte Folded Spill
	movq	-200(%rbp), %rax        ## 8-byte Reload
	addq	%rax, -144(%rbp)        ## 8-byte Folded Spill
	addq	%rax, -152(%rbp)        ## 8-byte Folded Spill
	addq	%rax, -272(%rbp)        ## 8-byte Folded Spill
	movq	-96(%rbp), %r9          ## 8-byte Reload
	movq	-112(%rbp), %rax        ## 8-byte Reload
	addl	%r9d, %eax
	movq	%rax, -112(%rbp)        ## 8-byte Spill
	movq	-120(%rbp), %rax        ## 8-byte Reload
	addl	%r9d, %eax
	movq	%rax, -120(%rbp)        ## 8-byte Spill
	addl	%r9d, -124(%rbp)        ## 4-byte Folded Spill
	movq	-208(%rbp), %rax        ## 8-byte Reload
	cmpq	-264(%rbp), %rax        ## 8-byte Folded Reload
	jne	LBB0_52
## %bb.57:                              ##   in Loop: Header=BB0_19 Depth=1
	movq	-320(%rbp), %rcx        ## 8-byte Reload
	movq	%rcx, %rax
	cmpq	-72(%rbp), %rcx         ## 8-byte Folded Reload
	jne	LBB0_19
	jmp	LBB0_59
	.p2align	4, 0x90
LBB0_58:                                ##   in Loop: Header=BB0_19 Depth=1
	movq	%rax, %rcx
	addq	$1, %rcx
	movq	%rcx, %rax
	cmpq	-72(%rbp), %rcx         ## 8-byte Folded Reload
	jne	LBB0_19
LBB0_59:
	movq	_var_false@GOTPCREL(%rip), %rax
	cmpl	$0, (%rax)
	je	LBB0_61
## %bb.60:
	movq	%rbx, %rdi
	vzeroupper
	callq	_dummy
	movq	-80(%rbp), %rdi         ## 8-byte Reload
	callq	_dummy
	leaq	-56(%rbp), %rdi
	callq	_dummy
LBB0_61:
	xorl	%eax, %eax
	addq	$408, %rsp              ## imm = 0x198
	popq	%rbx
	popq	%r12
	popq	%r13
	popq	%r14
	popq	%r15
	popq	%rbp
	vzeroupper
	retq
	.cfi_endproc
                                        ## -- End function

.subsections_via_symbols
