#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#define MATRIX_SIZE 3
#define VECTOR_SIZE 3

void printMatrix(int matrix[MATRIX_SIZE][MATRIX_SIZE], int rows) {
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < MATRIX_SIZE; ++j) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
}

void printVector(int vector[VECTOR_SIZE]) {
    for (int i = 0; i < VECTOR_SIZE; ++i) {
        printf("%d ", vector[i]);
    }
    printf("\n");
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if (size != MATRIX_SIZE) {
        printf("This application is meant to be run with %d MPI processes.\n", MATRIX_SIZE);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // Define the matrix and vector
    int matrix[MATRIX_SIZE][MATRIX_SIZE] = { {1, 2, 3}, {4, 5, 6}, {7, 8, 9} };
    int vector[VECTOR_SIZE] = { 1, 2, 3 };

    // Calculate the local product (each process handles one row of the matrix)
    int local_product[VECTOR_SIZE] = { 0 };
    for (int i = 0; i < VECTOR_SIZE; ++i) {
        for (int j = 0; j < MATRIX_SIZE; ++j) {
            local_product[i] += matrix[rank][j] * vector[j];
        }
    }

    // Perform the reduction operation to get the global product (resultant vector)
    int global_product[VECTOR_SIZE] = { 0 };
    MPI_Allreduce(local_product, global_product, VECTOR_SIZE, MPI_INT, MPI_SUM, MPI_COMM_WORLD);

    if (rank == 0) {
        printf("Matrix:\n");
        printMatrix(matrix, MATRIX_SIZE);

        printf("Vector: ");
        printVector(vector);

        printf("Resultant Vector (Matrix-Vector product):\n");
        printVector(global_product);
    }

    MPI_Finalize();
    return 0;
}
