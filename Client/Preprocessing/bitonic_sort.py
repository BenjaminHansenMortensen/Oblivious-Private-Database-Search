from math import log
from subprocess import Popen, PIPE
from os import chdir
from re import findall
from pathlib import Path
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
    """  """
    value = int(hexadecimal_string, encoding_base())
    if (value & (1 << (block_size() - 1))) != 0:
        value = value - (1 << block_size())
    return value


def write_as_MP_SPDZ_inputs(swap: int, records: list[list[str]], key_streams: list[list[str]],
                            new_key_stream: list[list[str]] = None):
    """  """

    with open(server_MP_SPDZ_input_path().parent / f"{server_MP_SPDZ_input_path()}-P0-0", 'w') as file:
        for i in range(len(records)):
            for block in range(len(records[i])):
                file.write(f"{twos_complement(records[i][block])} ")
            file.write("\n")
        file.close()

    with open(client_MP_SPDZ_input_path().parent / f"{client_MP_SPDZ_input_path()}-P1-0", 'w') as file:
        file.write(f"{swap} \n")
        for i in range(len(key_streams)):
            for block in range(len(key_streams[i])):
                file.write(f"{twos_complement(key_streams[i][block])} ")
            file.write("\n")
        if new_key_stream:
            for i in range(len(new_key_stream)):
                for block in range(len(new_key_stream[i])):
                    file.write(f"{twos_complement(new_key_stream[i][block])} ")
                file.write("\n")
        file.close()


def encrypt_record():
    """  """

    chdir(MP_SPDZ_directory())

    server_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "compare_and_encrypt",
                                    "-p", "0",
                                    "-IF", f"{server_MP_SPDZ_input_path()}",
                                    "-OF", f"{server_MP_SPDZ_output_path()}"]
                                   ,stdout=PIPE, stderr=PIPE
                                   )
    client_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "compare_and_encrypt",
                                    "-p", "1",
                                    "-IF", f"{client_MP_SPDZ_input_path()}"]
                                    , stdout=PIPE, stderr=PIPE
                                   )
    empty_party_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "compare_and_encrypt",
                                    "-p", "2"]
                                    , stdout=PIPE, stderr=PIPE
                                   )

    server_output, server_error = server_MP_SPDZ_process.communicate()
    client_output, client_error = client_MP_SPDZ_process.communicate()
    empty_party_output, empty_party_error = empty_party_MP_SPDZ_process.communicate()

    #server_MP_SPDZ_process.wait()
    #client_MP_SPDZ_process.wait()
    #empty_party_MP_SPDZ_process.wait()

    server_MP_SPDZ_process.kill()
    client_MP_SPDZ_process.kill()
    empty_party_MP_SPDZ_process.kill()

    chdir(working_directory())


def reencrypt_record():
    """  """

    chdir(MP_SPDZ_directory())

    server_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "compare_and_reencrypt",
                                    "-p", "0",
                                    "-IF", f"{server_MP_SPDZ_input_path()}",
                                    "-OF", f"{server_MP_SPDZ_output_path()}"]
                                    , stdout=PIPE, stderr=PIPE
                                   )
    client_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "compare_and_reencrypt",
                                    "-p", "1",
                                    "-IF", f"{client_MP_SPDZ_input_path()}"]
                                    , stdout=PIPE, stderr=PIPE
                                   )
    empty_party_MP_SPDZ_process = Popen([f"{MP_SPDZ_directory() / 'replicated-field-party.x'}",
                                    "compare_and_reencrypt",
                                    "-p", "2"]
                                    , stdout=PIPE, stderr=PIPE
                                   )

    server_output, server_error = server_MP_SPDZ_process.communicate()
    client_output, client_error = client_MP_SPDZ_process.communicate()
    empty_party_output, empty_party_error = empty_party_MP_SPDZ_process.communicate()

    #server_MP_SPDZ_process.wait()
    #client_MP_SPDZ_process.wait()
    #empty_party_MP_SPDZ_process.wait()

    server_MP_SPDZ_process.kill()
    client_MP_SPDZ_process.kill()
    empty_party_MP_SPDZ_process.kill()

    chdir(working_directory())


def write_MP_SDPZ_output_to_encrypted_database(file_names: list[str]):
    """   """

    with open(server_MP_SPDZ_output_path().parent / f"{server_MP_SPDZ_output_path().name}-P0-0", "r") as file:
        hexadecimals_pattern = r"0x([a-fA-F0-9]+)"
        ciphertexts = findall(hexadecimals_pattern, file.read())
        file.close()

    for i in range(len(file_names)):
        with open(encrypted_PNR_records_directory() / file_names[i], "w") as file:
            file.write(' '.join(ciphertexts[i * number_of_blocks(): (i + 1) * number_of_blocks()]))
            file.close()


def read_ciphertexts(file_path: Path) -> list[str]:
    """  """

    if not file_path.exists() and not file_path.is_file():
        raise FileNotFoundError(f"Did not find file at {file_path}.")
    if file_path.suffix != ".txt":
        raise ValueError("File is not in the correct format.")

    with file_path.open(mode='r') as f:
        file_content = f.read()

    file_content = file_content.split(" ")

    return file_content


def compare_init(encryption_keys: list[list[str]], record_indexing: dict, index: int, permutation: list, descending: bool, mid_point: int):
    """  """

    # Client
    index_a, index_b = index, index + mid_point
    key_streams = [get_key_streams(), get_key_streams()]

    # Server
    name_record_a, name_record_b = [record_indexing[index_a], record_indexing[index_b]]
    record_a, record_b = encode_file(name_record_a), encode_file(name_record_b)
    records = [record_a, record_b]

    swap = 0
    # Compares them based on permutation
    permutation_a, permutation_b = permutation[index_a], permutation[index_b]
    if (permutation_a > permutation_b and not descending) or (permutation_b > permutation_a and descending):
        # Swaps indexing
        name_record_a, name_record_b = name_record_b, name_record_a
        permutation_a, permutation_b = permutation_b, permutation_a
        swap = 1

    # Updates indexing
    record_indexing[index_a], record_indexing[index_b] = name_record_a, name_record_b
    permutation[index_a], permutation[index_b] = permutation_a, permutation_b

    # Updates encryption keys indexing
    encryption_keys[index_a], encryption_keys[index_b] = key_streams

    # Executes the mpc encryption and comparison
    file_names = [f"{index_a}.txt", f"{index_b}.txt"]
    write_as_MP_SPDZ_inputs(swap, records, key_streams)
    encrypt_record()
    write_MP_SDPZ_output_to_encrypted_database(file_names)

    if not swap:
        print(f"{index_a}   plaintext: {records[0][0]}, key_stream: {key_streams[0][0]}")
        print(f"{index_b}   plaintext: {records[1][0]}, key_stream: {key_streams[1][0]}")
    else:
        print(f"{index_a}   plaintext: {records[1][0]}, key_stream: {key_streams[0][0]}")
        print(f"{index_b}   plaintext: {records[0][0]}, key_stream: {key_streams[1][0]}")


def compare(encryption_keys: list[list[str]], index: int, permutation: list, descending: bool, mid_point: int):
    """

    :return:
    """

    # Client
    index_record_a, index_record_b = index, index + mid_point
    key_streams = [encryption_keys[index_record_a], encryption_keys[index_record_b]]
    new_key_streams = [get_key_streams(), get_key_streams()]

    # Server
    name_record_a = encrypted_PNR_records_directory() / f"{index_record_a}.txt"
    name_record_b = encrypted_PNR_records_directory() / f"{index_record_b}.txt"
    record_a, record_b = read_ciphertexts(name_record_a), read_ciphertexts(name_record_b)
    records = [record_a, record_b]

    swap = 0
    # Compares them based on permutation
    permutation_a, permutation_b = permutation[index], permutation[index + mid_point]
    if (permutation_a > permutation_b and not descending) or (permutation_b > permutation_a and descending):
        # Swaps indexing
        index_record_a, index_record_b = index_record_b, index_record_a
        permutation_a, permutation_b = permutation_b, permutation_a
        swap = 1

    # Updates indexing
    permutation[index], permutation[index + mid_point] = permutation_a, permutation_b

    # Updates encryption keys indexing
    encryption_keys[index_record_a], encryption_keys[index_record_b] = new_key_streams

    # Executes the mpc encryption and comparison
    file_names = [f"{index_record_a}.txt", f"{index_record_b}.txt"]

    write_as_MP_SPDZ_inputs(swap, records, key_streams, new_key_streams)
    reencrypt_record()
    write_MP_SDPZ_output_to_encrypted_database(file_names)

    if not swap:
        print(f"{index}   ciphertext: {records[0][0]}, new_key_stream: {new_key_streams[0][0]}")
        print(f"{index + mid_point}   ciphertext: {records[1][0]}, key_stream: {new_key_streams[1][0]}")
    else:
        print(f"{index + mid_point}   ciphertext: {records[0][0]}, key_stream: {new_key_streams[0][0]}")
        print(f"{index}   ciphertext: {records[1][0]}, new_key_stream: {new_key_streams[1][0]}")


def init(indexing: dict, permutation: list) -> list[list[str]]:
    """

    :return:
    """

    encryption_keys = [[] for i in range(database_size())]

    partition_size = 2
    partition_mid_point = partition_size // 2

    descending = False
    for index in range(0, database_size(), partition_size):

        #   Parallelizable to log_2(n) processes
        compare_init(encryption_keys, indexing, index, permutation, descending, partition_mid_point)

        descending = (descending + 1) % 2

    return encryption_keys


def merge_partition(encryption_keys: list[list[str]], descending: bool, permutation: list, partition_index: int, partition_mid_point: int):
    """

    :return:
    """

    for value in range(partition_mid_point):
        index = partition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(encryption_keys, index, permutation, descending, partition_mid_point)


def merge(encryption_keys: list[list[str]], permutation: list, partition_size, partition_mid_point: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        merge_partition(encryption_keys, descending, permutation, partition_index, partition_mid_point)

        descending = (descending + 1) % 2


def sort_subpartition(encryption_keys: list[list[str]], permutation: list,descending: bool, partition_index: int, subpartition_index: int,
                      subpartition_mid_point: int):
    """

    :return:
    """

    for value in range(subpartition_mid_point):
        index = partition_index + subpartition_index + value

        #   Parallelizable to log_(partition_split)(n) processes
        compare(encryption_keys, index, permutation, descending, subpartition_mid_point)


def sort_partition(encryption_keys: list[list[str]], permutation: list, descending: bool, partition_size: int, partition_index: int):
    """

    :return:
    """

    for sublevel in range(-int(log(partition_size, 2)) + 1, 0):
        subpartition_size = 2 ** (sublevel * -1)
        subpartition_mid_point = subpartition_size // 2

        for subpartition_index in range(0, partition_size, subpartition_size):

            #  Parallelizable to log_(subpartition_size)(n) processes
            sort_subpartition(encryption_keys, permutation, descending, partition_index, subpartition_index,
                              subpartition_mid_point)


def sort(encryption_keys: list[list[str]], permutation: list, partition_size: int):
    """

    :return:
    """

    descending = False
    for partition_index in range(0, database_size(), partition_size):

        #   Parallelizable to log_(partition_size)(n) processes
        sort_partition(encryption_keys, permutation, descending, partition_size, partition_index)

        descending = (descending + 1) % 2


def bitonic_sort() -> tuple[dict, list[list[str]]]:
    """

    :param array_size:
    :param working_directory:
    :return:
    """

    if not log(database_size(), 2).is_integer():
        raise ValueError("Array size has to be of power 2.")

    # Server's indexing of the same files
    # file_names = [path for path in PNR_records_directory().glob('*') if path.name not in excluded()]
    # Sorting the record names for clarity so that it matches its index
    file_names = sorted([path for path in PNR_records_directory().glob('*') if path.name not in excluded_PNR_records()],
                        key=lambda x: int(findall(r"\d+", string=x.name)[0]))
    record_indexing = dict(enumerate(file_names))
    # permutation = random.permutation(database_size()).tolist()

    # Creates new indexing of the shuffeled database
    permutation = [2, 5, 4, 6, 3, 0, 7, 1]
    index_translation = dict(enumerate(permutation))

    # Initializes the encrypted databases and sorts the first level
    encryption_keys = init(record_indexing, permutation)

    # Completes the sorting of the encrypted database
    #for level in range(2, int(log(database_size(), 2) + 1)):  # Skip 2**1 as it was done in the initiation
    #    partition_size = 2 ** level
    #    partition_mid_point = partition_size // 2

    #    merge(encryption_keys, permutation, partition_size, partition_mid_point)

    #    sort(encryption_keys, permutation, partition_size)

    for i in range(len(encryption_keys)):
        print(f"stored keys {i}: {encryption_keys[i][0]}")

    return index_translation, encryption_keys
