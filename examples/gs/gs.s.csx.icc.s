# mark_description "Intel(R) Fortran Intel(R) 64 Compiler for applications running on Intel(R) 64, Version 19.0.5.281 Build 2019";
# mark_description "0815";
# mark_description "-qopenmp-simd -fno-alias -unroll -fno-builtin -xCORE-AVX512 -qopt-zmm-usage=high -Ofast -S -use-msasm -o gs.";
# mark_description "s.csx.icc.s";
	.file "gs.f90"
	.text
..TXTST0:
.L_2__routine_start_MAIN___0:
# -- Begin  MAIN__
	.text
# mark_begin;
       .align    16,0x90
	.globl MAIN__
# --- HEAT
MAIN__:
..B1.1:                         # Preds ..B1.0
                                # Execution count [1.00e+00]
	.cfi_startproc
..___tag_value_MAIN__.1:
..L2:
                                                          #1.9
        pushq     %rbp                                          #1.9
	.cfi_def_cfa_offset 16
        movq      %rsp, %rbp                                    #1.9
	.cfi_def_cfa 6, 16
	.cfi_offset 6, -16
        andq      $-128, %rsp                                   #1.9
        pushq     %r12                                          #1.9
        pushq     %r13                                          #1.9
        pushq     %r14                                          #1.9
        pushq     %r15                                          #1.9
        pushq     %rbx                                          #1.9
        subq      $216, %rsp                                    #1.9
        movq      $0x64199d9ffe, %rsi                           #1.9
        movl      $3, %edi                                      #1.9
        call      __intel_new_feature_proc_init                 #1.9
	.cfi_escape 0x10, 0x03, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xd8, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0c, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xf8, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0d, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xf0, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0e, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xe8, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0f, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xe0, 0xff, 0xff, 0xff, 0x22
                                # LOE
..B1.95:                        # Preds ..B1.1
                                # Execution count [1.00e+00]
        vstmxcsr  (%rsp)                                        #1.9
        movl      $__NLITPACK_0.0.1, %edi                       #1.9
        xorl      %eax, %eax                                    #1.9
        orl       $32832, (%rsp)                                #1.9
        vldmxcsr  (%rsp)                                        #1.9
..___tag_value_MAIN__.11:
        call      for_set_reentrancy                            #1.9
..___tag_value_MAIN__.12:
                                # LOE
..B1.2:                         # Preds ..B1.95
                                # Execution count [1.00e+00]
        movl      $-4, %esi                                     #12.3
        lea       152(%rsp), %rax                               #12.3
        movq      %rax, -24(%rax)                               #12.3
        lea       (%rsp), %rdi                                  #12.3
        movq      $0x1208384ff00, %rdx                          #12.3
        movl      $__STRLITPACK_3.0.1, %ecx                     #12.3
        xorl      %eax, %eax                                    #12.3
        lea       128(%rsp), %r8                                #12.3
        movq      $0, (%rdi)                                    #12.3
..___tag_value_MAIN__.13:
        call      for_read_seq_lis                              #12.3
..___tag_value_MAIN__.14:
                                # LOE
..B1.3:                         # Preds ..B1.2
                                # Execution count [1.00e+00]
        movl      $__STRLITPACK_4.0.1, %esi                     #12.3
        lea       156(%rsp), %rax                               #12.3
        movq      %rax, -20(%rax)                               #12.3
        lea       (%rsp), %rdi                                  #12.3
        xorl      %eax, %eax                                    #12.3
        lea       136(%rsp), %rdx                               #12.3
..___tag_value_MAIN__.15:
        call      for_read_seq_lis_xmit                         #12.3
..___tag_value_MAIN__.16:
                                # LOE
..B1.4:                         # Preds ..B1.3
                                # Execution count [1.00e+00]
        movq      24+heat_$PHI.0.1(%rip), %r9                   #15.3
        movq      %r9, %r10                                     #15.3
        andq      $-256, %r10                                   #15.3
        movq      $0xf000000000, %r12                           #15.3
        shrq      $8, %r10                                      #15.3
        andq      %r12, %r9                                     #15.3
        movl      152(%rsp), %r14d                              #14.3
        movq      $0xffffff0fffffffff, %rbx                     #15.3
        movslq    %r14d, %r12                                   #15.3
        xorl      %esi, %esi                                    #15.3
        shlq      $63, %r10                                     #15.3
        movq      %r12, %r15                                    #15.3
        shrq      $55, %r10                                     #15.3
        movl      $8, %r11d                                     #15.3
        addq      $133, %r10                                    #15.3
        sarq      $63, %r15                                     #15.3
        andq      %rbx, %r10                                    #15.3
        movl      156(%rsp), %r13d                              #13.3
        lea       1(%r12), %rbx                                 #15.3
        andn      %rbx, %r15, %rdx                              #15.3
        movslq    %r13d, %rbx                                   #15.3
        movq      %rbx, %rdi                                    #15.3
        sarq      $63, %rdi                                     #15.3
        shrq      $36, %r9                                      #15.3
        lea       (,%rdx,8), %r8                                #15.3
        movq      %r8, 80+heat_$PHI.0.1(%rip)                   #15.3
        lea       1(%rbx), %rax                                 #15.3
        andn      %rax, %rdi, %rcx                              #15.3
        lea       144(%rsp), %rdi                               #15.3
        imulq     %rcx, %r8                                     #15.3
        shlq      $60, %r9                                      #15.3
        xorl      %eax, %eax                                    #15.3
        shrq      $24, %r9                                      #15.3
        movq      %rsi, 16+heat_$PHI.0.1(%rip)                  #15.3
        orq       %r9, %r10                                     #15.3
        movq      %rsi, 64+heat_$PHI.0.1(%rip)                  #15.3
        movq      %rsi, 88+heat_$PHI.0.1(%rip)                  #15.3
        movl      $3, %esi                                      #15.3
        movq      %r8, 104+heat_$PHI.0.1(%rip)                  #15.3
        movl      $16, %r8d                                     #15.3
        movq      %r10, 24+heat_$PHI.0.1(%rip)                  #15.3
        movq      %r11, 8+heat_$PHI.0.1(%rip)                   #15.3
        movq      $3, 32+heat_$PHI.0.1(%rip)                    #15.3
        movq      %r11, 56+heat_$PHI.0.1(%rip)                  #15.3
        movq      %rdx, 48+heat_$PHI.0.1(%rip)                  #15.3
        movq      $1, 112+heat_$PHI.0.1(%rip)                   #15.3
        movq      $2, 96+heat_$PHI.0.1(%rip)                    #15.3
        movq      %rcx, 72+heat_$PHI.0.1(%rip)                  #15.3
..___tag_value_MAIN__.17:
        call      for_check_mult_overflow64                     #15.3
..___tag_value_MAIN__.18:
                                # LOE rbx r12 eax r13d r14d
..B1.5:                         # Preds ..B1.4
                                # Execution count [1.00e+00]
        movq      $0xfffffff00fffffff, %r8                      #15.3
        movq      $0xf000000000, %rcx                           #15.3
        andq      24+heat_$PHI.0.1(%rip), %r8                   #15.3
        andl      $1, %eax                                      #15.3
        addq      $1073741824, %r8                              #15.3
        movl      $heat_$PHI.0.1, %esi                          #15.3
        movq      %r8, 24+heat_$PHI.0.1(%rip)                   #15.3
        andq      %r8, %rcx                                     #15.3
        movl      %r8d, %edx                                    #15.3
        andq      $-256, %r8                                    #15.3
        shrq      $8, %r8                                       #15.3
        andl      $1, %edx                                      #15.3
        shll      $4, %eax                                      #15.3
        addl      %edx, %edx                                    #15.3
        andl      $1, %r8d                                      #15.3
        orl       %eax, %edx                                    #15.3
        shll      $21, %r8d                                     #15.3
        xorl      %eax, %eax                                    #15.3
        shrq      $36, %rcx                                     #15.3
        orl       %r8d, %edx                                    #15.3
        andl      $-31457281, %edx                              #15.3
        shll      $21, %ecx                                     #15.3
        orl       %ecx, %edx                                    #15.3
        addl      $262144, %edx                                 #15.3
        movq      144(%rsp), %rdi                               #15.3
..___tag_value_MAIN__.19:
        call      for_alloc_allocatable                         #15.3
..___tag_value_MAIN__.20:
                                # LOE rbx r12 r13d r14d
..B1.6:                         # Preds ..B1.5
                                # Execution count [1.00e+00]
        xorl      %r8d, %r8d                                    #21.3
        lea       -1(%r13), %eax                                #21.3
        movl      %eax, 96(%rsp)                                #21.3[spill]
        testl     %eax, %eax                                    #21.3
        jle       ..B1.31       # Prob 2%                       #21.3
                                # LOE rbx r8 r12 r13d r14d
..B1.7:                         # Preds ..B1.6
                                # Execution count [9.79e-01]
        movq      heat_$PHI.0.1(%rip), %r9                      #23.9
        lea       -1(%r14), %r15d                               #22.6
        movq      104+heat_$PHI.0.1(%rip), %rcx                 #23.9
        lea       -1(%rbx), %r11                                #21.3
        movq      80+heat_$PHI.0.1(%rip), %r10                  #23.9
        xorl      %edx, %edx                                    #21.3
        movslq    %r15d, %rdi                                   #22.6
        vmovdqu   .L_2il0floatpacket.0(%rip), %ymm2             #22.6
        lea       (%r9,%rcx,2), %rsi                            #24.9
        vmovdqu   .L_2il0floatpacket.1(%rip), %ymm0             #22.6
        movl      %r14d, 104(%rsp)                              #21.3[spill]
        movq      %rbx, 112(%rsp)                               #21.3[spill]
        movq      %r12, 120(%rsp)                               #21.3[spill]
        movl      %r13d, 64(%rsp)                               #21.3[spill]
        vpxord    %zmm1, %zmm1, %zmm1                           #23.9
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r15d ymm0 ymm2 zmm1
..B1.8:                         # Preds ..B1.29 ..B1.7
                                # Execution count [5.00e+00]
        testl     %r15d, %r15d                                  #22.6
        jle       ..B1.29       # Prob 50%                      #22.6
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r15d ymm0 ymm2 zmm1
..B1.9:                         # Preds ..B1.8
                                # Execution count [4.89e+00]
        movq      %rdi, 72(%rsp)                                #[spill]
        movq      %r11, 80(%rsp)                                #[spill]
                                # LOE rdx rcx rsi r8 r9 r10 r15d ymm0 ymm2 zmm1
..B1.10:                        # Preds ..B1.90 ..B1.9
                                # Execution count [5.33e+00]
        cmpl      $16, %r15d                                    #22.6
        jl        ..B1.92       # Prob 10%                      #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r15d ymm0 ymm2 zmm1
..B1.11:                        # Preds ..B1.10
                                # Execution count [5.33e+00]
        movq      %r10, %r12                                    #24.9
        subq      %rcx, %r12                                    #24.9
        lea       8(%r12,%rsi), %rbx                            #22.6
        addq      %rdx, %rbx                                    #22.6
        andq      $63, %rbx                                     #22.6
        testb     $7, %bl                                       #22.6
        je        ..B1.13       # Prob 50%                      #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r12 ebx r15d ymm0 ymm2 zmm1
..B1.12:                        # Preds ..B1.11
                                # Execution count [2.66e+00]
        xorl      %ebx, %ebx                                    #22.6
        jmp       ..B1.15       # Prob 100%                     #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r12 ebx r15d ymm0 ymm2 zmm1
..B1.13:                        # Preds ..B1.11
                                # Execution count [2.66e+00]
        testl     %ebx, %ebx                                    #22.6
        je        ..B1.15       # Prob 50%                      #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r12 ebx r15d ymm0 ymm2 zmm1
..B1.14:                        # Preds ..B1.13
                                # Execution count [2.96e+01]
        negl      %ebx                                          #22.6
        addl      $64, %ebx                                     #22.6
        shrl      $3, %ebx                                      #22.6
        cmpl      %ebx, %r15d                                   #22.6
        cmovl     %r15d, %ebx                                   #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r12 ebx r15d ymm0 ymm2 zmm1
..B1.15:                        # Preds ..B1.12 ..B1.14 ..B1.13
                                # Execution count [5.44e+00]
        movl      %r15d, %eax                                   #22.6
        subl      %ebx, %eax                                    #22.6
        andl      $15, %eax                                     #22.6
        negl      %eax                                          #22.6
        addl      %r15d, %eax                                   #22.6
        cmpl      $1, %ebx                                      #22.6
        jb        ..B1.20       # Prob 50%                      #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r12 eax ebx r15d ymm0 ymm2 zmm1
..B1.17:                        # Preds ..B1.15
                                # Execution count [5.33e+00]
        vmovdqa   %ymm2, %ymm4                                  #22.6
        lea       (%r12,%rcx,2), %r13                           #24.9
        addq      %r9, %r13                                     #24.9
        lea       (%r10,%r9), %r11                              #23.9
        vpbroadcastd %ebx, %ymm3                                #22.6
        xorl      %r14d, %r14d                                  #22.6
        movslq    %ebx, %rdi                                    #22.6
        addq      %rdx, %r13                                    #24.9
        addq      %rdx, %r11                                    #23.9
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r12 r13 r14 eax ebx r15d ymm0 ymm2 ymm3 ymm4 zmm1
..B1.18:                        # Preds ..B1.18 ..B1.17
                                # Execution count [2.96e+01]
        vpcmpgtd  %ymm4, %ymm3, %k1                             #22.6
        vpaddd    %ymm0, %ymm4, %ymm4                           #22.6
        vmovupd   %zmm1, 8(%r11,%r14,8){%k1}                    #23.9
        vmovupd   %zmm1, 8(%r13,%r14,8){%k1}                    #24.9
        addq      $8, %r14                                      #22.6
        cmpq      %rdi, %r14                                    #22.6
        jb        ..B1.18       # Prob 82%                      #22.6
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r12 r13 r14 eax ebx r15d ymm0 ymm2 ymm3 ymm4 zmm1
..B1.19:                        # Preds ..B1.18
                                # Execution count [5.33e+00]
        cmpl      %ebx, %r15d                                   #22.6
        je        ..B1.90       # Prob 10%                      #22.6
                                # LOE rdx rcx rsi r8 r9 r10 r12 eax ebx r15d ymm0 ymm2 zmm1
..B1.20:                        # Preds ..B1.15 ..B1.19
                                # Execution count [4.79e+00]
        movq      72(%rsp), %rdi                                #[spill]
        movq      80(%rsp), %r11                                #[spill]
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r12 eax ebx r15d ymm0 ymm2 zmm1
..B1.21:                        # Preds ..B1.20
                                # Execution count [2.96e+01]
        lea       16(%rbx), %r13d                               #22.6
        cmpl      %r13d, %eax                                   #22.6
        jl        ..B1.25       # Prob 50%                      #22.6
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r12 eax ebx r15d ymm0 ymm2 zmm1
..B1.22:                        # Preds ..B1.21
                                # Execution count [5.33e+00]
        movslq    %ebx, %rbx                                    #22.6
        lea       (%r12,%rcx,2), %r14                           #24.9
        addq      %r9, %r14                                     #24.9
        lea       (%r10,%r9), %r13                              #23.9
        movslq    %eax, %r12                                    #22.6
        addq      %rdx, %r14                                    #24.9
        addq      %rdx, %r13                                    #23.9
                                # LOE rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r13 r14 eax r15d ymm0 ymm2 zmm1
..B1.23:                        # Preds ..B1.23 ..B1.22
                                # Execution count [2.96e+01]
        vmovupd   %zmm1, 8(%r13,%rbx,8)                         #23.9
        vmovupd   %zmm1, 8(%r14,%rbx,8)                         #24.9
        vmovupd   %zmm1, 72(%r13,%rbx,8)                        #23.9
        vmovupd   %zmm1, 72(%r14,%rbx,8)                        #24.9
        addq      $16, %rbx                                     #22.6
        cmpq      %r12, %rbx                                    #22.6
        jb        ..B1.23       # Prob 82%                      #22.6
                                # LOE rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r13 r14 eax r15d ymm0 ymm2 zmm1
..B1.25:                        # Preds ..B1.23 ..B1.21 ..B1.92
                                # Execution count [5.44e+00]
        lea       1(%rax), %ebx                                 #22.6
        cmpl      %r15d, %ebx                                   #22.6
        ja        ..B1.29       # Prob 50%                      #22.6
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 eax r15d ymm0 ymm2 zmm1
..B1.26:                        # Preds ..B1.25
                                # Execution count [5.33e+00]
        movq      %r10, %rbx                                    #23.9
        lea       (%rcx,%r9), %r14                              #23.9
        subq      %rcx, %rbx                                    #23.9
        xorl      %r13d, %r13d                                  #22.6
        movslq    %eax, %r12                                    #23.9
        negl      %eax                                          #22.6
        addl      %r15d, %eax                                   #22.6
        vpbroadcastd %eax, %ymm3                                #22.6
        vmovdqa   %ymm2, %ymm4                                  #22.6
        lea       (%rsi,%rbx), %rax                             #24.9
        addq      %r14, %rbx                                    #23.9
        addq      %rdx, %rax                                    #24.9
        addq      %rdx, %rbx                                    #23.9
        lea       (%rax,%r12,8), %rax                           #24.9
        lea       (%rbx,%r12,8), %rbx                           #23.9
        negq      %r12                                          #22.6
        addq      %rdi, %r12                                    #22.6
                                # LOE rax rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r13 r15d ymm0 ymm2 ymm3 ymm4 zmm1
..B1.27:                        # Preds ..B1.27 ..B1.26
                                # Execution count [2.96e+01]
        vpcmpgtd  %ymm4, %ymm3, %k1                             #22.6
        vpaddd    %ymm0, %ymm4, %ymm4                           #22.6
        vmovupd   %zmm1, 8(%rbx,%r13,8){%k1}                    #23.9
        vmovupd   %zmm1, 8(%rax,%r13,8){%k1}                    #24.9
        addq      $8, %r13                                      #22.6
        cmpq      %r12, %r13                                    #22.6
        jb        ..B1.27       # Prob 82%                      #22.6
                                # LOE rax rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r13 r15d ymm0 ymm2 ymm3 ymm4 zmm1
..B1.29:                        # Preds ..B1.27 ..B1.8 ..B1.25
                                # Execution count [4.91e+00]
        incq      %r8                                           #21.3
        addq      %r10, %rdx                                    #21.3
        cmpq      %r11, %r8                                     #21.3
        jb        ..B1.8        # Prob 82%                      #21.3
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 r15d ymm0 ymm2 zmm1
..B1.30:                        # Preds ..B1.90 ..B1.29
                                # Execution count [8.83e-01]
        movl      104(%rsp), %r14d                              #[spill]
        movq      112(%rsp), %rbx                               #[spill]
        movq      120(%rsp), %r12                               #[spill]
        movl      64(%rsp), %r13d                               #[spill]
                                # LOE rbx r12 r13d r14d
..B1.31:                        # Preds ..B1.6 ..B1.30
                                # Execution count [1.00e+00]
        xorl      %eax, %eax                                    #29.3
        testl     %r14d, %r14d                                  #29.3
        jl        ..B1.40       # Prob 50%                      #29.3
                                # LOE rbx r12 eax r13d r14d
..B1.32:                        # Preds ..B1.31
                                # Execution count [4.35e-01]
        movq      80+heat_$PHI.0.1(%rip), %r8                   #30.6
        lea       1(%r14), %edx                                 #14.3
        movq      104+heat_$PHI.0.1(%rip), %rdi                 #30.6
        movq      heat_$PHI.0.1(%rip), %rcx                     #30.6
        cmpl      $8, %edx                                      #29.3
        jl        ..B1.89       # Prob 10%                      #29.3
                                # LOE rcx rbx rdi r8 r12 eax edx r13d r14d
..B1.33:                        # Preds ..B1.32
                                # Execution count [4.35e-01]
        movq      %rbx, %r10                                    #30.6
        movq      %rcx, %rax                                    #31.6
        imulq     %r8, %r10                                     #30.6
        vmovupd   .L_2il0floatpacket.2(%rip), %ymm1             #30.6
        subq      %rdi, %rax                                    #31.6
        movl      %edx, %esi                                    #29.3
        andl      $-8, %esi                                     #29.3
        subq      %rdi, %r10                                    #30.6
        vxorpd    %ymm0, %ymm0, %ymm0                           #31.6
        lea       (%rdi,%rcx), %r9                              #30.6
        xorl      %r11d, %r11d                                  #29.3
        lea       (%rcx,%rdi,2), %r15                           #30.6
        addq      %r10, %r9                                     #30.6
        lea       (%rax,%rdi,2), %rax                           #31.6
        addq      %r15, %r10                                    #30.6
        movslq    %esi, %r15                                    #29.3
                                # LOE rax rcx rbx rdi r8 r9 r10 r11 r12 r15 edx esi r13d r14d ymm0 ymm1
..B1.34:                        # Preds ..B1.34 ..B1.33
                                # Execution count [4.90e+00]
        vmovupd   %ymm1, (%r9,%r11,8)                           #30.6
        vmovupd   %ymm0, (%rcx,%r11,8)                          #31.6
        vmovupd   %ymm1, (%r10,%r11,8)                          #30.6
        vmovupd   %ymm0, (%rax,%r11,8)                          #31.6
        vmovupd   %ymm1, 32(%r9,%r11,8)                         #30.6
        vmovupd   %ymm0, 32(%rcx,%r11,8)                        #31.6
        vmovupd   %ymm1, 32(%r10,%r11,8)                        #30.6
        vmovupd   %ymm0, 32(%rax,%r11,8)                        #31.6
        addq      $8, %r11                                      #29.3
        cmpq      %r15, %r11                                    #29.3
        jb        ..B1.34       # Prob 91%                      #29.3
                                # LOE rax rcx rbx rdi r8 r9 r10 r11 r12 r15 edx esi r13d r14d ymm0 ymm1
..B1.35:                        # Preds ..B1.34
                                # Execution count [4.35e-01]
        movl      %esi, %eax                                    #32.3
                                # LOE rcx rbx rdi r8 r12 eax edx esi r13d r14d
..B1.36:                        # Preds ..B1.35 ..B1.89
                                # Execution count [1.00e+00]
        lea       1(%rsi), %r9d                                 #29.3
        cmpl      %edx, %r9d                                    #29.3
        ja        ..B1.40       # Prob 50%                      #29.3
                                # LOE rcx rbx rdi r8 r12 eax edx esi r13d r14d
..B1.37:                        # Preds ..B1.36
                                # Execution count [4.35e-01]
        imulq     %rbx, %r8                                     #30.6
        vmovupd   .L_2il0floatpacket.2(%rip), %ymm2             #30.6
        vmovdqu   .L_2il0floatpacket.5(%rip), %xmm4             #29.3
        vmovdqu   .L_2il0floatpacket.6(%rip), %xmm3             #29.3
        movq      %r8, %r9                                      #30.6
        movq      %rcx, %r11                                    #31.6
        subq      %rdi, %r9                                     #30.6
        subq      %rdi, %r11                                    #31.6
        addq      %rcx, %r8                                     #30.6
        xorl      %r10d, %r10d                                  #29.3
        vxorpd    %ymm1, %ymm1, %ymm1                           #31.6
        lea       (%r9,%rdi,2), %rax                            #30.6
        addq      %rcx, %rax                                    #30.6
        lea       (%r11,%rdi,2), %r15                           #31.6
        movslq    %esi, %rdi                                    #30.6
        negl      %esi                                          #29.3
        addl      %edx, %esi                                    #29.3
        vpbroadcastd %esi, %xmm0                                #29.3
        lea       (%rcx,%rdi,8), %r11                           #31.6
        movslq    %edx, %rcx                                    #29.3
        subq      %rdi, %rcx                                    #29.3
        lea       (%r15,%rdi,8), %r9                            #31.6
        lea       (%rax,%rdi,8), %rax                           #30.6
        lea       (%r8,%rdi,8), %r8                             #30.6
                                # LOE rax rcx rbx r8 r9 r10 r11 r12 edx r13d r14d xmm0 xmm3 xmm4 ymm1 ymm2
..B1.38:                        # Preds ..B1.38 ..B1.37
                                # Execution count [4.90e+00]
        vpcmpgtd  %xmm3, %xmm0, %k1                             #29.3
        vpaddd    %xmm4, %xmm3, %xmm3                           #29.3
        vmovupd   %ymm2, (%r8,%r10,8){%k1}                      #30.6
        vmovupd   %ymm1, (%r11,%r10,8){%k1}                     #31.6
        vmovupd   %ymm2, (%rax,%r10,8){%k1}                     #30.6
        vmovupd   %ymm1, (%r9,%r10,8){%k1}                      #31.6
        addq      $4, %r10                                      #29.3
        cmpq      %rcx, %r10                                    #29.3
        jb        ..B1.38       # Prob 91%                      #29.3
                                # LOE rax rcx rbx r8 r9 r10 r11 r12 edx r13d r14d xmm0 xmm3 xmm4 ymm1 ymm2
..B1.39:                        # Preds ..B1.38
                                # Execution count [4.35e-01]
        movl      %edx, %eax                                    #32.3
                                # LOE rbx r12 eax r13d r14d
..B1.40:                        # Preds ..B1.39 ..B1.36 ..B1.31
                                # Execution count [1.00e+00]
        testl     %r13d, %r13d                                  #33.3
        jl        ..B1.49       # Prob 50%                      #33.3
                                # LOE rbx r12 eax r13d r14d
..B1.41:                        # Preds ..B1.40
                                # Execution count [4.35e-01]
        movq      80+heat_$PHI.0.1(%rip), %r9                   #34.6
        incl      %r13d                                         #13.3
        movq      104+heat_$PHI.0.1(%rip), %r15                 #34.6
        movl      152(%rsp), %r11d                              #34.27
        movq      heat_$PHI.0.1(%rip), %r10                     #34.6
        testq     %r9, %r9                                      #55.82
        je        ..B1.79       # Prob 10%                      #55.82
                                # LOE rbx r9 r10 r12 r15 eax r11d r13d r14d
..B1.42:                        # Preds ..B1.41
                                # Execution count [4.35e-01]
        cmpl      $8, %r13d                                     #33.3
        jl        ..B1.78       # Prob 10%                      #33.3
                                # LOE rbx r9 r10 r12 r15 eax r11d r13d r14d
..B1.43:                        # Preds ..B1.42
                                # Execution count [4.35e-01]
        vxorpd    %xmm1, %xmm1, %xmm1                           #34.19
        vxorpd    %xmm0, %xmm0, %xmm0                           #34.27
        vcvtsi2sd %eax, %xmm1, %xmm1                            #34.19
        vcvtsi2sd %r11d, %xmm0, %xmm0                           #34.27
        vpbroadcastd %r9d, %zmm3                                #34.6
        vdivsd    %xmm0, %xmm1, %xmm2                           #34.6
        movq      %r10, %rsi                                    #34.6
        movl      %r13d, %r8d                                   #33.3
        subq      %r15, %rsi                                    #34.6
        andl      $-8, %r8d                                     #33.3
        movslq    %r8d, %r8                                     #33.3
        lea       (,%r12,8), %rdi                               #35.6
        xorl      %ecx, %ecx                                    #33.3
        subq      %r15, %rdi                                    #35.6
        movl      %r11d, 80(%rsp)                               #34.6[spill]
        lea       (%rsi,%r15,2), %rdx                           #34.6
        movq      %rdx, 64(%rsp)                                #34.6[spill]
        lea       (%r15,%r10), %rsi                             #35.6
        movl      %eax, 88(%rsp)                                #34.6[spill]
        lea       (%r10,%r15,2), %rdx                           #35.6
        vbroadcastsd %xmm2, %zmm1                               #34.6
        addq      %rdi, %rsi                                    #35.6
        vpmuldq   .L_2il0floatpacket.8(%rip), %zmm3, %zmm0      #34.6
        movq      %r15, 72(%rsp)                                #34.6[spill]
        addq      %rdx, %rdi                                    #35.6
        movq      %r8, %r11                                     #34.6
        xorl      %edx, %edx                                    #33.3
        movq      64(%rsp), %rax                                #34.6[spill]
        .align    16,0x90
                                # LOE rax rdx rcx rbx rsi rdi r9 r10 r11 r12 r8d r13d r14d zmm0 zmm1
..B1.44:                        # Preds ..B1.44 ..B1.43
                                # Execution count [4.90e+00]
        vpcmpeqb  %xmm0, %xmm0, %k1                             #34.6
        lea       (%r10,%rdx), %r15                             #34.6
        vpcmpeqb  %xmm0, %xmm0, %k2                             #35.6
        vpcmpeqb  %xmm0, %xmm0, %k3                             #34.6
        vpcmpeqb  %xmm0, %xmm0, %k4                             #35.6
        vscatterqpd %zmm1, (%r15,%zmm0){%k1}                    #34.6
        addq      $8, %rcx                                      #33.3
        lea       (%rsi,%rdx), %r15                             #35.6
        vscatterqpd %zmm1, (%r15,%zmm0){%k2}                    #35.6
        lea       (%rax,%rdx), %r15                             #34.6
        vscatterqpd %zmm1, (%r15,%zmm0){%k3}                    #34.6
        lea       (%rdi,%rdx), %r15                             #35.6
        vscatterqpd %zmm1, (%r15,%zmm0){%k4}                    #35.6
        lea       (%rdx,%r9,8), %rdx                            #33.3
        cmpq      %r11, %rcx                                    #33.3
        jb        ..B1.44       # Prob 91%                      #33.3
                                # LOE rax rdx rcx rbx rsi rdi r9 r10 r11 r12 r8d r13d r14d zmm0 zmm1
..B1.45:                        # Preds ..B1.44
                                # Execution count [4.35e-01]
        movq      72(%rsp), %r15                                #[spill]
        movl      80(%rsp), %r11d                               #[spill]
        movl      88(%rsp), %eax                                #[spill]
                                # LOE rbx r9 r10 r12 r15 eax r8d r11d r13d r14d
..B1.46:                        # Preds ..B1.45 ..B1.78
                                # Execution count [9.56e-01]
        lea       1(%r8), %edx                                  #33.3
        cmpl      %r13d, %edx                                   #33.3
        ja        ..B1.49       # Prob 50%                      #33.3
                                # LOE rbx r9 r10 r12 r15 eax r8d r11d r13d r14d
..B1.47:                        # Preds ..B1.46
                                # Execution count [4.35e-01]
        vxorpd    %xmm1, %xmm1, %xmm1                           #34.19
        vxorpd    %xmm2, %xmm2, %xmm2                           #34.27
        vcvtsi2sd %eax, %xmm1, %xmm1                            #34.19
        vcvtsi2sd %r11d, %xmm2, %xmm2                           #34.27
        vdivsd    %xmm2, %xmm1, %xmm3                           #34.6
        subl      %r8d, %r13d                                   #33.3
        movq      %r10, %rax                                    #34.6
        movslq    %r8d, %r8                                     #34.6
        lea       (,%r12,8), %rdi                               #35.6
        imulq     %r9, %r8                                      #34.6
        vpbroadcastd %r13d, %ymm0                               #33.3
        vpbroadcastd %r9d, %zmm4                                #34.6
        vbroadcastsd %xmm3, %zmm6                               #34.6
        vpcmpgtd  .L_2il0floatpacket.0(%rip), %ymm0, %k4        #33.3
        vpmuldq   .L_2il0floatpacket.8(%rip), %zmm4, %zmm5      #34.6
        subq      %r15, %rax                                    #34.6
        subq      %r15, %rdi                                    #35.6
        kmovw     %k4, %k1                                      #34.6
        lea       (%r15,%r10), %rcx                             #35.6
        addq      %rdi, %rcx                                    #35.6
        lea       (%r10,%r8), %rdx                              #34.6
        kmovw     %k4, %k2                                      #35.6
        lea       (%r10,%r15,2), %r10                           #35.6
        addq      %r10, %rdi                                    #35.6
        lea       (%rax,%r15,2), %rsi                           #34.6
        addq      %r8, %rcx                                     #35.6
        addq      %r8, %rsi                                     #34.6
        addq      %r8, %rdi                                     #35.6
        kmovw     %k4, %k3                                      #34.6
        vscatterqpd %zmm6, (%rdx,%zmm5){%k1}                    #34.6
        vscatterqpd %zmm6, (%rcx,%zmm5){%k2}                    #35.6
        vscatterqpd %zmm6, (%rsi,%zmm5){%k3}                    #34.6
        vscatterqpd %zmm6, (%rdi,%zmm5){%k4}                    #35.6
                                # LOE rbx r12 r14d
..B1.49:                        # Preds ..B1.79 ..B1.40 ..B1.80 ..B1.83 ..B1.47
                                #       ..B1.46
                                # Execution count [8.00e-01]
        decl      %r14d                                         #54.9
        decq      %rbx                                          #53.6
        movl      %r14d, %r13d                                  #54.9
        decq      %r12                                          #54.9
        shrl      $2, %r13d                                     #54.9
        movl      $10, %r15d                                    #43.3
        movl      %r13d, %eax                                   #54.9
        movq      %rbx, 112(%rsp)                               #54.9[spill]
        vmovsd    .L_2il0floatpacket.3(%rip), %xmm1             #44.17
        vmovsd    .L_2il0floatpacket.4(%rip), %xmm0             #55.31
        movq      %rax, 80(%rsp)                                #54.9[spill]
        movq      %r12, 120(%rsp)                               #54.9[spill]
        movl      96(%rsp), %ebx                                #54.9[spill]
                                # LOE ebx r13d r14d r15d
..B1.50:                        # Preds ..B1.87 ..B1.49 ..B1.69
                                # Execution count [2.33e+00]
        xorl      %eax, %eax                                    #47.8
        lea       168(%rsp), %rdi                               #47.8
        addl      %r15d, %r15d                                  #45.3
        lea       176(%rsp), %rsi                               #47.8
        vzeroupper                                              #47.8
..___tag_value_MAIN__.46:
        call      timing_                                       #47.8
..___tag_value_MAIN__.47:
                                # LOE ebx r13d r14d r15d
..B1.51:                        # Preds ..B1.50
                                # Execution count [2.28e+00]
        movl      $1, %r12d                                     #50.3
        testl     %r15d, %r15d                                  #50.3
        jle       ..B1.86       # Prob 0%                       #50.3
                                # LOE ebx r12d r13d r14d r15d
..B1.52:                        # Preds ..B1.51
                                # Execution count [2.28e+00]
        movq      80+heat_$PHI.0.1(%rip), %rsi                  #55.35
        xorl      %r10d, %r10d                                  #50.3
        movq      heat_$PHI.0.1(%rip), %r9                      #55.12
        movq      %rsi, %rcx                                    #55.50
        movq      104+heat_$PHI.0.1(%rip), %rax                 #55.35
        subq      %rax, %rcx                                    #55.50
        addq      %r9, %rax                                     #55.50
        xorl      %r11d, %r11d                                  #55.66
        vmovsd    .L_2il0floatpacket.4(%rip), %xmm0             #55.66
        lea       (%rsi,%r9), %rdi                              #55.50
        addq      %rax, %rcx                                    #55.50
        lea       (%r9,%rsi,2), %r8                             #55.66
                                # LOE rcx rsi rdi r8 r9 r11 ebx r10d r13d r14d r15d xmm0
..B1.53:                        # Preds ..B1.66 ..B1.52
                                # Execution count [1.27e+01]
        movq      %r11, %rdx                                    #53.6
        movq      %rdx, %rax                                    #53.6
        testl     %ebx, %ebx                                    #53.6
        jle       ..B1.66       # Prob 2%                       #53.6
                                # LOE rax rdx rcx rsi rdi r8 r9 r11 ebx r10d r13d r14d r15d xmm0
..B1.54:                        # Preds ..B1.53
                                # Execution count [1.24e+01]
        movl      %r10d, 64(%rsp)                               #[spill]
        movl      %r15d, 72(%rsp)                               #[spill]
                                # LOE rax rdx rcx rsi rdi r8 r9 r13d r14d xmm0
..B1.55:                        # Preds ..B1.64 ..B1.54
                                # Execution count [6.88e+01]
        testl     %r14d, %r14d                                  #54.9
        jle       ..B1.64       # Prob 50%                      #54.9
                                # LOE rax rdx rcx rsi rdi r8 r9 r13d r14d xmm0
..B1.56:                        # Preds ..B1.55
                                # Execution count [6.88e+01]
        xorl      %r15d, %r15d                                  #54.9
        movl      $1, %r12d                                     #54.9
        xorl      %r11d, %r11d                                  #54.9
        testl     %r13d, %r13d                                  #54.9
        je        ..B1.60       # Prob 2%                       #54.9
                                # LOE rax rdx rcx rsi rdi r8 r9 r11 r15 r12d r13d r14d xmm0
..B1.57:                        # Preds ..B1.56
                                # Execution count [6.74e+01]
        movl      %r14d, 104(%rsp)                              #55.66[spill]
        lea       (%rdi,%rax), %r12                             #55.50
        vmovsd    (%rax,%rcx), %xmm1                            #55.50
        lea       (%r9,%rax), %r10                              #55.35
        movq      80(%rsp), %r14                                #55.66[spill]
        lea       (%r8,%rax), %rbx                              #55.66
                                # LOE rax rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r14 r15 r13d xmm0 xmm1
        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.58:                        # Preds ..B1.58 ..B1.57
                                # Execution count [9.36e+01]
        vmovsd    8(%r11,%r10), %xmm2                           #55.35
        incq      %r15                                          #54.9
        vaddsd    16(%r11,%r12), %xmm2, %xmm3                   #55.12
        vaddsd    8(%r11,%rbx), %xmm3, %xmm4                    #55.12
        vaddsd    %xmm1, %xmm4, %xmm1                           #55.12
        vmulsd    %xmm1, %xmm0, %xmm5                           #55.12
        vmovsd    %xmm5, 8(%r11,%r12)                           #55.12
        vaddsd    16(%r11,%r10), %xmm5, %xmm6                   #55.48
        vaddsd    24(%r11,%r12), %xmm6, %xmm7                   #55.63
        vaddsd    16(%r11,%rbx), %xmm7, %xmm8                   #55.79
        vmulsd    %xmm8, %xmm0, %xmm9                           #55.12
        vmovsd    %xmm9, 16(%r11,%r12)                          #55.12
        vaddsd    24(%r11,%r10), %xmm9, %xmm10                  #55.48
        vaddsd    32(%r11,%r12), %xmm10, %xmm11                 #55.63
        vaddsd    24(%r11,%rbx), %xmm11, %xmm12                 #55.79
        vmulsd    %xmm12, %xmm0, %xmm13                         #55.12
        vmovsd    %xmm13, 24(%r11,%r12)                         #55.12
        vaddsd    32(%r11,%r10), %xmm13, %xmm14                 #55.48
        vaddsd    40(%r11,%r12), %xmm14, %xmm15                 #55.63
        vaddsd    32(%r11,%rbx), %xmm15, %xmm16                 #55.79
        vmulsd    %xmm16, %xmm0, %xmm1                          #55.12
        vmovsd    %xmm1, 32(%r11,%r12)                          #55.12
        addq      $32, %r11                                     #54.9
        cmpq      %r14, %r15                                    #54.9
        jb        ..B1.58       # Prob 28%                      #54.9
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
                                # LOE rax rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r14 r15 r13d xmm0 xmm1
..B1.59:                        # Preds ..B1.58
                                # Execution count [6.74e+01]
        movl      104(%rsp), %r14d                              #[spill]
        lea       1(,%r15,4), %r12d                             #55.12
                                # LOE rax rdx rcx rsi rdi r8 r9 r12d r13d r14d xmm0
..B1.60:                        # Preds ..B1.59 ..B1.56
                                # Execution count [6.88e+01]
        movslq    %r12d, %r12                                   #54.9
        decq      %r12                                          #54.9
        cmpq      120(%rsp), %r12                               #54.9[spill]
        jae       ..B1.64       # Prob 2%                       #54.9
                                # LOE rax rdx rcx rsi rdi r8 r9 r12 r13d r14d xmm0
..B1.61:                        # Preds ..B1.60
                                # Execution count [6.74e+01]
        movq      120(%rsp), %r15                               #55.66[spill]
        lea       (%rdi,%rax), %r11                             #55.50
        lea       (%r9,%rax), %r10                              #55.35
        lea       (%r8,%rax), %rbx                              #55.66
                                # LOE rax rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r15 r13d r14d xmm0
..B1.62:                        # Preds ..B1.62 ..B1.61
                                # Execution count [2.02e+02]
        vmovsd    8(%r10,%r12,8), %xmm1                         #55.35
        vaddsd    16(%r11,%r12,8), %xmm1, %xmm2                 #55.48
        vaddsd    8(%rbx,%r12,8), %xmm2, %xmm3                  #55.63
        vaddsd    (%r11,%r12,8), %xmm3, %xmm4                   #55.79
        vmulsd    %xmm4, %xmm0, %xmm5                           #55.12
        vmovsd    %xmm5, 8(%r11,%r12,8)                         #55.12
        incq      %r12                                          #54.9
        cmpq      %r15, %r12                                    #54.9
        jb        ..B1.62       # Prob 66%                      #54.9
                                # LOE rax rdx rcx rbx rsi rdi r8 r9 r10 r11 r12 r15 r13d r14d xmm0
..B1.64:                        # Preds ..B1.62 ..B1.55 ..B1.60
                                # Execution count [6.88e+01]
        incq      %rdx                                          #53.6
        addq      %rsi, %rax                                    #53.6
        cmpq      112(%rsp), %rdx                               #53.6[spill]
        jb        ..B1.55       # Prob 82%                      #53.6
                                # LOE rax rdx rcx rsi rdi r8 r9 r13d r14d xmm0
..B1.65:                        # Preds ..B1.64
                                # Execution count [1.24e+01]
        movl      64(%rsp), %r10d                               #[spill]
        xorl      %r11d, %r11d                                  #
        movl      72(%rsp), %r15d                               #[spill]
        movl      96(%rsp), %ebx                                #[spill]
                                # LOE rcx rsi rdi r8 r9 r11 ebx r10d r13d r14d r15d xmm0
..B1.66:                        # Preds ..B1.65 ..B1.53
                                # Execution count [1.27e+01]
        incl      %r10d                                         #50.3
        cmpl      %r15d, %r10d                                  #50.3
        jb        ..B1.53       # Prob 82%                      #50.3
                                # LOE rcx rsi rdi r8 r9 r11 ebx r10d r13d r14d r15d xmm0
..B1.67:                        # Preds ..B1.66
                                # Execution count [2.28e+00]
        xorl      %eax, %eax                                    #66.8
        lea       184(%rsp), %rdi                               #66.8
        lea       160(%rsp), %rsi                               #66.8
        lea       1(%r15), %r12d                                #50.3
..___tag_value_MAIN__.59:
        call      timing_                                       #66.8
..___tag_value_MAIN__.60:
                                # LOE ebx r12d r13d r14d r15d
..B1.68:                        # Preds ..B1.67
                                # Execution count [2.33e+00]
        vmovsd    184(%rsp), %xmm16                             #67.3
        vmovsd    .L_2il0floatpacket.3(%rip), %xmm0             #44.17
        vsubsd    168(%rsp), %xmm16, %xmm1                      #67.3
        vcomisd   %xmm1, %xmm0                                  #44.17
        jbe       ..B1.71       # Prob 18%                      #44.17
                                # LOE ebx r12d r13d r14d r15d
..B1.69:                        # Preds ..B1.68
                                # Execution count [1.91e+00]
        cmpl      $1000000000, %r15d                            #44.36
        jl        ..B1.50       # Prob 80%                      #44.36
                                # LOE ebx r12d r13d r14d r15d
..B1.71:                        # Preds ..B1.87 ..B1.68 ..B1.69
                                # Execution count [1.00e+00]
        cmpl      %r12d, %r15d                                  #70.8
        lea       (%rsp), %rdi                                  #72.3
        movq      $0x1208384ff00, %rdx                          #72.3
        movl      $__STRLITPACK_5.0.1, %ecx                     #72.3
        lea       64(%rsp), %r8                                 #72.3
        cmovl     %r15d, %r12d                                  #70.8
        movl      $-1, %esi                                     #70.8
        xorl      %eax, %eax                                    #70.8
        movq      $0, (%rdi)                                    #72.3
        movq      $14, 64(%rdi)                                 #72.3
        movq      $__STRLITPACK_2, 72(%rdi)                     #72.3
..___tag_value_MAIN__.61:
        call      for_write_seq_lis                             #72.3
..___tag_value_MAIN__.62:
                                # LOE r12d
..B1.72:                        # Preds ..B1.71
                                # Execution count [1.00e+00]
        movl      $__STRLITPACK_6.0.1, %esi                     #72.3
        lea       (%rsp), %rdi                                  #72.3
        xorl      %eax, %eax                                    #72.3
        lea       112(%rsp), %rdx                               #72.3
        movl      %r12d, (%rdx)                                 #72.3
..___tag_value_MAIN__.63:
        call      for_write_seq_lis_xmit                        #72.3
..___tag_value_MAIN__.64:
                                # LOE r12d
..B1.73:                        # Preds ..B1.72
                                # Execution count [1.00e+00]
        movl      $__STRLITPACK_7.0.1, %esi                     #72.3
        lea       (%rsp), %rdi                                  #72.3
        xorl      %eax, %eax                                    #72.3
        lea       80(%rsp), %rdx                                #72.3
        movq      $14, (%rdx)                                   #72.3
        movq      $__STRLITPACK_1, 8(%rdx)                      #72.3
..___tag_value_MAIN__.65:
        call      for_write_seq_lis_xmit                        #72.3
..___tag_value_MAIN__.66:
                                # LOE r12d
..B1.74:                        # Preds ..B1.73
                                # Execution count [1.00e+00]
        movl      152(%rsp), %eax                               #72.3
        vxorpd    %xmm0, %xmm0, %xmm0                           #72.49
        decl      %eax                                          #72.49
        vxorpd    %xmm2, %xmm2, %xmm2                           #72.60
        vcvtsi2sd %eax, %xmm0, %xmm0                            #72.49
        movl      156(%rsp), %edx                               #72.49
        vxorpd    %xmm7, %xmm7, %xmm7                           #72.71
        decl      %edx                                          #72.60
        lea       (%rsp), %rdi                                  #72.3
        vcvtsi2sd %edx, %xmm2, %xmm2                            #72.60
        vcvtsi2sd %r12d, %xmm7, %xmm7                           #72.71
        vmulsd    .L_2il0floatpacket.7(%rip), %xmm0, %xmm1      #72.59
        vmovsd    184(%rdi), %xmm3                              #72.70
        lea       120(%rsp), %rdx                               #72.3
        vmulsd    %xmm2, %xmm1, %xmm4                           #72.70
        vsubsd    48(%rdx), %xmm3, %xmm5                        #72.83
        vdivsd    %xmm5, %xmm4, %xmm6                           #72.79
        vmulsd    %xmm7, %xmm6, %xmm8                           #72.3
        movl      $__STRLITPACK_8.0.1, %esi                     #72.3
        xorl      %eax, %eax                                    #72.3
        vmovsd    %xmm8, (%rdx)                                 #72.3
..___tag_value_MAIN__.67:
        call      for_write_seq_lis_xmit                        #72.3
..___tag_value_MAIN__.68:
                                # LOE
..B1.75:                        # Preds ..B1.74
                                # Execution count [1.00e+00]
        movl      $__STRLITPACK_9.0.1, %esi                     #72.3
        lea       (%rsp), %rdi                                  #72.3
        xorl      %eax, %eax                                    #72.3
        lea       96(%rsp), %rdx                                #72.3
        movq      $6, (%rdx)                                    #72.3
        movq      $__STRLITPACK_0, 8(%rdx)                      #72.3
..___tag_value_MAIN__.69:
        call      for_write_seq_lis_xmit                        #72.3
..___tag_value_MAIN__.70:
                                # LOE
..B1.76:                        # Preds ..B1.75
                                # Execution count [1.00e+00]
        xorl      %esi, %esi                                    #73.3
        movl      $__STRLITPACK_10, %edi                        #73.3
        movq      $0x1208384ff00, %rdx                          #73.3
        xorl      %ecx, %ecx                                    #73.3
        xorl      %r8d, %r8d                                    #73.3
        xorl      %eax, %eax                                    #73.3
..___tag_value_MAIN__.71:
        call      for_stop_core                                 #73.3
..___tag_value_MAIN__.72:
                                # LOE
..B1.77:                        # Preds ..B1.76
                                # Execution count [1.00e+00]
        xorl      %eax, %eax                                    #74.3
        addq      $216, %rsp                                    #74.3
	.cfi_restore 3
        popq      %rbx                                          #74.3
	.cfi_restore 15
        popq      %r15                                          #74.3
	.cfi_restore 14
        popq      %r14                                          #74.3
	.cfi_restore 13
        popq      %r13                                          #74.3
	.cfi_restore 12
        popq      %r12                                          #74.3
        movq      %rbp, %rsp                                    #74.3
        popq      %rbp                                          #74.3
	.cfi_def_cfa 7, 8
	.cfi_restore 6
        ret                                                     #74.3
	.cfi_def_cfa 6, 16
	.cfi_escape 0x10, 0x03, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xd8, 0xff, 0xff, 0xff, 0x22
	.cfi_offset 6, -16
	.cfi_escape 0x10, 0x0c, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xf8, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0d, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xf0, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0e, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xe8, 0xff, 0xff, 0xff, 0x22
	.cfi_escape 0x10, 0x0f, 0x0e, 0x38, 0x1c, 0x0d, 0x80, 0xff, 0xff, 0xff, 0x1a, 0x0d, 0xe0, 0xff, 0xff, 0xff, 0x22
                                # LOE
..B1.78:                        # Preds ..B1.42
                                # Execution count [4.35e-02]: Infreq
        xorl      %r8d, %r8d                                    #33.3
        jmp       ..B1.46       # Prob 100%                     #33.3
                                # LOE rbx r9 r10 r12 r15 eax r8d r11d r13d r14d
..B1.79:                        # Preds ..B1.41
                                # Execution count [4.35e-02]: Infreq
        cmpl      $1, %r13d                                     #33.3
        jb        ..B1.49       # Prob 50%                      #33.3
                                # LOE rbx r10 r12 r15 eax r11d r13d r14d
..B1.80:                        # Preds ..B1.79
                                # Execution count [4.35e-01]: Infreq
        xorl      %ecx, %ecx                                    #33.3
        testl     %r13d, %r13d                                  #33.3
        je        ..B1.49       # Prob 56%                      #33.3
                                # LOE rcx rbx r10 r12 r15 eax r11d r13d r14d
..B1.81:                        # Preds ..B1.80
                                # Execution count [4.35e-01]: Infreq
        vxorpd    %xmm0, %xmm0, %xmm0                           #34.19
        vxorpd    %xmm1, %xmm1, %xmm1                           #34.27
        vcvtsi2sd %eax, %xmm0, %xmm0                            #34.19
        vcvtsi2sd %r11d, %xmm1, %xmm1                           #34.27
        movq      %r15, %rax                                    #34.6
        lea       (,%r12,8), %rdx                               #35.6
        negq      %rax                                          #34.6
        movq      %rdx, %rsi                                    #35.6
        vdivsd    %xmm1, %xmm0, %xmm0                           #34.6
        movslq    %r13d, %r13                                   #33.3
        subq      %r15, %rsi                                    #35.6
        lea       (%rax,%r15,2), %rax                           #34.6
                                # LOE rax rdx rcx rbx rsi r10 r12 r13 r15 r14d xmm0
..B1.82:                        # Preds ..B1.82 ..B1.81
                                # Execution count [4.90e+00]: Infreq
        incq      %rcx                                          #33.3
        vmovsd    %xmm0, (%r10)                                 #34.6
        vmovsd    %xmm0, (%r10,%rdx)                            #35.6
        vmovsd    %xmm0, (%rax,%r10)                            #34.6
        cmpq      %r13, %rcx                                    #33.3
        jb        ..B1.82       # Prob 91%                      #33.3
                                # LOE rax rdx rcx rbx rsi r10 r12 r13 r15 r14d xmm0
..B1.83:                        # Preds ..B1.82
                                # Execution count [4.35e-01]: Infreq
        lea       (%rsi,%r15,2), %rax                           #35.6
        vmovsd    %xmm0, (%rax,%r10)                            #35.6
        jmp       ..B1.49       # Prob 100%                     #35.6
                                # LOE rbx r12 r14d
..B1.86:                        # Preds ..B1.51
                                # Execution count [4.82e-02]: Infreq
        xorl      %eax, %eax                                    #66.8
        lea       184(%rsp), %rdi                               #66.8
        lea       160(%rsp), %rsi                               #66.8
..___tag_value_MAIN__.87:
        call      timing_                                       #66.8
..___tag_value_MAIN__.88:
                                # LOE ebx r12d r13d r14d r15d
..B1.87:                        # Preds ..B1.86
                                # Execution count [0.00e+00]: Infreq
        vmovsd    184(%rsp), %xmm16                             #67.3
        vmovsd    .L_2il0floatpacket.3(%rip), %xmm0             #44.17
        vsubsd    168(%rsp), %xmm16, %xmm1                      #67.3
        vcomisd   %xmm1, %xmm0                                  #44.17
        ja        ..B1.50       # Prob 82%                      #44.17
        jmp       ..B1.71       # Prob 100%                     #44.17
                                # LOE ebx r12d r13d r14d r15d
..B1.89:                        # Preds ..B1.32
                                # Execution count [4.35e-02]: Infreq
        xorl      %esi, %esi                                    #29.3
        jmp       ..B1.36       # Prob 100%                     #29.3
                                # LOE rcx rbx rdi r8 r12 eax edx esi r13d r14d
..B1.90:                        # Preds ..B1.19
                                # Execution count [5.33e-01]: Infreq
        incq      %r8                                           #21.3
        addq      %r10, %rdx                                    #21.3
        cmpq      80(%rsp), %r8                                 #21.3[spill]
        jb        ..B1.10       # Prob 82%                      #21.3
        jmp       ..B1.30       # Prob 100%                     #21.3
                                # LOE rdx rcx rsi r8 r9 r10 r15d ymm0 ymm2 zmm1
..B1.92:                        # Preds ..B1.10
                                # Execution count [5.33e-01]: Infreq
        movq      72(%rsp), %rdi                                #[spill]
        xorl      %eax, %eax                                    #22.6
        movq      80(%rsp), %r11                                #[spill]
        jmp       ..B1.25       # Prob 100%                     #
        .align    16,0x90
                                # LOE rdx rcx rsi rdi r8 r9 r10 r11 eax r15d ymm0 ymm2 zmm1
	.cfi_endproc
# mark_end;
	.type	MAIN__,@function
	.size	MAIN__,.-MAIN__
..LNMAIN__.0:
	.data
	.align 32
	.align 32
heat_$PHI.0.1:
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x40000080,0x00000000
	.long	0x00000003,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.long	0x00000000,0x00000000
	.section .rodata, "a"
	.align 64
	.align 4
__NLITPACK_0.0.1:
	.long	2
	.align 4
__STRLITPACK_3.0.1:
	.long	131849
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
__STRLITPACK_4.0.1:
	.long	66313
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
__STRLITPACK_5.0.1:
	.long	132152
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
__STRLITPACK_6.0.1:
	.long	131337
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
__STRLITPACK_7.0.1:
	.long	132152
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
__STRLITPACK_8.0.1:
	.long	131376
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
__STRLITPACK_9.0.1:
	.long	66616
	.byte	0
	.data
# -- End  MAIN__
	.section .rodata, "a"
	.space 7, 0x00 	# pad
	.align 64
.L_2il0floatpacket.8:
	.long	0x00000000,0x00000000,0x00000001,0x00000000,0x00000002,0x00000000,0x00000003,0x00000000,0x00000004,0x00000000,0x00000005,0x00000000,0x00000006,0x00000000,0x00000007,0x00000000
	.type	.L_2il0floatpacket.8,@object
	.size	.L_2il0floatpacket.8,64
	.align 32
.L_2il0floatpacket.0:
	.long	0x00000000,0x00000001,0x00000002,0x00000003,0x00000004,0x00000005,0x00000006,0x00000007
	.type	.L_2il0floatpacket.0,@object
	.size	.L_2il0floatpacket.0,32
	.align 32
.L_2il0floatpacket.1:
	.long	0x00000008,0x00000008,0x00000008,0x00000008,0x00000008,0x00000008,0x00000008,0x00000008
	.type	.L_2il0floatpacket.1,@object
	.size	.L_2il0floatpacket.1,32
	.align 32
.L_2il0floatpacket.2:
	.long	0x00000000,0x3ff00000,0x00000000,0x3ff00000,0x00000000,0x3ff00000,0x00000000,0x3ff00000
	.type	.L_2il0floatpacket.2,@object
	.size	.L_2il0floatpacket.2,32
	.align 16
.L_2il0floatpacket.5:
	.long	0x00000004,0x00000004,0x00000004,0x00000004
	.type	.L_2il0floatpacket.5,@object
	.size	.L_2il0floatpacket.5,16
	.align 16
.L_2il0floatpacket.6:
	.long	0x00000000,0x00000001,0x00000002,0x00000003
	.type	.L_2il0floatpacket.6,@object
	.size	.L_2il0floatpacket.6,16
	.align 8
.L_2il0floatpacket.3:
	.long	0x9999999a,0x3fc99999
	.type	.L_2il0floatpacket.3,@object
	.size	.L_2il0floatpacket.3,8
	.align 8
.L_2il0floatpacket.4:
	.long	0x00000000,0x3fd00000
	.type	.L_2il0floatpacket.4,@object
	.size	.L_2il0floatpacket.4,8
	.align 8
.L_2il0floatpacket.7:
	.long	0xa0b5ed8d,0x3eb0c6f7
	.type	.L_2il0floatpacket.7,@object
	.size	.L_2il0floatpacket.7,8
	.align 8
.L_2il0floatpacket.9:
	.long	0x00000000,0x3ff00000
	.type	.L_2il0floatpacket.9,@object
	.size	.L_2il0floatpacket.9,8
	.section .rodata.str1.4, "aMS",@progbits,1
	.align 4
	.align 4
__STRLITPACK_2:
	.long	1950949411
	.long	1952543333
	.long	1936617321
	.word	8250
	.byte	0
	.type	__STRLITPACK_2,@object
	.size	__STRLITPACK_2,15
	.space 1, 0x00 	# pad
	.align 4
__STRLITPACK_1:
	.long	1919242272
	.long	1836216166
	.long	1701015137
	.word	8250
	.byte	0
	.type	__STRLITPACK_1,@object
	.size	__STRLITPACK_1,15
	.space 1, 0x00 	# pad
	.align 4
__STRLITPACK_0:
	.long	1431063840
	.word	29520
	.byte	0
	.type	__STRLITPACK_0,@object
	.size	__STRLITPACK_0,7
	.space 1, 0x00 	# pad
	.align 4
__STRLITPACK_10:
	.byte	0
	.type	__STRLITPACK_10,@object
	.size	__STRLITPACK_10,1
	.data
	.section .note.GNU-stack, ""
# End
