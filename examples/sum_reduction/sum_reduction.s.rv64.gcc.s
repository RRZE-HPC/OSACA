sum_reduction_riscv:
.L3:
	fld	fa5,0(a0)
	addi	a0,a0,8
	fadd.d	fa0,fa0,fa5
	bne	a1,a0,.L3
	ret