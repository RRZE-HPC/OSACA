# Produced with ICC 2021.10.0 with -O3 -xcore-avx512, https://godbolt.org/z/87bYseh8r
..B1.1:                         # Preds ..B1.0
        push      rbp                                           #5.32
        mov       rbp, rsp                                      #5.32
        and       rsp, -128                                     #5.32
        push      r15                                           #5.32
        push      rbx                                           #5.32
        sub       rsp, 112                                      #5.32
        mov       edi, 3                                        #5.32
        mov       rsi, 0x64199d9ffe                             #5.32
        call      __intel_new_feature_proc_init                 #5.32
..B1.34:                        # Preds ..B1.1
        vstmxcsr  DWORD PTR [rsp]                               #5.32
        xor       edi, edi                                      #11.7
        or        DWORD PTR [rsp], 32832                        #5.32
        vldmxcsr  DWORD PTR [rsp]                               #5.32
        call      time                                          #11.7
..B1.2:                         # Preds ..B1.34
        mov       edi, eax                                      #11.1
        call      srand                                         #11.1
..B1.3:                         # Preds ..B1.2
        mov       edi, 1600                                     #13.16
        call      malloc                                        #13.16
..B1.35:                        # Preds ..B1.3
        mov       rsi, rax                                      #13.16
..B1.4:                         # Preds ..B1.35
        xor       eax, eax                                      #14.1
        mov       rbx, rsi                                      #14.1
        mov       r15, rax                                      #14.1
..B1.5:                         # Preds ..B1.6 ..B1.4
        mov       edi, 1600                                     #15.22
        call      malloc                                        #15.22
..B1.6:                         # Preds ..B1.5
        mov       QWORD PTR [rbx+r15*8], rax                    #15.5
        inc       r15                                           #14.1
        cmp       r15, 200                                      #14.1
        jb        ..B1.5        # Prob 82%                      #14.1
..B1.7:                         # Preds ..B1.6
        xor       eax, eax                                      #17.1
        mov       rsi, rbx                                      #
        mov       r15, rax                                      #19.44
        mov       QWORD PTR [rsp], r13                          #19.44[spill]
        mov       QWORD PTR [8+rsp], r14                        #19.44[spill]
..B1.8:                         # Preds ..B1.11 ..B1.7
        mov       r13, QWORD PTR [8+rbx+r15*8]                  #19.5
        xor       r14d, r14d                                    #18.3
..B1.9:                         # Preds ..B1.10 ..B1.8
        call      rand                                          #19.26
..B1.37:                        # Preds ..B1.9
        mov       r8d, eax                                      #19.26
..B1.10:                        # Preds ..B1.37
        mov       eax, 351843721                                #19.33
        mov       ecx, r8d                                      #19.33
        imul      r8d                                           #19.33
        sar       ecx, 31                                       #19.33
        vxorpd    xmm0, xmm0, xmm0                              #19.33
        sar       edx, 13                                       #19.33
        sub       edx, ecx                                      #19.33
        imul      edi, edx, -100000                             #19.33
        add       r8d, edi                                      #19.33
        vcvtsi2sd xmm0, xmm0, r8d                               #19.33
        vdivsd    xmm1, xmm0, QWORD PTR .L_2il0floatpacket.0[rip] #19.44
        vmovsd    QWORD PTR [8+r13+r14*8], xmm1                 #19.5
        inc       r14                                           #18.3
        cmp       r14, 198                                      #18.3
        jb        ..B1.9        # Prob 82%                      #18.3
..B1.11:                        # Preds ..B1.10
        inc       r15                                           #17.1
        cmp       r15, 198                                      #17.1
        jb        ..B1.8        # Prob 91%                      #17.1
..B1.12:                        # Preds ..B1.11
        mov       r13, QWORD PTR [rsp]                          #[spill]
        mov       rsi, rbx                                      #
        mov       r14, QWORD PTR [8+rsp]                        #[spill]
        xor       ecx, ecx                                      #23.1
        vmovsd    xmm0, QWORD PTR .L_2il0floatpacket.1[rip]     #10.14
        xor       dil, dil                                      #10.14
        mov       edx, 196                                      #10.14
..B1.13:                        # Preds ..B1.27 ..B1.12
        mov       rax, QWORD PTR [8+rsi+rcx*8]                  #25.5
        mov       r8, rax                                       #25.5
        lea       r9, QWORD PTR [8+rax]                         #25.5
        sub       r8, r9                                        #25.5
        cmp       r8, 1584                                      #24.3
        jge       ..B1.15       # Prob 50%                      #24.3
..B1.14:                        # Preds ..B1.13
        neg       r8                                            #26.7
        cmp       r8, 1584                                      #24.3
        jl        ..B1.22       # Prob 50%                      #24.3
..B1.15:                        # Preds ..B1.13 ..B1.14
        lea       r8, QWORD PTR [16+rax]                        #27.9
        sub       r9, r8                                        #27.9
        cmp       r9, 1584                                      #24.3
        jge       ..B1.17       # Prob 50%                      #24.3
..B1.16:                        # Preds ..B1.15
        neg       r9                                            #25.5
        cmp       r9, 1584                                      #24.3
        jl        ..B1.22       # Prob 50%                      #24.3
..B1.17:                        # Preds ..B1.15 ..B1.16
        vmovsd    xmm1, QWORD PTR [rax]                         #27.9
        mov       bl, dil                                       #24.3
        mov       r9, QWORD PTR [rsi+rcx*8]                     #27.21
        xor       r11d, r11d                                    #25.5
        mov       r10, QWORD PTR [16+rsi+rcx*8]                 #26.19
        mov       r8, QWORD PTR [8+rsi+rcx*8]                   #27.9
..B1.18:                        # Preds ..B1.18 ..B1.17
        vmovsd    xmm2, QWORD PTR [8+r11+r10]                   #26.19
        inc       bl                                            #24.3
        vaddsd    xmm3, xmm2, QWORD PTR [16+r11+r8]             #25.5
        vaddsd    xmm4, xmm3, QWORD PTR [8+r11+r9]              #25.5
        vaddsd    xmm1, xmm4, xmm1                              #25.5
        vmulsd    xmm8, xmm0, xmm1                              #27.21
        vmovsd    QWORD PTR [8+r11+r8], xmm8                    #25.5
        vmovsd    xmm5, QWORD PTR [16+r11+r10]                  #26.19
        vaddsd    xmm6, xmm5, QWORD PTR [24+r11+r8]             #26.19
        vaddsd    xmm7, xmm6, QWORD PTR [16+r11+r9]             #27.9
        vaddsd    xmm9, xmm7, xmm8                              #27.21
        vmulsd    xmm13, xmm0, xmm9                             #27.21
        vmovsd    QWORD PTR [16+r11+r8], xmm13                  #25.5
        vmovsd    xmm10, QWORD PTR [24+r11+r10]                 #26.19
        vaddsd    xmm11, xmm10, QWORD PTR [32+r11+r8]           #26.19
        vaddsd    xmm12, xmm11, QWORD PTR [24+r11+r9]           #27.9
        vaddsd    xmm14, xmm12, xmm13                           #27.21
        vmulsd    xmm18, xmm0, xmm14                            #27.21
        vmovsd    QWORD PTR [24+r11+r8], xmm18                  #25.5
        vmovsd    xmm15, QWORD PTR [32+r11+r10]                 #26.19
        vaddsd    xmm16, xmm15, QWORD PTR [40+r11+r8]           #26.19
        vaddsd    xmm17, xmm16, QWORD PTR [32+r11+r9]           #27.9
        vaddsd    xmm19, xmm17, xmm18                           #27.21
        vmulsd    xmm1, xmm0, xmm19                             #27.21
        vmovsd    QWORD PTR [32+r11+r8], xmm1                   #25.5
        add       r11, 32                                       #24.3
        cmp       bl, 49                                        #24.3
        jb        ..B1.18       # Prob 27%                      #24.3
..B1.19:                        # Preds ..B1.18
        mov       r11, rdx                                      #24.3
..B1.20:                        # Preds ..B1.20 ..B1.19
        vmovsd    xmm1, QWORD PTR [r8+r11*8]                    #26.7
        vaddsd    xmm2, xmm1, QWORD PTR [8+r10+r11*8]           #26.19
        vaddsd    xmm3, xmm2, QWORD PTR [16+r8+r11*8]           #27.9
        vaddsd    xmm4, xmm3, QWORD PTR [8+r9+r11*8]            #27.21
        vmulsd    xmm5, xmm0, xmm4                              #27.21
        vmovsd    QWORD PTR [8+r8+r11*8], xmm5                  #25.5
        inc       r11                                           #24.3
        cmp       r11, 198                                      #24.3
        jb        ..B1.20       # Prob 66%                      #24.3
        jmp       ..B1.27       # Prob 100%                     #24.3
..B1.22:                        # Preds ..B1.14 ..B1.16
        mov       r9, QWORD PTR [rsi+rcx*8]                     #27.21
        mov       bl, dil                                       #24.3
        mov       r10, QWORD PTR [16+rsi+rcx*8]                 #26.19
        xor       r11d, r11d                                    #25.5
        mov       r8, QWORD PTR [8+rsi+rcx*8]                   #26.7
..B1.23:                        # Preds ..B1.23 ..B1.22
        inc       bl                                            #24.3
        vmovsd    xmm1, QWORD PTR [r11+r8]                      #26.7
        vaddsd    xmm2, xmm1, QWORD PTR [8+r11+r10]             #26.19
        vaddsd    xmm3, xmm2, QWORD PTR [16+r11+r8]             #27.9
        vaddsd    xmm4, xmm3, QWORD PTR [8+r11+r9]              #27.21
        vmulsd    xmm5, xmm0, xmm4                              #27.21
        vmovsd    QWORD PTR [8+r11+r8], xmm5                    #25.5
        vaddsd    xmm6, xmm5, QWORD PTR [16+r11+r10]            #26.19
        vaddsd    xmm7, xmm6, QWORD PTR [24+r11+r8]             #27.9
        vaddsd    xmm8, xmm7, QWORD PTR [16+r11+r9]             #27.21
        vmulsd    xmm9, xmm0, xmm8                              #27.21
        vmovsd    QWORD PTR [16+r11+r8], xmm9                   #25.5
        vaddsd    xmm10, xmm9, QWORD PTR [24+r11+r10]           #26.19
        vaddsd    xmm11, xmm10, QWORD PTR [32+r11+r8]           #27.9
        vaddsd    xmm12, xmm11, QWORD PTR [24+r11+r9]           #27.21
        vmulsd    xmm13, xmm0, xmm12                            #27.21
        vmovsd    QWORD PTR [24+r11+r8], xmm13                  #25.5
        vaddsd    xmm14, xmm13, QWORD PTR [32+r11+r10]          #26.19
        vaddsd    xmm15, xmm14, QWORD PTR [40+r11+r8]           #27.9
        vaddsd    xmm16, xmm15, QWORD PTR [32+r11+r9]           #27.21
        vmulsd    xmm17, xmm0, xmm16                            #27.21
        vmovsd    QWORD PTR [32+r11+r8], xmm17                  #25.5
        add       r11, 32                                       #24.3
        cmp       bl, 49                                        #24.3
        jb        ..B1.23       # Prob 27%                      #24.3
..B1.24:                        # Preds ..B1.23
        mov       r11, rdx                                      #24.3
..B1.25:                        # Preds ..B1.25 ..B1.24
        vmovsd    xmm1, QWORD PTR [r8+r11*8]                    #26.7
        vaddsd    xmm2, xmm1, QWORD PTR [8+r10+r11*8]           #26.19
        vaddsd    xmm3, xmm2, QWORD PTR [16+r8+r11*8]           #27.9
        vaddsd    xmm4, xmm3, QWORD PTR [8+r9+r11*8]            #27.21
        vmulsd    xmm5, xmm0, xmm4                              #27.21
        vmovsd    QWORD PTR [8+r8+r11*8], xmm5                  #25.5
        inc       r11                                           #24.3
        cmp       r11, 198                                      #24.3
        jb        ..B1.25       # Prob 66%                      #24.3
..B1.27:                        # Preds ..B1.25 ..B1.20
        mov       r8, QWORD PTR [16+rsi+rcx*8]                  #30.3
        inc       rcx                                           #23.1
        mov       rax, QWORD PTR [1592+rax]                     #30.15
        mov       QWORD PTR [8+r8], rax                         #30.3
        cmp       rcx, 198                                      #23.1
        jb        ..B1.13       # Prob 91%                      #23.1
..B1.28:                        # Preds ..B1.27
        mov       rax, QWORD PTR [1584+rsi]                     #33.4
        vmovsd    xmm0, QWORD PTR [1584+rax]                    #33.4
        vucomisd  xmm0, QWORD PTR .L_2il0floatpacket.2[rip]     #33.29
        jp        ..B1.29       # Prob 0%                       #33.29
        je        ..B1.30       # Prob 5%                       #33.29
..B1.29:                        # Preds ..B1.28 ..B1.30
        xor       eax, eax                                      #34.1
        add       rsp, 112                                      #34.1
        pop       rbx                                           #34.1
        pop       r15                                           #34.1
        mov       rsp, rbp                                      #34.1
        pop       rbp                                           #34.1
        ret                                                     #34.1
..B1.30:                        # Preds ..B1.28
        mov       rax, QWORD PTR [rsi]                          #33.39
        mov       edi, offset flat: .L_2__STRING.0              #33.39
        vmovsd    xmm0, QWORD PTR [rax]                         #33.39
        mov       eax, 1                                        #33.39
        call      printf                                        #33.39
        jmp       ..B1.29       # Prob 100%                     #33.39
.L_2il0floatpacket.0:
        .long   0x00000000,0x408f4000
.L_2il0floatpacket.1:
        .long   0x7ae147ae,0x3ff3ae14
.L_2il0floatpacket.2:
        .long   0xfc8f3238,0x3ff3c0c1
.L_2__STRING.0:
        .long   681509
