    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q0, q1, [x9, #-256]
	ldp	q4, q5, [x9, #-224]
	ldp	q2, q3, [x10, #-256]
	ldp	q6, q7, [x10, #-224]
	fadd	v2.2d, v2.2d, v0.2d
	fadd	v3.2d, v3.2d, v1.2d
	stp	q2, q3, [x11, #-256]
	fadd	v0.2d, v6.2d, v4.2d
	fadd	v1.2d, v7.2d, v5.2d
	stp	q0, q1, [x11, #-224]
	ldp	q4, q5, [x9, #-192]
	ldp	q16, q17, [x9, #-160]
	ldp	q6, q7, [x10, #-192]
	ldp	q18, q19, [x10, #-160]
	fadd	v6.2d, v6.2d, v4.2d
	fadd	v7.2d, v7.2d, v5.2d
	stp	q6, q7, [x11, #-192]
	fadd	v4.2d, v18.2d, v16.2d
	fadd	v5.2d, v19.2d, v17.2d
	stp	q4, q5, [x11, #-160]
	ldp	q16, q17, [x9, #-128]
	ldp	q19, q20, [x9, #-96]
	ldp	q18, q21, [x10, #-128]
	ldp	q22, q23, [x10, #-96]
	fadd	v16.2d, v18.2d, v16.2d
	fadd	v18.2d, v21.2d, v17.2d
	stp	q16, q18, [x11, #-128]
	fadd	v17.2d, v22.2d, v19.2d
	fadd	v19.2d, v23.2d, v20.2d
	stp	q17, q19, [x11, #-96]
	ldp	q20, q21, [x9, #-64]
	ldp	q24, q25, [x10, #-64]
	ldp	q22, q23, [x9, #-32]
	ldp	q26, q27, [x10, #-32]
	fadd	v20.2d, v24.2d, v20.2d
	fadd	v21.2d, v25.2d, v21.2d
	stp	q20, q21, [x11, #-64]
	ldp	q24, q25, [x9]
	ldp	q28, q29, [x10]
	fadd	v22.2d, v26.2d, v22.2d
	fadd	v23.2d, v27.2d, v23.2d
	stp	q22, q23, [x11, #-32]
	ldp	q26, q27, [x9, #32]
	ldp	q30, q31, [x10, #32]
	fadd	v24.2d, v28.2d, v24.2d
	fadd	v25.2d, v29.2d, v25.2d
	stp	q24, q25, [x11]
	ldp	q28, q29, [x9, #64]
	ldp	q8, q10, [x10, #64]
	fadd	v26.2d, v30.2d, v26.2d
	fadd	v27.2d, v31.2d, v27.2d
	stp	q26, q27, [x11, #32]
	ldp	q30, q31, [x9, #96]
	ldp	q11, q12, [x10, #96]
	fadd	v28.2d, v8.2d, v28.2d
	fadd	v29.2d, v10.2d, v29.2d
	stp	q28, q29, [x11, #64]
	ldp	q8, q10, [x9, #128]
	ldp	q13, q14, [x10, #128]
	ldp	q3, q0, [x9, #192]
	ldp	q1, q6, [x10, #192]
	fadd	v30.2d, v11.2d, v30.2d
	fadd	v31.2d, v12.2d, v31.2d
	stp	q30, q31, [x11, #96]
	ldp	q11, q12, [x9, #160]
	fadd	v8.2d, v13.2d, v8.2d
	fadd	v10.2d, v14.2d, v10.2d
	stp	q8, q10, [x11, #128]
	ldp	q13, q14, [x10, #160]
	fadd	v1.2d, v1.2d, v3.2d
	ldp	q3, q4, [x9, #224]
	fadd	v0.2d, v6.2d, v0.2d
	stp	q1, q0, [x11, #192]
	ldp	q5, q6, [x10, #224]
	fadd	v11.2d, v13.2d, v11.2d
	fadd	v2.2d, v14.2d, v12.2d
	stp	q11, q2, [x11, #160]
	fadd	v3.2d, v5.2d, v3.2d
	fadd	v4.2d, v6.2d, v4.2d
	stp	q3, q4, [x11, #224]
	add	x8, x8, #64             // =64
	add	x11, x11, #512          // =512
	add	x10, x10, #512          // =512
	add	x9, x9, #512            // =512
	adds	x12, x12, #8            // =8
	b.ne	.LBB1_29
    // OSACA-END
