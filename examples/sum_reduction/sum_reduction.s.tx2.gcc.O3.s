    // OSACA-BEGIN
.L17:
	mov	x17, x16
	ldr	q4, [x17], 16
	ldr	q5, [x16, 16]
	add	x16, x16, 128
	ldr	q3, [x16, -80]
	ldr	q2, [x16, -64]
	ldr	q0, [x16, -48]
	ldr	q1, [x16, -32]
	ldr	q7, [x16, -16]
	dup	d16, v4.d[0]
	dup	d6, v4.d[1]
	ldr	q4, [x17, 16]
	dup	d22, v5.d[0]
	dup	d5, v5.d[1]
	dup	d20, v3.d[0]
	dup	d3, v3.d[1]
	dup	d19, v2.d[0]
	dup	d2, v2.d[1]
	dup	d21, v4.d[0]
	dup	d4, v4.d[1]
	fadd	d10, d8, d16
	dup	d18, v0.d[0]
	dup	d0, v0.d[1]
	dup	d8, v1.d[0]
	dup	d1, v1.d[1]
	dup	d17, v7.d[0]
	dup	d7, v7.d[1]
	fadd	d23, d6, d10
	fadd	d24, d23, d22
	fadd	d25, d5, d24
	fadd	d26, d25, d21
	fadd	d27, d4, d26
	fadd	d28, d27, d20
	fadd	d29, d3, d28
	fadd	d30, d29, d19
	fadd	d31, d2, d30
	fadd	d16, d31, d18
	fadd	d6, d0, d16
	fadd	d22, d6, d8
	fadd	d5, d1, d22
	fadd	d20, d5, d17
	fadd	d8, d7, d20
	cmp	x22, x16
	bne	.L17
    // OSACA-END
