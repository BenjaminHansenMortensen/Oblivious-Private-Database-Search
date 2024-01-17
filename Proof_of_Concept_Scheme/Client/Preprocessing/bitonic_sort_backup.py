from numpy import random
from math import log
from pathlib import Path
from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory


def compare(indexing: list, index: int, permutation: list,
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


def init(indexing: list, permutation: list):
    """

    :return:
    """

    partition_size = 2
    partition_mid_point = partition_size // 2

    descending = False
    for index in range(0, database_size(), partition_size):

        #   Parallelizable to log_2(n) processes
        compare(indexing, index, permutation, descending, partition_mid_point)

        descending = (descending + 1) % 2


def merge_partition(indexing: list, descending: bool, permutation: list, partition_index: int, partition_mid_point: int):
    """

    :return:
    """

    for value in range(partition_mid_point):
        index = partition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(indexing, index, permutation, descending, partition_mid_point)


def merge(indexing: list, permutation: list, partition_size, partition_mid_point: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        merge_partition(indexing, descending, permutation, partition_index, partition_mid_point)

        descending = (descending + 1) % 2


def sort_subpartition(indexing: list, permutation: list,descending: bool, partition_index: int, subpartition_index: int,
                      subpartition_mid_point: int):
    """

    :return:
    """

    for value in range(subpartition_mid_point):
        index = partition_index + subpartition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(indexing, index, permutation, descending, subpartition_mid_point)


def sort_partition(indexing: list, permutation: list, descending: bool, partition_size: int, partition_index: int):
    """

    :return:
    """

    for sublevel in range(-int(log(partition_size, 2)) + 1, 0):
        subpartition_size = 2 ** (sublevel * -1)
        subpartition_mid_point = subpartition_size // 2

        for subpartition_index in range(0, partition_size, subpartition_size):

            #  Parallelizable to log_(subpartition_size)(n) processes
            sort_subpartition(indexing, permutation, descending, partition_index, subpartition_index,
                              subpartition_mid_point)


def sort(indexing: list, permutation: list, partition_size: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        sort_partition(indexing, permutation, descending, partition_size, partition_index)

        descending = (descending + 1) % 2


def bitonic_sort() -> dict:
    """

    :param array_size:
    :param working_directory:
    :return:
    """

    if not log(database_size(), 2).is_integer():
        raise ValueError("Array size has to be of power 2.")

    # Creates a new indexing
    indexing = [i for i in range(database_size())]
    permutation = random.permutation(database_size()).tolist()
    permuted_indexing = dict(zip(indexing, permutation))

    # Initializes the encrypted databases and sorts the first level
    init(indexing, permutation)

    # Completes the sorting of the encrypted database
    for level in range(2, int(log(database_size(), 2) + 1)):  # Skip 2**1 as it was done in the initiation
        partition_size = 2 ** level
        partition_mid_point = partition_size // 2

        merge(indexing, permutation, partition_size, partition_mid_point)

        sort(indexing, permutation, partition_size)

    return permuted_indexing
