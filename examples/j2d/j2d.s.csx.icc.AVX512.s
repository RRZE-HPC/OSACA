        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.47:                        # Preds ..B1.63 ..B1.46
                                # Execution count [1.15e+04]
        lea       (%r12,%r11), %r8                              #94.5
                                # LOE rcx rbx r8 r9 r10 r11 r12 r14 r13d r15d zmm4
..B1.48:                        # Preds ..B1.47
                                # Execution count [1.73e+04]
        vmovupd   10032(%r8,%rcx,8), %zmm2                      #94.5
        vmovupd   10016(%r8,%rcx,8), %zmm0                      #94.5
                                # LOE rcx rbx r9 r10 r11 r12 r14 r13d r15d zmm0 zmm2 zmm4
..B1.51:                        # Preds ..B1.48
                                # Execution count [1.15e+04]
        lea       (%r12,%r11), %r8                              #94.5
        vaddpd    16(%r12,%rcx,8), %zmm0, %zmm0                 #94.5
        vaddpd    20032(%r10,%rcx,8), %zmm0, %zmm1              #94.5
        vaddpd    %zmm2, %zmm1, %zmm2                           #94.5
        vmulpd    %zmm2, %zmm4, %zmm3                           #94.5
        vmovupd   %zmm3, 10016(%r9,%rcx,8)                      #94.5
                                # LOE rcx rbx r8 r9 r10 r11 r12 r14 r13d r15d zmm4
..B1.52:                        # Preds ..B1.51
                                # Execution count [1.73e+04]
        vmovupd   10096(%r8,%rcx,8), %zmm2                      #94.5
        vmovupd   10080(%r8,%rcx,8), %zmm0                      #94.5
                                # LOE rcx rbx r9 r10 r11 r12 r14 r13d r15d zmm0 zmm2 zmm4
..B1.55:                        # Preds ..B1.52
                                # Execution count [1.15e+04]
        lea       (%r12,%r11), %r8                              #94.5
        vaddpd    80(%r12,%rcx,8), %zmm0, %zmm0                 #94.5
        vaddpd    20096(%r10,%rcx,8), %zmm0, %zmm1              #94.5
        vaddpd    %zmm2, %zmm1, %zmm2                           #94.5
        vmulpd    %zmm2, %zmm4, %zmm3                           #94.5
        vmovupd   %zmm3, 10080(%r9,%rcx,8)                      #94.5
                                # LOE rcx rbx r8 r9 r10 r11 r12 r14 r13d r15d zmm4
..B1.56:                        # Preds ..B1.55
                                # Execution count [1.73e+04]
        vmovupd   10160(%r8,%rcx,8), %zmm2                      #94.5
        vmovupd   10144(%r8,%rcx,8), %zmm0                      #94.5
                                # LOE rcx rbx r9 r10 r11 r12 r14 r13d r15d zmm0 zmm2 zmm4
..B1.59:                        # Preds ..B1.56
                                # Execution count [1.15e+04]
        lea       (%r12,%r11), %r8                              #94.5
        vaddpd    144(%r12,%rcx,8), %zmm0, %zmm0                #94.5
        vaddpd    20160(%r10,%rcx,8), %zmm0, %zmm1              #94.5
        vaddpd    %zmm2, %zmm1, %zmm2                           #94.5
        vmulpd    %zmm2, %zmm4, %zmm3                           #94.5
        vmovupd   %zmm3, 10144(%r9,%rcx,8)                      #94.5
                                # LOE rcx rbx r8 r9 r10 r11 r12 r14 r13d r15d zmm4
..B1.60:                        # Preds ..B1.59
                                # Execution count [1.73e+04]
        vmovupd   10224(%r8,%rcx,8), %zmm2                      #94.5
        vmovupd   10208(%r8,%rcx,8), %zmm0                      #94.5
                                # LOE rcx rbx r9 r10 r11 r12 r14 r13d r15d zmm0 zmm2 zmm4
..B1.63:                        # Preds ..B1.60
                                # Execution count [1.15e+04]
        vaddpd    208(%r12,%rcx,8), %zmm0, %zmm0                #94.5
        vaddpd    20224(%r10,%rcx,8), %zmm0, %zmm1              #94.5
        vaddpd    %zmm2, %zmm1, %zmm2                           #94.5
        vmulpd    %zmm2, %zmm4, %zmm3                           #94.5
        vmovupd   %zmm3, 10208(%r9,%rcx,8)                      #94.5
        addq      $32, %rcx                                     #94.5
        cmpq      %r14, %rcx                                    #94.5
        jb        ..B1.47       # Prob 82%                      #94.5
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
