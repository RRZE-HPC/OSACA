// OSACA-BEGIN
.L5:
        add     x10, x1, x11
        add     x6, x1, x8
        ld2d    {z0.d - z1.d}, p1/z, [x10]
        ld2d    {z2.d - z3.d}, p1/z, [x6]
        mov     z5.d, z1.d
        fadd    z20.d, z3.d, z3.d
        mov     z1.d, z0.d
        add     x6, x1, x7
        fadd    z2.d, z2.d, z2.d
        ld2d    {z6.d - z7.d}, p1/z, [x6]
        fmul    z4.d, z5.d, z20.d
        add     x10, x1, x12
        mov     z0.d, z7.d
        ld2d    {z16.d - z17.d}, p1/z, [x10]
        mov     z3.d, z4.d
        fmls    z3.d, p0/m, z0.d, z17.d
        fmul    z0.d, z0.d, z16.d
        fmla    z3.d, p0/m, z6.d, z16.d
        fmla    z0.d, p0/m, z6.d, z17.d
        fmls    z3.d, p0/m, z1.d, z2.d
        fmls    z0.d, p0/m, z1.d, z20.d
        mov     z18.d, z3.d
        fmsb    z5.d, p0/m, z2.d, z0.d
        mov     z19.d, z5.d
        st2d    {z18.d - z19.d}, p1, [x6]
        add     x5, x5, 8
        add     x1, x1, 128
        whilelo p1.d, x5, x9
        bne     .L5
// OSACA-END