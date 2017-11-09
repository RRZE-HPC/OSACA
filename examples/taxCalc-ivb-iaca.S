# mark_description "Intel(R) C Intel(R) 64 Compiler for applications running on Intel(R) 64, Version 16.0.3.210 Build 20160415";
# mark_description "-I../../iaca-lin64/include -fno-alias -O3 -fopenmp -xCORE-AVX-I -S -o ivb-asm.S";
	.file "taxCalc.c"
	.text
..TXTST0:
# -- Begin  main
	.text
# mark_begin;
       .align    16,0x90
	.globl main
# --- main(void)
main:
..B1.1:                         # Preds ..B1.0
	.cfi_startproc
..___tag_value_main.1:
..L2:
                                                          #4.15
        pushq     %rbp                                          #4.15
	.cfi_def_cfa_offset 16
        movq      %rsp, %rbp                                    #4.15
	.cfi_def_cfa 6, 16
	.cfi_offset 6, -16
        andq      $-128, %rsp                                   #4.15
        subq      $4096, %rsp                                   #4.15
        movl      $104446, %esi                                 #4.15
        movl      $3, %edi                                      #4.15
        call      __intel_new_feature_proc_init                 #4.15
                                # LOE rbx r12 r13 r14 r15
..B1.10:                        # Preds ..B1.1
        vstmxcsr  (%rsp)                                        #4.15
        movl      $.2.3_2_kmpc_loc_struct_pack.3, %edi          #4.15
        xorl      %esi, %esi                                    #4.15
        orl       $32832, (%rsp)                                #4.15
        xorl      %eax, %eax                                    #4.15
        vldmxcsr  (%rsp)                                        #4.15
..___tag_value_main.6:
        call      __kmpc_begin                                  #4.15
..___tag_value_main.7:
                                # LOE rbx r12 r13 r14 r15
..B1.2:                         # Preds ..B1.10
        movl      $il0_peep_printf_format_0, %edi               #5.5
        call      puts                                          #5.5
                                # LOE rbx r12 r13 r14 r15
..B1.3:                         # Preds ..B1.2
        vmovss    .L_2il0floatpacket.0(%rip), %xmm0             #8.15
        xorl      %eax, %eax                                    #11.5
        vxorps    %xmm1, %xmm1, %xmm1                           #9.5
        vmovss    %xmm1, (%rsp)                                 #9.5

        movl $111,%ebx          #IACA START
        .byte 100,103,144       #IACA START
                                # LOE rax rbx r12 r13 r14 r15 xmm0 xmm1

..B1.4:                         # Preds ..B1.4 ..B1.3
        lea       1(%rax,%rax), %edx                            #12.9
        vcvtsi2ss %edx, %xmm2, %xmm2                            #12.27
        vmulss    %xmm2, %xmm0, %xmm3                           #12.29
        lea       2(%rax,%rax), %ecx                            #12.9
        vaddss    %xmm3, %xmm1, %xmm4                           #12.29
        vxorps    %xmm1, %xmm1, %xmm1                           #12.27
        vcvtsi2ss %ecx, %xmm1, %xmm1                            #12.27
        vmulss    %xmm1, %xmm0, %xmm5                           #12.29
        vmovss    %xmm4, 4(%rsp,%rax,8)                         #12.9
        vaddss    %xmm5, %xmm4, %xmm1                           #12.29
        vmovss    %xmm1, 8(%rsp,%rax,8)                         #12.9
        incq      %rax                                          #11.5
        cmpq      $499, %rax                                    #11.5
        jb        ..B1.4        # Prob 99%                      #11.5

        movl $222,%ebx          #IACA END
        .byte 100,103,144       #IACA END

                                # LOE rax rbx r12 r13 r14 r15 xmm0 xmm1
..B1.5:                         # Preds ..B1.4
        vmovss    3992(%rsp), %xmm0                             #12.18
        movl      $il0_peep_printf_format_1, %edi               #15.5
        vaddss    .L_2il0floatpacket.1(%rip), %xmm0, %xmm1      #12.29
        vmovss    %xmm1, 3996(%rsp)                             #12.9
        call      puts                                          #15.5
                                # LOE rbx r12 r13 r14 r15
..B1.6:                         # Preds ..B1.5
        movl      $.2.3_2_kmpc_loc_struct_pack.14, %edi         #16.12
        xorl      %eax, %eax                                    #16.12
..___tag_value_main.8:
        call      __kmpc_end                                    #16.12
..___tag_value_main.9:
                                # LOE rbx r12 r13 r14 r15
..B1.7:                         # Preds ..B1.6
        xorl      %eax, %eax                                    #16.12
        movq      %rbp, %rsp                                    #16.12
        popq      %rbp                                          #16.12
	.cfi_def_cfa 7, 8
	.cfi_restore 6
        ret                                                     #16.12
        .align    16,0x90
	.cfi_endproc
                                # LOE
# mark_end;
	.type	main,@function
	.size	main,.-main
	.data
	.align 4
	.align 4
.2.3_2_kmpc_loc_struct_pack.3:
	.long	0
	.long	2
	.long	0
	.long	0
	.quad	.2.3_2__kmpc_loc_pack.2
	.align 4
.2.3_2__kmpc_loc_pack.2:
	.byte	59
	.byte	117
	.byte	110
	.byte	107
	.byte	110
	.byte	111
	.byte	119
	.byte	110
	.byte	59
	.byte	109
	.byte	97
	.byte	105
	.byte	110
	.byte	59
	.byte	52
	.byte	59
	.byte	52
	.byte	59
	.byte	59
	.space 1, 0x00 	# pad
	.align 4
.2.3_2_kmpc_loc_struct_pack.14:
	.long	0
	.long	2
	.long	0
	.long	0
	.quad	.2.3_2__kmpc_loc_pack.13
	.align 4
.2.3_2__kmpc_loc_pack.13:
	.byte	59
	.byte	117
	.byte	110
	.byte	107
	.byte	110
	.byte	111
	.byte	119
	.byte	110
	.byte	59
	.byte	109
	.byte	97
	.byte	105
	.byte	110
	.byte	59
	.byte	49
	.byte	54
	.byte	59
	.byte	49
	.byte	54
	.byte	59
	.byte	59
	.section .rodata.str1.4, "aMS",@progbits,1
	.align 4
	.align 4
il0_peep_printf_format_0:
	.long	1128354639
	.long	1702109249
	.long	1931506803
	.long	1953653108
	.byte	0
	.space 3, 0x00 	# pad
	.align 4
il0_peep_printf_format_1:
	.long	1128354639
	.long	1702109249
	.long	1696625779
	.word	25710
	.byte	0
	.data
# -- End  main
	.section .rodata, "a"
	.align 4
	.align 4
.L_2il0floatpacket.0:
	.long	0x3e428f5c
	.type	.L_2il0floatpacket.0,@object
	.size	.L_2il0floatpacket.0,4
	.align 4
.L_2il0floatpacket.1:
	.long	0x433dcf5c
	.type	.L_2il0floatpacket.1,@object
	.size	.L_2il0floatpacket.1,4
	.data
	.section .note.GNU-stack, ""
// -- Begin DWARF2 SEGMENT .eh_frame
	.section .eh_frame,"a",@progbits
.eh_frame_seg:
	.align 8
# End
