#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Specify the total number of elements for domain decomposition
    const int total_elements = 100;
    const int elements_per_process = total_elements / size;

    // Calculate the start and end indices for each process
    int start_index = rank * elements_per_process;
    int end_index = (rank + 1) * elements_per_process;
    if (rank == size - 1) {
        // Last process may have more elements if total_elements % size != 0
        end_index = total_elements;
    }

    // Seed the random number generator with a unique seed for each process
    srand(rank);

    // Generate random data for each process
    int* local_array = (int*)malloc(elements_per_process * sizeof(int));
    for (int i = start_index; i < end_index; ++i) {
        local_array[i - start_index] = rand() % 100;
    }

    // Calculate the sum of local_array
    int local_sum = 0;
    for (int i = 0; i < elements_per_process; ++i) {
        local_sum += local_array[i];
    }

    // Perform the reduction operation to get the global sum
    int global_sum = 0;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    // Calculate the average
    double average = (double)global_sum / total_elements;

    if (rank == 0) {
        printf("Average value: %lf\n", average);
    }

    // Clean up
    free(local_array);
    MPI_Finalize();
    return 0;
}