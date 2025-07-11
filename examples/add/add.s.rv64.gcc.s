add_riscv:
.L3:
	vsetvli	a5,a3,e64,m1,ta,ma
	vle64.v	v2,0(a1)
	vle64.v	v1,0(a2)
	slli	a4,a5,3
	sub	a3,a3,a5
	add	a1,a1,a4
	add	a2,a2,a4
	vfadd.vv	v1,v1,v2
	vse64.v	v1,0(a0)
	add	a0,a0,a4
	bne	a3,zero,.L3