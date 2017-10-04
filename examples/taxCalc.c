#include <stdio.h>
//#include "iacaMarks.h"

int main(void){
    printf("OSACA test start\n");
    int i = 1;
    float arr[1000];
    float tax = 0.19;
    arr[0] = 0;
    //STARTLOOP
    while(i < 1000){
        arr[i] = arr[i-1]+i*tax;
        i += 1;
    }

    printf("OSACA test end\n");
    return 0;
}
