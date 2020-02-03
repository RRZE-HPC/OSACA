    // OSACA-BEGIN
.L17:
	add	x12, x11, 16
	ldr	q29, [x22, x11]
	ldr	q30, [x20, x11]
	add	x7, x11, 32
	ldr	q31, [x21, x11]
	ldr	q7, [x22, x12]
	add	x6, x11, 48
	add	x5, x11, 64
	ldr	q6, [x20, x12]
	ldr	q2, [x21, x12]
	add	x8, x11, 80
	add	x0, x11, 96
	ldr	q9, [x22, x7]
	ldr	q5, [x20, x7]
	add	x13, x11, 112
	ldr	q1, [x21, x7]
	ldr	q16, [x22, x6]
	ldr	q4, [x20, x6]
	ldr	q0, [x21, x6]
	fmla	v30.2d, v29.2d, v31.2d
	ldr	q23, [x22, x5]
	ldr	q3, [x20, x5]
	fmla	v6.2d, v7.2d, v2.2d
	ldr	q22, [x21, x5]
	ldr	q21, [x22, x8]
	ldr	q24, [x20, x8]
	ldr	q20, [x21, x8]
	fmla	v5.2d, v9.2d, v1.2d
	ldr	q19, [x22, x0]
	ldr	q25, [x20, x0]
	fmla	v4.2d, v16.2d, v0.2d
	ldr	q18, [x21, x0]
	ldr	q17, [x22, x13]
	ldr	q26, [x20, x13]
	ldr	q27, [x21, x13]
	fmla	v3.2d, v23.2d, v22.2d
	fmla	v24.2d, v21.2d, v20.2d
	str	q30, [x19, x11]
	add	x11, x11, 128
	str	q6, [x19, x12]
	fmla	v25.2d, v19.2d, v18.2d
	str	q5, [x19, x7]
	fmla	v26.2d, v17.2d, v27.2d
	str	q4, [x19, x6]
	str	q3, [x19, x5]
	str	q24, [x19, x8]
	str	q25, [x19, x0]
	str	q26, [x19, x13]
	cmp	x25, x11
	bne	.L17
    // OSACA-END
