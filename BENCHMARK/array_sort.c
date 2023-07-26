#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#define ARRAY_SIZE 100

void merge(int arr[], int left, int mid, int right) {
    int i, j, k;
    int n1 = mid - left + 1;
    int n2 = right - mid;

    int* L = (int*)malloc(n1 * sizeof(int));
    int* R = (int*)malloc(n2 * sizeof(int));

    for (i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];

    i = 0;
    j = 0;
    k = left;

    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        }
        else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }

    // Free the dynamically allocated memory
    free(L);
    free(R);
}

void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;

        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);

        merge(arr, left, mid, right);
    }
}

int main(int argc, char* argv[]) {
    MPI_Init(&argc, &argv);
    int size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    // Generate some random data
    int* local_array = (int*)malloc(ARRAY_SIZE / size * sizeof(int));
    for (int i = 0; i < ARRAY_SIZE / size; ++i) {
        local_array[i] = rand() % 100;
    }

    // Perform local merge sort
    mergeSort(local_array, 0, ARRAY_SIZE / size - 1);

    // Gather all sorted subarrays to root process
    int* sorted_array = NULL;
    if (rank == 0) {
        sorted_array = (int*)malloc(ARRAY_SIZE * sizeof(int));
    }

    MPI_Gather(local_array, ARRAY_SIZE / size, MPI_INT, sorted_array, ARRAY_SIZE / size, MPI_INT, 0, MPI_COMM_WORLD);

    // Perform final merge sort on root process
    if (rank == 0) {
        mergeSort(sorted_array, 0, ARRAY_SIZE - 1);

        printf("Sorted Array:\n");
        for (int i = 0; i < ARRAY_SIZE; ++i) {
            printf("%d ", sorted_array[i]);
        }
        printf("\n");

        free(sorted_array);
    }

    // Clean up
    free(local_array);
    MPI_Finalize();
    return 0;
}
