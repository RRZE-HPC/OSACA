	.file	"triad.c"
	.option pic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	kernel
	.type	kernel, @function
kernel:
.LFB22:
	.cfi_startproc
	ble	a3,zero,.L1
	slli	a3,a3,3
	add	a5,a1,a3
.L3:
	fld	fa5,0(a2)
	fld	fa4,0(a1)
	addi	a1,a1,8
	addi	a2,a2,8
	fmadd.d	fa5,fa5,fa0,fa4
	addi	a0,a0,8
	fsd	fa5,-8(a0)
	bne	a1,a5,.L3
.L1:
	ret
	.cfi_endproc
.LFE22:
	.size	kernel, .-kernel
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align	3
.LC0:
	.string	"RISC-V STREAM triad: a[i] = b[i] + s * c[i], size=%d\n"
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
	bgt	a0,a5,.L21
	li	a1,1000
	lla	a0,.LC0
	call	printf@plt
	li	a0,8192
	addi	a0,a0,-192
	call	malloc@plt
	mv	s1,a0
	li	a0,8192
	addi	a0,a0,-192
	call	malloc@plt
	mv	s2,a0
	li	a0,8192
	addi	a0,a0,-192
	call	malloc@plt
	li	s0,8192
	mv	s3,a0
	addi	s0,s0,-192
	li	s4,1000
.L13:
	slli	a5,s4,32
	srli	a2,a5,29
	li	a1,0
	mv	a0,s1
	call	memset@plt
	mv	a4,s2
	mv	a3,s2
	li	a5,0
.L9:
	fcvt.d.w	fa5,a5
	mv	a1,a5
	addiw	a5,a5,1
	fsd	fa5,0(a3)
	addi	a3,a3,8
	bne	a5,s4,.L9
	mv	a2,s3
	mv	a3,s3
	li	a5,0
.L10:
	fcvt.d.w	fa5,a5
	mv	a0,a5
	addi	a3,a3,8
	fadd.d	fa5,fa5,fa5
	addiw	a5,a5,1
	fsd	fa5,-8(a3)
	bne	a0,a1,.L10
	fld	fa3,.LC1,a5
	add	a1,s2,s0
	mv	a5,s1
	mv	a3,s1
.L11:
	fld	fa5,0(a2)
	fld	fa4,0(a4)
	addi	a4,a4,8
	addi	a2,a2,8
	fmadd.d	fa5,fa5,fa3,fa4
	addi	a3,a3,8
	fsd	fa5,-8(a3)
	bne	a4,a1,.L11
	fmv.d.x	fa5,zero
	add	s0,s1,s0
.L12:
	fld	fa4,0(a5)
	addi	a5,a5,8
	fadd.d	fa5,fa5,fa4
	bne	a5,s0,.L12
.L8:
	fmv.x.d	a1,fa5
	lla	a0,.LC2
	call	printf@plt
	mv	a0,s1
	call	free@plt
	mv	a0,s2
	call	free@plt
	mv	a0,s3
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
.L21:
	.cfi_restore_state
	ld	a0,8(a1)
	li	a2,10
	li	a1,0
	call	strtol@plt
	sext.w	s4,a0
	mv	a1,s4
	lla	a0,.LC0
	call	printf@plt
	slli	s0,s4,3
	mv	a0,s0
	call	malloc@plt
	mv	s1,a0
	mv	a0,s0
	call	malloc@plt
	mv	s2,a0
	mv	a0,s0
	call	malloc@plt
	mv	s3,a0
	bgt	s4,zero,.L13
	fmv.d.x	fa5,zero
	j	.L8
	.cfi_endproc
.LFE23:
	.size	main, .-main
	.section	.rodata.cst8,"aM",@progbits,8
	.align	3
.LC1:
	.word	1374389535
	.word	1074339512
	.ident	"GCC: (GNU) 14.2.1 20250207"
	.section	.note.GNU-stack,"",@progbits