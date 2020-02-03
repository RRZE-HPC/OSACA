    // OSACA-BEGIN
.L93:
	add	x5, x0, 16
	ldr	q2, [x14, x0]
	ldr	q5, [x25, x0]
	add	x7, x0, 32
	ldr	q13, [x22, x0]
	ldr	q4, [x25, x5]
	add	x6, x0, 48
	ldr	x9, [sp, 144]
	ldr	q19, [x22, x5]
	ldr	q7, [x14, x5]
	ldr	q6, [x14, x7]
	ldr	q3, [x25, x7]
	ldr	q18, [x22, x7]
	fadd	v17.2d, v2.2d, v30.2d
	ldr	q16, [x14, x6]
	ldr	q20, [x25, x6]
	fadd	v23.2d, v5.2d, v13.2d
	ldr	q22, [x22, x6]
	fadd	v24.2d, v4.2d, v19.2d
	fadd	v25.2d, v7.2d, v2.2d
	fadd	v27.2d, v6.2d, v7.2d
	fadd	v26.2d, v3.2d, v18.2d
	fadd	v28.2d, v16.2d, v6.2d
	mov	v30.16b, v16.16b
	fadd	v29.2d, v20.2d, v22.2d
	fadd	v31.2d, v23.2d, v17.2d
	fadd	v0.2d, v24.2d, v25.2d
	fadd	v2.2d, v26.2d, v27.2d
	fadd	v1.2d, v29.2d, v28.2d
	fmul	v5.2d, v31.2d, v21.2d
	fmul	v13.2d, v0.2d, v21.2d
	fmul	v4.2d, v2.2d, v21.2d
	fmul	v19.2d, v1.2d, v21.2d
	str	q5, [x28, x0]
	add	x0, x0, 64
	str	q13, [x28, x5]
	str	q4, [x28, x7]
	str	q19, [x28, x6]
	cmp	x9, x0
	bne	.L93
    // OSACA-END
