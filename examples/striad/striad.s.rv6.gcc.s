striad_riscv:
.L3:
	vsetvli	a5,a4,e64,m1,ta,ma
	vle64.v	v2,0(a1)
	vle64.v	v3,0(a2)
	vle64.v	v1,0(a3)
	slli	a6,a5,3
	sub	a4,a4,a5
	add	a1,a1,a6
	add	a2,a2,a6
	add	a3,a3,a6
	vfmadd.vv	v1,v3,v2
	vse64.v	v1,0(a0)
	add	a0,a0,a6
	bne	a4,zero,.L3