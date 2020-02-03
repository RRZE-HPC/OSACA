    // OSACA-BEGIN
.L17:
	add	x0, x10, 16
	ldr	q23, [x20, x10]
	ldr	q24, [x21, x10]
	add	x7, x10, 32
	ldr	q25, [x20, x0]
	ldr	q26, [x21, x0]
	add	x6, x10, 48
	add	x5, x10, 64
	ldr	q27, [x20, x7]
	ldr	q28, [x21, x7]
	add	x4, x10, 80
	add	x11, x10, 96
	ldr	q29, [x20, x6]
	ldr	q30, [x21, x6]
	add	x2, x10, 112
	fmla	v23.2d, v3.2d, v24.2d
	ldr	q31, [x20, x5]
	ldr	q4, [x21, x5]
	fmla	v25.2d, v3.2d, v26.2d
	ldr	q2, [x20, x4]
	ldr	q5, [x21, x4]
	fmla	v27.2d, v3.2d, v28.2d
	ldr	q1, [x20, x11]
	ldr	q6, [x21, x11]
	fmla	v29.2d, v3.2d, v30.2d
	ldr	q0, [x20, x2]
	ldr	q7, [x21, x2]
	fmla	v31.2d, v3.2d, v4.2d
	fmla	v2.2d, v3.2d, v5.2d
	fmla	v1.2d, v3.2d, v6.2d
	str	q23, [x19, x10]
	add	x10, x10, 128
	fmla	v0.2d, v3.2d, v7.2d
	str	q25, [x19, x0]
	str	q27, [x19, x7]
	str	q29, [x19, x6]
	str	q31, [x19, x5]
	str	q2, [x19, x4]
	str	q1, [x19, x11]
	str	q0, [x19, x2]
	cmp	x24, x10
	bne	.L17
    // OSACA-END
