        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.39:                        # Preds ..B1.39 ..B1.38
                                # Execution count [2.22e+03]
        vmovups   (%r13,%rax,8), %zmm1                          #77.5
        vfmadd213pd (%r14,%rax,8), %zmm2, %zmm1                 #77.5
        vmovupd   %zmm1, (%r14,%rax,8)                          #77.5
        addq      $8, %rax                                      #77.5
        cmpq      %rbx, %rax                                    #77.5
        jb        ..B1.39       # Prob 82%                      #77.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
