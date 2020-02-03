    // OSACA-BEGIN
.LBB1_32:                               //   Parent Loop BB1_20 Depth=1
                                        //     Parent Loop BB1_22 Depth=2
                                        // =>    This Inner Loop Header: Depth=3
	ldp	q0, q1, [x8]
	ldp	q2, q3, [x8, #-32]
	fmul	v2.2d, v2.2d, v26.2d
	fmul	v3.2d, v3.2d, v26.2d
	stp	q2, q3, [x8, #-32]
	fmul	v0.2d, v0.2d, v26.2d
	fmul	v1.2d, v1.2d, v26.2d
	stp	q0, q1, [x8], #64
	adds	x9, x9, #1              // =1
	b.ne	.LBB1_32
    // OSACA-END
