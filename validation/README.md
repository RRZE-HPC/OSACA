# Validation

View the validation analysis at https://nbviewer.jupyter.org/github/RRZE-HPC/OSACA/blob/master/validation/Analysis.ipynb

To reconstruct, download the `validataion-data.tar.gz` from a github release and extraxct into the base folder (`OSACA`). Alternativly, update the configuration in `buiild_and_run.py` and run your own measurements.

## Dev Stories
### ZEN2: only simple or all store AGU on port 10?
`('ZEN2','clang','O1','add')`
was predicted too slow (1.5 vs 1.0 cy/it) with only simple address generation on port 10
with only store address-genration, but both complex and simple, this fits perfectly
moved too slow predictions generally into the categories of "perfect" or "too fast".

### ZEN & ZEN2: LEA on ALU or AGU?
`('ZEN','clang','O2','3d-r3-11pt')`
was predicted too slow (10 vs 8.3 cy/it.) with LEAs bound to AGUs. Changing this on ZEN and ZEN2 moved too slow predictions into perfect or a little too fast regions.

# sumreduction and gs-2d-5pt: overlapping iterations
If the compile was unable to remove the dependency chain in this kernel, performance can still exceed predictions because of the way benchmarks were run. With short inner ("kernel") and long outer ("repeat") loop, kernel iterations can overlap and lead to better-than-predicted measurments (which would normally contradict the model assumptions). The measured performance converges towards the prediction

### Special knowlege on scheduling
('IVB','clang', 'O3','3d-7pt')

IACA predicts Port5 as Bottleneck and thus a throughput which fits measurment. Ports 1 and 2 could theoretically take load from Port 5, if perfectly scheduled, because all  instructions on Port 5 could also be executed on Ports 1 and 2. The scheduling decision is unexplained, but the relevant instructions are all on the critical path, this could mean that instructions reusing results of previous are preferrably scheduled on the same port.


### Frontend bottlenecks
IACA models the front end and therefore predicts better in scenarios where this is the bottleneck.

### Pre Indexed
idx = ('TX2','gcc', 'O2','gs-2d-5pt')
decent with pre-indexed support

### Undetected memory dependency
('A64FX','gcc', 'O1','gs-2d-5pt')

### ZEN2: Stragen Load throughput
build/ZEN2/clang/O3/3d-27pt.marked.s
is almost perfectly predicted by LLVM-MCA, because `vaddsd` is assigned by it to a single prot. This contradicts micro-benchmarks, where `vaddsd` has a throughput of 0.5 cy. The kernel is also heavy on loads

Checking with the ('ZEN2','clang', 'Ofast','copy') kernel, which is load/store bound with vector instructions, reveals that both LLVM-MCA and OSACA can not predict it well (33% and 27% relative error).

1cy/load ('ZEN2','icc', 'Ofast','copy') with  vmovupd (%r8,%rax,8), %ymm0; vmovupd %ymm0, (%rdx,%rax,8)
  400f83:       c4 c1 7d 10 04 c0       vmovupd (%r8,%rax,8),%ymm0
  400f89:       c5 fd 11 04 c2          vmovupd %ymm0,(%rdx,%rax,8)
  400f8e:       48 83 c0 04             add    $0x4,%rax
  400f92:       49 3b c1                cmp    %r9,%rax
  400f95:       72 ec                   jb     400f83 <kernel+0xe3>
2cy/load ('ZEN2','gcc', 'Ofast','copy') with  vmovupd (%r15,%rax), %ymm1; vmovupd %ymm1, (%rdx,%rax)
  400df0:       c4 c1 7d 10 0c 07       vmovupd (%r15,%rax,1),%ymm1
  400df6:       c5 fd 11 0c 02          vmovupd %ymm1,(%rdx,%rax,1)
  400dfb:       48 83 c0 20             add    $0x20,%rax
  400dff:       48 39 d8                cmp    %rbx,%rax
  400e02:       75 ec                   jne    400df0 <kernel+0xd0>
2cy/load ('ZEN2','clang', 'Ofast','copy') with 4x unrolled  vmovups (%rbp,%rax,8), %ymm0; vmovups %ymm0, (%rdi,%rax,8)
  4009e0:       c5 fc 10 44 c5 00       vmovups 0x0(%rbp,%rax,8),%ymm0
  4009e6:       c5 fc 10 4c c5 20       vmovups 0x20(%rbp,%rax,8),%ymm1
  4009ec:       c5 fc 10 54 c5 40       vmovups 0x40(%rbp,%rax,8),%ymm2
  4009f2:       c5 fc 10 5c c5 60       vmovups 0x60(%rbp,%rax,8),%ymm3
  4009f8:       c5 fc 11 04 c7          vmovups %ymm0,(%rdi,%rax,8)
  4009fd:       c5 fc 11 4c c7 20       vmovups %ymm1,0x20(%rdi,%rax,8)
  400a03:       c5 fc 11 54 c7 40       vmovups %ymm2,0x40(%rdi,%rax,8)
  400a09:       c5 fc 11 5c c7 60       vmovups %ymm3,0x60(%rdi,%rax,8)
  400a0f:       48 83 c0 10             add    $0x10,%rax
  400a13:       49 39 c5                cmp    %rax,%r13
  400a16:       75 c8                   jne    4009e0 <kernel+0x90>
1cy/load likwid-bench -t copy_avx -w S0:8kB:1
    bbc0:       c5 fc 28 0c c6          vmovaps (%rsi,%rax,8),%ymm1
    bbc5:       c5 fc 28 54 c6 20       vmovaps 0x20(%rsi,%rax,8),%ymm2
    bbcb:       c5 fc 28 5c c6 40       vmovaps 0x40(%rsi,%rax,8),%ymm3
    bbd1:       c5 fc 28 64 c6 60       vmovaps 0x60(%rsi,%rax,8),%ymm4
    bbd7:       c5 fc 29 0c c2          vmovaps %ymm1,(%rdx,%rax,8)
    bbdc:       c5 fc 29 54 c2 20       vmovaps %ymm2,0x20(%rdx,%rax,8)
    bbe2:       c5 fc 29 5c c2 40       vmovaps %ymm3,0x40(%rdx,%rax,8)
    bbe8:       c5 fc 29 64 c2 60       vmovaps %ymm4,0x60(%rdx,%rax,8)
    bbee:       48 83 c0 10             add    $0x10,%rax
    bbf2:       48 39 f8                cmp    %rdi,%rax
    bbf5:       7c c9                   jl     bbc0 <copy_avx+0x40>

### Update Kernel: FrontEnd and Branch TP limit
On Zen2 the update kernel is preticted 50% faster, because OSACA does not see a bottleneck due to short loop body. When unrolled, the performance increases and is well predicted.

On SKX unrolling and wider SIMD does not give better performance 

"The fused branch instructions can execute at a throughput of two such branches per clock
cycle if they are not taken, or one branch per two clock cycles if taken" (21.4., Agner Fog)

### Store AGU usage on ZEN
When looking at predictions of the copy kernel, it became clear that the AGUs for store also required to µops if a 256-bit wide store was issued and two addresses need to be generated.