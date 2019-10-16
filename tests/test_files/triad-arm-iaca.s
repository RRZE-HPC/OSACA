	.text
	.file	"triad.c"
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3               // -- Begin function triad
.LCPI0_0:
	.xword	4596373779694328218     // double 0.20000000000000001
.LCPI0_1:
	.xword	4652007308841189376     // double 1000
.LCPI0_2:
	.xword	4517329193108106637     // double 9.9999999999999995E-7
.LCPI0_3:
	.xword	4629700416936869888     // double 32
.LCPI0_4:
	.xword	4562146422526312448     // double 9.765625E-4
	.text
	.globl	triad
	.p2align	6
	.type	triad,@function
triad:                                  // @triad
	.cfi_startproc
// %bb.0:
	sub	sp, sp, #224            // =224
	str	d8, [sp, #112]          // 8-byte Folded Spill
	stp	x28, x27, [sp, #128]    // 16-byte Folded Spill
	stp	x26, x25, [sp, #144]    // 16-byte Folded Spill
	stp	x24, x23, [sp, #160]    // 16-byte Folded Spill
	stp	x22, x21, [sp, #176]    // 16-byte Folded Spill
	stp	x20, x19, [sp, #192]    // 16-byte Folded Spill
	stp	x29, x30, [sp, #208]    // 16-byte Folded Spill
	add	x29, sp, #208           // =208
	.cfi_def_cfa w29, 16
	.cfi_offset w30, -8
	.cfi_offset w29, -16
	.cfi_offset w19, -24
	.cfi_offset w20, -32
	.cfi_offset w21, -40
	.cfi_offset w22, -48
	.cfi_offset w23, -56
	.cfi_offset w24, -64
	.cfi_offset w25, -72
	.cfi_offset w26, -80
	.cfi_offset w27, -88
	.cfi_offset w28, -96
	.cfi_offset b8, -112
	mov	w19, w0
	orr	w0, wzr, #0x40
	sbfiz	x23, x19, #3, #32
	mov	x1, x23
	bl	aligned_alloc
	mov	x20, x0
	orr	w0, wzr, #0x40
	mov	x1, x23
	bl	aligned_alloc
	str	x0, [sp, #88]           // 8-byte Folded Spill
	orr	w0, wzr, #0x40
	mov	x1, x23
	bl	aligned_alloc
	mov	x22, x0
	orr	w0, wzr, #0x40
	mov	x1, x23
	bl	aligned_alloc
	mov	x23, x0
	cmp	w19, #0                 // =0
	b.le	.LBB0_3
// %bb.1:
	mov	w24, w19
	cmp	w19, #7                 // =7
	b.hi	.LBB0_9
// %bb.2:
	mov	x8, xzr
	b	.LBB0_17
.LBB0_3:
	adrp	x8, .LCPI0_0
	orr	w25, wzr, #0x1
	ldr	d8, [x8, :lo12:.LCPI0_0]
	.p2align	6
.LBB0_4:                                // =>This Loop Header: Depth=1
                                        //     Child Loop BB0_5 Depth 2
	sub	x0, x29, #88            // =88
	add	x1, sp, #96             // =96
	bl	timing
	mov	w21, w25
	cbz	w25, .LBB0_8
	.p2align	6
.LBB0_5:                                //   Parent Loop BB0_4 Depth=1
                                        // =>  This Inner Loop Header: Depth=2
	ldr	d0, [x20]
	fcmp	d0, #0.0
	b.le	.LBB0_7
// %bb.6:                               //   in Loop: Header=BB0_5 Depth=2
	mov	x0, x20
	bl	dummy
.LBB0_7:                                //   in Loop: Header=BB0_5 Depth=2
	subs	w21, w21, #1            // =1
	b.ne	.LBB0_5
.LBB0_8:                                //   in Loop: Header=BB0_4 Depth=1
	add	x0, sp, #104            // =104
	add	x1, sp, #96             // =96
	bl	timing
	ldr	d0, [sp, #104]
	ldur	d1, [x29, #-88]
	fsub	d1, d0, d1
	lsl	w25, w25, #1
	fcmp	d1, d8
	b.mi	.LBB0_4
	b	.LBB0_38
.LBB0_9:
	and	x8, x24, #0xfffffff8
	sub	x10, x8, #8             // =8
	lsr	x11, x10, #3
	add	w9, w11, #1             // =1
	and	x9, x9, #0x3
	cmp	x10, #24                // =24
	b.hs	.LBB0_11
// %bb.10:
	orr	w13, wzr, #0x20
	cbnz	x9, .LBB0_14
	b	.LBB0_16
.LBB0_11:
	mov	x16, #28286
	movk	x16, #29109, lsl #16
	ldr	x15, [sp, #88]          // 8-byte Folded Reload
	movk	x16, #34426, lsl #32
	movk	x16, #16000, lsl #48
	dup	v0.2d, x16
	mvn	x11, x11
	mov	x10, xzr
	add	x11, x9, x11
	add	x12, x23, #128          // =128
	add	x13, x20, #128          // =128
	add	x14, x22, #128          // =128
	add	x15, x15, #128          // =128
	.p2align	6
.LBB0_12:                               // =>This Inner Loop Header: Depth=1
	stp	q0, q0, [x12]
	stp	q0, q0, [x12, #-128]
	stp	q0, q0, [x12, #32]
	stp	q0, q0, [x12, #-96]
	stp	q0, q0, [x14]
	add	x10, x10, #32           // =32
	stp	q0, q0, [x14, #-128]
	stp	q0, q0, [x14, #32]
	stp	q0, q0, [x14, #-96]
	stp	q0, q0, [x15]
	stp	q0, q0, [x15, #-128]
	stp	q0, q0, [x15, #32]
	stp	q0, q0, [x15, #-96]
	stp	q0, q0, [x13]
	stp	q0, q0, [x13, #-128]
	stp	q0, q0, [x13, #32]
	stp	q0, q0, [x13, #-96]
	stp	q0, q0, [x12, #64]
	stp	q0, q0, [x12, #-64]
	stp	q0, q0, [x12, #96]
	stp	q0, q0, [x12, #-32]
	add	x12, x12, #256          // =256
	stp	q0, q0, [x14, #64]
	stp	q0, q0, [x14, #-64]
	stp	q0, q0, [x14, #96]
	stp	q0, q0, [x14, #-32]
	add	x14, x14, #256          // =256
	stp	q0, q0, [x15, #64]
	stp	q0, q0, [x15, #-64]
	stp	q0, q0, [x15, #96]
	stp	q0, q0, [x15, #-32]
	add	x15, x15, #256          // =256
	stp	q0, q0, [x13, #64]
	stp	q0, q0, [x13, #-64]
	stp	q0, q0, [x13, #96]
	stp	q0, q0, [x13, #-32]
	add	x13, x13, #256          // =256
	adds	x11, x11, #4            // =4
	b.ne	.LBB0_12
// %bb.13:
	lsl	x10, x10, #3
	orr	x13, x10, #0x20
	cbz	x9, .LBB0_16
.LBB0_14:
	ldr	x14, [sp, #88]          // 8-byte Folded Reload
	add	x10, x23, x13
	add	x11, x22, x13
	add	x12, x20, x13
	add	x13, x14, x13
	mov	x14, #28286
	movk	x14, #29109, lsl #16
	movk	x14, #34426, lsl #32
	movk	x14, #16000, lsl #48
	dup	v0.2d, x14
	neg	x9, x9
	.p2align	6
.LBB0_15:                               // =>This Inner Loop Header: Depth=1
	stp	q0, q0, [x10]
	stp	q0, q0, [x11]
	stp	q0, q0, [x10, #-32]
	stp	q0, q0, [x13]
	stp	q0, q0, [x11, #-32]
	add	x10, x10, #64           // =64
	stp	q0, q0, [x12]
	stp	q0, q0, [x13, #-32]
	add	x11, x11, #64           // =64
	stp	q0, q0, [x12, #-32]
	add	x12, x12, #64           // =64
	add	x13, x13, #64           // =64
	adds	x9, x9, #1              // =1
	b.ne	.LBB0_15
.LBB0_16:
	cmp	x8, x24
	b.eq	.LBB0_19
.LBB0_17:
	ldr	x10, [sp, #88]          // 8-byte Folded Reload
	mov	x13, #28286
	movk	x13, #29109, lsl #16
	lsl	x12, x8, #3
	movk	x13, #34426, lsl #32
	add	x9, x20, x12
	movk	x13, #16000, lsl #48
	add	x10, x10, x12
	add	x11, x22, x12
	add	x12, x23, x12
	sub	x8, x24, x8
	.p2align	6
.LBB0_18:                               // =>This Inner Loop Header: Depth=1
	str	x13, [x12], #8
	str	x13, [x11], #8
	str	x13, [x10], #8
	str	x13, [x9], #8
	subs	x8, x8, #1              // =1
	b.ne	.LBB0_18
.LBB0_19:
	ldr	x10, [sp, #88]          // 8-byte Folded Reload
	add	x8, x20, #256           // =256
	and	x26, x24, #0xfffffff8
	str	x8, [sp, #40]           // 8-byte Folded Spill
	add	x8, x23, #256           // =256
	sub	x27, x26, #8            // =8
	str	x8, [sp, #32]           // 8-byte Folded Spill
	add	x8, x22, #256           // =256
	orr	w25, wzr, #0x1
	str	x8, [sp, #24]           // 8-byte Folded Spill
	add	x8, x10, #256           // =256
	str	x8, [sp, #16]           // 8-byte Folded Spill
	lsr	x8, x27, #3
	add	w9, w8, #1              // =1
	mvn	x8, x8
	and	x28, x9, #0x7
	add	x8, x28, x8
	str	x8, [sp, #8]            // 8-byte Folded Spill
	neg	x8, x28
	str	x8, [sp, #80]           // 8-byte Folded Spill
	add	x8, x10, #32            // =32
	str	x8, [sp, #72]           // 8-byte Folded Spill
	add	x8, x22, #32            // =32
	str	x8, [sp, #64]           // 8-byte Folded Spill
	add	x8, x20, #32            // =32
	str	x8, [sp, #56]           // 8-byte Folded Spill
	add	x8, x23, #32            // =32
	str	x8, [sp, #48]           // 8-byte Folded Spill
	adrp	x8, .LCPI0_0
	ldr	d8, [x8, :lo12:.LCPI0_0]
	.p2align	6
.LBB0_20:                               // =>This Loop Header: Depth=1
                                        //     Child Loop BB0_22 Depth 2
                                        //       Child Loop BB0_29 Depth 3
                                        //       Child Loop BB0_32 Depth 3
                                        //       Child Loop BB0_35 Depth 3
	sub	x0, x29, #88            // =88
	add	x1, sp, #96             // =96
	bl	timing
	cbz	w25, .LBB0_37
// %bb.21:                              //   in Loop: Header=BB0_20 Depth=1
	mov	w21, wzr
	.p2align	6
.LBB0_22:                               //   Parent Loop BB0_20 Depth=1
                                        // =>  This Loop Header: Depth=2
                                        //       Child Loop BB0_29 Depth 3
                                        //       Child Loop BB0_32 Depth 3
                                        //       Child Loop BB0_35 Depth 3
	ldr	d0, [x20]
	fcmp	d0, #0.0
	b.le	.LBB0_24
// %bb.23:                              //   in Loop: Header=BB0_22 Depth=2
	mov	x0, x20
	bl	dummy
.LBB0_24:                               //   in Loop: Header=BB0_22 Depth=2
	cmp	w19, #7                 // =7
	b.hi	.LBB0_26
// %bb.25:                              //   in Loop: Header=BB0_22 Depth=2
	mov	x12, xzr
	b	.LBB0_34
	.p2align	6
.LBB0_26:                               //   in Loop: Header=BB0_22 Depth=2
	cmp	x27, #56                // =56
	b.hs	.LBB0_28
// %bb.27:                              //   in Loop: Header=BB0_22 Depth=2
	mov	x8, xzr
	cbnz	x28, .LBB0_31
	b	.LBB0_33
	.p2align	6
.LBB0_28:                               //   in Loop: Header=BB0_22 Depth=2
	ldp	x9, x10, [sp, #16]      // 8-byte Folded Reload
	ldp	x11, x12, [sp, #32]     // 8-byte Folded Reload
	ldr	x13, [sp, #8]           // 8-byte Folded Reload
	mov	x8, xzr
	.p2align	6
    mov x1, #111                // OSACA START
    .byte 213,3,32,31           // OSACA START
.LBB0_29:                               //   Parent Loop BB0_20 Depth=1
                                        //     Parent Loop BB0_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q2, q5, [x10, #-256]
	ldp	q6, q7, [x10, #-224]
	ldp	q16, q17, [x11, #-256]
	ldp	q18, q19, [x11, #-224]
	fmul	v2.2d, v2.2d, v16.2d
	fmul	v5.2d, v5.2d, v17.2d
	fmul	v6.2d, v6.2d, v18.2d
	ldp	q0, q1, [x9, #-256]
	ldp	q3, q4, [x9, #-224]
	fmul	v7.2d, v7.2d, v19.2d
	fadd	v0.2d, v0.2d, v2.2d
	fadd	v2.2d, v1.2d, v5.2d
	stp	q0, q2, [x12, #-256]
	fadd	v1.2d, v3.2d, v6.2d
	ldp	q6, q17, [x10, #-192]
	ldp	q18, q19, [x10, #-160]
	ldp	q20, q21, [x11, #-192]
	ldp	q22, q23, [x11, #-160]
	fmul	v6.2d, v6.2d, v20.2d
	fmul	v17.2d, v17.2d, v21.2d
	fmul	v18.2d, v18.2d, v22.2d
	fadd	v3.2d, v4.2d, v7.2d
	stp	q1, q3, [x12, #-224]
	ldp	q4, q5, [x9, #-192]
	ldp	q7, q16, [x9, #-160]
	fmul	v19.2d, v19.2d, v23.2d
	fadd	v4.2d, v4.2d, v6.2d
	fadd	v6.2d, v5.2d, v17.2d
	stp	q4, q6, [x12, #-192]
	fadd	v5.2d, v7.2d, v18.2d
	ldp	q18, q21, [x10, #-128]
	ldp	q22, q23, [x10, #-96]
	ldp	q24, q25, [x11, #-128]
	ldp	q26, q27, [x11, #-96]
	fmul	v18.2d, v18.2d, v24.2d
	fmul	v21.2d, v21.2d, v25.2d
	fmul	v22.2d, v22.2d, v26.2d
	fadd	v7.2d, v16.2d, v19.2d
	stp	q5, q7, [x12, #-160]
	ldp	q16, q17, [x9, #-128]
	ldp	q19, q20, [x9, #-96]
	fadd	v16.2d, v16.2d, v18.2d
	fadd	v18.2d, v17.2d, v21.2d
	stp	q16, q18, [x12, #-128]
	fadd	v17.2d, v19.2d, v22.2d
	ldp	q22, q25, [x10, #-64]
	ldp	q28, q29, [x11, #-64]
	fmul	v23.2d, v23.2d, v27.2d
	ldp	q26, q27, [x10, #-32]
	fmul	v22.2d, v22.2d, v28.2d
	fmul	v25.2d, v25.2d, v29.2d
	ldp	q28, q29, [x11, #-32]
	fmul	v26.2d, v26.2d, v28.2d
	fmul	v27.2d, v27.2d, v29.2d
	fadd	v19.2d, v20.2d, v23.2d
	stp	q17, q19, [x12, #-96]
	ldp	q20, q21, [x9, #-64]
	ldp	q23, q24, [x9, #-32]
	fadd	v20.2d, v20.2d, v22.2d
	fadd	v22.2d, v21.2d, v25.2d
	stp	q20, q22, [x12, #-64]
	fadd	v21.2d, v23.2d, v26.2d
	fadd	v23.2d, v24.2d, v27.2d
	stp	q21, q23, [x12, #-32]
	ldp	q24, q25, [x10]
	ldp	q28, q29, [x11]
	ldp	q26, q27, [x10, #32]
	fmul	v24.2d, v24.2d, v28.2d
	fmul	v25.2d, v25.2d, v29.2d
	ldp	q28, q29, [x11, #32]
	fmul	v26.2d, v26.2d, v28.2d
	fmul	v27.2d, v27.2d, v29.2d
	ldp	q28, q29, [x9]
	fadd	v24.2d, v28.2d, v24.2d
	fadd	v25.2d, v29.2d, v25.2d
	stp	q24, q25, [x12]
	ldp	q28, q29, [x9, #32]
	fadd	v26.2d, v28.2d, v26.2d
	fadd	v27.2d, v29.2d, v27.2d
	stp	q26, q27, [x12, #32]
	ldp	q24, q25, [x10, #64]
	ldp	q28, q29, [x11, #64]
	ldp	q26, q27, [x10, #96]
	fmul	v24.2d, v24.2d, v28.2d
	fmul	v25.2d, v25.2d, v29.2d
	ldp	q28, q29, [x11, #96]
	fmul	v26.2d, v26.2d, v28.2d
	fmul	v27.2d, v27.2d, v29.2d
	ldp	q28, q29, [x9, #64]
	fadd	v24.2d, v28.2d, v24.2d
	fadd	v25.2d, v29.2d, v25.2d
	stp	q24, q25, [x12, #64]
	ldp	q28, q29, [x9, #96]
	fadd	v26.2d, v28.2d, v26.2d
	fadd	v27.2d, v29.2d, v27.2d
	stp	q26, q27, [x12, #96]
	ldp	q24, q25, [x10, #128]
	ldp	q28, q29, [x11, #128]
	ldp	q26, q27, [x10, #160]
	fmul	v24.2d, v24.2d, v28.2d
	fmul	v25.2d, v25.2d, v29.2d
	ldp	q28, q29, [x11, #160]
	fmul	v26.2d, v26.2d, v28.2d
	fmul	v27.2d, v27.2d, v29.2d
	ldp	q28, q29, [x9, #128]
	fadd	v24.2d, v28.2d, v24.2d
	fadd	v25.2d, v29.2d, v25.2d
	stp	q24, q25, [x12, #128]
	ldp	q28, q29, [x9, #160]
	fadd	v26.2d, v28.2d, v26.2d
	fadd	v27.2d, v29.2d, v27.2d
	stp	q26, q27, [x12, #160]
	ldp	q24, q25, [x10, #192]
	ldp	q26, q27, [x11, #192]
	fmul	v24.2d, v24.2d, v26.2d
	ldp	q26, q28, [x10, #224]
	fmul	v25.2d, v25.2d, v27.2d
	ldp	q27, q0, [x11, #224]
	fmul	v2.2d, v26.2d, v27.2d
	fmul	v0.2d, v28.2d, v0.2d
	ldp	q1, q3, [x9, #192]
	ldp	q4, q5, [x9, #224]
	fadd	v1.2d, v1.2d, v24.2d
	fadd	v3.2d, v3.2d, v25.2d
	stp	q1, q3, [x12, #192]
	fadd	v2.2d, v4.2d, v2.2d
	fadd	v0.2d, v5.2d, v0.2d
	stp	q2, q0, [x12, #224]
	add	x8, x8, #64             // =64
	add	x12, x12, #512          // =512
	add	x11, x11, #512          // =512
	add	x10, x10, #512          // =512
	add	x9, x9, #512            // =512
	adds	x13, x13, #8            // =8
	b.ne	.LBB0_29
    mov x1, #222                // OSACA END
    .byte 213,3,32,31           // OSACA END
// %bb.30:                              //   in Loop: Header=BB0_22 Depth=2
	cbz	x28, .LBB0_33
.LBB0_31:                               //   in Loop: Header=BB0_22 Depth=2
	lsl	x11, x8, #3
	ldp	x9, x8, [sp, #64]       // 8-byte Folded Reload
	ldp	x12, x10, [sp, #48]     // 8-byte Folded Reload
	add	x8, x8, x11
	add	x9, x9, x11
	add	x10, x10, x11
	add	x11, x12, x11
	ldr	x12, [sp, #80]          // 8-byte Folded Reload
	.p2align	6
.LBB0_32:                               //   Parent Loop BB0_20 Depth=1
                                        //     Parent Loop BB0_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q4, q5, [x9, #-32]
	ldp	q6, q7, [x9], #64
	ldp	q16, q17, [x11, #-32]
	ldp	q18, q19, [x11], #64
	fmul	v4.2d, v4.2d, v16.2d
	fmul	v5.2d, v5.2d, v17.2d
	fmul	v6.2d, v6.2d, v18.2d
	fmul	v7.2d, v7.2d, v19.2d
	ldp	q0, q1, [x8, #-32]
	ldp	q2, q3, [x8], #64
	fadd	v0.2d, v0.2d, v4.2d
	fadd	v1.2d, v1.2d, v5.2d
	stp	q0, q1, [x10, #-32]
	fadd	v2.2d, v2.2d, v6.2d
	fadd	v3.2d, v3.2d, v7.2d
	stp	q2, q3, [x10]
	add	x10, x10, #64           // =64
	adds	x12, x12, #1            // =1
	b.ne	.LBB0_32
.LBB0_33:                               //   in Loop: Header=BB0_22 Depth=2
	mov	x12, x26
	cmp	x26, x24
	b.eq	.LBB0_36
.LBB0_34:                               //   in Loop: Header=BB0_22 Depth=2
	ldr	x8, [sp, #88]           // 8-byte Folded Reload
	lsl	x11, x12, #3
	sub	x12, x24, x12
	add	x8, x8, x11
	add	x9, x22, x11
	add	x10, x23, x11
	add	x11, x20, x11
	.p2align	6
.LBB0_35:                               //   Parent Loop BB0_20 Depth=1
                                        //     Parent Loop BB0_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldr	d0, [x8], #8
	ldr	d1, [x9], #8
	ldr	d2, [x10], #8
	fmul	d1, d1, d2
	fadd	d0, d0, d1
	str	d0, [x11], #8
	subs	x12, x12, #1            // =1
	b.ne	.LBB0_35
.LBB0_36:                               //   in Loop: Header=BB0_22 Depth=2
	add	w21, w21, #1            // =1
	cmp	w21, w25
	b.ne	.LBB0_22
.LBB0_37:                               //   in Loop: Header=BB0_20 Depth=1
	add	x0, sp, #104            // =104
	add	x1, sp, #96             // =96
	bl	timing
	ldr	d0, [sp, #104]
	ldur	d1, [x29, #-88]
	fsub	d1, d0, d1
	lsl	w25, w25, #1
	fcmp	d1, d8
	b.mi	.LBB0_20
.LBB0_38:
	scvtf	d4, w19
	lsr	w1, w25, #1
	adrp	x8, .LCPI0_1
	scvtf	d6, w1
	fadd	d2, d4, d4
	ldr	d5, [x8, :lo12:.LCPI0_1]
	adrp	x8, .LCPI0_2
	fmov	d0, #8.00000000
	fmul	d2, d2, d6
	ldr	d3, [x8, :lo12:.LCPI0_2]
	adrp	x8, .LCPI0_3
	adrp	x0, .L.str
	fmul	d2, d2, d3
	ldr	d3, [x8, :lo12:.LCPI0_3]
	adrp	x8, .LCPI0_4
	add	x0, x0, :lo12:.L.str
	fmul	d3, d6, d3
	fmul	d0, d4, d0
	fmul	d3, d3, d4
	fmul	d4, d4, d6
	fdiv	d3, d3, d1
	fdiv	d4, d4, d1
	fdiv	d4, d4, d5
	fdiv	d0, d0, d5
	fdiv	d2, d2, d1
	ldr	d7, [x8, :lo12:.LCPI0_4]
	fmul	d3, d3, d7
	fdiv	d4, d4, d5
	fmul	d3, d3, d7
	mov	w2, w19
	bl	printf
	mov	x0, x20
	bl	free
	ldr	x0, [sp, #88]           // 8-byte Folded Reload
	bl	free
	mov	x0, x22
	bl	free
	mov	x0, x23
	bl	free
	ldp	x29, x30, [sp, #208]    // 16-byte Folded Reload
	ldp	x20, x19, [sp, #192]    // 16-byte Folded Reload
	ldp	x22, x21, [sp, #176]    // 16-byte Folded Reload
	ldp	x24, x23, [sp, #160]    // 16-byte Folded Reload
	ldp	x26, x25, [sp, #144]    // 16-byte Folded Reload
	ldp	x28, x27, [sp, #128]    // 16-byte Folded Reload
	ldr	d8, [sp, #112]          // 8-byte Folded Reload
	add	sp, sp, #224            // =224
	ret
.Lfunc_end0:
	.size	triad, .Lfunc_end0-triad
	.cfi_endproc
                                        // -- End function
	.globl	main                    // -- Begin function main
	.p2align	6
	.type	main,@function
main:                                   // @main
	.cfi_startproc
// %bb.0:
	stp	x29, x30, [sp, #-16]!   // 16-byte Folded Spill
	mov	x29, sp
	.cfi_def_cfa w29, 16
	.cfi_offset w30, -8
	.cfi_offset w29, -16
	adrp	x0, .Lstr
	add	x0, x0, :lo12:.Lstr
	bl	puts
	adrp	x0, .Lstr.3
	add	x0, x0, :lo12:.Lstr.3
	bl	puts
	mov	w0, #190
	bl	triad
	mov	w0, #247
	bl	triad
	mov	w0, #321
	bl	triad
	mov	w0, #417
	bl	triad
	mov	w0, #542
	bl	triad
	mov	w0, #705
	bl	triad
	mov	w0, #917
	bl	triad
	mov	w0, #1192
	bl	triad
	mov	w0, #1550
	bl	triad
	mov	w0, #2015
	bl	triad
	mov	w0, #2619
	bl	triad
	mov	w0, #3405
	bl	triad
	mov	w0, #4427
	bl	triad
	mov	w0, #5756
	bl	triad
	mov	w0, #7482
	bl	triad
	mov	w0, #9727
	bl	triad
	mov	w0, wzr
	ldp	x29, x30, [sp], #16     // 16-byte Folded Reload
	ret
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
	.type	.L.str,@object          // @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"%12.1f | %9.8f | %9.3f | %7.1f | %7.1f | %7d | %4d \n"
	.size	.L.str, 53
	.type	.Lstr,@object           // @str
	.section	.rodata.str1.16,"aMS",@progbits,1
	.p2align	4
.Lstr:
	.asciz	"TRIAD a[i] = b[i]+c[i]*d[i], 32 byte/it, 2 Flop/it"
	.size	.Lstr, 51
	.type	.Lstr.3,@object         // @str.3
	.p2align	4
.Lstr.3:
	.asciz	"Size (KByte) |   runtime  |  MFlop/s  |  MB/s   |  MLUP/s | repeat | size"
	.size	.Lstr.3, 74
	.ident	"Arm C/C++/Fortran Compiler version 19.0 (build number 69) (based on LLVM 7.0.2)"
	.section	".note.GNU-stack","",@progbits
	.addrsig
