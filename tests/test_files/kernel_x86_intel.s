; https://godbolt.org/z/o49jjojnx /std:c++latest /O1 /fp:contract /arch:AVX2
$LL13@foo:
	vmovsd  xmm1, QWORD PTR [rax]
	vmovsd  xmm0, QWORD PTR [rcx+rax]
	vfmadd213sd xmm1, xmm0, QWORD PTR [rdx+rax]
	vmovsd  QWORD PTR [r8+rax], xmm1
	lea     rax, QWORD PTR [rax+8]
	sub     rbx, 1
	jne     SHORT $LL13@foo
