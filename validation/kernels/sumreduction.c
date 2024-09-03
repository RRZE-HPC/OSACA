#ifdef MAIN
#include <stdio.h>
#include <stdlib.h>
#include <likwid.h>
#ifdef __ARM_FEATURE_SVE
#include <sys/prctl.h>
#endif
#endif

#define DTYPE double

void dummy(void *);

void kernel(DTYPE* a, const int repeat, const int cur_elements)
#ifndef MAIN
{
    for(int r=0; r < repeat; r++) {
        DTYPE s = 0;
        for(int i=0; i<cur_elements; i++) {
            s += a[i];
        }
        a[0] = s; // to prevent subsequent kernel executions to overlap
        dummy((void*)&s);
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
    printf("kernel: sumreduction\n");
    printf("elementsize: %lu\n", sizeof(DTYPE));
#ifdef __ARM_FEATURE_SVE
    int vl_in_bytes = prctl(PR_SVE_GET_VL) & PR_SVE_VL_LEN_MASK;
    printf("vector length: %d bits\n", vl_in_bytes*8);
#endif

    //SETUP
    DTYPE* a = malloc(maxelements*sizeof(DTYPE));
    for(int i=0; i<maxelements; i++) {
        a[i] = rand();
    }

    likwid_markerInit();

    char cur_region_name[128];
    for(int t=0; t<tests; t++) {
        const int cur_elements = elements[t];
        const int cur_repeats = repeats[t];
        sprintf(cur_region_name, "sumreduction_%i_%i", cur_repeats, cur_elements);
        likwid_markerRegisterRegion(cur_region_name);
        printf("%s:iterations: %i\n", cur_region_name, cur_elements);
        printf("%s:repetitions: %i\n", cur_region_name, cur_repeats);

        for(int warmup = 1; warmup >= 0; --warmup) {
            int repeat = 2;
            if(warmup == 0) {
                repeat = cur_repeats;
                likwid_markerStartRegion(cur_region_name);
            }

            kernel(a, repeat, cur_elements);
        }
        likwid_markerStopRegion(cur_region_name);
    }
    likwid_markerClose();
    free(a);
    return 0;
}
#endif
