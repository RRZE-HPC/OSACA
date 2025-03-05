; Translated from kernel_x86_memdep.s
L4:
  vmovsd [rax+8], xmm0
  add rax, 8
  vmovsd [rax+rcx*8+8], xmm0
  vaddsd xmm0, xmm0, [rax]
  sub rax, -8
  vaddsd xmm0, xmm0, [rax-8]
  dec rcx
  vaddsd xmm0, xmm0, [rax+rcx*8+8]
  mov rdx, rcx
  vaddsd xmm0, xmm0, [rax+rdx*8+8]
  vmulsd xmm0, xmm0, xmm1
  add rax, 8
  cmp rsi, rax
  jne L4
; Added to test LOAD dependencies
  shl rax, 5
  subsd xmm10, QWORD PTR [rax+r8]
