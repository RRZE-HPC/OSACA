        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.40:                        # Preds ..B1.40 ..B1.39
                                # Execution count [2.22e+03]
        vmovups   (%rcx,%rax,8), %zmm1                          #78.5
        vmovups   64(%rcx,%rax,8), %zmm3                        #78.5
        vaddpd    (%r13,%rax,8), %zmm1, %zmm2                   #78.5
        vaddpd    64(%r13,%rax,8), %zmm3, %zmm4                 #78.5
        vmovupd   %zmm2, (%r14,%rax,8)                          #78.5
        vmovupd   %zmm4, 64(%r14,%rax,8)                        #78.5
        addq      $16, %rax                                     #78.5
        cmpq      %r12, %rax                                    #78.5
        jb        ..B1.40       # Prob 82%                      #78.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
