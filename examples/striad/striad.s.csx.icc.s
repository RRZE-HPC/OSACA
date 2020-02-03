        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.41:                        # Preds ..B1.41 ..B1.40
                                # Execution count [2.22e+03]
        vmovups   (%rcx,%rax,8), %zmm2                          #80.5
        vmovups   64(%rcx,%rax,8), %zmm4                        #80.5
        vmovups   (%r14,%rax,8), %zmm1                          #80.5
        vmovups   64(%r14,%rax,8), %zmm3                        #80.5
        vfmadd213pd (%r8,%rax,8), %zmm1, %zmm2                  #80.5
        vfmadd213pd 64(%r8,%rax,8), %zmm3, %zmm4                #80.5
        vmovupd   %zmm2, (%r13,%rax,8)                          #80.5
        vmovupd   %zmm4, 64(%r13,%rax,8)                        #80.5
        addq      $16, %rax                                     #80.5
        cmpq      %r12, %rax                                    #80.5
        jb        ..B1.41       # Prob 82%                      #80.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
