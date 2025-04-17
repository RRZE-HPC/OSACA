// STREAM triad benchmark for RISC-V testing
// a[i] = b[i] + s * c[i]

#include <stdio.h>
#include <stdlib.h>

#define DTYPE double

void kernel(DTYPE* a, DTYPE* b, DTYPE* c, const DTYPE s, const int size)
{
    // OSACA start marker will be added around this loop
    for(int i=0; i<size; i++) {
        a[i] = b[i] + s * c[i];
    }
    // OSACA end marker will be added
}

int main(int argc, char *argv[]) {
    int size = 1000;
    if(argc > 1) {
        size = atoi(argv[1]);
    }
    
    printf("RISC-V STREAM triad: a[i] = b[i] + s * c[i], size=%d\n", size);
    
    // Allocate memory
    DTYPE* a = (DTYPE*)malloc(size * sizeof(DTYPE));
    DTYPE* b = (DTYPE*)malloc(size * sizeof(DTYPE));
    DTYPE* c = (DTYPE*)malloc(size * sizeof(DTYPE));
    
    // Initialize arrays
    for(int i=0; i<size; i++) {
        a[i] = 0.0;
        b[i] = i;
        c[i] = i * 2.0;
    }
    
    // Run kernel
    DTYPE scalar = 3.14;
    kernel(a, b, c, scalar, size);
    
    // Check result (to prevent optimization)
    DTYPE checksum = 0.0;
    for(int i=0; i<size; i++) {
        checksum += a[i];
    }
    printf("Checksum: %f\n", checksum);
    
    // Cleanup
    free(a);
    free(b);
    free(c);
    
    return 0;
} 