#ifdef MAIN
#include <stdio.h>
#include <stdlib.h>
#include <likwid.h>
#ifdef __ARM_FEATURE_SVE
#include <sys/prctl.h>
#endif
#endif

#define USE_IACA 0

#if USE_IACA
#include "intel\iacaMarks.h"
#endif

#define DTYPE double

void dummy(void *);

void kernel(DTYPE* a, DTYPE* b, DTYPE* c, const DTYPE s, const int repeat, const int cur_elements)
#ifndef MAIN
{
    for(int r=0; r < repeat; r++) {
        for(int i=0; i<cur_elements; i++) {
#if USE_IACA
            IACA_VC64_START
#endif
            a[i] = b[i] + s * c[i];
#if USE_IACA
            IACA_VC64_END
#endif
        }
        dummy((void*)a);
    }
}
#else
;
int main(int argc, char *argv[]) {
    if(argc < 2) {
        printf("Usage: %s (repeat elements)...\n", argv[0]);
        return 1;
    }
    const int tests = (argc-1) / 2;
    int repeats[tests];
    int elements[tests];
    int maxelements = 0;
    for(int t=0; t<tests; t++) {
        repeats[t] = atoi(argv[1+t*2]);
        elements[t] = atoi(argv[2+t*2]);
        if(maxelements < elements[t]) {
            maxelements = elements[t];
        }
    }
    printf("kernel: triad\n");
    printf("elementsize: %lu\n", sizeof(DTYPE));
#ifdef __ARM_FEATURE_SVE
    int vl_in_bytes = prctl(PR_SVE_GET_VL) & PR_SVE_VL_LEN_MASK;
    printf("vector length: %d bits\n", vl_in_bytes*8);
#endif

    //SETUP
    DTYPE* a = malloc(maxelements*sizeof(DTYPE));
    DTYPE* b = malloc(maxelements*sizeof(DTYPE));
    DTYPE* c = malloc(maxelements*sizeof(DTYPE));
    for(int i=0; i<maxelements; i++) {
        a[i] = i;
        b[i] = maxelements-i;
        c[i] = 12.34;
    }

    likwid_markerInit();

    char cur_region_name[128];
    for(int t=0; t<tests; t++) {
        const int cur_elements = elements[t];
        const int cur_repeats = repeats[t];
        sprintf(cur_region_name, "triad_%i_%i", cur_repeats, cur_elements);
        likwid_markerRegisterRegion(cur_region_name);
        printf("%s:iterations: %i\n", cur_region_name, cur_elements);
        printf("%s:repetitions: %i\n", cur_region_name, cur_repeats);

        for(int warmup = 1; warmup >= 0; --warmup) {
            int repeat = 2;
            if(warmup == 0) {
                repeat = cur_repeats;
                likwid_markerStartRegion(cur_region_name);
            }

            kernel(a, b, c, 1.234, repeat, cur_elements);
        }
        likwid_markerStopRegion(cur_region_name);
    }
    likwid_markerClose();
    free(a);
    return 0;
}
#endif
