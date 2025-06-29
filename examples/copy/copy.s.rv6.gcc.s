copy_riscv:
.L3:
	vsetvli	a5,a2,e8,m1,ta,ma
	vle8.v	v1,0(a1)
	sub	a2,a2,a5
	add	a1,a1,a5
	vse8.v	v1,0(a0)
	add	a0,a0,a5
	bne	a2,zero,.L3