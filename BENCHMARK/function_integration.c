#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <math.h>

#define NUM_INTERVALS 1000000000

double func(double x) {
    // Define the function whose integral needs to be calculated
    return x * x;
}

double integrate(double a, double b, int num_intervals) {
    double sum = 0.0;
    double dx = (b - a) / num_intervals;

    for (int i = 0; i < num_intervals; i++) {
        double x = a + (i + 0.5) * dx;
        sum += func(x);
    }

    return sum * dx;
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    double a = 0.0; // Lower limit of the integration
    double b = 1.0; // Upper limit of the integration

    double local_integral = integrate(a + (b - a) * rank / size, a + (b - a) * (rank + 1) / size, NUM_INTERVALS / size);

    double global_integral;
    MPI_Reduce(&local_integral, &global_integral, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Integral of the function from %.2f to %.2f: %.8f\n", a, b, global_integral);
    }

    MPI_Finalize();
    return 0;
}
