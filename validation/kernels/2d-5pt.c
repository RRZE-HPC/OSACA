#ifdef MAIN
#include <stdio.h>
#include <stdlib.h>
#include <likwid.h>
#endif

#define DTYPE double

void dummy(void *);

void kernel(DTYPE* a, DTYPE* b, const int repeat, const int cur_elementsy, const int cur_elementsx)
#ifndef MAIN
{
    for(int r=0; r < repeat; r++) {
        for(int y=1; y<cur_elementsy-1; y++) {
            for(int x=1; x<cur_elementsx-1; x++) {
                a[y*cur_elementsx+x] =
                    b[(y-1)*cur_elementsx+x] + 
                    b[y*cur_elementsx+x-1] +
                    b[y*cur_elementsx+x+1] +
                    b[(y+1)*cur_elementsx+x];
            }
        }
        double* c = a;
        a = b;
        b = c;
        dummy((void*)&a);
    }
}
#else
;
int main(int argc, char *argv[]) {
    if(argc < 2) {
        printf("Usage: %s (repeat elementsx)...\n", argv[0]);
        return 1;
    }
    const int tests = (argc-1) / 2;
    int repeats[tests];
    int elementsy[tests];
    int elementsx[tests];
    int maxproduct = 0;
    for(int t=0; t<tests; t++) {
        repeats[t] = atoi(argv[1+t*2]);
        elementsy[t] = 3;
        elementsx[t] = atoi(argv[2+t*2]);
        if(maxproduct < elementsy[t]*elementsx[t]) {
            maxproduct = elementsy[t]*elementsx[t];
        }
    }
    printf("kernel: 2d-5pt\n");
    printf("elementsize: %lu\n", sizeof(DTYPE));
    
    //SETUP
    DTYPE* a = malloc(maxproduct*sizeof(DTYPE));
    DTYPE* b = malloc(maxproduct*sizeof(DTYPE));
    for(int i=0; i<maxproduct; i++) {
        a[i] = i;
        b[i] = maxproduct-i;
    }

    likwid_markerInit();

    char cur_region_name[128];
    for(int t=0; t<tests; t++) {
        const int cur_elementsy = elementsy[t];
        const int cur_elementsx = elementsx[t];
        const int cur_repeats = repeats[t];
        sprintf(cur_region_name, "2d-5pt_%i_%i_%i", cur_repeats, cur_elementsy, cur_elementsx);
        likwid_markerRegisterRegion(cur_region_name);
        printf("%s:iterations: %i\n", cur_region_name, (cur_elementsy-2)*(cur_elementsx-2));
        printf("%s:repetitions: %i\n", cur_region_name, cur_repeats);

        for(int warmup = 1; warmup >= 0; --warmup) {
            int repeat = 2;
            if(warmup == 0) {
                repeat = cur_repeats;
                likwid_markerStartRegion(cur_region_name);
            }

            kernel(a, b, repeat, cur_elementsy, cur_elementsx);
        }
        likwid_markerStopRegion(cur_region_name);
    }
    likwid_markerClose();
    free(a);
    return 0;
}
#endif