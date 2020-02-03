        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.47:                        # Preds ..B1.47 ..B1.46
                                # Execution count [1.15e+04]
        vmovupd   10016(%r8,%rcx,8), %ymm1                      #94.5
        vmovupd   10048(%r8,%rcx,8), %ymm6                      #94.5
        vmovupd   10080(%r8,%rcx,8), %ymm11                     #94.5
        vaddpd    16(%r12,%rcx,8), %ymm1, %ymm2                 #94.5
        vaddpd    48(%r12,%rcx,8), %ymm6, %ymm7                 #94.5
        vaddpd    80(%r12,%rcx,8), %ymm11, %ymm12               #94.5
        vaddpd    20032(%r10,%rcx,8), %ymm2, %ymm3              #94.5
        vaddpd    20064(%r10,%rcx,8), %ymm7, %ymm8              #94.5
        vaddpd    20096(%r10,%rcx,8), %ymm12, %ymm13            #94.5
        vaddpd    10032(%r8,%rcx,8), %ymm3, %ymm4               #94.5
        vaddpd    10064(%r8,%rcx,8), %ymm8, %ymm9               #94.5
        vaddpd    10096(%r8,%rcx,8), %ymm13, %ymm14             #94.5
        vmovupd   10112(%r8,%rcx,8), %ymm1                      #94.5
        vmulpd    %ymm4, %ymm0, %ymm5                           #94.5
        vmulpd    %ymm9, %ymm0, %ymm10                          #94.5
        vmulpd    %ymm14, %ymm0, %ymm15                         #94.5
        vaddpd    112(%r12,%rcx,8), %ymm1, %ymm2                #94.5
        vmovupd   %ymm5, 10016(%r9,%rcx,8)                      #94.5
        vmovupd   %ymm10, 10048(%r9,%rcx,8)                     #94.5
        vmovupd   %ymm15, 10080(%r9,%rcx,8)                     #94.5
        vaddpd    20128(%r10,%rcx,8), %ymm2, %ymm3              #94.5
        vaddpd    10128(%r8,%rcx,8), %ymm3, %ymm4               #94.5
        vmulpd    %ymm4, %ymm0, %ymm5                           #94.5
        vmovupd   %ymm5, 10112(%r9,%rcx,8)                      #94.5
        addq      $16, %rcx                                     #94.5
        cmpq      %r14, %rcx                                    #94.5
        jb        ..B1.47       # Prob 82%                      #94.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
