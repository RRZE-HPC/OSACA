	.text
	.file	"gs-e4c67a.ll"
	.section	.rodata.cst8,"aM",@progbits,8
	.p2align	3               // -- Begin function MAIN_
.LCPI0_0:
	.xword	4596373779694328218     // double 0.20000000000000001
.LCPI0_1:
	.xword	4696837146684686336     // double 1.0E+6
	.text
	.globl	MAIN_
	.p2align	6
	.type	MAIN_,@function
MAIN_:                                  // @MAIN_
	.cfi_startproc
// %bb.0:                               // %L.entry
	stp	d9, d8, [sp, #-112]!    // 16-byte Folded Spill
	stp	x28, x27, [sp, #16]     // 16-byte Folded Spill
	stp	x26, x25, [sp, #32]     // 16-byte Folded Spill
	stp	x24, x23, [sp, #48]     // 16-byte Folded Spill
	stp	x22, x21, [sp, #64]     // 16-byte Folded Spill
	stp	x20, x19, [sp, #80]     // 16-byte Folded Spill
	stp	x29, x30, [sp, #96]     // 16-byte Folded Spill
	sub	sp, sp, #432            // =432
	.cfi_def_cfa_offset 544
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
	.cfi_offset b8, -104
	.cfi_offset b9, -112
	adrp	x19, .C283_MAIN_
	add	x19, x19, :lo12:.C283_MAIN_
	mov	x0, x19
	bl	fort_init
	adrp	x0, .C329_MAIN_
	adrp	x1, .C327_MAIN_
	add	x0, x0, :lo12:.C329_MAIN_
	add	x1, x1, :lo12:.C327_MAIN_
	orr	w2, wzr, #0x6
	str	xzr, [sp, #424]
	bl	f90io_src_info03a
	adrp	x0, .C330_MAIN_
	mov	x1, xzr
	mov	x2, x19
	mov	x3, x19
	add	x0, x0, :lo12:.C330_MAIN_
	bl	f90io_ldr_init
	adrp	x20, .C334_MAIN_
	adrp	x21, .C285_MAIN_
	add	x20, x20, :lo12:.C334_MAIN_
	add	x21, x21, :lo12:.C285_MAIN_
	mov	x0, x20
	mov	x1, x21
	mov	x2, x19
	add	x3, sp, #420            // =420
	bl	f90io_ldra
	mov	x0, x20
	mov	x1, x21
	mov	x2, x19
	add	x3, sp, #416            // =416
	bl	f90io_ldra
	bl	f90io_ldr_end
	ldrsw	x24, [sp, #416]
	ldr	w22, [sp, #420]
	sxtw	x21, w22
	and	x8, x24, #0xffffffff
	str	x8, [sp, #160]          // 8-byte Folded Spill
	add	x9, x21, #1             // =1
	add	x8, x24, #1             // =1
	adrp	x1, .C366_MAIN_
	mul	x23, x9, x8
	stp	xzr, xzr, [sp]
	adrp	x2, .C365_MAIN_
	adrp	x6, .C286_MAIN_
	adrp	x7, .C284_MAIN_
	mov	x3, xzr
	mov	x5, xzr
	add	x1, x1, :lo12:.C366_MAIN_
	add	x2, x2, :lo12:.C365_MAIN_
	add	x6, x6, :lo12:.C286_MAIN_
	add	x7, x7, :lo12:.C284_MAIN_
	add	x0, sp, #408            // =408
	lsl	x20, x23, #1
	add	x4, sp, #424            // =424
	str	x9, [sp, #360]          // 8-byte Folded Spill
	str	x20, [sp, #408]
	bl	f90_alloc04_chka_i8
	str	x22, [sp, #200]         // 8-byte Folded Spill
	cmp	w24, #2                 // =2
	b.lt	.LBB0_30
// %bb.1:                               // %L.LB1_367.preheader
	cmp	w22, #2                 // =2
	b.lt	.LBB0_30
// %bb.2:                               // %L.LB1_367.preheader64
	mvn	w9, w22
	orr	w10, wzr, #0xfffffffd
	ldr	x8, [sp, #424]
	cmn	w9, #3                  // =3
	csinv	w9, w10, w22, le
	ldr	x18, [sp, #160]         // 8-byte Folded Reload
	add	w11, w22, w9
	add	x12, x23, x21
	mvn	w16, w18
	add	w9, w11, #1             // =1
	add	x10, x9, #1             // =1
	add	x13, x12, x9
	add	x9, x21, x9
	add	x15, x8, x13, lsl #3
	add	x13, x8, x9, lsl #3
	add	x4, x8, x21, lsl #3
	add	x9, x8, x12, lsl #3
	add	x14, x4, #16            // =16
	add	x15, x15, #24           // =24
	add	x12, x13, #24           // =24
	add	x13, x9, #16            // =16
	and	x16, x16, #0x1
	cmp	w18, #2                 // =2
	b.ne	.LBB0_10
// %bb.3:
	orr	w9, wzr, #0x1
	cbz	w16, .LBB0_30
.LBB0_4:                                // %L.LB1_367.epil
	cmp	x10, #8                 // =8
	b.lo	.LBB0_7
// %bb.5:                               // %vector.memcheck.epil
	cmp	x14, x15
	b.hs	.LBB0_27
// %bb.6:                               // %vector.memcheck.epil
	cmp	x13, x12
	b.hs	.LBB0_27
.LBB0_7:
	orr	w10, wzr, #0x1
	mov	w11, w22
.LBB0_8:                                // %L.LB1_370.preheader.epil
	ldr	x14, [sp, #360]         // 8-byte Folded Reload
	add	x13, x9, x24
	add	x12, x8, x10, lsl #3
	lsl	x13, x13, #3
	add	x13, x13, #8            // =8
	madd	x9, x9, x14, x10
	madd	x12, x13, x14, x12
	add	x8, x8, x9, lsl #3
	add	w9, w11, #1             // =1
	.p2align	6
.LBB0_9:                                // %L.LB1_370.epil
                                        // =>This Inner Loop Header: Depth=1
	str	xzr, [x8], #8
	str	xzr, [x12], #8
	sub	w9, w9, #1              // =1
	cmp	w9, #2                  // =2
	b.gt	.LBB0_9
	b	.LBB0_30
.LBB0_10:                               // %L.LB1_367.preheader64.new
	mvn	x17, x16
	cmp	x14, x15
	add	w1, w11, #2             // =2
	add	x5, x23, x21, lsl #1
	add	x17, x17, x18
	cset	w18, lo
	cmp	x13, x12
	cset	w0, lo
	and	w18, w18, w0
	and	w0, w1, #0x7
	sub	x1, x10, x0
	add	x6, x9, #8              // =8
	ldr	x9, [sp, #360]          // 8-byte Folded Reload
	movi	v0.2d, #0000000000000000
	sub	w3, w22, w1
	add	x22, x8, x5, lsl #3
	lsl	x5, x21, #4
	add	x25, x8, x5
	add	x7, x8, x9, lsl #3
	add	x2, x1, #1              // =1
	add	x4, x4, #64             // =64
	add	x5, x5, #16             // =16
	add	x19, x25, #40           // =40
	add	x22, x22, #16           // =16
	add	x25, x25, #16           // =16
	orr	w9, wzr, #0x1
	.p2align	6
.LBB0_11:                               // %L.LB1_367
                                        // =>This Loop Header: Depth=1
                                        //     Child Loop BB0_14 Depth 2
                                        //     Child Loop BB0_17 Depth 2
                                        //     Child Loop BB0_21 Depth 2
                                        //     Child Loop BB0_24 Depth 2
	cmp	x10, #8                 // =8
	cset	w26, lo
	orr	w26, w26, w18
	tbz	w26, #0, .LBB0_13
// %bb.12:                              //   in Loop: Header=BB0_11 Depth=1
	ldr	x28, [sp, #200]         // 8-byte Folded Reload
	orr	w27, wzr, #0x1
	mov	w29, w28
	b	.LBB0_16
	.p2align	6
.LBB0_13:                               // %vector.ph
                                        //   in Loop: Header=BB0_11 Depth=1
	mov	x27, x4
	mov	x28, x1
	.p2align	6
.LBB0_14:                               // %vector.body
                                        //   Parent Loop BB0_11 Depth=1
                                        // =>  This Inner Loop Header: Depth=2
	add	x29, x27, x23, lsl #3
	stp	q0, q0, [x27, #-48]
	stp	q0, q0, [x27, #-16]
	add	x27, x27, #64           // =64
	stp	q0, q0, [x29, #-48]
	stp	q0, q0, [x29, #-16]
	subs	x28, x28, #8            // =8
	b.ne	.LBB0_14
// %bb.15:                              // %middle.block
                                        //   in Loop: Header=BB0_11 Depth=1
	mov	x27, x2
	mov	w29, w3
	cbz	w0, .LBB0_18
.LBB0_16:                               // %L.LB1_370.preheader
                                        //   in Loop: Header=BB0_11 Depth=1
	lsl	x28, x27, #3
	add	x27, x6, x28
	add	x28, x7, x28
	add	w29, w29, #1            // =1
	.p2align	6
.LBB0_17:                               // %L.LB1_370
                                        //   Parent Loop BB0_11 Depth=1
                                        // =>  This Inner Loop Header: Depth=2
	str	xzr, [x28], #8
	str	xzr, [x27], #8
	sub	w29, w29, #1            // =1
	cmp	w29, #2                 // =2
	b.gt	.LBB0_17
.LBB0_18:                               // %L.LB1_371
                                        //   in Loop: Header=BB0_11 Depth=1
	tbz	w26, #0, .LBB0_20
// %bb.19:                              //   in Loop: Header=BB0_11 Depth=1
	ldr	x27, [sp, #200]         // 8-byte Folded Reload
	orr	w26, wzr, #0x1
	mov	w28, w27
	b	.LBB0_23
	.p2align	6
.LBB0_20:                               // %vector.ph.1
                                        //   in Loop: Header=BB0_11 Depth=1
	mov	x26, x19
	mov	x27, x1
	.p2align	6
.LBB0_21:                               // %vector.body.1
                                        //   Parent Loop BB0_11 Depth=1
                                        // =>  This Inner Loop Header: Depth=2
	add	x28, x26, x23, lsl #3
	stp	q0, q0, [x26]
	stur	q0, [x26, #-16]
	str	q0, [x26, #32]
	add	x26, x26, #64           // =64
	stp	q0, q0, [x28, #-16]
	stp	q0, q0, [x28, #16]
	subs	x27, x27, #8            // =8
	b.ne	.LBB0_21
// %bb.22:                              // %middle.block.1
                                        //   in Loop: Header=BB0_11 Depth=1
	mov	x26, x2
	mov	w28, w3
	cbz	w0, .LBB0_25
.LBB0_23:                               // %L.LB1_370.preheader.1
                                        //   in Loop: Header=BB0_11 Depth=1
	lsl	x27, x26, #3
	add	x26, x22, x27
	add	x27, x25, x27
	add	w28, w28, #1            // =1
	.p2align	6
.LBB0_24:                               // %L.LB1_370.1
                                        //   Parent Loop BB0_11 Depth=1
                                        // =>  This Inner Loop Header: Depth=2
	str	xzr, [x27], #8
	str	xzr, [x26], #8
	sub	w28, w28, #1            // =1
	cmp	w28, #2                 // =2
	b.gt	.LBB0_24
.LBB0_25:                               // %L.LB1_371.1
                                        //   in Loop: Header=BB0_11 Depth=1
	add	x4, x4, x5
	add	x6, x6, x5
	add	x7, x7, x5
	add	x19, x19, x5
	add	x22, x22, x5
	add	x9, x9, #2              // =2
	add	x25, x25, x5
	subs	x17, x17, #2            // =2
	b.ne	.LBB0_11
// %bb.26:                              // %L.LB1_368.loopexit.unr-lcssa.loopexit
	ldr	x22, [sp, #200]         // 8-byte Folded Reload
	cbnz	w16, .LBB0_4
	b	.LBB0_30
.LBB0_27:                               // %vector.ph.epil
	ldr	x16, [sp, #360]         // 8-byte Folded Reload
	add	x12, x9, x24
	movi	v0.2d, #0000000000000000
	lsl	x12, x12, #3
	add	x15, x12, #8            // =8
	mul	x14, x9, x16
	add	w11, w11, #2            // =2
	and	w12, w11, #0x7
	madd	x15, x15, x16, x8
	sub	x13, x10, x12
	sub	w11, w22, w13
	add	x10, x13, #1            // =1
	add	x14, x8, x14, lsl #3
	add	x14, x14, #40           // =40
	add	x15, x15, #40           // =40
	.p2align	6
.LBB0_28:                               // %vector.body.epil
                                        // =>This Inner Loop Header: Depth=1
	stp	q0, q0, [x14, #-32]
	stp	q0, q0, [x14], #64
	stp	q0, q0, [x15, #-32]
	stp	q0, q0, [x15], #64
	subs	x13, x13, #8            // =8
	b.ne	.LBB0_28
// %bb.29:                              // %middle.block.epil
	cbnz	w12, .LBB0_8
.LBB0_30:                               // %L.LB1_368
	tbnz	w22, #31, .LBB0_33
// %bb.31:                              // %L.LB1_373.preheader
	orr	w8, wzr, #0xfffffffe
	sub	w12, w8, w22
	ldr	x10, [sp, #424]
	cmn	w12, #2                 // =2
	csel	w8, w12, w8, gt
	add	w13, w22, w8
	mvn	x11, x21
	add	w14, w13, #2            // =2
	add	w9, w22, #1             // =1
	add	x12, x14, #1            // =1
	cmp	x12, #8                 // =8
	b.hs	.LBB0_34
// %bb.32:
	ldr	x6, [sp, #160]          // 8-byte Folded Reload
	mov	x8, xzr
	b	.LBB0_43
.LBB0_33:
	ldr	x6, [sp, #160]          // 8-byte Folded Reload
	fmov	d0, xzr
	tbz	w6, #31, .LBB0_47
	b	.LBB0_49
.LBB0_34:                               // %vector.memcheck159
	add	x16, x23, x14
	add	x14, x20, x14
	add	x17, x10, x16, lsl #3
	sub	x16, x16, x21
	add	x15, x23, x11
	add	x6, x17, #8             // =8
	sub	x14, x14, x21
	add	x18, x10, x16, lsl #3
	add	x16, x20, x11
	add	x15, x10, x15, lsl #3
	add	x2, x10, x14, lsl #3
	add	x4, x10, x12, lsl #3
	add	x0, x10, x16, lsl #3
	cmp	x15, x2
	cset	w7, lo
	cmp	x0, x18
	cset	w19, lo
	cmp	x15, x4
	cset	w14, lo
	add	x5, x10, x23, lsl #3
	cmp	x10, x18
	cset	w16, lo
	cmp	x15, x6
	cset	w15, lo
	cmp	x5, x18
	cset	w18, lo
	cmp	x0, x4
	cset	w17, lo
	cmp	x10, x2
	cset	w1, lo
	cmp	x0, x6
	cset	w0, lo
	cmp	x5, x2
	cset	w3, lo
	cmp	x10, x6
	cset	w2, lo
	ldr	x6, [sp, #160]          // 8-byte Folded Reload
	mov	x8, xzr
	cmp	x5, x4
	cset	w4, lo
	and	w5, w7, w19
	tbnz	w5, #0, .LBB0_43
// %bb.35:                              // %vector.memcheck159
	and	w14, w14, w16
	tbnz	w14, #0, .LBB0_43
// %bb.36:                              // %vector.memcheck159
	and	w14, w15, w18
	tbnz	w14, #0, .LBB0_43
// %bb.37:                              // %vector.memcheck159
	and	w14, w17, w1
	tbnz	w14, #0, .LBB0_43
// %bb.38:                              // %vector.memcheck159
	and	w14, w0, w3
	tbnz	w14, #0, .LBB0_43
// %bb.39:                              // %vector.memcheck159
	and	w14, w2, w4
	tbnz	w14, #0, .LBB0_43
// %bb.40:                              // %vector.ph160
	add	w8, w13, #3             // =3
	and	w13, w8, #0x7
	fmov	v0.2d, #1.00000000
	movi	v1.2d, #0000000000000000
	sub	x8, x12, x13
	lsl	x14, x23, #4
	lsl	x15, x21, #3
	lsl	x12, x23, #3
	sub	x14, x14, x15
	sub	w9, w9, w8
	sub	x12, x12, x15
	mov	x15, x10
	mov	x16, x8
	.p2align	6
.LBB0_41:                               // %vector.body115
                                        // =>This Inner Loop Header: Depth=1
	add	x17, x15, x12
	stur	q0, [x17, #-8]
	stur	q0, [x17, #8]
	stur	q0, [x17, #24]
	stur	q0, [x17, #40]
	add	x17, x15, x14
	stur	q0, [x17, #-8]
	stur	q0, [x17, #8]
	stur	q0, [x17, #24]
	stur	q0, [x17, #40]
	add	x17, x15, x23, lsl #3
	stp	q1, q1, [x15]
	stp	q1, q1, [x15, #32]
	add	x15, x15, #64           // =64
	stp	q1, q1, [x17]
	stp	q1, q1, [x17, #32]
	subs	x16, x16, #8            // =8
	b.ne	.LBB0_41
// %bb.42:                              // %middle.block116
	cbz	w13, .LBB0_46
.LBB0_43:                               // %L.LB1_373.preheader189
	add	x15, x8, x23
	add	x16, x8, x20
	add	x14, x15, x11
	add	x11, x16, x11
	mov	x12, xzr
	add	w9, w9, #1              // =1
	add	x13, x10, x8, lsl #3
	add	x14, x10, x14, lsl #3
	add	x11, x10, x11, lsl #3
	add	x10, x10, x15, lsl #3
	orr	x15, xzr, #0x3ff0000000000000
	.p2align	6
.LBB0_44:                               // %L.LB1_373
                                        // =>This Inner Loop Header: Depth=1
	lsl	x16, x12, #3
	add	x12, x12, #1            // =1
	sub	w9, w9, #1              // =1
	str	x15, [x14, x16]
	str	x15, [x11, x16]
	str	xzr, [x13, x16]
	str	xzr, [x10, x16]
	cmp	w9, #1                  // =1
	b.gt	.LBB0_44
// %bb.45:                              // %L.LB1_374.loopexit.loopexit
	add	w8, w8, w12
.LBB0_46:                               // %L.LB1_374.loopexit
	scvtf	d0, w8
	tbnz	w6, #31, .LBB0_49
.LBB0_47:                               // %L.LB1_382.preheader
	ldr	s1, [sp, #420]
	ldr	x8, [sp, #424]
	lsl	x10, x21, #3
	add	x9, x10, #8             // =8
	sshll	v1.2d, v1.2s, #0
	add	x10, x10, x23, lsl #3
	add	w11, w24, #2            // =2
	scvtf	d1, d1
	fdiv	d0, d0, d1
	.p2align	6
.LBB0_48:                               // %L.LB1_382
                                        // =>This Inner Loop Header: Depth=1
	str	d0, [x8]
	sub	w11, w11, #1            // =1
	str	d0, [x8, x23, lsl #3]
	str	d0, [x8, x21, lsl #3]
	str	d0, [x8, x10]
	add	x8, x8, x9
	cmp	w11, #1                 // =1
	b.gt	.LBB0_48
.LBB0_49:                               // %L.LB1_383
	sub	w9, w6, #1              // =1
	and	w25, w9, #0x7
	mvn	x9, x25
	add	x9, x9, x6
	str	x9, [sp, #168]          // 8-byte Folded Spill
	lsl	x9, x21, #6
	lsl	x28, x21, #1
	mov	w19, #10
	add	x29, x9, #64            // =64
	add	x9, x21, #2             // =2
	str	x9, [sp, #152]          // 8-byte Folded Spill
	add	x9, x28, #4             // =4
	str	x9, [sp, #144]          // 8-byte Folded Spill
	add	x9, x28, x21
	add	x10, x9, #4             // =4
	str	x10, [sp, #136]         // 8-byte Folded Spill
	add	x10, x28, #3            // =3
	str	x10, [sp, #128]         // 8-byte Folded Spill
	add	x10, x9, #5             // =5
	lsl	x9, x9, #1
	str	x10, [sp, #120]         // 8-byte Folded Spill
	lsl	x10, x21, #2
	add	x11, x10, #5            // =5
	str	x11, [sp, #112]         // 8-byte Folded Spill
	add	x11, x10, #6            // =6
	add	x10, x10, x21
	str	x11, [sp, #104]         // 8-byte Folded Spill
	add	x11, x10, #6            // =6
	add	x10, x10, #7            // =7
	lsl	x8, x21, #3
	add	x24, x8, #8             // =8
	fmov	d9, #0.25000000
	sub	x23, x6, #2             // =2
	add	w20, w22, #1            // =1
	stp	x25, x23, [sp, #176]    // 16-byte Folded Spill
	stp	x10, x11, [sp, #88]     // 16-byte Folded Spill
	add	x10, x9, #7             // =7
	add	x9, x9, #8              // =8
	stp	x9, x10, [sp, #72]      // 16-byte Folded Spill
	sub	x9, x8, x21
	add	x10, x9, #8             // =8
	add	x9, x9, #9              // =9
	stp	x9, x10, [sp, #56]      // 16-byte Folded Spill
	add	x9, x8, #9              // =9
	str	x9, [sp, #48]           // 8-byte Folded Spill
	add	x9, x8, #10             // =10
	add	x8, x8, x21
	add	x8, x8, #10             // =10
	stp	x8, x9, [sp, #32]       // 16-byte Folded Spill
	adrp	x8, .LCPI0_0
	ldr	d8, [x8, :lo12:.LCPI0_0]
	.p2align	6
.LBB0_50:                               // %L.LB1_471
                                        // =>This Loop Header: Depth=1
                                        //     Child Loop BB0_55 Depth 2
                                        //       Child Loop BB0_59 Depth 3
                                        //         Child Loop BB0_60 Depth 4
                                        //         Child Loop BB0_62 Depth 4
                                        //         Child Loop BB0_64 Depth 4
                                        //         Child Loop BB0_66 Depth 4
                                        //         Child Loop BB0_68 Depth 4
                                        //         Child Loop BB0_70 Depth 4
                                        //         Child Loop BB0_72 Depth 4
                                        //         Child Loop BB0_74 Depth 4
                                        //       Child Loop BB0_78 Depth 3
                                        //         Child Loop BB0_79 Depth 4
	lsl	w8, w19, #1
	add	x0, sp, #400            // =400
	add	x1, sp, #392            // =392
	str	w8, [sp, #196]          // 4-byte Folded Spill
	bl	timing_
	cbz	w19, .LBB0_53
// %bb.51:                              // %L.LB1_392.preheader
                                        //   in Loop: Header=BB0_50 Depth=1
	ldr	x8, [sp, #160]          // 8-byte Folded Reload
	cmp	w8, #2                  // =2
	b.ge	.LBB0_54
// %bb.52:                              // %L.LB1_392.us.preheader
                                        //   in Loop: Header=BB0_50 Depth=1
	ldr	w9, [sp, #196]          // 4-byte Folded Reload
	mvn	w8, w9
	cmn	w8, #2                  // =2
	orr	w8, wzr, #0xfffffffe
	csinv	w8, w8, w9, le
	add	w8, w8, w9
	add	w26, w8, #3             // =3
	b	.LBB0_82
	.p2align	6
.LBB0_53:                               //   in Loop: Header=BB0_50 Depth=1
	orr	w26, wzr, #0x1
	b	.LBB0_82
	.p2align	6
.LBB0_54:                               // %L.LB1_392.preheader90
                                        //   in Loop: Header=BB0_50 Depth=1
	ldr	x10, [sp, #424]
	ldr	x8, [sp, #360]          // 8-byte Folded Reload
	add	x9, x10, x8, lsl #3
	orr	w26, wzr, #0x1
	ldr	x8, [sp, #152]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #328]          // 8-byte Folded Spill
	ldr	x8, [sp, #144]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #320]          // 8-byte Folded Spill
	ldr	x8, [sp, #136]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #312]          // 8-byte Folded Spill
	ldr	x8, [sp, #128]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #304]          // 8-byte Folded Spill
	ldr	x8, [sp, #120]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #296]          // 8-byte Folded Spill
	ldr	x8, [sp, #112]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #288]          // 8-byte Folded Spill
	ldr	x8, [sp, #104]          // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #280]          // 8-byte Folded Spill
	ldr	x8, [sp, #96]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #272]          // 8-byte Folded Spill
	ldr	x8, [sp, #88]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #264]          // 8-byte Folded Spill
	ldr	x8, [sp, #80]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #256]          // 8-byte Folded Spill
	ldr	x8, [sp, #72]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #248]          // 8-byte Folded Spill
	ldr	x8, [sp, #64]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #240]          // 8-byte Folded Spill
	ldr	x8, [sp, #56]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #232]          // 8-byte Folded Spill
	ldr	x8, [sp, #48]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #224]          // 8-byte Folded Spill
	ldr	x8, [sp, #40]           // 8-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #216]          // 8-byte Folded Spill
	add	x8, x10, #8             // =8
	str	x8, [sp, #352]          // 8-byte Folded Spill
	add	x8, x10, #16            // =16
	stp	x10, x8, [sp, #336]     // 16-byte Folded Spill
	ldr	x8, [sp, #32]           // 8-byte Folded Reload
	ldr	w30, [sp, #196]         // 4-byte Folded Reload
	add	x8, x10, x8, lsl #3
	str	x8, [sp, #208]          // 8-byte Folded Spill
	.p2align	6
.LBB0_55:                               // %L.LB1_392
                                        //   Parent Loop BB0_50 Depth=1
                                        // =>  This Loop Header: Depth=2
                                        //       Child Loop BB0_59 Depth 3
                                        //         Child Loop BB0_60 Depth 4
                                        //         Child Loop BB0_62 Depth 4
                                        //         Child Loop BB0_64 Depth 4
                                        //         Child Loop BB0_66 Depth 4
                                        //         Child Loop BB0_68 Depth 4
                                        //         Child Loop BB0_70 Depth 4
                                        //         Child Loop BB0_72 Depth 4
                                        //         Child Loop BB0_74 Depth 4
                                        //       Child Loop BB0_78 Depth 3
                                        //         Child Loop BB0_79 Depth 4
	cmp	w22, #2                 // =2
	b.lt	.LBB0_81
// %bb.56:                              // %L.LB1_395.preheader
                                        //   in Loop: Header=BB0_55 Depth=2
	cmp	x23, #7                 // =7
	b.hs	.LBB0_58
// %bb.57:                              //   in Loop: Header=BB0_55 Depth=2
	mov	x11, xzr
	orr	w12, wzr, #0x1
	cbnz	w25, .LBB0_77
	b	.LBB0_81
	.p2align	6
.LBB0_58:                               // %L.LB1_395.preheader199
                                        //   in Loop: Header=BB0_55 Depth=2
	ldp	x10, x5, [sp, #208]     // 16-byte Folded Reload
	ldp	x4, x3, [sp, #224]      // 16-byte Folded Reload
	ldp	x2, x1, [sp, #240]      // 16-byte Folded Reload
	ldp	x0, x18, [sp, #256]     // 16-byte Folded Reload
	ldp	x17, x16, [sp, #272]    // 16-byte Folded Reload
	ldp	x15, x14, [sp, #288]    // 16-byte Folded Reload
	ldp	x13, x25, [sp, #304]    // 16-byte Folded Reload
	ldp	x19, x27, [sp, #320]    // 16-byte Folded Reload
	ldr	x8, [sp, #336]          // 8-byte Folded Reload
	ldr	x6, [sp, #168]          // 8-byte Folded Reload
	mov	x11, xzr
	orr	w12, wzr, #0x1
	str	w26, [sp, #372]         // 4-byte Folded Spill
	.p2align	6
.LBB0_59:                               // %L.LB1_395
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        // =>    This Loop Header: Depth=3
                                        //         Child Loop BB0_60 Depth 4
                                        //         Child Loop BB0_62 Depth 4
                                        //         Child Loop BB0_64 Depth 4
                                        //         Child Loop BB0_66 Depth 4
                                        //         Child Loop BB0_68 Depth 4
                                        //         Child Loop BB0_70 Depth 4
                                        //         Child Loop BB0_72 Depth 4
                                        //         Child Loop BB0_74 Depth 4
	mul	x7, x24, x11
	mov	w22, w20
	ldr	d0, [x9, x7]
	mov	x7, x8
	.p2align	6
.LBB0_60:                               // %L.LB1_398
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x23, x7, x28, lsl #3
	add	x26, x7, x21, lsl #3
	ldr	d1, [x23, #24]
	ldr	d2, [x26, #24]
	ldr	d3, [x7, #8]!
	fadd	d0, d1, d0
	fadd	d1, d2, d3
	sub	w22, w22, #1            // =1
	fadd	d0, d0, d1
	fmul	d0, d0, d9
	str	d0, [x26, #16]
	cmp	w22, #2                 // =2
	b.gt	.LBB0_60
// %bb.61:                              // %L.LB1_399
                                        //   in Loop: Header=BB0_59 Depth=3
	orr	x7, x11, #0x1
	mov	x22, x19
	mul	x7, x24, x7
	mov	x23, x27
	mov	w26, w20
	ldr	d0, [x9, x7]
	mov	x7, x25
	.p2align	6
    // OSACA-BEGIN
.LBB0_62:                               // %L.LB1_398.1
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	ldr	d1, [x7], #8
	fadd	d0, d1, d0
	ldr	d2, [x22]
	ldr	d3, [x23], #8
	fadd	d2, d2, d3
	fadd	d0, d0, d2
	sub	w26, w26, #1            // =1
	fmul	d0, d0, d9
	stur	d0, [x22, #-8]
	add	x22, x22, #8            // =8
	cmp	w26, #2                 // =2
	b.gt	.LBB0_62
    // OSACA-END
// %bb.63:                              // %L.LB1_399.1
                                        //   in Loop: Header=BB0_59 Depth=3
	orr	x7, x11, #0x2
	mov	x22, x14
	mul	x7, x24, x7
	mov	x23, x13
	mov	w26, w20
	ldr	d0, [x9, x7]
	mov	x7, x15
	.p2align	6
.LBB0_64:                               // %L.LB1_398.2
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	ldr	d1, [x7], #8
	fadd	d0, d1, d0
	ldr	d2, [x22]
	ldr	d3, [x23], #8
	fadd	d2, d2, d3
	fadd	d0, d0, d2
	sub	w26, w26, #1            // =1
	fmul	d0, d0, d9
	stur	d0, [x22, #-8]
	add	x22, x22, #8            // =8
	cmp	w26, #2                 // =2
	b.gt	.LBB0_64
// %bb.65:                              // %L.LB1_399.2
                                        //   in Loop: Header=BB0_59 Depth=3
	orr	x22, x11, #0x3
	mov	x7, xzr
	mul	x22, x24, x22
	ldr	d0, [x9, x22]
	mov	w22, w20
	.p2align	6
.LBB0_66:                               // %L.LB1_398.3
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x23, x16, x7
	sub	w22, w22, #1            // =1
	ldr	d1, [x17, x7]
	ldr	d2, [x25, x7]
	ldr	d3, [x23]
	fadd	d2, d3, d2
	fadd	d0, d1, d0
	add	x7, x7, #8              // =8
	fadd	d0, d0, d2
	fmul	d0, d0, d9
	stur	d0, [x23, #-8]
	cmp	w22, #2                 // =2
	b.gt	.LBB0_66
// %bb.67:                              // %L.LB1_399.3
                                        //   in Loop: Header=BB0_59 Depth=3
	orr	x22, x11, #0x4
	mov	x7, xzr
	mul	x22, x24, x22
	ldr	d0, [x9, x22]
	mov	w22, w20
	.p2align	6
.LBB0_68:                               // %L.LB1_398.4
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x23, x18, x7
	sub	w22, w22, #1            // =1
	ldr	d1, [x0, x7]
	ldr	d2, [x15, x7]
	ldr	d3, [x23]
	fadd	d2, d3, d2
	fadd	d0, d1, d0
	add	x7, x7, #8              // =8
	fadd	d0, d0, d2
	fmul	d0, d0, d9
	stur	d0, [x23, #-8]
	cmp	w22, #2                 // =2
	b.gt	.LBB0_68
// %bb.69:                              // %L.LB1_399.4
                                        //   in Loop: Header=BB0_59 Depth=3
	mov	w22, #5
	orr	x22, x11, x22
	mul	x22, x24, x22
	mov	x7, xzr
	ldr	d0, [x9, x22]
	mov	w22, w20
	.p2align	6
.LBB0_70:                               // %L.LB1_398.5
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x23, x1, x7
	sub	w22, w22, #1            // =1
	ldr	d1, [x2, x7]
	ldr	d2, [x17, x7]
	ldr	d3, [x23]
	fadd	d2, d3, d2
	fadd	d0, d1, d0
	add	x7, x7, #8              // =8
	fadd	d0, d0, d2
	fmul	d0, d0, d9
	stur	d0, [x23, #-8]
	cmp	w22, #2                 // =2
	b.gt	.LBB0_70
// %bb.71:                              // %L.LB1_399.5
                                        //   in Loop: Header=BB0_59 Depth=3
	orr	x22, x11, #0x6
	mov	x7, xzr
	mul	x22, x24, x22
	ldr	d0, [x9, x22]
	mov	w22, w20
	.p2align	6
.LBB0_72:                               // %L.LB1_398.6
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x23, x3, x7
	sub	w22, w22, #1            // =1
	ldr	d1, [x4, x7]
	ldr	d2, [x0, x7]
	ldr	d3, [x23]
	fadd	d2, d3, d2
	fadd	d0, d1, d0
	add	x7, x7, #8              // =8
	fadd	d0, d0, d2
	fmul	d0, d0, d9
	stur	d0, [x23, #-8]
	cmp	w22, #2                 // =2
	b.gt	.LBB0_72
// %bb.73:                              // %L.LB1_399.6
                                        //   in Loop: Header=BB0_59 Depth=3
	orr	x22, x11, #0x7
	mov	x7, xzr
	mul	x22, x24, x22
	add	x12, x12, #8            // =8
	ldr	d0, [x9, x22]
	mov	w22, w20
	.p2align	6
.LBB0_74:                               // %L.LB1_398.7
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_59 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x23, x5, x7
	sub	w22, w22, #1            // =1
	ldr	d1, [x10, x7]
	ldr	d2, [x2, x7]
	ldr	d3, [x23]
	fadd	d2, d3, d2
	fadd	d0, d1, d0
	add	x7, x7, #8              // =8
	fadd	d0, d0, d2
	fmul	d0, d0, d9
	stur	d0, [x23, #-8]
	cmp	w22, #2                 // =2
	b.gt	.LBB0_74
// %bb.75:                              // %L.LB1_399.7
                                        //   in Loop: Header=BB0_59 Depth=3
	add	x8, x8, x29
	add	x27, x27, x29
	add	x19, x19, x29
	add	x25, x25, x29
	add	x13, x13, x29
	add	x11, x11, #8            // =8
	add	x14, x14, x29
	add	x15, x15, x29
	add	x16, x16, x29
	add	x17, x17, x29
	add	x18, x18, x29
	add	x0, x0, x29
	add	x1, x1, x29
	add	x2, x2, x29
	add	x3, x3, x29
	add	x4, x4, x29
	add	x5, x5, x29
	add	x10, x10, x29
	subs	x6, x6, #8              // =8
	b.ne	.LBB0_59
// %bb.76:                              // %L.LB1_396.loopexit.unr-lcssa.loopexit
                                        //   in Loop: Header=BB0_55 Depth=2
	ldp	x25, x23, [sp, #176]    // 16-byte Folded Reload
	ldr	x22, [sp, #200]         // 8-byte Folded Reload
	ldr	w26, [sp, #372]         // 4-byte Folded Reload
	cbz	w25, .LBB0_81
.LBB0_77:                               // %L.LB1_395.epil.preheader
                                        //   in Loop: Header=BB0_55 Depth=2
	ldr	x13, [sp, #360]         // 8-byte Folded Reload
	mul	x8, x13, x12
	ldr	x14, [sp, #344]         // 8-byte Folded Reload
	sub	x10, x12, #1            // =1
	add	x12, x12, #1            // =1
	mul	x10, x13, x10
	mul	x12, x13, x12
	add	x8, x14, x8, lsl #3
	mov	x13, x25
	ldr	x14, [sp, #352]         // 8-byte Folded Reload
	add	x10, x14, x10, lsl #3
	add	x12, x14, x12, lsl #3
	.p2align	6
.LBB0_78:                               // %L.LB1_395.epil
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        // =>    This Loop Header: Depth=3
                                        //         Child Loop BB0_79 Depth 4
	mul	x14, x24, x11
	mov	x15, x8
	mov	x16, x10
	ldr	d0, [x9, x14]
	mov	x14, x12
	mov	w17, w20
	.p2align	6
.LBB0_79:                               // %L.LB1_398.epil
                                        //   Parent Loop BB0_50 Depth=1
                                        //     Parent Loop BB0_55 Depth=2
                                        //       Parent Loop BB0_78 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	ldr	d1, [x14], #8
	fadd	d0, d1, d0
	ldr	d2, [x15]
	ldr	d3, [x16], #8
	fadd	d2, d2, d3
	fadd	d0, d0, d2
	sub	w17, w17, #1            // =1
	fmul	d0, d0, d9
	stur	d0, [x15, #-8]
	add	x15, x15, #8            // =8
	cmp	w17, #2                 // =2
	b.gt	.LBB0_79
// %bb.80:                              // %L.LB1_399.epil
                                        //   in Loop: Header=BB0_78 Depth=3
	add	x10, x10, x24
	add	x8, x8, x24
	add	x12, x12, x24
	add	x11, x11, #1            // =1
	subs	x13, x13, #1            // =1
	b.ne	.LBB0_78
.LBB0_81:                               // %L.LB1_396
                                        //   in Loop: Header=BB0_55 Depth=2
	add	w26, w26, #1            // =1
	subs	w30, w30, #1            // =1
	b.gt	.LBB0_55
.LBB0_82:                               // %L.LB1_393
                                        //   in Loop: Header=BB0_50 Depth=1
	add	x0, sp, #384            // =384
	add	x1, sp, #376            // =376
	bl	timing_
	ldr	d0, [sp, #384]
	ldr	d1, [sp, #400]
	fsub	d0, d0, d1
	ldr	w19, [sp, #196]         // 4-byte Folded Reload
	mov	w8, #51712
	movk	w8, #15258, lsl #16
	fcmp	d0, d8
	ccmp	w19, w8, #2, lt
	b.lo	.LBB0_50
// %bb.83:                              // %L.LB1_391
	adrp	x0, .C345_MAIN_
	adrp	x1, .C327_MAIN_
	cmp	w26, w19
	add	x0, x0, :lo12:.C345_MAIN_
	add	x1, x1, :lo12:.C327_MAIN_
	orr	w2, wzr, #0x6
	csel	w19, w19, w26, gt
	bl	f90io_src_info03a
	adrp	x20, .C283_MAIN_
	add	x20, x20, :lo12:.C283_MAIN_
	adrp	x0, .C326_MAIN_
	mov	x1, xzr
	mov	x2, x20
	mov	x3, x20
	add	x0, x0, :lo12:.C326_MAIN_
	bl	f90io_print_init
	adrp	x0, .C348_MAIN_
	add	x0, x0, :lo12:.C348_MAIN_
	orr	w1, wzr, #0xe
	orr	w2, wzr, #0xe
	bl	f90io_sc_ch_ldw
	mov	w0, w19
	mov	w1, #25
	bl	f90io_sc_i_ldw
	adrp	x0, .C349_MAIN_
	add	x0, x0, :lo12:.C349_MAIN_
	orr	w1, wzr, #0xe
	orr	w2, wzr, #0xe
	bl	f90io_sc_ch_ldw
	ldr	w8, [sp, #416]
	sub	w8, w8, #1              // =1
	orr	w0, wzr, #0x1c
	scvtf	d0, w19
	scvtf	d1, w8
	ldr	w8, [sp, #420]
	sub	w8, w8, #1              // =1
	scvtf	d2, w8
	fmul	d0, d1, d0
	ldr	d1, [sp, #384]
	adrp	x8, .LCPI0_1
	fmul	d0, d0, d2
	ldr	d2, [sp, #400]
	fsub	d1, d1, d2
	ldr	d2, [x8, :lo12:.LCPI0_1]
	fmul	d1, d1, d2
	fdiv	d0, d0, d1
	bl	f90io_sc_d_ldw
	adrp	x0, .C351_MAIN_
	add	x0, x0, :lo12:.C351_MAIN_
	orr	w1, wzr, #0xe
	orr	w2, wzr, #0x6
	bl	f90io_sc_ch_ldw
	bl	f90io_ldw_end
	mov	x0, x20
	mov	x1, xzr
	mov	x2, xzr
	bl	f90_stop08a
	add	sp, sp, #432            // =432
	ldp	x29, x30, [sp, #96]     // 16-byte Folded Reload
	ldp	x20, x19, [sp, #80]     // 16-byte Folded Reload
	ldp	x22, x21, [sp, #64]     // 16-byte Folded Reload
	ldp	x24, x23, [sp, #48]     // 16-byte Folded Reload
	ldp	x26, x25, [sp, #32]     // 16-byte Folded Reload
	ldp	x28, x27, [sp, #16]     // 16-byte Folded Reload
	ldp	d9, d8, [sp], #112      // 16-byte Folded Reload
	ret
.Lfunc_end0:
	.size	MAIN_, .Lfunc_end0-MAIN_
	.cfi_endproc
                                        // -- End function
	.type	.C351_MAIN_,@object     // @.C351_MAIN_
	.section	.rodata,"a",@progbits
	.p2align	2
.C351_MAIN_:
	.asciz	" MLUPs"
	.size	.C351_MAIN_, 7

	.type	.C349_MAIN_,@object     // @.C349_MAIN_
	.p2align	2
.C349_MAIN_:
	.asciz	" Performance: "
	.size	.C349_MAIN_, 15

	.type	.C348_MAIN_,@object     // @.C348_MAIN_
	.p2align	2
.C348_MAIN_:
	.asciz	"# Iterations: "
	.size	.C348_MAIN_, 15

	.type	.C326_MAIN_,@object     // @.C326_MAIN_
	.p2align	2
.C326_MAIN_:
	.word	6                       // 0x6
	.size	.C326_MAIN_, 4

	.type	.C345_MAIN_,@object     // @.C345_MAIN_
	.p2align	2
.C345_MAIN_:
	.word	72                      // 0x48
	.size	.C345_MAIN_, 4

	.type	.C366_MAIN_,@object     // @.C366_MAIN_
	.p2align	3
.C366_MAIN_:
	.xword	28                      // 0x1c
	.size	.C366_MAIN_, 8

	.type	.C365_MAIN_,@object     // @.C365_MAIN_
	.p2align	3
.C365_MAIN_:
	.xword	8                       // 0x8
	.size	.C365_MAIN_, 8

	.type	.C286_MAIN_,@object     // @.C286_MAIN_
	.p2align	3
.C286_MAIN_:
	.xword	1                       // 0x1
	.size	.C286_MAIN_, 8

	.type	.C285_MAIN_,@object     // @.C285_MAIN_
	.p2align	2
.C285_MAIN_:
	.word	1                       // 0x1
	.size	.C285_MAIN_, 4

	.type	.C334_MAIN_,@object     // @.C334_MAIN_
	.p2align	2
.C334_MAIN_:
	.word	25                      // 0x19
	.size	.C334_MAIN_, 4

	.type	.C330_MAIN_,@object     // @.C330_MAIN_
	.p2align	2
.C330_MAIN_:
	.word	5                       // 0x5
	.size	.C330_MAIN_, 4

	.type	.C327_MAIN_,@object     // @.C327_MAIN_
	.p2align	2
.C327_MAIN_:
	.asciz	"gs.f90"
	.size	.C327_MAIN_, 7

	.type	.C329_MAIN_,@object     // @.C329_MAIN_
	.p2align	2
.C329_MAIN_:
	.word	12                      // 0xc
	.size	.C329_MAIN_, 4

	.type	.C284_MAIN_,@object     // @.C284_MAIN_
	.p2align	3
.C284_MAIN_:
	.xword	0                       // 0x0
	.size	.C284_MAIN_, 8

	.type	.C283_MAIN_,@object     // @.C283_MAIN_
	.p2align	2
.C283_MAIN_:
	.word	0                       // 0x0
	.size	.C283_MAIN_, 4


	.section	".note.GNU-stack","",@progbits
	.addrsig
	.addrsig_sym .C351_MAIN_
	.addrsig_sym .C349_MAIN_
	.addrsig_sym .C348_MAIN_
	.addrsig_sym .C326_MAIN_
	.addrsig_sym .C345_MAIN_
	.addrsig_sym .C366_MAIN_
	.addrsig_sym .C365_MAIN_
	.addrsig_sym .C286_MAIN_
	.addrsig_sym .C285_MAIN_
	.addrsig_sym .C334_MAIN_
	.addrsig_sym .C330_MAIN_
	.addrsig_sym .C327_MAIN_
	.addrsig_sym .C329_MAIN_
	.addrsig_sym .C284_MAIN_
	.addrsig_sym .C283_MAIN_
