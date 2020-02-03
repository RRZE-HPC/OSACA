    // OSACA-BEGIN
.L17:
	add	x16, x15, 16
	ldr	q9, [x19, x15]
	add	x30, x15, 32
	add	x17, x15, 48
	ldr	q16, [x19, x16]
	ldr	q18, [x19, x30]
	add	x18, x15, 64
	add	x1, x15, 80
	ldr	q17, [x19, x17]
	ldr	q19, [x19, x18]
	add	x3, x15, 96
	add	x2, x15, 112
	ldr	q20, [x19, x1]
	ldr	q21, [x19, x3]
	str	q9, [x20, x15]
	ldr	q22, [x19, x2]
	add	x15, x15, 128
	str	q16, [x20, x16]
	str	q18, [x20, x30]
	str	q17, [x20, x17]
	str	q19, [x20, x18]
	str	q20, [x20, x1]
	str	q21, [x20, x3]
	str	q22, [x20, x2]
	cmp	x23, x15
	bne	.L17
    // OSACA-END
