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
