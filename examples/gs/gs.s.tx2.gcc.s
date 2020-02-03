	.arch armv8.1-a+crypto+crc
	.file	"gs.f90"
	.text
	.align	2
	.p2align 4,,15
	.type	MAIN__, %function
MAIN__:
.LFB0:
	.cfi_startproc
	sub	sp, sp, #720
	.cfi_def_cfa_offset 720
	mov	x0, 128
	mov	w1, 12
	stp	x29, x30, [sp]
	.cfi_offset 29, -720
	.cfi_offset 30, -712
	mov	x29, sp
	movk	x0, 0x5, lsl 32
	stp	x19, x20, [sp, 16]
	.cfi_offset 19, -704
	.cfi_offset 20, -696
	adrp	x19, .LC0
	add	x19, x19, :lo12:.LC0
	stp	x21, x22, [sp, 32]
	stp	x0, x19, [sp, 192]
	add	x0, sp, 192
	stp	x23, x24, [sp, 48]
	stp	x25, x26, [sp, 64]
	stp	x27, x28, [sp, 80]
	str	w1, [sp, 208]
	.cfi_offset 21, -688
	.cfi_offset 22, -680
	.cfi_offset 23, -672
	.cfi_offset 24, -664
	.cfi_offset 25, -656
	.cfi_offset 26, -648
	.cfi_offset 27, -640
	.cfi_offset 28, -632
	bl	_gfortran_st_read
	mov	w2, 4
	add	x1, sp, 144
	add	x0, sp, 192
	bl	_gfortran_transfer_integer
	mov	w2, 4
	add	x1, sp, 148
	add	x0, sp, 192
	bl	_gfortran_transfer_integer
	add	x0, sp, 192
	bl	_gfortran_st_read_done
	ldp	w24, w23, [sp, 144]
	mov	x3, -1
	mov	x5, 4611686018427387904
	mov	x2, 2305843009213693951
	sxtw	x25, w24
	sxtw	x20, w23
	cmp	x25, 0
	csel	x21, x25, x3, ge
	cmp	x20, 0
	csel	x4, x20, x3, ge
	add	x21, x21, 1
	add	x6, x4, 1
	mul	x26, x6, x21
	cmp	x26, x5
	lsl	x27, x26, 1
	lsl	x7, x26, 4
	cset	w8, eq
	cmp	x27, x2
	cinc	w9, w8, gt
	cmp	x25, 0
	ccmp	x20, 0, 1, ge
	csel	x10, x7, xzr, ge
	cbnz	w9, .L159
	cmp	x10, 0
	mov	x28, 1
	csel	x0, x10, x28, ne
	bl	malloc
	stp	d8, d9, [sp, 96]
	.cfi_offset 73, -616
	.cfi_offset 72, -624
	cbz	x0, .L160
	cmp	w23, 1
	ble	.L5
	cmp	w24, 1
	ble	.L6
	sub	w12, w24, #2
	sub	x4, x27, x26
	lsl	x22, x21, 3
	mov	w8, w28
	add	x13, x21, x12
	mvn	x14, x12
	add	x10, x4, x21
	mov	x6, x12
	add	x15, x0, x13, lsl 3
	lsl	x17, x14, 3
	mov	x9, x21
	add	x5, x15, 16
.L10:
	add	x1, x17, x5
	sub	x18, x10, x9
	sub	x16, x5, x1
	sub	x30, x16, #8
	lsr	x3, x30, 3
	add	x2, x3, 1
	ands	x7, x2, 7
	beq	.L7
	cmp	x7, 1
	beq	.L104
	cmp	x7, 2
	beq	.L105
	cmp	x7, 3
	beq	.L106
	cmp	x7, 4
	beq	.L107
	cmp	x7, 5
	beq	.L108
	cmp	x7, 6
	beq	.L109
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
.L109:
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
.L108:
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
.L107:
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
.L106:
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
.L105:
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
.L104:
	str	xzr, [x1]
	str	xzr, [x1, x18, lsl 3]
	add	x1, x1, 8
	cmp	x1, x5
	beq	.L155
.L7:
	str	xzr, [x1]
	add	x28, x1, 8
	add	x16, x1, 16
	add	x15, x1, 24
	str	xzr, [x1, x18, lsl 3]
	add	x14, x1, 32
	add	x13, x1, 40
	add	x12, x1, 48
	str	xzr, [x1, 8]
	add	x11, x1, 56
	add	x1, x1, 64
	str	xzr, [x28, x18, lsl 3]
	str	xzr, [x1, -48]
	str	xzr, [x16, x18, lsl 3]
	str	xzr, [x1, -40]
	str	xzr, [x15, x18, lsl 3]
	str	xzr, [x1, -32]
	str	xzr, [x14, x18, lsl 3]
	str	xzr, [x1, -24]
	str	xzr, [x13, x18, lsl 3]
	str	xzr, [x1, -16]
	str	xzr, [x12, x18, lsl 3]
	str	xzr, [x1, -8]
	str	xzr, [x11, x18, lsl 3]
	cmp	x1, x5
	bne	.L7
.L155:
	add	w8, w8, 1
	add	x10, x10, x21
	add	x9, x9, x21
	add	x5, x5, x22
	cmp	w23, w8
	bne	.L10
.L9:
	mul	x20, x21, x20
	fmov	d0, 1.0e+0
	sub	x17, x26, x27
	and	w18, w24, 7
	mov	x2, 1
	add	x30, x4, x20
	neg	x3, x20, lsl 3
	add	x7, x0, x30, lsl 3
	str	d0, [x7, x17, lsl 3]
	add	x1, x7, 8
	str	d0, [x7]
	str	xzr, [x0]
	str	xzr, [x7, x3]
	cmp	w24, 1
	blt	.L151
	cbz	w18, .L13
	cmp	w18, 1
	beq	.L119
	cmp	w18, 2
	beq	.L120
	cmp	w18, 3
	beq	.L121
	cmp	w18, 4
	beq	.L122
	cmp	w18, 5
	beq	.L123
	cmp	w18, 6
	beq	.L124
	str	d0, [x1, x17, lsl 3]
	mov	x2, 2
	str	d0, [x1]
	str	xzr, [x0, 8]
	str	xzr, [x1, x3]
	add	x1, x1, 8
.L124:
	str	d0, [x1, x17, lsl 3]
	str	d0, [x1]
	str	xzr, [x0, x2, lsl 3]
	add	x2, x2, 1
	str	xzr, [x1, x3]
	add	x1, x1, 8
.L123:
	str	d0, [x1, x17, lsl 3]
	str	d0, [x1]
	str	xzr, [x0, x2, lsl 3]
	add	x2, x2, 1
	str	xzr, [x1, x3]
	add	x1, x1, 8
.L122:
	str	d0, [x1, x17, lsl 3]
	str	d0, [x1]
	str	xzr, [x0, x2, lsl 3]
	add	x2, x2, 1
	str	xzr, [x1, x3]
	add	x1, x1, 8
.L121:
	str	d0, [x1, x17, lsl 3]
	str	d0, [x1]
	str	xzr, [x0, x2, lsl 3]
	add	x2, x2, 1
	str	xzr, [x1, x3]
	add	x1, x1, 8
.L120:
	str	d0, [x1, x17, lsl 3]
	str	d0, [x1]
	str	xzr, [x0, x2, lsl 3]
	add	x2, x2, 1
	str	xzr, [x1, x3]
	add	x1, x1, 8
.L119:
	str	d0, [x1, x17, lsl 3]
	str	d0, [x1]
	str	xzr, [x0, x2, lsl 3]
	add	x2, x2, 1
	str	xzr, [x1, x3]
	add	x1, x1, 8
	cmp	w24, w2
	blt	.L151
.L13:
	str	d0, [x1, x17, lsl 3]
	add	x28, x1, 8
	add	x15, x2, 1
	add	x16, x1, 16
	str	d0, [x1]
	add	x13, x2, 2
	add	x14, x1, 24
	add	x12, x2, 3
	str	xzr, [x0, x2, lsl 3]
	add	x9, x1, 32
	add	x4, x2, 4
	add	x8, x1, 40
	str	xzr, [x1, x3]
	add	x11, x2, 5
	add	x5, x1, 48
	add	x10, x2, 6
	str	d0, [x28, x17, lsl 3]
	add	x20, x1, 56
	add	x18, x2, 7
	add	x2, x2, 8
	str	d0, [x1, 8]
	add	x1, x1, 64
	str	xzr, [x0, x15, lsl 3]
	str	xzr, [x28, x3]
	str	d0, [x16, x17, lsl 3]
	str	d0, [x1, -48]
	str	xzr, [x0, x13, lsl 3]
	str	xzr, [x16, x3]
	str	d0, [x14, x17, lsl 3]
	str	d0, [x1, -40]
	str	xzr, [x0, x12, lsl 3]
	str	xzr, [x14, x3]
	str	d0, [x9, x17, lsl 3]
	str	d0, [x1, -32]
	str	xzr, [x0, x4, lsl 3]
	str	xzr, [x9, x3]
	str	d0, [x8, x17, lsl 3]
	str	d0, [x1, -24]
	str	xzr, [x0, x11, lsl 3]
	str	xzr, [x8, x3]
	str	d0, [x5, x17, lsl 3]
	str	d0, [x1, -16]
	str	xzr, [x0, x10, lsl 3]
	str	xzr, [x5, x3]
	str	d0, [x20, x17, lsl 3]
	str	d0, [x1, -8]
	str	xzr, [x0, x18, lsl 3]
	str	xzr, [x20, x3]
	cmp	w24, w2
	bge	.L13
.L151:
	cmp	w24, 0
	csel	w17, w24, wzr, ge
	add	w11, w17, 1
.L8:
	tbnz	w23, #31, .L11
.L12:
	scvtf	d2, w11
	scvtf	d1, w24
	sub	x30, x27, x26
	sub	x25, x25, x26
	add	x26, x25, x26
	add	x27, x25, x27
	mov	w3, 1
	and	w7, w23, 7
	add	x2, x0, x22
	fdiv	d3, d2, d1
	str	d3, [x0]
	str	d3, [x0, x30, lsl 3]
	str	d3, [x0, x26, lsl 3]
	str	d3, [x0, x27, lsl 3]
	cmp	w23, w3
	blt	.L11
	cbz	w7, .L15
	cmp	w7, 1
	beq	.L113
	cmp	w7, 2
	beq	.L114
	cmp	w7, 3
	beq	.L115
	cmp	w7, 4
	beq	.L116
	cmp	w7, 5
	beq	.L117
	cmp	w7, 6
	beq	.L118
	str	d3, [x2]
	mov	w3, 2
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
.L118:
	str	d3, [x2]
	add	w3, w3, 1
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
.L117:
	str	d3, [x2]
	add	w3, w3, 1
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
.L116:
	str	d3, [x2]
	add	w3, w3, 1
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
.L115:
	str	d3, [x2]
	add	w3, w3, 1
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
.L114:
	str	d3, [x2]
	add	w3, w3, 1
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
.L113:
	str	d3, [x2]
	add	w3, w3, 1
	str	d3, [x2, x30, lsl 3]
	str	d3, [x2, x26, lsl 3]
	str	d3, [x2, x27, lsl 3]
	add	x2, x2, x22
	cmp	w23, w3
	blt	.L11
.L15:
	str	d3, [x2]
	add	x1, x2, x22
	add	w3, w3, 8
	str	d3, [x2, x30, lsl 3]
	add	x28, x1, x22
	str	d3, [x2, x26, lsl 3]
	add	x15, x28, x22
	str	d3, [x2, x27, lsl 3]
	add	x14, x15, x22
	str	d3, [x1]
	add	x16, x14, x22
	str	d3, [x1, x30, lsl 3]
	add	x13, x16, x22
	str	d3, [x1, x26, lsl 3]
	add	x12, x13, x22
	str	d3, [x1, x27, lsl 3]
	add	x2, x12, x22
	str	d3, [x28]
	str	d3, [x28, x30, lsl 3]
	str	d3, [x28, x26, lsl 3]
	str	d3, [x28, x27, lsl 3]
	str	d3, [x15]
	str	d3, [x15, x30, lsl 3]
	str	d3, [x15, x26, lsl 3]
	str	d3, [x15, x27, lsl 3]
	str	d3, [x14]
	str	d3, [x14, x30, lsl 3]
	str	d3, [x14, x26, lsl 3]
	str	d3, [x14, x27, lsl 3]
	str	d3, [x16]
	str	d3, [x16, x30, lsl 3]
	str	d3, [x16, x26, lsl 3]
	str	d3, [x16, x27, lsl 3]
	str	d3, [x13]
	str	d3, [x13, x30, lsl 3]
	str	d3, [x13, x26, lsl 3]
	str	d3, [x13, x27, lsl 3]
	str	d3, [x12]
	str	d3, [x12, x30, lsl 3]
	str	d3, [x12, x26, lsl 3]
	str	d3, [x12, x27, lsl 3]
	cmp	w23, w3
	bge	.L15
.L11:
	add	x6, x21, x6, uxtw
	adrp	x4, .LC6
	add	x9, x22, 8
	fmov	d9, 2.5e-1
	ldr	d8, [x4, #:lo12:.LC6]
	add	x27, x0, x9
	mov	w20, 51711
	add	x0, x0, x6, lsl 3
	lsl	x28, x21, 1
	mov	w26, 10
	movk	w20, 0x3b9a, lsl 16
	add	x25, x0, 16
.L14:
	add	x0, sp, 176
	add	x1, sp, 160
	lsl	w26, w26, 1
	bl	timing_
	mov	w0, 0
	.p2align 4
.L18:
	cmp	w23, 1
	ble	.L21
	cmp	w24, 1
	ble	.L21
	mov	x11, 0
	mov	w10, 1
	mov	x7, x25
	mov	x9, x28
	mov	x8, x21
	mov	x6, x27
	.p2align 4
.L22:
	sub	x5, x7, x6
	add	w10, w10, 1
	mov	x15, x6
	sub	x18, x11, x8
	sub	x17, x5, #8
	sub	x30, x9, x8
	ldr	d30, [x6, -8]
	lsr	x3, x17, 3
	add	x2, x3, 1
	ands	x1, x2, 3
	beq	.L20
	cmp	x1, 1
	beq	.L111
	cmp	x1, 2
	beq	.L112
	ldr	d4, [x6, x18, lsl 3]
	ldr	d6, [x6, 8]
	ldr	d5, [x6, x30, lsl 3]
	fadd	d7, d4, d6
	fadd	d16, d7, d30
	fadd	d17, d16, d5
	fmul	d30, d17, d9
	str	d30, [x15], 8
.L112:
	ldr	d18, [x15, x18, lsl 3]
	ldr	d20, [x15, 8]
	ldr	d19, [x15, x30, lsl 3]
	fadd	d21, d18, d20
	fadd	d22, d21, d30
	fadd	d23, d22, d19
	fmul	d30, d23, d9
	str	d30, [x15], 8
.L111:
	ldr	d24, [x15, x18, lsl 3]
	ldr	d26, [x15, 8]
	ldr	d25, [x15, x30, lsl 3]
	fadd	d27, d24, d26
	fadd	d28, d27, d30
	fadd	d29, d28, d25
	fmul	d30, d29, d9
	str	d30, [x15], 8
	cmp	x7, x15
	beq	.L154
    // OSACA-BEGIN
.L20:
	ldr	d31, [x15, x18, lsl 3]
	ldr	d0, [x15, 8]
	mov	x14, x15
	add	x16, x15, 24
	ldr	d2, [x15, x30, lsl 3]
	add	x15, x15, 32
	fadd	d1, d31, d0
	fadd	d3, d1, d30
	fadd	d4, d3, d2
	fmul	d5, d4, d9
	str	d5, [x14], 8
	ldr	d6, [x14, x18, lsl 3]
	ldr	d16, [x14, 8]
	add	x13, x14, 8
	ldr	d7, [x14, x30, lsl 3]
	fadd	d17, d6, d16
	fadd	d18, d17, d5
	fadd	d19, d18, d7
	fmul	d20, d19, d9
	str	d20, [x15, -24]
	ldr	d21, [x13, x18, lsl 3]
	ldr	d23, [x14, 16]
	ldr	d22, [x13, x30, lsl 3]
	fadd	d24, d21, d23
	fadd	d25, d24, d20
	fadd	d26, d25, d22
	fmul	d27, d26, d9
	str	d27, [x14, 8]
	ldr	d30, [x15]
	ldr	d28, [x16, x18, lsl 3]
	ldr	d29, [x16, x30, lsl 3]
	fadd	d31, d28, d30
	fadd	d2, d31, d27
	fadd	d0, d2, d29
	fmul	d30, d0, d9
	str	d30, [x15, -8]
	cmp	x7, x15
	bne	.L20
    // OSACA-END
.L154:
	add	x6, x6, x22
	add	x11, x11, x21
	add	x8, x8, x21
	add	x9, x9, x21
	add	x7, x7, x22
	cmp	w23, w10
	bne	.L22
.L21:
	add	w4, w0, 1
	cmp	w26, w4
	beq	.L17
	mov	w0, w4
	b	.L18
.L17:
	add	w12, w0, 2
	add	x1, sp, 152
	add	x0, sp, 168
	str	w12, [sp, 124]
	str	w12, [sp, 140]
	bl	timing_
	ldp	d3, d1, [sp, 168]
	ldr	w5, [sp, 124]
	fsub	d4, d3, d1
	fcmpe	d4, d8
	ccmp	w26, w20, 0, lt
	ble	.L14
	cmp	w5, w26
	ble	.L23
	str	w26, [sp, 140]
.L23:
	mov	x21, 128
	add	x0, sp, 192
	mov	w22, 72
	movk	x21, 0x6, lsl 32
	str	w22, [sp, 208]
	sub	w24, w24, #1
	sub	w23, w23, #1
	stp	x21, x19, [sp, 192]
	bl	_gfortran_st_write
	adrp	x19, .LANCHOR0
	adrp	x27, .LC7
	add	x28, x19, :lo12:.LANCHOR0
	mov	x2, 14
	add	x0, sp, 192
	mov	x1, x28
	bl	_gfortran_transfer_character_write
	mov	w2, 4
	add	x1, sp, 140
	add	x0, sp, 192
	bl	_gfortran_transfer_integer_write
	add	x1, x28, 16
	mov	x2, 14
	add	x0, sp, 192
	bl	_gfortran_transfer_character_write
	ldr	w25, [sp, 140]
	scvtf	d9, w24
	scvtf	d8, w23
	ldr	d5, [x27, #:lo12:.LC7]
	ldp	d18, d19, [sp, 168]
	mov	w2, 8
	add	x1, sp, 184
	add	x0, sp, 192
	scvtf	d7, w25
	fsub	d20, d18, d19
	fmul	d6, d9, d8
	fmul	d16, d7, d5
	fmul	d17, d6, d16
	fdiv	d21, d17, d20
	str	d21, [sp, 184]
	bl	_gfortran_transfer_real_write
	add	x1, x28, 32
	mov	x2, 6
	add	x0, sp, 192
	bl	_gfortran_transfer_character_write
	add	x0, sp, 192
	bl	_gfortran_st_write_done
	mov	w2, 0
	mov	x1, 0
	mov	x0, 0
	bl	_gfortran_stop_string
.L5:
	tbnz	w24, #31, .L25
.L157:
	sub	x4, x27, x26
	lsl	x22, x21, 3
	sub	w6, w24, #2
	b	.L9
.L6:
	tbz	w24, #31, .L157
	mov	w11, 0
	lsl	x22, x21, 3
	sub	w6, w24, #2
	b	.L12
.L159:
	.cfi_restore 72
	.cfi_restore 73
	adrp	x26, .LC1
	stp	d8, d9, [sp, 96]
	.cfi_offset 73, -616
	.cfi_offset 72, -624
	add	x0, x26, :lo12:.LC1
	bl	_gfortran_runtime_error
.L25:
	mov	w11, 0
	lsl	x22, x21, 3
	sub	w6, w24, #2
	b	.L8
.L160:
	adrp	x20, .LC2
	add	x0, x20, :lo12:.LC2
	bl	_gfortran_os_error
	.cfi_endproc
.LFE0:
	.size	MAIN__, .-MAIN__
	.section	.text.startup,"ax",@progbits
	.align	2
	.p2align 4,,15
	.global	main
	.type	main, %function
main:
.LFB1:
	.cfi_startproc
	stp	x29, x30, [sp, -16]!
	.cfi_def_cfa_offset 16
	.cfi_offset 29, -16
	.cfi_offset 30, -8
	mov	x29, sp
	bl	_gfortran_set_args
	adrp	x1, .LANCHOR0
	mov	w0, 7
	add	x2, x1, :lo12:.LANCHOR0
	add	x1, x2, 40
	bl	_gfortran_set_options
	bl	MAIN__
	.cfi_endproc
.LFE1:
	.size	main, .-main
	.section	.rodata
	.align	3
	.set	.LANCHOR0,. + 0
.LC3:
	.ascii	"# Iterations: "
	.zero	2
.LC4:
	.ascii	" Performance: "
	.zero	2
.LC5:
	.ascii	" MLUPs"
	.zero	2
	.type	options.8.2753, %object
	.size	options.8.2753, 28
options.8.2753:
	.word	68
	.word	8191
	.word	0
	.word	1
	.word	1
	.word	0
	.word	31
	.section	.rodata.cst8,"aM",@progbits,8
	.align	3
.LC6:
	.word	2576980378
	.word	1070176665
.LC7:
	.word	2696277389
	.word	1051772663
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align	3
.LC0:
	.string	"gs.f90"
	.zero	1
.LC1:
	.string	"Integer overflow when calculating the amount of memory to allocate"
	.zero	5
.LC2:
	.string	"Allocation would exceed memory limit"
	.ident	"GCC: (ARM-build-8) 8.2.0"
	.section	.note.GNU-stack,"",@progbits
