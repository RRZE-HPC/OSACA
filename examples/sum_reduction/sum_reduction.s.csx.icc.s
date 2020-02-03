        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.38:                        # Preds ..B1.38 ..B1.37
                                # Execution count [2.22e+03]
        vaddpd    (%r13,%rax,8), %zmm4, %zmm4                   #76.5
        vaddpd    64(%r13,%rax,8), %zmm3, %zmm3                 #76.5
        vaddpd    128(%r13,%rax,8), %zmm2, %zmm2                #76.5
        vaddpd    192(%r13,%rax,8), %zmm1, %zmm1                #76.5
        addq      $32, %rax                                     #76.5
        cmpq      %r14, %rax                                    #76.5
        jb        ..B1.38       # Prob 82%                      #76.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
