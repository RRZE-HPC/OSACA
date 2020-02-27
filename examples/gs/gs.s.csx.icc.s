        movl      $111, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
..B1.58:                        # Preds ..B1.58 ..B1.57
                                # Execution count [9.36e+01]
        vmovsd    8(%r11,%r10), %xmm2                           #55.35
        incq      %r15                                          #54.9
        vaddsd    16(%r11,%r12), %xmm2, %xmm3                   #55.12
        vaddsd    8(%r11,%rbx), %xmm3, %xmm4                    #55.12
        vaddsd    %xmm1, %xmm4, %xmm1                           #55.12
        vmulsd    %xmm1, %xmm0, %xmm5                           #55.12
        vmovsd    %xmm5, 8(%r11,%r12)                           #55.12
        vaddsd    16(%r11,%r10), %xmm5, %xmm6                   #55.48
        vaddsd    24(%r11,%r12), %xmm6, %xmm7                   #55.63
        vaddsd    16(%r11,%rbx), %xmm7, %xmm8                   #55.79
        vmulsd    %xmm8, %xmm0, %xmm9                           #55.12
        vmovsd    %xmm9, 16(%r11,%r12)                          #55.12
        vaddsd    24(%r11,%r10), %xmm9, %xmm10                  #55.48
        vaddsd    32(%r11,%r12), %xmm10, %xmm11                 #55.63
        vaddsd    24(%r11,%rbx), %xmm11, %xmm12                 #55.79
        vmulsd    %xmm12, %xmm0, %xmm13                         #55.12
        vmovsd    %xmm13, 24(%r11,%r12)                         #55.12
        vaddsd    32(%r11,%r10), %xmm13, %xmm14                 #55.48
        vaddsd    40(%r11,%r12), %xmm14, %xmm15                 #55.63
        vaddsd    32(%r11,%rbx), %xmm15, %xmm16                 #55.79
        vmulsd    %xmm16, %xmm0, %xmm1                          #55.12
        vmovsd    %xmm1, 32(%r11,%r12)                          #55.12
        addq      $32, %r11                                     #54.9
        cmpq      %r14, %r15                                    #54.9
        jb        ..B1.58       # Prob 28%                      #54.9
        movl      $222, %ebx # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     100        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     103        # INSERTED BY KERNCRAFT IACA MARKER UTILITY
        .byte     144        # INSERTED BY KERNCRAFT IACA MARKER UTILITY

