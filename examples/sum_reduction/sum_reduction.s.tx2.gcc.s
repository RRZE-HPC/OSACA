	// OSACA-BEGIN
.L17:
	mov	x17, x16
	ldr	q10, [x17], 16
	ldr	q16, [x16, 16]
	add	x16, x16, 128
	ldr	q17, [x16, -80]
	ldr	q18, [x16, -64]
	ldr	q19, [x16, -48]
	ldr	q20, [x16, -32]
	ldr	q21, [x16, -16]
	fadd	v22.2d, v1.2d, v10.2d
	ldr	q23, [x17, 16]
	fadd	v24.2d, v22.2d, v16.2d
	fadd	v25.2d, v24.2d, v23.2d
	fadd	v26.2d, v25.2d, v17.2d
	fadd	v27.2d, v26.2d, v18.2d
	fadd	v28.2d, v27.2d, v19.2d
	fadd	v29.2d, v28.2d, v20.2d
	fadd	v1.2d, v29.2d, v21.2d
	cmp	x22, x16
	bne	.L17
    // OSACA-END
