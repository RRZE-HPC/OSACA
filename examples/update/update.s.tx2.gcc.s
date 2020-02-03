    // OSACA-BEGIN
.L17:
	ldr	q23, [x16]
	mov	x17, x16
	add	x16, x16, 128
	fmul	v24.2d, v23.2d, v2.2d
	str	q24, [x17], 16
	ldr	q25, [x16, -112]
	fmul	v26.2d, v25.2d, v2.2d
	str	q26, [x16, -112]
	ldr	q27, [x17, 16]
	fmul	v28.2d, v27.2d, v2.2d
	str	q28, [x17, 16]
	ldr	q29, [x16, -80]
	ldr	q30, [x16, -64]
	ldr	q31, [x16, -48]
	ldr	q1, [x16, -32]
	ldr	q0, [x16, -16]
	fmul	v5.2d, v29.2d, v2.2d
	fmul	v4.2d, v30.2d, v2.2d
	fmul	v3.2d, v31.2d, v2.2d
	fmul	v6.2d, v1.2d, v2.2d
	fmul	v7.2d, v0.2d, v2.2d
	str	q5, [x16, -80]
	str	q4, [x16, -64]
	str	q3, [x16, -48]
	str	q6, [x16, -32]
	str	q7, [x16, -16]
	cmp	x22, x16
	bne	.L17
    // OSACA-END
