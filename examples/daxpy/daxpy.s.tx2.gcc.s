    // OSACA-BEGIN
.L17:
	mov	x5, x3
	ldr	q23, [x10]
	ldr	q24, [x5], 16
	mov	x6, x10
	ldr	q25, [x3, 16]
	ldr	q26, [x3, 48]
	add	x10, x10, 128
	add	x3, x3, 128
	ldr	q27, [x3, -64]
	ldr	q28, [x3, -48]
	ldr	q29, [x3, -32]
	ldr	q30, [x3, -16]
	fmla	v23.2d, v3.2d, v24.2d
	ldr	q31, [x5, 16]
	str	q23, [x6], 16
	ldr	q0, [x10, -112]
	fmla	v0.2d, v3.2d, v25.2d
	str	q0, [x10, -112]
	ldr	q2, [x6, 16]
	fmla	v2.2d, v3.2d, v31.2d
	str	q2, [x6, 16]
	ldr	q5, [x10, -80]
	ldr	q4, [x10, -64]
	ldr	q6, [x10, -48]
	ldr	q1, [x10, -32]
	ldr	q7, [x10, -16]
	fmla	v5.2d, v3.2d, v26.2d
	fmla	v4.2d, v3.2d, v27.2d
	fmla	v6.2d, v3.2d, v28.2d
	fmla	v1.2d, v3.2d, v29.2d
	fmla	v7.2d, v3.2d, v30.2d
	str	q5, [x10, -80]
	str	q4, [x10, -64]
	str	q6, [x10, -48]
	str	q1, [x10, -32]
	str	q7, [x10, -16]
	cmp	x23, x10
	bne	.L17
    // OSACA-END
