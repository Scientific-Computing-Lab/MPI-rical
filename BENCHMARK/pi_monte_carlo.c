#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#define TOTAL_POINTS 100000000

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    int local_points = TOTAL_POINTS / size;
    int local_inside_circle = 0;
    double x, y;

    // Perform Monte Carlo estimation in each process
    for (int i = 0; i < local_points; i++) {
        x = (double)rand() / RAND_MAX;
        y = (double)rand() / RAND_MAX;

        if (x * x + y * y <= 1.0) {
            local_inside_circle++;
        }
    }

    // Sum the local counts to get the total inside circle count for all processes
    int total_inside_circle = 0;
    MPI_Reduce(&local_inside_circle, &total_inside_circle, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    // Calculate the final estimation of π in the root process (rank 0)
    if (rank == 0) {
        double pi_estimate = 4.0 * total_inside_circle / TOTAL_POINTS;
        printf("Estimation of π: %.6f\n", pi_estimate);
    }

    MPI_Finalize();
    return 0;
}
