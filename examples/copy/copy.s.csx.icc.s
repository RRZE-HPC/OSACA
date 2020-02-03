        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.39:                        # Preds ..B1.39 ..B1.38
                                # Execution count [2.22e+03]
        vmovups   (%r14,%rax,8), %zmm1                          #79.5
        vmovupd   %zmm1, (%r13,%rax,8)                          #79.5
        addq      $8, %rax                                      #79.5
        cmpq      %r12, %rax                                    #79.5
        jb        ..B1.39       # Prob 82%                      #79.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
