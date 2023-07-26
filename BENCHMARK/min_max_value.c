#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

void printArray(int* arr, int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Generate some random data
    const int array_size = 100;
    srand(rank);
    int* local_array = (int*)malloc(array_size * sizeof(int));
    for (int i = 0; i < array_size; ++i) {
        local_array[i] = rand() % 100;
    }
   

    // Calculate the local minimum and maximum
    int local_min = local_array[0];
    int local_max = local_array[0];
    for (int i = 1; i < array_size; ++i) {
        if (local_array[i] < local_min) {
            local_min = local_array[i];
        }
        if (local_array[i] > local_max) {
            local_max = local_array[i];
        }
    }

    // Perform the reduction operation to get the global minimum and maximum
    int global_min, global_max;
    MPI_Allreduce(&local_min, &global_min, 1, MPI_INT, MPI_MIN, MPI_COMM_WORLD);
    MPI_Allreduce(&local_max, &global_max, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Global Minimum: %d\n", global_min);
        printf("Global Maximum: %d\n", global_max);
    }

    // Clean up
    free(local_array);
    MPI_Finalize();
    return 0;
}
