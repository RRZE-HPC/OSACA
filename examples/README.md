# Examples
We collected sample kernels for the user to run examples with OSACA.
The assembly files contain only the extracted and already marked kernel for code compiled with on Intel Cascade Lake&nbsp;(CSX), AMD Zen and Marvell ThunderX2&nbsp;(TX2), but can be run on any system supporting the ISA and supported by OSACA.
The used compilers were Intel Parallel Studio&nbsp;19.0up05 and GNU&nbsp;9.1.0 in case of the x86 systems and ARM HPC Compiler for Linux version&nbsp;19.2 and GNU&nbsp;8.2.0 for the ARM-based TX2.

To analyze the kernels with OSACA, run
```
osaca --arch ARCH FILE
```
While all Zen and TX2 kernels use the comment-style OSACA markers, the kernels for Intel Cascade Lake (*.csx.*.s) use the byte markers to be able to be analyzed by IACA as well.
For this use
```
gcc -c FILE.s
iaca -arch SKX FILE.o
```

------------
The kernels currently contained in the examples are shown briefly in the following.

### Copy (`copy/`)
```c
double * restrict a, * restrict b;

for(long i=0; i < size; ++i){
    a[i] = b[i];
}
```

### Vector add (`add/`)
```c
double * restrict a, * restrict b, * restrict c;

for(long i=0; i < size; ++i){
    a[i] = b[i] + c[i];
}
```

### Vector update (`update/`)
```c
double * restrict a;

for(long i=0; i < size; ++i){
    a[i] = scale * a[i];
}
```

### Sum reduction (`sum_reduction/`)
```c
double * restrict a;

for(long i=0; i < size; ++i){
    scale = scale + a[i];
}
```
For this kernel we noticed an overlap of the loop bodies when using gcc with `-Ofast` flag (see this [blog post](https://blogs.fau.de/hager/archives/7658) for more information).
We therefore compiled all gcc version additionally with `-O3` flag instead.
These versions are named accordingly.

### DAXPY (`daxpy/`)
```c
double * restrict a, * restrict b;

for(long i=0; i < size; ++i){
    a[i] = a[i] + scale * b[i];
}
```

### STREAM triad (`triad/`)
```c
double * restrict a, * restrict b, * restrict c;

for(long i=0; i < size; ++i){
    a[i] = b[i] + scale * c[i];
}
```

### Schönauer triad (`striad/`)
```c
double * restrict a, * restrict b, * restrict c, *  restrict d;

for(long i=0; i < size; ++i){
    a[i] = b[i] + c[i] * d[i];
}
```

### Gauss-Seidel method (`gs/`)
```c
double ** restrict a;

for(long k=1; k < size_k-1; ++k){
  for(long i=1; i < size_i-1; ++i){
    a[k][i] = scale * (
      a[k][i-1] + a[k+1][i]
      + a[k][i+1] + a[k-1][i]
    );
  }
}
```

### Jacobi 2D (`j2d/`)
```c
double ** restrict a, ** restrict b;

for(long k=1; k < size_k-1; ++k){
  for(long i=1; i < size_i-1; ++i){
    a[k][i] = 0.25 * (
      b[k][i-1] + b[k+1][i]
      + b[k][i+1] + b[k-1][i]
    );
  }
}
```
For this kernel we noticed a discrepancy between measurements and predcitions especially when using AVX-512 instructions.
We therefore compiled the x86 kernels additionally with AVX/SSE instruction and marekd those kernels accordingly.
