    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q0, q1, [x9, #-256]
	ldp	q2, q3, [x9, #-224]
	stp	q0, q1, [x10, #-256]
	stp	q2, q3, [x10, #-224]
	add	x8, x8, #64             // =64
	ldp	q0, q1, [x9]
	ldp	q2, q3, [x9, #32]
	stp	q0, q1, [x10]
	stp	q2, q3, [x10, #32]
	ldp	q0, q1, [x9, #-192]
	ldp	q2, q3, [x9, #-160]
	stp	q0, q1, [x10, #-192]
	stp	q2, q3, [x10, #-160]
	ldp	q0, q1, [x9, #64]
	ldp	q2, q3, [x9, #96]
	stp	q0, q1, [x10, #64]
	stp	q2, q3, [x10, #96]
	ldp	q0, q1, [x9, #-128]
	ldp	q2, q3, [x9, #-96]
	stp	q0, q1, [x10, #-128]
	stp	q2, q3, [x10, #-96]
	ldp	q0, q1, [x9, #128]
	ldp	q2, q3, [x9, #160]
	stp	q0, q1, [x10, #128]
	stp	q2, q3, [x10, #160]
	ldp	q0, q1, [x9, #-64]
	ldp	q2, q3, [x9, #-32]
	stp	q0, q1, [x10, #-64]
	stp	q2, q3, [x10, #-32]
	ldp	q0, q1, [x9, #192]
	ldp	q2, q3, [x9, #224]
	add	x9, x9, #512            // =512
	stp	q0, q1, [x10, #192]
	stp	q2, q3, [x10, #224]
	add	x10, x10, #512          // =512
	adds	x11, x11, #8            // =8
	b.ne	.LBB1_29
    // OSACA-END
