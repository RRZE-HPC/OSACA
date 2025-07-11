daxpy_riscv:
.L3:
	vsetvli	a5,a2,e64,m1,ta,ma
	vle64.v	v1,0(a0)
	vle64.v	v2,0(a1)
	slli	a3,a5,3
	sub	a2,a2,a5
	add	a0,a0,a3
	add	a1,a1,a3
	vfmacc.vv	v1,v3,v2
	vse64.v	v1,0(a4)
	add	a4,a4,a3
	bne	a2,zero,.L3