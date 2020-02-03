        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.38:                        # Preds ..B1.38 ..B1.37
                                # Execution count [2.22e+03]
        vmulpd    (%r13,%rax,8), %zmm3, %zmm1                   #75.5
        vmulpd    64(%r13,%rax,8), %zmm3, %zmm2                 #75.5
        vmovupd   %zmm1, (%r13,%rax,8)                          #75.5
        vmovupd   %zmm2, 64(%r13,%rax,8)                        #75.5
        addq      $16, %rax                                     #75.5
        cmpq      %r14, %rax                                    #75.5
        jb        ..B1.38       # Prob 82%                      #75.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
