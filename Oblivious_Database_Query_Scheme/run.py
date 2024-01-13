""" Runs the oblivious data query scheme """

from subprocess import run
from os import chdir
from json import load
from Oblivious_Database_Query_Scheme.getters import working_directory_validation, MP_SPDZ_directory_validation
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_directory as MP_SPDZ_directory
from Oblivious_Database_Query_Scheme.getters import get_working_directory as working_directory
from Oblivious_Database_Query_Scheme.getters import get_MP_SDPZ_compile_path as MP_SPDZ_compile_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_encrypt_mpc_script_path as compare_and_encrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_compare_and_reencrypt_mpc_script_path as compare_and_reencrypt_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_aes_128_mpc_script_path as aes_128_mpc_script_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_scripts_directory as MP_SDPZ_scripts_directory
from Oblivious_Database_Query_Scheme.getters import get_permutation_indexing_path as permutation_indexing_path
from Oblivious_Database_Query_Scheme.getters import get_encrypted_inverted_index_matrix_path as encrypted_inverted_index_matrix_path
from Oblivious_Database_Query_Scheme.getters import get_encrypted_PNR_records_directory as encrypted_PNR_records_directory
from Oblivious_Database_Query_Scheme.getters import get_records_encryption_key_streams_directory as encryption_key_streams_directory
from Oblivious_Database_Query_Scheme.getters import get_if_else_circuit_path as if_else_circuit_path
from Oblivious_Database_Query_Scheme.getters import get_MP_SPDZ_circuits_directory as MP_SPDZ_circuits_directory


from Client.Networking.client import Communicate as Client
from Client.Preprocessing.bitonic_sort import bitonic_sort as permute_and_encrypt_database
from Client.Encoding.file_decryptor import run as decrypt_files

from Server.Networking.server import Communicate as Server


def setup_MPC_scripts():
    """

    """

    chdir(MP_SPDZ_directory())

    run(["cp", f"{if_else_circuit_path()}", f"{MP_SPDZ_circuits_directory() / if_else_circuit_path().name}"])

    run(["cp", f"{compare_and_encrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_encrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_encrypt_mpc_script_path().name}", "-F", "128"])
    run(["cp", f"{compare_and_reencrypt_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / compare_and_reencrypt_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{compare_and_reencrypt_mpc_script_path().name}", "-F", "128"])
    run(["cp", f"{aes_128_mpc_script_path()}", f"{MP_SDPZ_scripts_directory() / aes_128_mpc_script_path().name}"])
    run([f"{MP_SPDZ_compile_path()}", f"{aes_128_mpc_script_path().name}", "-F", "128"])

    chdir(working_directory())


if __name__ == '__main__':
    # Sets the working directory and validates it and MP-SPDZ's path
    working_directory_validation()
    MP_SPDZ_directory_validation()

    # Moves and compiles the MP-SDPZ scripts
    setup_MPC_scripts()

    server = Server()
    client = Client()

    # Initializes the database with PNR records
    server.create_database()

    # Creates an inverted index matrix of the database
    server.create_indexing()

    # Creates a new secret database
    client.send_init()
    permute_and_encrypt_database(client)

    with permutation_indexing_path().open('r') as file:
        indexing = load(file)
        file.close()

    # Searching with file retrieval
    while True:

        # Ephemeral encryption of the indexing
        server.encrypt_indexing()

        with encrypted_inverted_index_matrix_path().open("r") as file:
            encrypted_inverted_index_matrix = load(file)
            file.close()

        search_query = input("Search Query: ")
        if search_query == "exit":
            break

        encrypted_query = client.send_query(search_query)

        pointers = encrypted_inverted_index_matrix[encrypted_query]

        for pointer in pointers:
            true_index = indexing[pointer]

            ciphertext_path = encrypted_PNR_records_directory() / f"{true_index}.txt"

            key_streams_path = encryption_key_streams_directory() / f"{true_index}.txt"
            with key_streams_path.open("r") as file:
                record_encryption_keys = file.read().split(" ")
                file.close()

            with ciphertext_path.open("r") as file:
                ciphertexts = file.read().split(" ")
                file.close()

            decrypt_files([ciphertexts], [record_encryption_keys])

    server.kill()
    client.kill()
