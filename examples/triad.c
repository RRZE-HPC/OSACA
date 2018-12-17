
void triad(int N){
    void dummy(double*);
    double a[N], b[N], c[N], d[N];
    double s;

    //STARTLOOP
    for(int i=0; i<N; ++i)
        a[i] = b[i] + c[i] * d[i];
    
    dummy(&a[1]);
}
