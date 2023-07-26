#include <stdio.h>
#include <mpi.h>

int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    int n = 10; // Calculate Fibonacci sequence up to the 10th element

    if (rank == 0) {
        printf("Calculating Fibonacci sequence up to the %dth element.\n", n);
    }

    // Divide the work among processes using domain decomposition
    int local_n = n / size; // Number of elements each process calculates
    int start = rank * local_n + 1; // Start index for the current process
    int end = (rank + 1) * local_n; // End index (inclusive) for the current process

    if (rank == size - 1) {
        // Handle the remainder elements for the last process
        end = n;
    }

    int local_result = 0;
    for (int i = start; i <= end; i++) {
        local_result += fibonacci(i);
    }

    int global_result;
    MPI_Reduce(&local_result, &global_result, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Sum of the Fibonacci sequence up to the %dth element: %d\n", n, global_result);
    }

    MPI_Finalize();
    return 0;
}
