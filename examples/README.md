# Examples
We collected sample kernels for the user to run examples with OSACA.
The assembly files contain only the extracted and already marked kernel for code compiled with on Intel Cascade Lake&nbsp;(CSX), AMD Zen and Marvell ThunderX2&nbsp;(TX2), but can be run on any system supporting the ISA and supported by OSACA.
The used compilers were Intel Parallel Studio&nbsp;19.0up05 and GNU&nbsp;9.1.0 in case of the x86 systems and ARM HPC Compiler for Linux version&nbsp;19.2 and GNU&nbsp;8.2.0 for the ARM-based TX2.

To analyze the kernels with OSACA, run
```
osaca --arch ARCH filepath
```
While all Zen and TX2 kernels use the comment-style OSACA markers, the kernels for Intel Cascade Lake (*.csx.*.s) use the byte markers to be able to be analyzed by IACA as well.
For this use
```
iaca -arch SKX filepath
```

------------
The kernels will be explained briefly in the following.

### Copy
```c
double * restrict a, * restrict b;

for(long i=0; i < size; ++i){
    a[i] = b[i];
}
```

### Vector add

### Vector update

### Sum reduction

### DAXPY

### STREAM triad

### Schönauer triad

### Gauss-Seidel method

### Jacobi 2D

