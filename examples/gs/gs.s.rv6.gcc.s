gs_riscv:
.L5:
	fld	fa2,0(a3)
	fld	fa3,0(a5)
	fld	fa4,0(a4)
	fadd.d	fa5,fa5,fa2
	addi	a5,a5,8
	addi	a3,a3,8
	addi	a4,a4,8
	fadd.d	fa5,fa5,fa3
	fadd.d	fa5,fa5,fa4
	fmul.d	fa5,fa5,fa0
	fsd	fa5,-16(a5)
	bne	a2,a5,.L5
	addi	a0,a0,8
	bne	a6,a0,.L4