        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.42:                        # Preds ..B1.42 ..B1.41
                                # Execution count [1.15e+04]
        movups    10016(%r8,%rcx,8), %xmm0                      #94.5
        addpd     16(%r12,%rcx,8), %xmm0                        #94.5
        addpd     20032(%r10,%rcx,8), %xmm0                     #94.5
        movups    10032(%r8,%rcx,8), %xmm2                      #94.5
        movups    32(%r12,%rcx,8), %xmm1                        #94.5
        addpd     %xmm2, %xmm0                                  #94.5
        addpd     %xmm1, %xmm2                                  #94.5
        mulpd     %xmm7, %xmm0                                  #94.5
        addpd     20048(%r10,%rcx,8), %xmm2                     #94.5
        movups    10048(%r8,%rcx,8), %xmm4                      #94.5
        movups    48(%r12,%rcx,8), %xmm3                        #94.5
        addpd     %xmm4, %xmm2                                  #94.5
        addpd     %xmm3, %xmm4                                  #94.5
        mulpd     %xmm7, %xmm2                                  #94.5
        addpd     20064(%r10,%rcx,8), %xmm4                     #94.5
        movups    10064(%r8,%rcx,8), %xmm6                      #94.5
        movups    64(%r12,%rcx,8), %xmm5                        #94.5
        addpd     %xmm6, %xmm4                                  #94.5
        addpd     %xmm5, %xmm6                                  #94.5
        mulpd     %xmm7, %xmm4                                  #94.5
        addpd     20080(%r10,%rcx,8), %xmm6                     #94.5
        addpd     10080(%r8,%rcx,8), %xmm6                      #94.5
        mulpd     %xmm7, %xmm6                                  #94.5
        movups    %xmm0, 10016(%r9,%rcx,8)                      #94.5
        movups    %xmm2, 10032(%r9,%rcx,8)                      #94.5
        movups    %xmm4, 10048(%r9,%rcx,8)                      #94.5
        movups    %xmm6, 10064(%r9,%rcx,8)                      #94.5
        addq      $8, %rcx                                      #94.5
        cmpq      %r14, %rcx                                    #94.5
        jb        ..B1.42       # Prob 82%                      #94.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
