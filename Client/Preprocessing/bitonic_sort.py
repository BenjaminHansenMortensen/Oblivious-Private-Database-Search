from numpy import random
from math import log
from pathlib import Path
from subprocess import Popen
from os import chdir
from Oblivious_Database_Query_Scheme.getters import get_number_of_blocks as number_of_blocks
from Oblivious_Database_Query_Scheme.getters import get_block_size as block_size
from Oblivious_Database_Query_Scheme.getters import get_encoding_base as encoding_base
from Oblivious_Database_Query_Scheme.getters import get_database_size as database_size
from Oblivious_Database_Query_Scheme.getters import get_PNR_records_directory as PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_excluded_PNR_records as excluded_PNR_records
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_client_MP_SPDZ_input_path as client_MP_SPDZ_input_path
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_input_path as server_MP_SPDZ_input_path
from Oblivious_Database_Query_Scheme.getters import get_server_MP_SPDZ_output_path as server_MP_SPDZ_output_path
from Client.Preprocessing.key_stream_generator import get_key_streams
from Server.Encoding.file_encoder import encode_file


def twos_complement(hexadecimal_string: str):
    value = int(hexadecimal_string, encoding_base())
    if (value & (1 << (block_size() - 1))) != 0:
        value = value - (1 << block_size())
    return value


def write_as_MP_SPDZ_inputs(record: list[str], key_streams: list[str]):
    """  """

    with open(server_MP_SPDZ_input_path().parent / f"{server_MP_SPDZ_input_path()}-P0-0", 'w') as file:
        for block in range(len(record)):
            file.write(f"{twos_complement(record[block])} ")

    with open(client_MP_SPDZ_input_path().parent / f"{client_MP_SPDZ_input_path()}-P1-0", 'w') as file:
        for block in range(len(key_streams)):
            file.write(f"{twos_complement(key_streams[block])} ")


def encrypt_records():
    """  """

    chdir(MP_SPDZ_directory())

    server_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "xor",
                                    "-p", "0",
                                    "-IF", f"{server_MP_SPDZ_input_path()}",
                                    "-OF", f"{server_MP_SPDZ_output_path()}"]
                                   )
    client_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "xor",
                                    "-p", "1",
                                    "-IF", f"{client_MP_SPDZ_input_path()}"]
                                   )
    empty_party_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "xor",
                                    "-p", "2"]
                                   )
    server_MP_SPDZ_process.wait()
    client_MP_SPDZ_process.wait()
    empty_party_MP_SPDZ_process.wait()

    server_MP_SPDZ_process.kill()
    client_MP_SPDZ_process.kill()
    empty_party_MP_SPDZ_process.kill()

    chdir(working_directory())


def write_ciphertext_to_encrypted_database():
    """   """
    pass


def compare_init(encrypted_PNR_records_indexing: dict, index: int, permutation: list, descending: bool, mid_point: int):
    """  """

    a, b = encrypted_PNR_records_indexing[index], encrypted_PNR_records_indexing[index + mid_point]

    encoded_records = [encode_file(a), encode_file(b)]
    key_streams = [get_key_streams(), get_key_streams()]
    for i in range(len(encoded_records)):
        write_as_MP_SPDZ_inputs(encoded_records[i], key_streams[i])
        encrypt_records()
        write_ciphertext_to_encrypted_database()

    c, d = permutation[index], permutation[index + mid_point]
    if (c > d and not descending) or (d > c and descending):
        # Updates indexing
        a, b = b, a
        # Updates sorting
        c, d = d, c

    encrypted_PNR_records_indexing[index], encrypted_PNR_records_indexing[index + mid_point] = a, b
    permutation[index], permutation[index + mid_point] = c, d


def compare(encrypted_PNR_records_indexing: dict, index: int, permutation: list, descending: bool, mid_point: int):
    """

    :return:
    """
    # Grab names of index
    a, b = encrypted_PNR_records_indexing[index], encrypted_PNR_records_indexing[index + mid_point]
    c, d = permutation[index], permutation[index + mid_point]

    if (c > d and not descending) or (d > c and descending):
        a, b = b, a
        c, d = d, c
    # Update names of file at index
    encrypted_PNR_records_indexing[index], encrypted_PNR_records_indexing[index + mid_point] = a, b
    permutation[index], permutation[index + mid_point] = c, d


def init(indexing: dict, permutation: list):
    """

    :return:
    """

    partition_size = 2
    partition_mid_point = partition_size // 2

    descending = False
    for index in range(0, database_size(), partition_size):

        #   Parallelizable to log_2(n) processes
        compare_init(indexing, index, permutation, descending, partition_mid_point)

        descending = (descending + 1) % 2


def merge_partition(indexing: dict, descending: bool, permutation: list, partition_index: int, partition_mid_point: int):
    """

    :return:
    """

    for value in range(partition_mid_point):
        index = partition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(indexing, index, permutation, descending, partition_mid_point)


def merge(indexing: dict, permutation: list, partition_size, partition_mid_point: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        merge_partition(indexing, descending, permutation, partition_index, partition_mid_point)

        descending = (descending + 1) % 2


def sort_subpartition(indexing: dict, permutation: list,descending: bool, partition_index: int, subpartition_index: int,
                      subpartition_mid_point: int):
    """

    :return:
    """

    for value in range(subpartition_mid_point):
        index = partition_index + subpartition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(indexing, index, permutation, descending, subpartition_mid_point)


def sort_partition(indexing: dict, permutation: list, descending: bool, partition_size: int, partition_index: int):
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


def sort(indexing: dict, permutation: list, partition_size: int):
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
    from re import match, sub, findall, search

    # file_names = [path for path in PNR_records_directory().glob('*') if path.name not in excluded()]
    # Sorting the record names for clarity so that it matches its index
    file_names = sorted([path for path in PNR_records_directory().glob('*') if path.name not in excluded_PNR_records()],
                        key=lambda x: int(findall(r"\d+", string=x.name)[0]))
    secret_database_indexing = dict(enumerate(file_names))
    # permutation = random.permutation(database_size()).tolist()
    permutation = [2, 5, 4, 6, 3, 0, 7, 1]
    index_translation = dict(zip(secret_database_indexing.keys(), permutation))

    # Initializes the encrypted databases and sorts the first level
    init(secret_database_indexing, permutation)

    # Completes the sorting of the encrypted database
    for level in range(2, int(log(database_size(), 2) + 1)):  # Skip 2**1 as it was done in the initiation
        partition_size = 2 ** level
        partition_mid_point = partition_size // 2

        merge(secret_database_indexing, permutation, partition_size, partition_mid_point)

        sort(secret_database_indexing, permutation, partition_size)

    return index_translation
