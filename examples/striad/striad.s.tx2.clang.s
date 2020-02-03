    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q0, q1, [x9, #-256]
	ldp	q2, q3, [x9, #-224]
	ldp	q4, q5, [x10, #-256]
	ldp	q6, q7, [x10, #-224]
	ldp	q16, q17, [x11, #-256]
	ldp	q18, q19, [x11, #-224]
	fmla	v0.2d, v16.2d, v4.2d
	fmla	v1.2d, v17.2d, v5.2d
	stp	q1, q0, [sp, #96]       // 32-byte Folded Spill
	fmla	v2.2d, v18.2d, v6.2d
	fmla	v3.2d, v19.2d, v7.2d
	ldp	q4, q5, [x9, #-192]
	ldp	q6, q7, [x9, #-160]
	ldp	q16, q17, [x10, #-192]
	ldp	q18, q19, [x10, #-160]
	ldp	q20, q21, [x11, #-192]
	ldp	q22, q23, [x11, #-160]
	fmla	v4.2d, v20.2d, v16.2d
	stp	q3, q4, [x12, #-208]
	fmla	v5.2d, v21.2d, v17.2d
	fmla	v6.2d, v22.2d, v18.2d
	stp	q5, q6, [x12, #-176]
	fmla	v7.2d, v23.2d, v19.2d
	ldp	q16, q18, [x9, #-128]
	ldp	q17, q19, [x9, #-96]
	ldp	q20, q21, [x10, #-128]
	ldp	q22, q23, [x10, #-96]
	ldp	q24, q25, [x11, #-128]
	ldp	q26, q27, [x11, #-96]
	fmla	v16.2d, v24.2d, v20.2d
	stp	q7, q16, [x12, #-144]
	fmla	v18.2d, v25.2d, v21.2d
	fmla	v17.2d, v26.2d, v22.2d
	stp	q18, q17, [x12, #-112]
	fmla	v19.2d, v27.2d, v23.2d
	ldp	q22, q23, [x9, #-64]
	ldp	q20, q21, [x9, #-32]
	ldp	q24, q25, [x10, #-64]
	ldp	q26, q27, [x10, #-32]
	ldp	q28, q29, [x11, #-64]
	ldp	q30, q31, [x11, #-32]
	fmla	v22.2d, v28.2d, v24.2d
	stp	q19, q22, [x12, #-80]
	fmla	v23.2d, v29.2d, v25.2d
	fmla	v20.2d, v30.2d, v26.2d
	stp	q23, q20, [x12, #-48]
	fmla	v21.2d, v31.2d, v27.2d
	stur	q21, [x12, #-16]
	ldp	q24, q25, [x9]
	ldp	q26, q27, [x9, #32]
	ldp	q28, q29, [x10]
	ldp	q30, q31, [x10, #32]
	ldp	q8, q10, [x11]
	ldp	q11, q12, [x11, #32]
	fmla	v24.2d, v8.2d, v28.2d
	fmla	v25.2d, v10.2d, v29.2d
	stp	q24, q25, [x12]
	fmla	v26.2d, v11.2d, v30.2d
	fmla	v27.2d, v12.2d, v31.2d
	stp	q26, q27, [x12, #32]
	ldp	q28, q29, [x9, #64]
	ldp	q30, q31, [x9, #96]
	ldp	q8, q10, [x10, #64]
	ldp	q11, q12, [x10, #96]
	ldp	q13, q14, [x11, #64]
	ldp	q15, q9, [x11, #96]
	fmla	v28.2d, v13.2d, v8.2d
	fmla	v29.2d, v14.2d, v10.2d
	stp	q28, q29, [x12, #64]
	fmla	v30.2d, v15.2d, v11.2d
	fmla	v31.2d, v9.2d, v12.2d
	stp	q30, q31, [x12, #96]
	ldp	q8, q9, [x9, #128]
	ldp	q12, q13, [x10, #128]
	ldp	q14, q15, [x11, #128]
	ldp	q10, q11, [x9, #160]
	fmla	v8.2d, v14.2d, v12.2d
	ldp	q12, q14, [x10, #160]
	fmla	v9.2d, v15.2d, v13.2d
	stp	q8, q9, [x12, #128]
	ldp	q13, q15, [x11, #160]
	fmla	v10.2d, v13.2d, v12.2d
	fmla	v11.2d, v15.2d, v14.2d
	stp	q10, q11, [x12, #160]
	ldp	q12, q13, [x9, #192]
	ldp	q14, q15, [x10, #192]
	ldp	q0, q1, [x11, #192]
	fmla	v12.2d, v0.2d, v14.2d
	ldr	q0, [sp, #112]          // 16-byte Folded Reload
	stur	q0, [x12, #-256]
	ldr	q0, [sp, #96]           // 16-byte Folded Reload
	stp	q0, q2, [x12, #-240]
	ldp	q0, q2, [x9, #224]
	ldp	q3, q4, [x10, #224]
	ldp	q5, q6, [x11, #224]
	fmla	v13.2d, v1.2d, v15.2d
	stp	q12, q13, [x12, #192]
	fmla	v0.2d, v5.2d, v3.2d
	fmla	v2.2d, v6.2d, v4.2d
	stp	q0, q2, [x12, #224]
	add	x8, x8, #64             // =64
	add	x12, x12, #512          // =512
	add	x11, x11, #512          // =512
	add	x10, x10, #512          // =512
	add	x9, x9, #512            // =512
	adds	x13, x13, #8            // =8
	b.ne	.LBB1_29
    // OSACA-END
