    // OSACA-BEGIN
.LBB1_29:                               //   Parent Loop BB1_16 Depth=1
                                        //     Parent Loop BB1_19 Depth=2
                                        //       Parent Loop BB1_24 Depth=3
                                        // =>      This Inner Loop Header: Depth=4
	add	x0, x5, x16
	add	x18, x21, x16
	ldp	q4, q5, [x0, #16]
	ldp	q6, q7, [x0, #48]
	ldur	q0, [x18, #8]
	ldur	q1, [x18, #24]
	ldur	q2, [x18, #40]
	ldur	q3, [x18, #56]
	add	x1, x28, x16
	add	x15, x15, #32           // =32
	fadd	v0.2d, v4.2d, v0.2d
	fadd	v4.2d, v5.2d, v1.2d
	fadd	v5.2d, v6.2d, v2.2d
	fadd	v6.2d, v7.2d, v3.2d
	ldp	q7, q16, [x1, #16]
	fadd	v1.2d, v7.2d, v1.2d
	ldp	q17, q18, [x1, #48]
	ldur	q19, [x18, #72]
	fadd	v0.2d, v0.2d, v1.2d
	fadd	v1.2d, v16.2d, v2.2d
	fadd	v2.2d, v17.2d, v3.2d
	fadd	v3.2d, v18.2d, v19.2d
	ldp	q16, q17, [x0, #80]
	ldp	q18, q19, [x0, #112]
	fadd	v1.2d, v4.2d, v1.2d
	fadd	v2.2d, v5.2d, v2.2d
	fadd	v3.2d, v6.2d, v3.2d
	ldur	q4, [x18, #72]
	ldur	q5, [x18, #88]
	ldur	q6, [x18, #104]
	ldur	q7, [x18, #120]
	fadd	v4.2d, v16.2d, v4.2d
	fadd	v16.2d, v17.2d, v5.2d
	fadd	v17.2d, v18.2d, v6.2d
	fadd	v18.2d, v19.2d, v7.2d
	ldp	q19, q20, [x1, #80]
	fadd	v5.2d, v19.2d, v5.2d
	ldp	q21, q22, [x1, #112]
	ldur	q23, [x18, #136]
	fadd	v4.2d, v4.2d, v5.2d
	fadd	v5.2d, v20.2d, v6.2d
	fadd	v6.2d, v21.2d, v7.2d
	fadd	v7.2d, v22.2d, v23.2d
	ldp	q20, q21, [x0, #144]
	ldp	q22, q23, [x0, #176]
	fadd	v5.2d, v16.2d, v5.2d
	fadd	v6.2d, v17.2d, v6.2d
	fadd	v7.2d, v18.2d, v7.2d
	ldur	q16, [x18, #136]
	ldur	q17, [x18, #152]
	ldur	q18, [x18, #168]
	ldur	q19, [x18, #184]
	fadd	v16.2d, v20.2d, v16.2d
	fadd	v20.2d, v21.2d, v17.2d
	fadd	v21.2d, v22.2d, v18.2d
	fadd	v22.2d, v23.2d, v19.2d
	ldp	q23, q24, [x1, #144]
	fadd	v17.2d, v23.2d, v17.2d
	ldp	q25, q26, [x1, #176]
	fadd	v16.2d, v16.2d, v17.2d
	fadd	v17.2d, v24.2d, v18.2d
	fadd	v18.2d, v25.2d, v19.2d
	ldp	q24, q25, [x0, #208]
	ldur	q23, [x18, #200]
	fadd	v17.2d, v20.2d, v17.2d
	fadd	v18.2d, v21.2d, v18.2d
	ldur	q20, [x18, #200]
	ldur	q21, [x18, #216]
	fadd	v19.2d, v26.2d, v23.2d
	fadd	v20.2d, v24.2d, v20.2d
	fadd	v24.2d, v25.2d, v21.2d
	ldp	q25, q26, [x1, #208]
	fadd	v21.2d, v25.2d, v21.2d
	fadd	v20.2d, v20.2d, v21.2d
	ldp	q21, q25, [x0, #240]
	fadd	v19.2d, v22.2d, v19.2d
	ldur	q22, [x18, #232]
	fadd	v21.2d, v21.2d, v22.2d
	fadd	v22.2d, v26.2d, v22.2d
	fadd	v22.2d, v24.2d, v22.2d
	ldp	q24, q26, [x1, #240]
	ldur	q23, [x18, #248]
	fadd	v25.2d, v25.2d, v23.2d
	fadd	v23.2d, v24.2d, v23.2d
	add	x18, x18, #264          // =264
	fmul	v0.2d, v0.2d, v28.2d
	fmul	v1.2d, v1.2d, v28.2d
	fmul	v2.2d, v2.2d, v28.2d
	fmul	v5.2d, v5.2d, v28.2d
	fadd	v21.2d, v21.2d, v23.2d
	ldr	q23, [x18]
	add	x18, x25, x16
	stur	q0, [x18, #8]
	stur	q1, [x18, #24]
	fmul	v3.2d, v3.2d, v28.2d
	stur	q2, [x18, #40]
	fadd	v23.2d, v26.2d, v23.2d
	stur	q5, [x18, #88]
	fmul	v4.2d, v4.2d, v28.2d
	stur	q3, [x18, #56]
	fmul	v6.2d, v6.2d, v28.2d
	stur	q4, [x18, #72]
	fmul	v0.2d, v7.2d, v28.2d
	stur	q6, [x18, #104]
	fmul	v1.2d, v16.2d, v28.2d
	stur	q0, [x18, #120]
	fmul	v2.2d, v17.2d, v28.2d
	stur	q1, [x18, #136]
	fmul	v4.2d, v19.2d, v28.2d
	stur	q2, [x18, #152]
	fadd	v5.2d, v25.2d, v23.2d
	stur	q4, [x18, #184]
	fmul	v3.2d, v18.2d, v28.2d
	stur	q3, [x18, #168]
	fmul	v6.2d, v20.2d, v28.2d
	stur	q6, [x18, #200]
	fmul	v0.2d, v22.2d, v28.2d
	stur	q0, [x18, #216]
	fmul	v1.2d, v21.2d, v28.2d
	stur	q1, [x18, #232]
	add	x16, x16, #256          // =256
	fmul	v2.2d, v5.2d, v28.2d
	stur	q2, [x18, #248]
	adds	x17, x17, #4            // =4
	b.ne	.LBB1_29
    // OSACA-END
