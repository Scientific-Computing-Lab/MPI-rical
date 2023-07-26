#include <stdio.h>
#include <math.h>
#include <mpi.h>

#define NUM_INTERVALS 100000000

double f(double x) {
    return 4.0 / (1.0 + x * x);
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    double interval_width = 1.0 / NUM_INTERVALS;
    int local_intervals = NUM_INTERVALS / size;
    double local_sum = 0.0;

    for (int i = rank * local_intervals; i < (rank + 1) * local_intervals; i++) {
        double x = (i + 0.5) * interval_width;
        local_sum += f(x);
    }

    double global_sum;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        double pi = global_sum * interval_width;
        printf("Approximation of π: %lf\n", pi);
    }

    MPI_Finalize();
    return 0;
}
