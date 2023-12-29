from numpy import random
from math import log
from pathlib import Path


def compare(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, index: int, permutation: list,
            descending: bool, mid_point: int):
    """

    :return:
    """

    a, b = indexing[index], indexing[index + mid_point]
    c, d = permutation[index], permutation[index + mid_point]

    if (c > d and not descending) or (d > c and descending):
        a, b = b, a
        c, d = d, c

    indexing[index], indexing[index + mid_point] = a, b
    permutation[index], permutation[index + mid_point] = c, d


def init(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, array_size: int, permutation: list):
    """

    :return:
    """

    partition_size = 2
    partition_mid_point = partition_size // 2

    descending = False
    for index in range(0, array_size, partition_size):

        #   Parallelizable to log_2(n) processes
        compare(indexing, working_directory, MP_SPDZ_directory, index, permutation, descending, partition_mid_point)

        descending = (descending + 1) % 2


def merge_partition(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, descending: bool,
                    permutation: list, partition_index: int, partition_mid_point: int):
    """

    :return:
    """

    for value in range(partition_mid_point):
        index = partition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(indexing, working_directory, MP_SPDZ_directory, index, permutation, descending, partition_mid_point)


def merge(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, array_size: int, permutation: list,
          partition_size, partition_mid_point: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, array_size, partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        merge_partition(indexing, working_directory, MP_SPDZ_directory, descending, permutation, partition_index,
                        partition_mid_point)

        descending = (descending + 1) % 2


def sort_subpartition(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, permutation: list,
                      descending: bool, partition_index: int, subpartition_index: int, subpartition_mid_point: int):
    """

    :return:
    """

    for value in range(subpartition_mid_point):
        index = partition_index + subpartition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(indexing, working_directory, MP_SPDZ_directory, index, permutation, descending, subpartition_mid_point)


def sort_partition(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, permutation: list,
                   descending: bool, partition_size: int, partition_index: int):
    """

    :return:
    """

    for sublevel in range(-int(log(partition_size, 2)) + 1, 0):
        subpartition_size = 2 ** (sublevel * -1)
        subpartition_mid_point = subpartition_size // 2

        for subpartition_index in range(0, partition_size, subpartition_size):

            #  Parallelizable to log_(subpartition_size)(n) processes
            sort_subpartition(indexing, working_directory, MP_SPDZ_directory, permutation, descending, partition_index,
                              subpartition_index, subpartition_mid_point)


def sort(indexing: list, working_directory: Path, MP_SPDZ_directory: Path, array_size: int, permutation: list,
         partition_size: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, array_size, partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        sort_partition(indexing, working_directory, MP_SPDZ_directory, permutation, descending, partition_size,
                       partition_index)

        descending = (descending + 1) % 2


def bitonic_sort(array_size: int, working_directory: Path,  MP_SPDZ_directory: Path,) -> dict:
    """

    :param array_size:
    :param working_directory:
    :return:
    """

    if not log(array_size, 2).is_integer():
        raise ValueError("Array size has to be of power 2.")

    # Creates a new indexing
    indexing = [i for i in range(array_size)]
    permutation = random.permutation(array_size).tolist()
    permuted_indexing = dict(zip(indexing, permutation))

    # Initializes the encrypted databases and sorts the first level
    init(indexing, working_directory, MP_SPDZ_directory, array_size, permutation)

    # Completes the sorting of the encrypted database
    for level in range(2, int(log(array_size, 2) + 1)):  # Skip 2**1 as it was done in the initiation
        partition_size = 2 ** level
        partition_mid_point = partition_size // 2

        merge(indexing, working_directory, MP_SPDZ_directory, array_size, permutation, partition_size,
              partition_mid_point)

        sort(indexing, working_directory, MP_SPDZ_directory, array_size, permutation, partition_size)

    return permuted_indexing
