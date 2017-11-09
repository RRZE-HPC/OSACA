# mark_description "Intel(R) C Intel(R) 64 Compiler for applications running on Intel(R) 64, Version 17.0.5.239 Build 20170817";
# mark_description "-fno-alias -O3 -fopenmp -xCORE-AVX-I -S -o 2d.S";
	.file "2d-5pt.c"
	.text
..TXTST0:
# -- Begin  jacobi2D5pt
	.text
# mark_begin;
       .align    16,0x90
	.globl jacobi2D5pt
# --- jacobi2D5pt(int, int)
jacobi2D5pt:
# parameter 1: %edi
# parameter 2: %esi
..B1.1:                         # Preds ..B1.0
                                # Execution count [1.00e+00]
	.cfi_startproc
..___tag_value_jacobi2D5pt.1:
..L2:
                                                          #2.31
        pushq     %rbx                                          #2.31
	.cfi_def_cfa_offset 16
        movq      %rsp, %rbx                                    #2.31
	.cfi_def_cfa 3, 16
	.cfi_offset 3, -16
        andq      $-32, %rsp                                    #2.31
        pushq     %rbp                                          #2.31
        pushq     %rbp                                          #2.31
        movq      8(%rbx), %rbp                                 #2.31
        movq      %rbp, 8(%rsp)                                 #2.31
        movq      %rsp, %rbp                                    #2.31
	.cfi_escape 0x10, 0x06, 0x02, 0x76, 0x00
        pushq     %r13                                          #2.31
        pushq     %r14                                          #2.31
        pushq     %r15                                          #2.31
        subq      $88, %rsp                                     #2.31
        movslq    %esi, %rsi                                    #2.31
        movslq    %edi, %rcx                                    #2.31
	.cfi_escape 0x10, 0x0d, 0x02, 0x76, 0x78
	.cfi_escape 0x10, 0x0e, 0x02, 0x76, 0x70
	.cfi_escape 0x10, 0x0f, 0x02, 0x76, 0x68
        movq      %rsi, %r13                                    #4.17
        imulq     %rcx, %r13                                    #4.17
        shlq      $3, %r13                                      #4.12
        movq      %r13, %rax                                    #4.12
        addq      $31, %rax                                     #4.12
        andq      $-32, %rax                                    #4.12
        subq      %rax, %rsp                                    #4.12
        movq      %rsp, %rax                                    #4.12
                                # LOE rax rcx rsi r12 r13 edi
..B1.29:                        # Preds ..B1.1
                                # Execution count [1.00e+00]
        movq      %rax, %r14                                    #4.12
                                # LOE rcx rsi r12 r13 r14 edi
..B1.2:                         # Preds ..B1.29
                                # Execution count [1.00e+00]
        movq      %r13, %rax                                    #5.12
        addq      $31, %rax                                     #5.12
        andq      $-32, %rax                                    #5.12
        subq      %rax, %rsp                                    #5.12
        movq      %rsp, %rax                                    #5.12
                                # LOE rax rcx rsi r12 r13 r14 edi
..B1.30:                        # Preds ..B1.2
                                # Execution count [1.00e+00]
        movq      %rax, %r15                                    #5.12
                                # LOE rcx rsi r12 r13 r14 r15 edi
..B1.3:                         # Preds ..B1.30
                                # Execution count [1.00e+00]
        xorl      %r10d, %r10d                                  #9.5
        lea       (%r15,%rcx,8), %r11                           #13.13
        vxorpd    %xmm1, %xmm1, %xmm1                           #6.5
        lea       (%r14,%rcx,8), %rdx                           #13.37
        cmpq      $2, %rsi                                      #9.18
        jle       ..B1.21       # Prob 9%                       #9.18
                                # LOE rdx rcx rsi r10 r11 r12 r13 r14 r15 edi xmm1
..B1.4:                         # Preds ..B1.3
                                # Execution count [9.00e-01]
        addl      $-2, %edi                                     #12.9
        movq      %rcx, %r9                                     #13.61
        movl      %edi, %eax                                    #12.9
        addq      $-2, %rsi                                     #9.18
        andl      $-16, %eax                                    #12.9
        xorl      %r8d, %r8d                                    #9.5
        shlq      $4, %r9                                       #13.61
        movslq    %eax, %rax                                    #12.9
        addq      %r14, %r9                                     #13.61
        movslq    %edi, %rdi                                    #12.9
        vxorps    %ymm0, %ymm0, %ymm0                           #6.5
        movq      %rax, -80(%rbp)                               #12.9[spill]
        movq      %rdi, -88(%rbp)                               #12.9[spill]
        movl      %eax, -72(%rbp)                               #9.5[spill]
        movq      %rsi, -48(%rbp)                               #9.5[spill]
        movq      %rdx, -64(%rbp)                               #9.5[spill]
        movq      %r15, -96(%rbp)                               #9.5[spill]
        movq      %r14, -56(%rbp)                               #9.5[spill]
        movq      %r13, -104(%rbp)                              #9.5[spill]
        movq      %r12, -112(%rbp)                              #9.5[spill]
	.cfi_escape 0x10, 0x0c, 0x03, 0x76, 0x90, 0x7f
                                # LOE rcx r8 r9 r10 r11 edi xmm1 ymm0
..B1.5:                         # Preds ..B1.19 ..B1.4
                                # Execution count [5.00e+00]
        cmpq      $2, %rcx                                      #12.22
        jle       ..B1.19       # Prob 50%                      #12.22
                                # LOE rcx r8 r9 r10 r11 edi xmm1 ymm0
..B1.6:                         # Preds ..B1.5
                                # Execution count [4.50e+00]
        cmpl      $16, %edi                                     #12.9
        jl        ..B1.26       # Prob 10%                      #12.9
                                # LOE rcx r8 r9 r10 r11 edi xmm1 ymm0
..B1.7:                         # Preds ..B1.6
                                # Execution count [4.50e+00]
        movl      -72(%rbp), %r14d                              #12.9[spill]
        xorl      %edx, %edx                                    #12.9
        movq      -80(%rbp), %r12                               #13.13[spill]
        lea       (%r11,%r8), %rax                              #13.13
                                # LOE rax rdx rcx r8 r9 r10 r11 r12 edi r14d xmm1 ymm0
..B1.8:                         # Preds ..B1.8 ..B1.7
                                # Execution count [2.50e+01]
        vmovupd   %ymm0, 8(%rax,%rdx,8)                         #13.13
        vmovupd   %ymm0, 40(%rax,%rdx,8)                        #13.13
        vmovupd   %ymm0, 72(%rax,%rdx,8)                        #13.13
        vmovupd   %ymm0, 104(%rax,%rdx,8)                       #13.13
        addq      $16, %rdx                                     #12.9
        cmpq      %r12, %rdx                                    #12.9
        jb        ..B1.8        # Prob 82%                      #12.9
                                # LOE rax rdx rcx r8 r9 r10 r11 r12 edi r14d xmm1 ymm0
..B1.10:                        # Preds ..B1.8 ..B1.26
                                # Execution count [5.00e+00]
        lea       1(%r14), %eax                                 #12.9
        cmpl      %edi, %eax                                    #12.9
        ja        ..B1.19       # Prob 50%                      #12.9
                                # LOE rcx r8 r9 r10 r11 edi r14d xmm1 ymm0
..B1.11:                        # Preds ..B1.10
                                # Execution count [4.50e+00]
        movslq    %r14d, %r14                                   #12.9
        movq      -88(%rbp), %r13                               #12.9[spill]
        subq      %r14, %r13                                    #12.9
        cmpq      $4, %r13                                      #12.9
        jl        ..B1.25       # Prob 10%                      #12.9
                                # LOE rcx r8 r9 r10 r11 r13 r14 edi xmm1 ymm0
..B1.12:                        # Preds ..B1.11
                                # Execution count [4.50e+00]
        movl      %r13d, %r15d                                  #12.9
        lea       (%r11,%r8), %rax                              #13.13
        andl      $-4, %r15d                                    #12.9
        xorl      %edx, %edx                                    #12.9
        movslq    %r15d, %r15                                   #12.9
        lea       (%rax,%r14,8), %rax                           #13.13
                                # LOE rax rdx rcx r8 r9 r10 r11 r13 r14 r15 edi xmm1 ymm0
..B1.13:                        # Preds ..B1.13 ..B1.12
                                # Execution count [2.50e+01]
        vmovupd   %ymm0, 8(%rax,%rdx,8)                         #13.13
        addq      $4, %rdx                                      #12.9
        cmpq      %r15, %rdx                                    #12.9
        jb        ..B1.13       # Prob 82%                      #12.9
                                # LOE rax rdx rcx r8 r9 r10 r11 r13 r14 r15 edi xmm1 ymm0
..B1.15:                        # Preds ..B1.13 ..B1.25
                                # Execution count [5.00e+00]
        cmpq      %r13, %r15                                    #12.9
        jae       ..B1.19       # Prob 10%                      #12.9
                                # LOE rcx r8 r9 r10 r11 r13 r14 r15 edi xmm1 ymm0
..B1.16:                        # Preds ..B1.15
                                # Execution count [4.50e+00]
        movq      -56(%rbp), %rax                               #13.49[spill]
        lea       (%r11,%r8), %r12                              #13.13
        movq      -64(%rbp), %rsi                               #13.25[spill]
        lea       (%r9,%r8), %rdx                               #13.61
        lea       (%r12,%r14,8), %r12                           #13.13
        addq      %r8, %rax                                     #13.49
        addq      %r8, %rsi                                     #13.25
        lea       (%rdx,%r14,8), %rdx                           #13.61
        lea       (%rax,%r14,8), %rax                           #13.49
        lea       (%rsi,%r14,8), %r14                           #13.25
                                # LOE rax rdx rcx r8 r9 r10 r11 r12 r13 r14 r15 edi xmm1 ymm0
        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.17:                        # Preds ..B1.17 ..B1.16
                                # Execution count [2.50e+01]
        vmovsd    (%r14,%r15,8), %xmm2                          #13.25
        vaddsd    16(%r14,%r15,8), %xmm2, %xmm3                 #13.37
        vaddsd    8(%rax,%r15,8), %xmm3, %xmm4                  #13.49
        vaddsd    8(%rdx,%r15,8), %xmm4, %xmm5                  #13.61
        vmulsd    %xmm5, %xmm1, %xmm6                           #13.74
        vmovsd    %xmm6, 8(%r12,%r15,8)                         #13.13
        incq      %r15                                          #12.9
        cmpq      %r13, %r15                                    #12.9
        jb        ..B1.17       # Prob 82%                      #12.9
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
                                # LOE rax rdx rcx r8 r9 r10 r11 r12 r13 r14 r15 edi xmm1 ymm0
..B1.19:                        # Preds ..B1.17 ..B1.5 ..B1.10 ..B1.15
                                # Execution count [5.00e+00]
        incq      %r10                                          #9.5
        lea       (%r8,%rcx,8), %r8                             #9.5
        cmpq      -48(%rbp), %r10                               #9.5[spill]
        jb        ..B1.5        # Prob 82%                      #9.5
                                # LOE rcx r8 r9 r10 r11 edi xmm1 ymm0
..B1.20:                        # Preds ..B1.19
                                # Execution count [9.00e-01]
        movq      -64(%rbp), %rdx                               #[spill]
        movq      -96(%rbp), %r15                               #[spill]
        movq      -56(%rbp), %r14                               #[spill]
        movq      -104(%rbp), %r13                              #[spill]
        movq      -112(%rbp), %r12                              #[spill]
	.cfi_restore 12
                                # LOE rdx r11 r12 r13 r14 r15
..B1.21:                        # Preds ..B1.3 ..B1.20
                                # Execution count [1.00e+00]
        addq      $8, %rdx                                      #16.5
        addq      $8, %r11                                      #16.5
        movq      %rdx, %rdi                                    #16.5
        movq      %r11, %rsi                                    #16.5
        vzeroupper                                              #16.5
..___tag_value_jacobi2D5pt.12:
#       dummy(double *, double *)
        call      dummy                                         #16.5
..___tag_value_jacobi2D5pt.13:
                                # LOE r12 r13 r14 r15
..B1.22:                        # Preds ..B1.21
                                # Execution count [1.00e+00]
        movq      %r15, %rdx                                    #16.5
        movq      %r13, %rax                                    #16.5
        addq      $31, %rax                                     #16.5
        andq      $-32, %rax                                    #16.5
        addq      %rax, %rsp                                    #16.5
                                # LOE r12 r13 r14
..B1.23:                        # Preds ..B1.22
                                # Execution count [1.00e+00]
        movq      %r14, %rdx                                    #16.5
        movq      %r13, %rax                                    #16.5
        addq      $31, %rax                                     #16.5
        andq      $-32, %rax                                    #16.5
        addq      %rax, %rsp                                    #16.5
                                # LOE r12
..B1.24:                        # Preds ..B1.23
                                # Execution count [1.00e+00]
        lea       -24(%rbp), %rsp                               #17.1
	.cfi_restore 15
        popq      %r15                                          #17.1
	.cfi_restore 14
        popq      %r14                                          #17.1
	.cfi_restore 13
        popq      %r13                                          #17.1
        popq      %rbp                                          #17.1
	.cfi_restore 6
        movq      %rbx, %rsp                                    #17.1
        popq      %rbx                                          #17.1
	.cfi_def_cfa 7, 8
	.cfi_restore 3
        ret                                                     #17.1
	.cfi_def_cfa 3, 16
	.cfi_offset 3, -16
	.cfi_escape 0x10, 0x06, 0x02, 0x76, 0x00
	.cfi_escape 0x10, 0x0c, 0x03, 0x76, 0x90, 0x7f
	.cfi_escape 0x10, 0x0d, 0x02, 0x76, 0x78
	.cfi_escape 0x10, 0x0e, 0x02, 0x76, 0x70
	.cfi_escape 0x10, 0x0f, 0x02, 0x76, 0x68
                                # LOE
..B1.25:                        # Preds ..B1.11
                                # Execution count [4.50e-01]: Infreq
        xorl      %r15d, %r15d                                  #12.9
        jmp       ..B1.15       # Prob 100%                     #12.9
                                # LOE rcx r8 r9 r10 r11 r13 r14 r15 edi xmm1 ymm0
..B1.26:                        # Preds ..B1.6
                                # Execution count [4.50e-01]: Infreq
        xorl      %r14d, %r14d                                  #12.9
        jmp       ..B1.10       # Prob 100%                     #12.9
        .align    16,0x90
                                # LOE rcx r8 r9 r10 r11 edi r14d xmm1 ymm0
	.cfi_endproc
# mark_end;
	.type	jacobi2D5pt,@function
	.size	jacobi2D5pt,.-jacobi2D5pt
	.data
# -- End  jacobi2D5pt
	.data
	.section .note.GNU-stack, ""
// -- Begin DWARF2 SEGMENT .eh_frame
	.section .eh_frame,"a",@progbits
.eh_frame_seg:
	.align 8
# End
