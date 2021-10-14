mov       x1, #111    // OSACA START MARKER
.byte     213,3,32,31 // OSACA START MARKER
// pointer_increment=8 bcc2ad06facad03d27f4cce90dbe3f50
.L4:
ldr d0, [x2]
ldr d3, [x1]
ldr d2, [x1, 16]
ldr d1, [x2, x4, lsl 3]
add x2, x2, 8
fadd d0, d0, d3
fadd d0, d0, d2
fadd d0, d0, d1
fmul d0, d0, d4
str d0, [x1, 8]!
cmp x5, x1
bne .L4
mov       x1, #222    // OSACA END MARKER
.byte     213,3,32,31 // OSACA END MARKER