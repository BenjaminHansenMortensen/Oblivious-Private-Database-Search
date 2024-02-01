""" Permutes and shuffles the records using the oblivious sorting algorithm bitonic sort. """

# Imports.
from math import log
from numpy import random

# Local getters imports.
from Oblivious_Private_Database_Search.getters import (get_database_size as
                                                       database_size)


def compare_init(client, connection, index: int, permutation: list, descending: bool, midpoint: int) -> None:
    """ 
        Sorts and encrypts two records.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - index (int) : An index of a record to be evaluated.
            - permutation (list) : The order the records will be shuffled.
            - descending (bool) : Indicates the order the records should be sorted.
            - midpoint (int) : An index of a record to be evaluated.

        Returns:
            :raises
            -  
    """
    
    index_a, index_b = index, index + midpoint
    
    # Evaluates whether the records should be swapped or not.
    swap = False
    permutation_a, permutation_b = permutation[index_a], permutation[index_b]
    if (permutation_a > permutation_b and not descending) or (permutation_b > permutation_a and descending):
        permutation_a, permutation_b = permutation_b, permutation_a
        swap = True

    # Updates permutation.
    permutation[index_a], permutation[index_b] = permutation_a, permutation_b

    # Executes the mpc encryption and sorting.
    decrypt_first = False
    client.send_indices_and_encrypt(connection, swap, index_a, index_b, decrypt_first)

    return 


def compare(client, connection, index: int, permutation: list, descending: bool, midpoint: int) -> None:
    """
        Sorts and re-encrypts two records.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - index (int) : An index of a record to be evaluated.
            - permutation (list) : The order the records will be shuffled.
            - descending (bool) : Indicates the order the records should be sorted.
            - midpoint (int) : An index of a record to be evaluated.

        Returns:
            :raises
            -  
    """

    index_record_a, index_record_b = index, index + midpoint
    
    # Evaluates whether the records should be swapped or not.
    swap = False
    permutation_a, permutation_b = permutation[index], permutation[index + midpoint]
    if (permutation_a > permutation_b and not descending) or (permutation_b > permutation_a and descending):
        permutation_a, permutation_b = permutation_b, permutation_a
        swap = True

    # Updates permutation.
    permutation[index], permutation[index + midpoint] = permutation_a, permutation_b

    # Executes the mpc encryption and sorting.
    decrypt_first = True
    client.send_indices_and_encrypt(connection, swap, index_record_a, index_record_b, decrypt_first)

    return


def init(client, connection, permutation: list) -> None:
    """
        Performs the first layer of the bitonic sort and encrypts the records.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - permutation (list) : The order the records will be shuffled.

        Returns:
            :raises
            -  
    """

    partition_size = 2
    partition_midpoint = partition_size // 2

    descending = False
    for index in range(0, database_size(), partition_size):

        # Parallelizable
        compare_init(client, connection, index, permutation, descending, partition_midpoint)

        descending = (descending + 1) % 2
        
    return 


def merge_partition(client, connection, descending: bool, permutation: list, partition_index: int, partition_midpoint: int) -> None:
    """
        Merges two bitonic sequences.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - permutation (list) : The order the records will be shuffled.
            - partition_ex (int) : The first index of a partition.
            - partition_midpoint (int) : Midpoint of a partition.

        Returns:
            :raises
            -  
    """

    for value in range(partition_midpoint):
        index = partition_index + value

        # Parallelizable
        compare(client, connection, index, permutation, descending, partition_midpoint)
    
    return 


def merge(client, connection, permutation: list, partition_size, partition_midpoint: int) -> None:
    """
        Merges the bitonic sequences of a layer.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - permutation (list) : The order the records will be shuffled.
            - partition_size (int) : Size of the partition.
            - partition_midpoint (int) : Midpoint of a partition.

        Returns:
            :raises
            -  
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        # Parallelizable
        merge_partition(client, connection, descending, permutation, partition_index, partition_midpoint)

        descending = (descending + 1) % 2
        
    return 


def sort_subpartition(client, connection, permutation: list, descending: bool, partition_index: int,
                      subpartition_index: int, subpartition_midpoint: int) -> None:
    """
        Sorts the sub-partition into a bitonic sequences.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - permutation (list) : The order the records will be shuffled.
            - descending (bool) : Indicates the order the records should be sorted.
            - partition_index (int) : The first index of a partition.
            - subpartition_index (int) : The first index of a subpartition.
            - subpartition_midpoint (int) : The subpartition midpoint. 

        Returns:
            :raises
            -  
    """

    for value in range(subpartition_midpoint):
        index = partition_index + subpartition_index + value

        # Parallelizable
        compare(client, connection, index, permutation, descending, subpartition_midpoint)
    
    return 


def sort_partition(client, connection, permutation: list, descending: bool, partition_size: int, partition_index: int) -> None:
    """
        Sorts all sub-layers into bitonic sequences.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - permutation (list) : The order the records will be shuffled.
            - descending (bool) : Indicates the order the records should be sorted.
            - partition_size (int) : Size of the partition.
            - partition_index (int) : The first index of a partition.

        Returns:
            :raises
            -  
    """

    for sub_layer in range(-int(log(partition_size, 2)) + 1, 0):
        subpartition_size = 2 ** (sub_layer * -1)
        subpartition_midpoint = subpartition_size // 2

        for subpartition_index in range(0, partition_size, subpartition_size):

            # Parallelizable
            sort_subpartition(client, connection, permutation, descending, partition_index, subpartition_index,
                              subpartition_midpoint)
            
    return 


def sort(client, connection, permutation: list, partition_size: int) -> None:
    """
        Sorts a layer into bitonic sequences.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.
            - permutation (list) : The order the records will be shuffled.
            - partition_size (int) : Size of the partition.

        Returns:
            :raises
            -  
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        # Parallelizable
        sort_partition(client, connection, permutation, descending, partition_size, partition_index)

        descending = (descending + 1) % 2
        
    return 


def bitonic_sort(client, connection) -> dict[int, int]:
    """
        Performs a random oblivious shuffling of the server's records.

        Parameters:
            - client (Communicator) : The client.
            - connection (SSLSocket) : Connection with the server.

        Returns:
            :raises
            -  permutation_indexing (dict[int, int]) : The mapping from the original record indexing to their shuffled 
                                                       location.
    """

    if not log(database_size(), 2).is_integer():
        raise ValueError('Array size has to be of power 2.')

    # Creates new indexing of the shuffled records
    permutation = random.permutation(database_size()).tolist()
    permutation_indexing = dict(zip([str(i) for i in range(len(permutation))], permutation))

    # Encrypts the records and sorts the first layer
    init(client, connection, permutation)

    # Completes the sorting of the encrypted records
    for layer in range(2, int(log(database_size(), 2) + 1)):
        partition_size = 2 ** layer
        partition_midpoint = partition_size // 2

        merge(client, connection, permutation, partition_size, partition_midpoint)

        sort(client, connection, permutation, partition_size)

    return permutation_indexing
