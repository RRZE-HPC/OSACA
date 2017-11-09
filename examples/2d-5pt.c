
void jacobi2D5pt(int N, int M){
    void dummy(double*, double*);
    double a[M][N];
    double b[M][N];
    double s;

    for(int j=1; j<M-1; ++j){
        #pragma vector aligned
        //STARTLOOP
        for(int i=1; i<N-1; ++i){
            b[j][i] = ( a[j][i-1] + a[j][i+1] + a[j-1][i] + a[j+1][i]) * s;
        }
    }   
    dummy(&a[1][1], &b[1][1]);
}
