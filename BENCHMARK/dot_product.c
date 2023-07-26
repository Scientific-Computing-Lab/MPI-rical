#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#define VECTOR_SIZE 100

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Generate two random vectors
    int* vectorA = (int*)malloc(VECTOR_SIZE * sizeof(int));
    int* vectorB = (int*)malloc(VECTOR_SIZE * sizeof(int));
    for (int i = 0; i < VECTOR_SIZE; ++i) {
        vectorA[i] = rand() % 100;
        vectorB[i] = rand() % 100;
    }

    // Calculate the local dot product
    int local_dot_product = 0;
    int elements_per_process = VECTOR_SIZE / size;
    int start_index = rank * elements_per_process;
    int end_index = (rank == size - 1) ? VECTOR_SIZE : (rank + 1) * elements_per_process;

    for (int i = start_index; i < end_index; ++i) {
        local_dot_product += vectorA[i] * vectorB[i];
    }

    // Perform the reduction operation to get the global dot product
    int global_dot_product = 0;
    MPI_Reduce(&local_dot_product, &global_dot_product, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Dot Product: %d\n", global_dot_product);
    }

    // Clean up
    free(vectorA);
    free(vectorB);
    MPI_Finalize();
    return 0;
}
