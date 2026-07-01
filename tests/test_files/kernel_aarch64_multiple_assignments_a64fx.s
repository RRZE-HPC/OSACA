sub     x6, x11, #2    
mov     w10, w2
mov     w10, w2
lsl     x1, x10, #1
cmp     x6, #1 
sub     x19, x1, #2
and     x6, x6, #0xfffffffffffffffe
and     w21, w1, w21
.LBB0_13
// OSACA-BEGIN
smlal   v2.4s, v1.2d, v1.2d
smlal   v3.4s, v1.2d, v1.2d
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
dup     v1.2d, v0.d[0]
// OSACA-END
b.eq .LBB0_13

