    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q4, q5, [x9, #-256]
	fadd	v0.2d, v4.2d, v0.2d
	fadd	v1.2d, v5.2d, v1.2d
	ldp	q4, q5, [x9, #-192]
	ldp	q16, q17, [x9, #-128]
	fadd	v4.2d, v4.2d, v16.2d
	ldp	q6, q7, [x9, #-224]
	fadd	v2.2d, v6.2d, v2.2d
	fadd	v3.2d, v7.2d, v3.2d
	fadd	v0.2d, v0.2d, v4.2d
	fadd	v4.2d, v5.2d, v17.2d
	ldp	q6, q7, [x9, #-160]
	ldp	q18, q19, [x9, #-96]
	ldp	q16, q17, [x9]
	add	x8, x8, #64             // =64
	fadd	v1.2d, v1.2d, v4.2d
	fadd	v4.2d, v6.2d, v18.2d
	fadd	v2.2d, v2.2d, v4.2d
	fadd	v4.2d, v7.2d, v19.2d
	ldp	q6, q7, [x9, #-32]
	ldp	q18, q19, [x9, #32]
	fadd	v6.2d, v6.2d, v18.2d
	fadd	v7.2d, v7.2d, v19.2d
	fadd	v3.2d, v3.2d, v4.2d
	ldp	q4, q5, [x9, #-64]
	fadd	v4.2d, v4.2d, v16.2d
	fadd	v5.2d, v5.2d, v17.2d
	ldp	q16, q17, [x9, #64]
	fadd	v4.2d, v4.2d, v16.2d
	fadd	v5.2d, v5.2d, v17.2d
	ldp	q16, q17, [x9, #128]
	fadd	v0.2d, v0.2d, v16.2d
	fadd	v1.2d, v1.2d, v17.2d
	ldp	q16, q17, [x9, #192]
	ldp	q18, q19, [x9, #96]
	fadd	v6.2d, v6.2d, v18.2d
	fadd	v7.2d, v7.2d, v19.2d
	fadd	v4.2d, v4.2d, v16.2d
	ldp	q18, q19, [x9, #160]
	fadd	v2.2d, v2.2d, v18.2d
	fadd	v3.2d, v3.2d, v19.2d
	fadd	v0.2d, v0.2d, v4.2d
	fadd	v4.2d, v5.2d, v17.2d
	ldp	q18, q19, [x9, #224]
	add	x9, x9, #512            // =512
	fadd	v1.2d, v1.2d, v4.2d
	fadd	v4.2d, v6.2d, v18.2d
	fadd	v2.2d, v2.2d, v4.2d
	fadd	v4.2d, v7.2d, v19.2d
	fadd	v3.2d, v3.2d, v4.2d
	adds	x10, x10, #8            // =8
	b.ne	.LBB1_29
    // OSACA-END
