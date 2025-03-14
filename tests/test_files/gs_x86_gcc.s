# Produced with gcc 14.2 with -O3 -march=sapphirerapids -fopenmp-simd -mprefer-vector-width=512, https://godbolt.org/z/drE47x1b4.
.LC3:
        .string "%f\n"
main:
        push    r14
        xor     edi, edi
        push    r13
        push    r12
        push    rbp
        push    rbx
        call    time
        mov     edi, eax
        call    srand
        mov     edi, 1600
        call    malloc
        mov     r12, rax
        mov     rbp, rax
        lea     r13, [rax+1600]
        mov     rbx, rax
.L2:
        mov     edi, 1600
        add     rbx, 8
        call    malloc
        mov     QWORD PTR [rbx-8], rax
        cmp     r13, rbx
        jne     .L2
        lea     rbx, [r12+8]
        lea     r13, [r12+1592]
.L5:
        mov     r14d, 8
.L4:
        call    rand
        vxorpd  xmm2, xmm2, xmm2
        mov     rcx, QWORD PTR [rbx]
        movsx   rdx, eax
        mov     esi, eax
        imul    rdx, rdx, 351843721
        sar     esi, 31
        sar     rdx, 45
        sub     edx, esi
        imul    edx, edx, 100000
        sub     eax, edx
        vcvtsi2sd       xmm0, xmm2, eax
        vdivsd  xmm0, xmm0, QWORD PTR .LC0[rip]
        vmovsd  QWORD PTR [rcx+r14], xmm0
        add     r14, 8
        cmp     r14, 1592
        jne     .L4
        add     rbx, 8
        cmp     r13, rbx
        jne     .L5
        vmovsd  xmm1, QWORD PTR .LC1[rip]
        lea     rdi, [r12+1584]
.L6:
        mov     rdx, QWORD PTR [rbp+8]
        mov     rcx, QWORD PTR [rbp+16]
        mov     eax, 1
        mov     rsi, QWORD PTR [rbp+0]
        vmovsd  xmm0, QWORD PTR [rdx]
.L7:
        vaddsd  xmm0, xmm0, QWORD PTR [rcx+rax*8]
        vaddsd  xmm0, xmm0, QWORD PTR [rdx+8+rax*8]
        vaddsd  xmm0, xmm0, QWORD PTR [rsi+rax*8]
        vmulsd  xmm0, xmm0, xmm1
        vmovsd  QWORD PTR [rdx+rax*8], xmm0
        inc     rax
        cmp     rax, 199
        jne     .L7
        vmovsd  xmm0, QWORD PTR [rdx+1592]
        add     rbp, 8
        vmovsd  QWORD PTR [rcx+8], xmm0
        cmp     rdi, rbp
        jne     .L6
        mov     rax, QWORD PTR [r12+1584]
        vmovsd  xmm0, QWORD PTR .LC2[rip]
        vucomisd        xmm0, QWORD PTR [rax+1584]
        jp      .L9
        je      .L19
.L9:
        pop     rbx
        xor     eax, eax
        pop     rbp
        pop     r12
        pop     r13
        pop     r14
        ret
.L19:
        mov     rax, QWORD PTR [r12]
        mov     edi, OFFSET FLAT:.LC3
        vmovsd  xmm0, QWORD PTR [rax]
        mov     eax, 1
        call    printf
        jmp     .L9
.LC0:
        .long   0
        .long   1083129856
.LC1:
        .long   2061584302
        .long   1072934420
.LC2:
        .long   -57724360
        .long   1072939201
