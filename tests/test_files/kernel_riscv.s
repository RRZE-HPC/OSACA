saxpy_golden:
        beq     a0,zero,.L12
        addi    a5,a1,4
        csrr    a4,vlenb
        sub     a5,a2,a5
        addi    a4,a4,-8
        bleu    a5,a4,.L3
        vsetvli a5,zero,e32,m1,ta,ma
        vfmv.v.f        v3,fa0
        mv      a4,a2
.L4:
        vsetvli a5,a0,e32,m1,ta,ma
        vle32.v v1,0(a1)
        vle32.v v2,0(a2)
        slli    a3,a5,2
        sub     a0,a0,a5
        add     a1,a1,a3
        add     a2,a2,a3
        vfmadd.vv       v1,v3,v2
        vse32.v v1,0(a4)
        add     a4,a4,a3
        bne     a0,zero,.L4
        ret
.L3:
        slli    a0,a0,2
        add     a0,a2,a0
.L6:
        flw     fa5,0(a1)
        flw     fa4,0(a2)
        addi    a2,a2,4
        addi    a1,a1,4
        fmadd.s fa5,fa0,fa5,fa4
        fsw     fa5,-4(a2)
        bne     a2,a0,.L6
.L12:
        ret
saxpy_vec:
        beq     a0,zero,.L25
.L18:
        vsetvli a5,a0,e32,m8,ta,ma
        vle32.v v16,0(a1)
        vle32.v v8,0(a2)
        slli    a4,a5,2
        sub     a0,a0,a5
        add     a1,a1,a4
        vfmacc.vf       v8,fa0,v16
        vse32.v v8,0(a2)
        add     a2,a2,a4
        bne     a0,zero,.L18
.L25:
        ret
fp_eq:
        fabs.s  fa4,fa0
        fsub.s  fa1,fa1,fa0
        fmv.s   fa5,fa2
        fgt.s   a5,fa4,fa2
        fabs.s  fa1,fa1
        beq     a5,zero,.L28
        fmv.s   fa5,fa4
.L28:
        fmul.s  fa5,fa5,fa2
        flt.s   a0,fa1,fa5
        ret
.LC2:
        .string "fail, %f=!%f\n"
.LC3:
        .string "pass"
main:
        addi    sp,sp,-64
        sd      s1,40(sp)
        lui     a5,%hi(.LC0)
        lui     s1,%hi(.LANCHOR0)
        flw     fa5,%lo(.LC0)(a5)
        addi    a5,s1,%lo(.LANCHOR0)
        vsetivli        zero,4,e32,m1,ta,ma
        addi    a4,a5,144
        sd      s0,48(sp)
        vle32.v v7,0(a4)
        addi    a3,a5,336
        addi    a4,a5,352
        addi    s0,a5,256
        addi    a7,a5,272
        addi    a6,a5,288
        addi    a0,a5,304
        addi    a1,a5,320
        addi    a2,a5,128
        addi    t6,a5,160
        addi    t5,a5,176
        addi    t4,a5,192
        addi    t3,a5,208
        addi    t1,a5,224
        vle32.v v10,0(a3)
        vle32.v v9,0(a4)
        vle32.v v15,0(s0)
        vle32.v v14,0(a7)
        vle32.v v13,0(a6)
        vle32.v v12,0(a0)
        vle32.v v11,0(a1)
        vle32.v v8,0(a2)
        vle32.v v6,0(t6)
        vle32.v v5,0(t5)
        vle32.v v4,0(t4)
        vle32.v v3,0(t3)
        vle32.v v2,0(t1)
        vfmv.v.f        v1,fa5
        sd      s2,32(sp)
        sd      ra,56(sp)
        vfmadd.vv       v8,v1,v15
        vfmadd.vv       v3,v1,v10
        vfmadd.vv       v2,v1,v9
        vfmadd.vv       v7,v1,v14
        vfmadd.vv       v6,v1,v13
        vfmadd.vv       v5,v1,v12
        vfmadd.vv       v4,v1,v11
        sd      s3,24(sp)
        sd      s4,16(sp)
        fsd     fs0,8(sp)
        vse32.v v3,0(a3)
        vse32.v v2,0(a4)
        vse32.v v8,0(s0)
        vse32.v v7,0(a7)
        vse32.v v6,0(a6)
        vse32.v v5,0(a0)
        vse32.v v4,0(a1)
        addi    a4,a5,240
        vsetivli        zero,3,e32,m1,ta,ma
        addi    a5,a5,368
        vfmv.v.f        v3,fa5
        addi    s2,s1,%lo(.LANCHOR0)
        vle32.v v1,0(a4)
        vle32.v v2,0(a5)
        addi    a4,s1,%lo(.LANCHOR0)
        li      a3,31
        vfmadd.vv       v1,v3,v2
        vse32.v v1,0(a5)
.L31:
        vsetvli a5,a3,e32,m8,ta,ma
        vle32.v v16,0(a2)
        vle32.v v8,0(a4)
        slli    a1,a5,2
        sub     a3,a3,a5
        add     a2,a2,a1
        vfmacc.vf       v8,fa5,v16
        vse32.v v8,0(a4)
        add     a4,a4,a1
        bne     a3,zero,.L31
        lui     a5,%hi(.LC1)
        flw     fs0,%lo(.LC1)(a5)
        addi    s1,s1,%lo(.LANCHOR0)
        addi    s2,s2,380
        li      s3,1
        lui     s4,%hi(.LC2)
        j       .L35
.L32:
        addi    s0,s0,4
        addi    s1,s1,4
        beq     s2,s0,.L48
.L35:
        flw     fa3,0(s0)
        flw     fa1,0(s1)
        fmv.s   fa5,fs0
        fabs.s  fa2,fa3
        fsub.s  fa4,fa1,fa3
        fgt.s   a5,fa2,fs0
        fabs.s  fa4,fa4
        beq     a5,zero,.L34
        fmv.s   fa5,fa2
.L34:
        fmul.s  fa5,fa5,fs0
        fgt.s   a5,fa5,fa4
        bne     a5,zero,.L32
        fcvt.d.s        fa5,fa1
        addi    a0,s4,%lo(.LC2)
        addi    s0,s0,4
        fmv.x.d a2,fa5
        fcvt.d.s        fa5,fa3
        li      s3,0
        addi    s1,s1,4
        fmv.x.d a1,fa5
        call    printf
        bne     s2,s0,.L35
.L48:
        bne     s3,zero,.L49
.L43:
        ld      ra,56(sp)
        ld      s0,48(sp)
        ld      s1,40(sp)
        ld      s2,32(sp)
        ld      s4,16(sp)
        fld     fs0,8(sp)
        xori    a0,s3,1
        ld      s3,24(sp)
        addi    sp,sp,64
        jr      ra
.L49:
        lui     a0,%hi(.LC3)
        addi    a0,a0,%lo(.LC3)
        call    puts
        j       .L43
.LC0:
        .word   1113498583
.LC1:
        .word   897988541
        .set    .LANCHOR0,. + 0