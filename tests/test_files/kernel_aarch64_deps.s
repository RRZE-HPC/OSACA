// OSACA-BEGIN
.LBB0_32:
    ldp q4, q5, [x9, #-32]
    ldp q6, q7, [x9], #64
    add x9, x9, x9
    add x10, x9, #64           // =64
    fmul    v4.2d, v4.2d, v6.2d
    fmul    v5.2d, v4.2d, v7.2d
    adds x10, x10, x10
    csel, x9, x1, x9, eq
    stp q14, q15, [x9, #-32]!
    stp q14, q15, [x9], #64
    b.ne    .LBB0_32
// OSACA-END
