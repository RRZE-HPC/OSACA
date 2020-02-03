        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.40:                        # Preds ..B1.40 ..B1.39
                                # Execution count [2.22e+03]
        vmovups   (%r13,%rax,8), %zmm1                          #78.5
        vfmadd213pd (%rcx,%rax,8), %zmm2, %zmm1                 #78.5
        vmovupd   %zmm1, (%r14,%rax,8)                          #78.5
        addq      $8, %rax                                      #78.5
        cmpq      %r12, %rax                                    #78.5
        jb        ..B1.40       # Prob 82%                      #78.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
