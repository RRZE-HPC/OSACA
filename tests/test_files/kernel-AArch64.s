.LBB0_32:
    ldp q4, q5, [x9, #-32]
    ldp q6, q7, [x9], #64
    ldp q16, q17, [x11, #-32]
    ldp q18, q19, [x11], #64
    fmul    v4.2d, v4.2d, v16.2d
    fmul    v5.2d, v5.2d, v17.2d
    fmul    v6.2d, v6.2d, v18.2d
    fmul    v7.2d, v7.2d, v19.2d
    ldp q0, q1, [x8, #-32]
    ldp q2, q3, [x8], #64
    fadd    v0.2d, v0.2d, v4.2d
    fadd    v1.2d, v1.2d, v5.2d
    stp q0, q1, [x10, #-32]
    fadd    v2.2d, v2.2d, v6.2d
    fadd    v3.2d, v3.2d, v7.2d
    stp q2, q3, [x10]
    add x10, x10, #64           // =64
    adds    x12, x12, #1            // =1
    b.ne    .LBB0_32
