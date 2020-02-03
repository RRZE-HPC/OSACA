    // OSACA-BEGIN
.L17:
	add	x0, x10, 16
	ldr	q29, [x21, x10]
	ldr	q30, [x20, x10]
	add	x7, x10, 32
	ldr	q31, [x21, x0]
	ldr	q2, [x20, x0]
	add	x6, x10, 48
	add	x5, x10, 64
	ldr	q5, [x21, x7]
	ldr	q1, [x20, x7]
	add	x4, x10, 80
	add	x11, x10, 96
	ldr	q4, [x21, x6]
	ldr	q0, [x20, x6]
	add	x2, x10, 112
	fadd	v7.2d, v29.2d, v30.2d
	ldr	q3, [x21, x5]
	ldr	q9, [x20, x5]
	fadd	v6.2d, v31.2d, v2.2d
	ldr	q19, [x21, x4]
	ldr	q18, [x20, x4]
	fadd	v20.2d, v5.2d, v1.2d
	ldr	q21, [x21, x11]
	ldr	q17, [x20, x11]
	fadd	v22.2d, v4.2d, v0.2d
	ldr	q23, [x21, x2]
	ldr	q16, [x20, x2]
	fadd	v24.2d, v3.2d, v9.2d
	fadd	v25.2d, v19.2d, v18.2d
	fadd	v26.2d, v21.2d, v17.2d
	str	q7, [x19, x10]
	add	x10, x10, 128
	fadd	v27.2d, v23.2d, v16.2d
	str	q6, [x19, x0]
	str	q20, [x19, x7]
	str	q22, [x19, x6]
	str	q24, [x19, x5]
	str	q25, [x19, x4]
	str	q26, [x19, x11]
	str	q27, [x19, x2]
	cmp	x24, x10
	bne	.L17
    // OSACA-END
