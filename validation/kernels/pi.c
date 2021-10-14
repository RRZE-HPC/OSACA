#ifdef MAIN
#include <stdio.h>
#include <stdlib.h>
#include <likwid.h>
#endif

#define DTYPE double

void dummy(void *);

double kernel(const int slices)
#ifndef MAIN
{
    const double delta_x = 1./slices;
    double x, sum = 0;
    for(int i=0; i<slices; i++) {
        x = (i + 0.5) * delta_x;
        sum = sum + 4.0 / (1.0 + x * x);
    }
    dummy((void*)&x);
    return sum * delta_x;
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
    printf("kernel: pi\n");
    printf("elementsize: %lu\n", sizeof(DTYPE));
    
    //SETUP

    likwid_markerInit();

    char cur_region_name[128];
    for(int t=0; t<tests; t++) {
        const int cur_slices = elements[t];
        const int cur_repeats = repeats[t];
        sprintf(cur_region_name, "pi_%i_%i", cur_repeats, cur_slices);
        likwid_markerRegisterRegion(cur_region_name);
        printf("%s:iterations: %i\n", cur_region_name, cur_slices);
        printf("%s:repetitions: %i\n", cur_region_name, cur_repeats);

        for(int warmup = 1; warmup >= 0; --warmup) {
            int repeat = 2;
            if(warmup == 0) {
                repeat = cur_repeats;
                likwid_markerStartRegion(cur_region_name);
            }

            kernel(cur_slices*repeat);
        }
        likwid_markerStopRegion(cur_region_name);
    }
    likwid_markerClose();
    return 0;
}
#endif