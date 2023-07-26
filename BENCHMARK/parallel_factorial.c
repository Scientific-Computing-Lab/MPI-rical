#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    int num = 10; // Change this number to compute the factorial of a different value

    if (num <= 0) {
        if (rank == 0) {
            printf("Invalid input: The number must be a positive integer.\n");
        }
        MPI_Finalize();
        return 1;
    }

    // Calculate the number of iterations for each process
    int iterations_per_process = num / size;
    int remaining_iterations = num % size;
    int start_iteration = rank * iterations_per_process + 1;
    int end_iteration = (rank == size - 1) ? num : (rank + 1) * iterations_per_process;

    long long local_factorial = 1;
    for (int i = start_iteration; i <= end_iteration; i++) {
        local_factorial *= i;
    }

    // Perform the partial reduction operation to get the local factorial for each process
    long long* local_factorials = (long long*)malloc(size * sizeof(long long));
    MPI_Allgather(&local_factorial, 1, MPI_LONG_LONG, local_factorials, 1, MPI_LONG_LONG, MPI_COMM_WORLD);

    // Calculate the total factorial in the root process (rank 0)
    long long total_factorial = 1;
    if (rank == 0) {
        for (int i = 0; i < size; i++) {
            total_factorial *= local_factorials[i];
        }
    }

    if (rank == 0) {
        printf("Factorial of %d is: %lld\n", num, total_factorial);
    }

    free(local_factorials);
    MPI_Finalize();
    return 0;
}
