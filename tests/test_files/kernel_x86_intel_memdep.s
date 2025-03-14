; Translated from kernel_x86_memdep.s
L4:
  vmovsd [rax+8], xmm0              # line 3          <---------------------------------+
  add rax, 8                        #  rax=rax_orig+8                                   |
  vmovsd [rax+rcx*8+8], xmm0        # line 5          <------------------------------------------+
  vaddsd xmm0, xmm0, [rax]          # depends on line 3, rax+8;[rax] == [rax+8] --------+        |
  sub rax, -8                       #  rax=rax_orig+16                                  |        |
  vaddsd xmm0, xmm0, [rax-8]        # depends on line 3, rax+16;[rax-8] == [rax+8] -----+        |
  dec rcx                           #  rcx=rcx_orig-1                                            |
  vaddsd xmm0, xmm0, [rax+rcx*8+8]  # depends on line 5, [(rax+8)+(rcx-1)*8+8] == [rax+rcx*+8] --+
  mov rdx, rcx                      #                                                            |
  vaddsd xmm0, xmm0, [rax+rdx*8+8]  # depends on line 5, rcx == rdx -----------------------------+
  vmulsd xmm0, xmm0, xmm1
  add rax, 8
  cmp rsi, rax
  jne L4
; Added to test LOAD dependencies
  shl rax, 5
  subsd xmm10, QWORD PTR [rax+r8]
