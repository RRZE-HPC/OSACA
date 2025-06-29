update_riscv:
.L3:
	vsetvli	a5,a1,e64,m1,ta,ma
	vle64.v	v1,0(a0)
	slli	a3,a5,3
	sub	a1,a1,a5
	add	a0,a0,a3
	vfmul.vf	v1,v1,fa0
	vse64.v	v1,0(a4)
	add	a4,a4,a3
	bne	a1,zero,.L3