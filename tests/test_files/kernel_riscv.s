# Basic RISC-V test kernel with various instructions

.text
.globl vector_add
.align 2

# Example of a basic function
vector_add:
    # Prologue
    addi sp, sp, -16
    sw ra, 12(sp)
    sw s0, 8(sp)
    addi s0, sp, 16

    # Setup
    mv a3, a0
    lw a0, 0(a0)     # Load first element
    lw a4, 0(a1)     # Load second element
    add a0, a0, a4   # Add elements
    sw a0, 0(a2)     # Store to result array

    # Integer operations
    addi t0, zero, 10
    addi t1, zero, 5
    add t2, t0, t1
    sub t3, t0, t1
    and t4, t0, t1
    or t5, t0, t1
    xor t6, t0, t1
    sll a0, t0, t1
    srl a1, t0, t1
    sra a2, t0, t1

    # Memory operations
    lw a0, 8(sp)
    sw a1, 4(sp)
    lbu a2, 1(sp)
    sb a3, 0(sp)
    lh a4, 2(sp)
    sh a5, 2(sp)

    # Branch and jump instructions
    beq t0, t1, skip
    bne t0, t1, continue
    jal ra, function
    jalr t0, 0(ra)

.L1:                       # Loop Header
    beq t0, t1, .L2
    addi t0, t0, 1
    j .L1

.L2:
    # Floating point operations
    flw fa0, 0(a0)
    flw fa1, 4(a0)
    fadd.s fa2, fa0, fa1
    fsub.s fa3, fa0, fa1
    fmv.x.w a0, fa0
    fmv.w.x fa4, a0

    # CSR operations
    csrr t0, mstatus
    csrw mtvec, t0
    csrs mie, t0
    csrc mip, t0

    # Vector instructions (RVV)
    vsetvli t0, a0, e32, m4, ta, ma
    vle32.v v0, (a0)
    vle32.v v4, (a1)
    vadd.vv v8, v0, v4
    vse32.v v8, (a2)

    # Atomic operations
    lr.w t0, (a0)
    sc.w t1, t2, (a0)
    amoswap.w t3, t4, (a0)
    amoadd.w t5, t6, (a0)

    # Multiply/divide instructions
    mul t0, t1, t2
    mulh t3, t4, t5
    div t0, t1, t2
    rem t3, t4, t5

    # Pseudo-instructions
    li t0, 1234
    la t1, data
    li a0, %hi(data)
    addi a1, a0, %lo(data)

skip:
    # Skip destination
    addi t2, zero, 20

continue:
    # Continue destination
    addi t3, zero, 30

function:
    # Function destination
    addi a0, zero, 0
    ret

    # Epilogue
    lw ra, 12(sp)
    lw s0, 8(sp)
    addi sp, sp, 16
    ret

.data
.align 4
data:
    .word 0x12345678
    .byte 0x01, 0x02, 0x03, 0x04
    .half 0xABCD, 0xEF01
    .float 3.14159
    .space 16
    .ascii "RISC-V Test String"