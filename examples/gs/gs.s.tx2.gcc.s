    // OSACA-BEGIN
.L20:
	ldr	d31, [x15, x18, lsl 3]
	ldr	d0, [x15, 8]
	mov	x14, x15
	add	x16, x15, 24
	ldr	d2, [x15, x30, lsl 3]
	add	x15, x15, 32
	fadd	d1, d31, d0
	fadd	d3, d1, d30
	fadd	d4, d3, d2
	fmul	d5, d4, d9
	str	d5, [x14], 8
	ldr	d6, [x14, x18, lsl 3]
	ldr	d16, [x14, 8]
	add	x13, x14, 8
	ldr	d7, [x14, x30, lsl 3]
	fadd	d17, d6, d16
	fadd	d18, d17, d5
	fadd	d19, d18, d7
	fmul	d20, d19, d9
	str	d20, [x15, -24]
	ldr	d21, [x13, x18, lsl 3]
	ldr	d23, [x14, 16]
	ldr	d22, [x13, x30, lsl 3]
	fadd	d24, d21, d23
	fadd	d25, d24, d20
	fadd	d26, d25, d22
	fmul	d27, d26, d9
	str	d27, [x14, 8]
	ldr	d30, [x15]
	ldr	d28, [x16, x18, lsl 3]
	ldr	d29, [x16, x30, lsl 3]
	fadd	d31, d28, d30
	fadd	d2, d31, d27
	fadd	d0, d2, d29
	fmul	d30, d0, d9
	str	d30, [x15, -8]
	cmp	x7, x15
	bne	.L20
    // OSACA-END
