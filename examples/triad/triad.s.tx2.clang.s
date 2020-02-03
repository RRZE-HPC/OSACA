    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q2, q3, [x9, #-256]
	ldp	q0, q1, [x9, #-224]
	ldp	q4, q5, [x10, #-256]
	ldp	q6, q7, [x10, #-224]
	fmla	v2.2d, v4.2d, v16.2d
	fmla	v3.2d, v5.2d, v16.2d
	stp	q2, q3, [x11, #-256]
	fmla	v0.2d, v6.2d, v16.2d
	fmla	v1.2d, v7.2d, v16.2d
	stp	q0, q1, [x11, #-224]
	ldp	q6, q7, [x9, #-192]
	ldp	q16, q17, [x10, #-192]
	ldr	q20, [sp, #80]          // 16-byte Folded Reload
	fmla	v6.2d, v16.2d, v20.2d
	ldr	q16, [sp, #80]          // 16-byte Folded Reload
	ldp	q4, q5, [x9, #-160]
	ldp	q18, q19, [x10, #-160]
	fmla	v7.2d, v17.2d, v16.2d
	stp	q6, q7, [x11, #-192]
	ldr	q16, [sp, #80]          // 16-byte Folded Reload
	fmla	v4.2d, v18.2d, v16.2d
	ldr	q16, [sp, #80]          // 16-byte Folded Reload
	fmla	v5.2d, v19.2d, v16.2d
	stp	q4, q5, [x11, #-160]
	ldp	q17, q19, [x9, #-128]
	ldp	q20, q21, [x10, #-128]
	ldr	q24, [sp, #80]          // 16-byte Folded Reload
	fmla	v17.2d, v20.2d, v24.2d
	ldr	q20, [sp, #80]          // 16-byte Folded Reload
	ldp	q16, q18, [x9, #-96]
	ldp	q22, q23, [x10, #-96]
	fmla	v19.2d, v21.2d, v20.2d
	stp	q17, q19, [x11, #-128]
	ldr	q20, [sp, #80]          // 16-byte Folded Reload
	fmla	v16.2d, v22.2d, v20.2d
	ldr	q20, [sp, #80]          // 16-byte Folded Reload
	ldp	q24, q25, [x10, #-64]
	fmla	v18.2d, v23.2d, v20.2d
	stp	q16, q18, [x11, #-96]
	ldp	q20, q22, [x9, #-64]
	ldr	q28, [sp, #80]          // 16-byte Folded Reload
	fmla	v20.2d, v24.2d, v28.2d
	ldr	q24, [sp, #80]          // 16-byte Folded Reload
	ldp	q21, q23, [x9, #-32]
	ldp	q26, q27, [x10, #-32]
	fmla	v22.2d, v25.2d, v24.2d
	stp	q20, q22, [x11, #-64]
	ldr	q24, [sp, #80]          // 16-byte Folded Reload
	fmla	v21.2d, v26.2d, v24.2d
	ldr	q24, [sp, #80]          // 16-byte Folded Reload
	ldp	q28, q29, [x10]
	ldr	q8, [sp, #80]           // 16-byte Folded Reload
	ldp	q30, q31, [x10, #32]
	ldr	q9, [sp, #80]           // 16-byte Folded Reload
	fmla	v23.2d, v27.2d, v24.2d
	stp	q21, q23, [x11, #-32]
	ldp	q24, q25, [x9]
	fmla	v24.2d, v28.2d, v8.2d
	ldr	q28, [sp, #80]          // 16-byte Folded Reload
	ldp	q26, q27, [x9, #32]
	ldp	q8, q10, [x10, #64]
	ldp	q11, q12, [x10, #96]
	fmla	v25.2d, v29.2d, v28.2d
	stp	q24, q25, [x11]
	ldr	q28, [sp, #80]          // 16-byte Folded Reload
	fmla	v26.2d, v30.2d, v28.2d
	ldr	q28, [sp, #80]          // 16-byte Folded Reload
	ldp	q13, q14, [x10, #128]
	ldr	q2, [sp, #80]           // 16-byte Folded Reload
	ldp	q1, q3, [x10, #192]
	fmla	v27.2d, v31.2d, v28.2d
	stp	q26, q27, [x11, #32]
	ldp	q28, q29, [x9, #64]
	fmla	v28.2d, v8.2d, v9.2d
	ldr	q8, [sp, #80]           // 16-byte Folded Reload
	ldp	q30, q31, [x9, #96]
	ldr	q9, [sp, #80]           // 16-byte Folded Reload
	ldr	q6, [sp, #80]           // 16-byte Folded Reload
	ldr	q5, [sp, #80]           // 16-byte Folded Reload
	fmla	v29.2d, v10.2d, v8.2d
	stp	q28, q29, [x11, #64]
	ldr	q8, [sp, #80]           // 16-byte Folded Reload
	fmla	v30.2d, v11.2d, v8.2d
	ldr	q8, [sp, #80]           // 16-byte Folded Reload
	ldr	q16, [sp, #80]          // 16-byte Folded Reload
	add	x8, x8, #64             // =64
	fmla	v31.2d, v12.2d, v8.2d
	stp	q30, q31, [x11, #96]
	ldp	q8, q10, [x9, #128]
	fmla	v8.2d, v13.2d, v9.2d
	ldr	q9, [sp, #80]           // 16-byte Folded Reload
	ldp	q11, q12, [x9, #160]
	fmla	v10.2d, v14.2d, v9.2d
	stp	q8, q10, [x11, #128]
	ldp	q13, q14, [x10, #160]
	fmla	v12.2d, v14.2d, v2.2d
	ldp	q2, q0, [x9, #192]
	ldr	q9, [sp, #80]           // 16-byte Folded Reload
	fmla	v2.2d, v1.2d, v6.2d
	ldp	q1, q4, [x9, #224]
	fmla	v0.2d, v3.2d, v5.2d
	stp	q2, q0, [x11, #192]
	ldp	q3, q5, [x10, #224]
	fmla	v11.2d, v13.2d, v9.2d
	stp	q11, q12, [x11, #160]
	fmla	v1.2d, v3.2d, v16.2d
	fmla	v4.2d, v5.2d, v16.2d
	stp	q1, q4, [x11, #224]
	add	x11, x11, #512          // =512
	add	x10, x10, #512          // =512
	add	x9, x9, #512            // =512
	adds	x12, x12, #8            // =8
	b.ne	.LBB1_29
    // OSACA-END
