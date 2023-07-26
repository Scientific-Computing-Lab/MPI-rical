#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#define ARRAY_SIZE 1000000

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Calculate the number of elements each process will handle
    int elements_per_process = ARRAY_SIZE / size;
    int remaining_elements = ARRAY_SIZE % size;
    int start_index = rank * elements_per_process;
    int end_index = start_index + elements_per_process;

    // For the last process, add remaining elements to its local array
    if (rank == size - 1) {
        end_index += remaining_elements;
    }

    // Generate a local random array for each process
    int* local_array = (int*)malloc((end_index - start_index) * sizeof(int));
    for (int i = 0; i < end_index - start_index; ++i) {
        local_array[i] = rand() % 100;
    }

    // Calculate the local sum
    long long local_sum = 0;
    for (int i = 0; i < end_index - start_index; ++i) {
        local_sum += local_array[i];
    }

    // Perform the reduction operation to get the global sum
    long long global_sum = 0;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_LONG_LONG, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Global Sum: %lld\n", global_sum);
    }

    // Clean up
    free(local_array);
    MPI_Finalize();
    return 0;
}
