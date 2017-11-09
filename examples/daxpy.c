
void daxpy(int N){
    void dummy(double*, double*);
    double a[N], b[N];
    double s;

    //STARTLOOP  
    for(int i=0; i<N; ++i)
            a[i] = a[i] + s * b[i];

    dummy(&a[1], &b[1]);
}

