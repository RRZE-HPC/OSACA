    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q1, q2, [x9, #-256]
	ldp	q3, q0, [x9, #-224]
	ldp	q4, q5, [x10, #-256]
	ldp	q6, q7, [x10, #-224]
	fmla	v1.2d, v4.2d, v31.2d
	fmla	v2.2d, v5.2d, v31.2d
	stp	q1, q2, [x9, #-256]
	fmla	v3.2d, v6.2d, v31.2d
	fmla	v0.2d, v7.2d, v31.2d
	stp	q3, q0, [x9, #-224]
	ldp	q5, q6, [x9, #-192]
	ldp	q7, q4, [x9, #-160]
	ldp	q16, q17, [x10, #-192]
	ldp	q18, q19, [x10, #-160]
	fmla	v5.2d, v16.2d, v31.2d
	fmla	v6.2d, v17.2d, v31.2d
	stp	q5, q6, [x9, #-192]
	fmla	v7.2d, v18.2d, v31.2d
	fmla	v4.2d, v19.2d, v31.2d
	stp	q7, q4, [x9, #-160]
	ldp	q19, q18, [x9, #-128]
	ldp	q16, q17, [x9, #-96]
	ldp	q20, q21, [x10, #-128]
	ldp	q22, q23, [x10, #-96]
	fmla	v18.2d, v21.2d, v31.2d
	fmla	v16.2d, v22.2d, v31.2d
	ldp	q21, q22, [x9, #-64]
	ldp	q24, q25, [x10, #-64]
	fmla	v19.2d, v20.2d, v31.2d
	stp	q19, q18, [x9, #-128]
	fmla	v17.2d, v23.2d, v31.2d
	stp	q16, q17, [x9, #-96]
	ldp	q23, q20, [x9, #-32]
	ldp	q26, q27, [x10, #-32]
	fmla	v21.2d, v24.2d, v31.2d
	fmla	v22.2d, v25.2d, v31.2d
	stp	q21, q22, [x9, #-64]
	ldp	q24, q25, [x9]
	ldp	q28, q29, [x10]
	fmla	v23.2d, v26.2d, v31.2d
	fmla	v20.2d, v27.2d, v31.2d
	stp	q23, q20, [x9, #-32]
	ldp	q26, q27, [x9, #32]
	fmla	v24.2d, v28.2d, v31.2d
	fmla	v25.2d, v29.2d, v31.2d
	stp	q24, q25, [x9]
	ldp	q28, q29, [x10, #32]
	fmla	v26.2d, v28.2d, v31.2d
	fmla	v27.2d, v29.2d, v31.2d
	stp	q26, q27, [x9, #32]
	ldp	q24, q25, [x9, #64]
	ldp	q28, q29, [x10, #64]
	ldp	q26, q27, [x9, #96]
	fmla	v24.2d, v28.2d, v31.2d
	fmla	v25.2d, v29.2d, v31.2d
	stp	q24, q25, [x9, #64]
	ldp	q28, q29, [x10, #96]
	fmla	v26.2d, v28.2d, v31.2d
	fmla	v27.2d, v29.2d, v31.2d
	stp	q26, q27, [x9, #96]
	ldp	q24, q25, [x9, #128]
	ldp	q26, q27, [x10, #128]
	fmla	v24.2d, v26.2d, v31.2d
	fmla	v25.2d, v27.2d, v31.2d
	stp	q24, q25, [x9, #128]
	ldp	q26, q27, [x9, #160]
	ldp	q1, q2, [x10, #160]
	fmla	v26.2d, v1.2d, v31.2d
	fmla	v27.2d, v2.2d, v31.2d
	stp	q26, q27, [x9, #160]
	ldp	q0, q1, [x9, #192]
	ldp	q2, q3, [x10, #192]
	fmla	v0.2d, v2.2d, v31.2d
	fmla	v1.2d, v3.2d, v31.2d
	stp	q0, q1, [x9, #192]
	ldp	q2, q3, [x9, #224]
	ldp	q4, q5, [x10, #224]
	fmla	v2.2d, v4.2d, v31.2d
	fmla	v3.2d, v5.2d, v31.2d
	stp	q2, q3, [x9, #224]
	add	x8, x8, #64             // =64
	add	x10, x10, #512          // =512
	add	x9, x9, #512            // =512
	adds	x11, x11, #8            // =8
	b.ne	.LBB1_29
    // OSACA-END
