	.file	"add_riscv.c"
	.option pic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_v1p0_zicsr2p0_zifencei2p0_zve32f1p0_zve32x1p0_zve64d1p0_zve64f1p0_zve64x1p0_zvl128b1p0_zvl32b1p0_zvl64b1p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	kernel
	.type	kernel, @function
kernel:
.LFB22:
	.cfi_startproc
	ble	a3,zero,.L10
	addiw	a5,a3,-1
	li	a4,2
	bleu	a5,a4,.L3
	addi	a5,a2,8
	addi	a4,a1,8
	sub	a5,a0,a5
	sub	a4,a0,a4
	bgtu	a5,a4,.L14
.L4:
	csrr	a4,vlenb
	addi	a4,a4,-16
	bleu	a5,a4,.L3
.L5:
	vsetvli	a5,a3,e64,m1,ta,ma
	vle64.v	v1,0(a1)
	vle64.v	v2,0(a2)
	slli	a4,a5,3
	sub	a3,a3,a5
	add	a1,a1,a4
	add	a2,a2,a4
	vfadd.vv	v1,v1,v2
	vse64.v	v1,0(a0)
	add	a0,a0,a4
	bne	a3,zero,.L5
	ret
.L3:
	slli	a3,a3,3
	add	a3,a1,a3
.L7:
	fld	fa5,0(a1)
	fld	fa4,0(a2)
	addi	a1,a1,8
	addi	a2,a2,8
	fadd.d	fa5,fa5,fa4
	addi	a0,a0,8
	fsd	fa5,-8(a0)
	bne	a1,a3,.L7
.L10:
	ret
.L14:
	mv	a5,a4
	j	.L4
	.cfi_endproc
.LFE22:
	.size	kernel, .-kernel
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align	3
.LC0:
	.string	"RISC-V Vector add: a[i] = b[i] + c[i], size=%d\n"
	.align	3
.LC2:
	.string	"Checksum: %f\n"
	.section	.text.startup,"ax",@progbits
	.align	1
	.globl	main
	.type	main, @function
main:
.LFB23:
	.cfi_startproc
	addi	sp,sp,-48
	.cfi_def_cfa_offset 48
	sd	ra,40(sp)
	sd	s0,32(sp)
	sd	s1,24(sp)
	sd	s2,16(sp)
	sd	s3,8(sp)
	sd	s4,0(sp)
	.cfi_offset 1, -8
	.cfi_offset 8, -16
	.cfi_offset 9, -24
	.cfi_offset 18, -32
	.cfi_offset 19, -40
	.cfi_offset 20, -48
	li	a5,1
	bgt	a0,a5,.L35
	li	a1,1000
	lla	a0,.LC0
	call	printf@plt
	li	a0,8192
	addi	a0,a0,-192
	call	malloc@plt
	mv	s0,a0
	li	a0,8192
	addi	a0,a0,-192
	call	malloc@plt
	mv	s2,a0
	li	a0,8192
	addi	a0,a0,-192
	call	malloc@plt
	li	s3,8192
	mv	s1,a0
	addi	s3,s3,-192
	li	s4,1000
.L22:
	slli	a5,s4,32
	srli	a2,a5,29
	li	a1,0
	mv	a0,s0
	call	memset@plt
	mv	a4,s2
	li	a5,0
.L18:
	fcvt.d.w	fa5,a5
	addiw	a5,a5,1
	addi	a4,a4,8
	fsd	fa5,-8(a4)
	bne	a5,s4,.L18
	fld	fa5,.LC1,a4
	vsetvli	a3,zero,e64,m1,ta,ma
	mv	a2,a5
	vfmv.v.f	v4,fa5
	vsetvli	zero,zero,e32,mf2,ta,ma
	vid.v	v2
	mv	a3,s1
.L19:
	vsetvli	a4,a2,e32,mf2,ta,ma
	vfwcvt.f.x.v	v1,v2
	vsetvli	a0,zero,e32,mf2,ta,ma
	vmv.v.x	v3,a4
	vsetvli	zero,a4,e64,m1,ta,ma
	vfmul.vv	v1,v1,v4
	vsetvli	a0,zero,e32,mf2,ta,ma
	vadd.vv	v2,v2,v3
	vsetvli	zero,a4,e64,m1,ta,ma
	slli	a1,a4,3
	sub	a2,a2,a4
	vse64.v	v1,0(a3)
	add	a3,a3,a1
	bne	a2,zero,.L19
	mv	a3,s0
	mv	a0,s1
	mv	a1,s2
.L20:
	vsetvli	a4,a5,e64,m1,ta,ma
	vle64.v	v2,0(a1)
	vle64.v	v1,0(a0)
	slli	a2,a4,3
	sub	a5,a5,a4
	add	a1,a1,a2
	add	a0,a0,a2
	vfadd.vv	v1,v1,v2
	vse64.v	v1,0(a3)
	add	a3,a3,a2
	bne	a5,zero,.L20
	fmv.d.x	fa5,zero
	add	s3,s0,s3
	mv	a5,s0
.L21:
	fld	fa4,0(a5)
	addi	a5,a5,8
	fadd.d	fa5,fa5,fa4
	bne	s3,a5,.L21
.L17:
	fmv.x.d	a1,fa5
	lla	a0,.LC2
	call	printf@plt
	mv	a0,s0
	call	free@plt
	mv	a0,s2
	call	free@plt
	mv	a0,s1
	call	free@plt
	ld	ra,40(sp)
	.cfi_remember_state
	.cfi_restore 1
	ld	s0,32(sp)
	.cfi_restore 8
	ld	s1,24(sp)
	.cfi_restore 9
	ld	s2,16(sp)
	.cfi_restore 18
	ld	s3,8(sp)
	.cfi_restore 19
	ld	s4,0(sp)
	.cfi_restore 20
	li	a0,0
	addi	sp,sp,48
	.cfi_def_cfa_offset 0
	jr	ra
.L35:
	.cfi_restore_state
	ld	a0,8(a1)
	li	a2,10
	li	a1,0
	call	strtol@plt
	sext.w	s4,a0
	mv	a1,s4
	lla	a0,.LC0
	call	printf@plt
	slli	s3,s4,3
	mv	a0,s3
	call	malloc@plt
	mv	s0,a0
	mv	a0,s3
	call	malloc@plt
	mv	s2,a0
	mv	a0,s3
	call	malloc@plt
	mv	s1,a0
	bgt	s4,zero,.L22
	fmv.d.x	fa5,zero
	j	.L17
	.cfi_endproc
.LFE23:
	.size	main, .-main
	.section	.rodata.cst8,"aM",@progbits,8
	.align	3
.LC1:
	.word	0
	.word	1073741824
	.ident	"GCC: (GNU) 14.2.1 20250207"
	.section	.note.GNU-stack,"",@progbits